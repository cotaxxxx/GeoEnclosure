"""Run the fixed MPFR bisection after the scheduled Judge execution approval."""

import argparse
from contextlib import ExitStack
from ctypes import CDLL, POINTER, Structure, byref, c_char, c_char_p, c_int, c_long
from dataclasses import dataclass
from datetime import datetime, timezone
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys


HERE = Path(__file__).resolve().parent
MODE = {"f": 0, "df": 1, "omega": 2}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path,data):
    with path.open("x",encoding="utf-8") as target:
        target.write(json.dumps(data,ensure_ascii=False,indent=2)+"\n")


def line(target,data):
    target.write(json.dumps(data,separators=(",",":"))+"\n")


class Bounds(Structure):
    _fields_ = [("lo",c_char*192),("hi",c_char*192),("lo_exp",c_long),("hi_exp",c_long)]


class Kernel:
    def __init__(self,path):
        self.lib = CDLL(str(path))
        self.lib.mjb_enclose.argtypes = [c_int,c_int,c_char_p,c_char_p,POINTER(Bounds)]
        self.lib.mjb_enclose.restype = c_int

    def evaluate(self,mode,bits,lower,upper):
        a,b = (str(x).encode("ascii") for x in (lower,upper))
        output = Bounds()
        status = self.lib.mjb_enclose(MODE[mode],bits,a,b,byref(output))
        if status:
            raise ValueError(f"MPFR kernel rejected {mode} on [{lower},{upper}]: status {status}")
        return ([output.lo.decode("ascii"),int(output.lo_exp)],
                [output.hi.decode("ascii"),int(output.hi_exp)])


@dataclass(frozen=True)
class Evaluation:
    ident: str
    left: Q
    right: Q
    bound: tuple

    @property
    def sign(self):
        return 1 if self.bound[0]>0 else -1 if self.bound[1]<0 else 0


def monotone_cell(left,right,status):
    return dict(box=[str(left.left),str(right.right)],
                interval=[str(left.bound[0]),str(right.bound[1])],
                status=status,method="mpfr_endpoints_monotonicity",
                left_eval=left.ident,right_eval=right.ident,
                left_open=False,right_open=False)


def analytic_cells(cfg):
    a,b = cfg["central"]
    return [
        dict(box=["0",a],interval=cfg["small_e_bounds"],status="NEGATIVE",
             method="small_e_remainder",left_open=True,right_open=False),
        dict(box=[b,"1"],interval=cfg["small_q_bounds"],status="POSITIVE",
             method="small_q_remainder",left_open=False,right_open=True),
    ]


def solve(kernel,cfg,evaluations,steps,state,box_records):
    serial = 0

    def probe(mode,lo,hi):
        nonlocal serial
        attempts = []
        for bits in cfg["precisions"]:
            ends = kernel.evaluate(mode,bits,lo,hi)
            bound = tuple(Q(int(n))*Q(2)**exp for n,exp in ends)
            if bound[0]>bound[1]:
                raise ValueError("reversed MPFR enclosure")
            serial += 1
            ident = f"E{serial:04d}"
            line(evaluations,dict(id=ident,mode=mode,precision=bits,box=[str(lo),str(hi)],
                                  endpoints=ends))
            last = Evaluation(ident,lo,hi,bound)
            attempts.append(ident)
            if mode=="omega" or mode=="f" and last.sign or mode=="df" and last.sign==1:
                break
        return last,attempts

    a,b = map(Q,cfg["central"])
    width = Q(cfg["target_width"])
    left,la = probe("f",a,a)
    right,ra = probe("f",b,b)
    state["anchors"] = [la,ra]
    if left.sign!=-1 or right.sign!=1:
        raise ValueError("MPFR did not confirm the opposite anchor signs")
    for index in range(1,cfg["max_steps"]+1):
        u,v = left.left,right.right
        if v-u<=width:
            break
        m = (u+v)/2
        middle,ma = probe("f",m,m)
        probes = [ma]
        points = [middle]
        if not middle.sign:
            for x in ((3*u+v)/4,(u+3*v)/4):
                found,attempts = probe("f",x,x)
                points.append(found)
                probes.append(attempts)
        neg = max([left]+[p for p in points if p.sign==-1],key=lambda p:p.left)
        pos = min([right]+[p for p in points if p.sign==1],key=lambda p:p.right)
        line(steps,dict(step=index,before=[str(u),str(v)],probes=probes,
                        after=[str(neg.left),str(pos.right)]))
        if neg.left>=pos.right:
            raise ValueError("signs are inconsistent with monotonicity")
        if neg==left and pos==right:
            raise ValueError("neither endpoint could advance")
        if neg.left>u:
            box_records.append(monotone_cell(left,neg,"NEGATIVE"))
        if pos.right<v:
            box_records.append(monotone_cell(pos,right,"POSITIVE"))
        left,right = neg,pos
        state["last_bracket"] = [str(left.left),str(right.right)]
    lo,hi = left.left,right.right
    if hi-lo>width:
        raise ValueError("bisection limit before target width")
    derivative,da = probe("df",lo,hi)
    state["derivative_checks"] = da
    if derivative.sign!=1:
        raise ValueError("root interval derivative guard did not separate from zero")
    omega,oa = probe("omega",lo,hi)
    state["omega_checks"] = oa
    box_records.append(monotone_cell(left,right,"ROOT_BRACKET"))
    state.update(status="RECORDED",root=[str(lo),str(hi)],width=str(hi-lo),
                 left_eval=left.ident,right_eval=right.ident,
                 df_interval=list(map(str,derivative.bound)),omega_mpfr=list(map(str,omega.bound)))


def preflight():
    static = json.loads((HERE/"MANIFEST.json").read_text())
    expected = dict(static["files"],**{"MANIFEST.json":digest(HERE/"MANIFEST.json")})
    checksum = [(name,h) for h,name in (s.split("  ",1) for s in
                                        (HERE/"SHA256SUMS.txt").read_text().splitlines())]
    if len(checksum)!=len(expected) or dict(checksum)!=expected:
        raise ValueError("bundle checksum list differs from the manifest")
    for name,sha in expected.items():
        if digest(HERE/name)!=sha:
            raise ValueError(f"bundle digest mismatch for {name}")
    build = json.loads((HERE/"build/BUILD.json").read_text())
    library = HERE/"build/libmacl_jacobi.so"
    if (build["library_sha256"]!=digest(library) or
        build["bundle_manifest_sha256"]!=expected["MANIFEST.json"] or
        build["compile_log_sha256"]!=digest(HERE/"build/compile.log") or
        build["k1_sha256"]!=digest(HERE/"build/K1.log") or build["gmp_limb_bits"]!=64):
        raise ValueError("build receipt differs from compiled kernel or saved logs")
    return static,build,library


def approvals(args,cfg):
    for commit in (args.bundle_commit,args.judge_execution):
        if not re.fullmatch("[0-9a-f]{40}",commit):
            raise ValueError("use the full bundle and execution approval Git commit hashes")
    if args.bundle_commit==args.judge_execution:
        raise ValueError("the Judge execution approval follows the bundle commit")
    now = datetime.now(timezone.utc)
    threshold = datetime.fromisoformat(cfg["research_pc_not_before"])
    end = datetime.fromisoformat(args.candidate_b_v2_ended_at)
    if end.tzinfo is None or not args.candidate_b_v2_end_record.strip():
        raise ValueError("provide the Candidate B v2 end time with offset and its record")
    if now<threshold or now<end:
        raise ValueError("wait for the Candidate B v2 end and for 18:14 JST")


def run(args):
    cfg = json.loads((HERE/"PLAN_INPUTS.json").read_text())
    approvals(args,cfg)
    static,build,location = preflight()
    output = args.output.resolve()
    output.mkdir(parents=True,exist_ok=False)
    started = datetime.now(timezone.utc).isoformat()
    names = ["PLAN_INPUTS.json","BUILD.json","HEADER.json","K1.log","compile.log"]
    shutil.copyfile(HERE/names[0],output/names[0])
    for name in names[1:]:
        shutil.copyfile(HERE/"build"/name,output/name)
    state = dict(grade="DIAGNOSTIC_ONLY",status="PARTIAL")
    records = analytic_cells(cfg)
    with ExitStack() as stack:
        evals,steps,ledger = (stack.enter_context((output/name).open("x",encoding="utf-8",
                                                                    buffering=1))
                              for name in ("EVALUATIONS.jsonl","STEPS.jsonl","SIGN_LEDGER.jsonl"))
        try:
            solve(Kernel(location),cfg,evals,steps,state,records)
        except (ValueError,OSError) as error:
            state.update(status="PARTIAL",reason=str(error))
        for row in sorted(records,key=lambda x:Q(x["box"][0])):
            line(ledger,row)
    save(output/"RESULT.json",state)
    manifest = dict(grade="DIAGNOSTIC_ONLY",bundle_commit=args.bundle_commit,
                    execution_approval=args.judge_execution,started_utc=started,
                    candidate_b_v2_ended_at=args.candidate_b_v2_ended_at,
                    candidate_b_v2_end_record=args.candidate_b_v2_end_record,
                    cmd=sys.argv,bundle=static,build=build)
    save(output/"MANIFEST.json",manifest)
    if state["status"]=="RECORDED":
        checked = subprocess.run([sys.executable,"-I","-B",str(HERE/"verify_certificate.py"),
                                  "--unsealed",str(output)],capture_output=True,text=True)
        with (output/"INDEPENDENT_CHECK.json").open("x",encoding="utf-8") as out:
            if checked.returncode==0:
                out.write(checked.stdout)
            else:
                json.dump(dict(status="UNRESOLVED",stdout=checked.stdout,stderr=checked.stderr),out)
                out.write("\n")
        returncode = checked.returncode
    else:
        save(output/"INDEPENDENT_CHECK.json",dict(status="UNRESOLVED",reason=state["reason"]))
        returncode = 2
    hashed = sorted(p for p in output.iterdir() if p.is_file())
    (output/"RESULT_SHA256SUMS.txt").write_text(
        "".join(f"{digest(path)}  {path.name}\n" for path in hashed),encoding="ascii")
    print((output/"INDEPENDENT_CHECK.json").read_text(),end="")
    return returncode


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle-commit",required=True)
    parser.add_argument("--judge-execution",required=True)
    parser.add_argument("--candidate-b-v2-ended-at",required=True)
    parser.add_argument("--candidate-b-v2-end-record",required=True)
    parser.add_argument("output",type=Path)
    return run(parser.parse_args())


if __name__=="__main__":
    raise SystemExit(main())
