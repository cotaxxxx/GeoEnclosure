"""Reconstruct the cover and re-enclose its signs with independent integer arithmetic."""

import argparse
from datetime import datetime
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
# With python -I the script directory is not searched automatically.
sys.path.insert(0,str(HERE))
from rational_series import Series


def need(condition,message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    return json.loads(path.read_text())


def read_jsonl(path):
    with path.open(encoding="utf-8") as stream:
        for row in stream:
            need(row.endswith("\n"),f"truncated record in {path.name}")
            yield json.loads(row)


def two(values):
    need(len(values)==2,"wrong interval arity")
    lo,hi = map(Q,values)
    need(lo<=hi,"inverted rational interval")
    return lo,hi


def decode_dyad(a):
    n,exponent = a
    need(isinstance(n,str) and re.fullmatch(r"-?[0-9]+",n) is not None
         and type(exponent) is int,"invalid dyadic endpoint")
    return int(n)*Q(2)**exponent


def read_sign(interval):
    l,r = interval
    return -1 if r<0 else 1 if l>0 else 0


def decimal_box(interval,digits):
    scale = 10**digits
    lo,hi = (x*scale for x in interval)
    ns = lo.numerator//lo.denominator,-((-hi.numerator)//hi.denominator)
    result = []
    for k in ns:
        integer,decimals = divmod(abs(k),scale)
        result.append(f"{'-' if k<0 else ''}{integer}.{decimals:0{digits}d}")
    return result


class Tape:
    def __init__(self, rows, cfg, secondary):
        self.rows = iter(rows)
        self.cfg = cfg
        self.secondary = secondary
        self.index = 0
        self.cache = {}

    def take(self, attempts, kind, parameter_box):
        precision = self.cfg["precisions"]
        need(1<=len(attempts)<=len(precision),"invalid precision attempt count")
        if (kind,parameter_box) not in self.cache:
            self.cache[kind,parameter_box] = self.secondary.enclose(kind,*parameter_box)
        separate = self.cache[kind,parameter_box]
        good = False
        for k,ident in enumerate(attempts):
            need(not good,"additional evaluation after the specified guard succeeded")
            row = next(self.rows,None)
            self.index += 1
            need(row is not None and ident==row["id"]==f"E{self.index:04d}"
                 and row["mode"]==kind and precision[k]==row["precision"]
                 and two(row["box"])==parameter_box,"evaluation order or box does not match")
            envelope = tuple(map(decode_dyad,row["endpoints"]))
            need(len(envelope)==2 and envelope[0]<=envelope[1],"bad MPFR interval")
            need(max(envelope[0],separate[0])<=min(envelope[1],separate[1]),
                 f"MPFR and series bounds are disjoint at {ident}")
            sign = read_sign(envelope)
            if kind in ("f","df") and sign:
                need(read_sign(separate)==sign,f"strict sign not corroborated at {ident}")
            good = kind=="omega" or (kind=="f" and bool(sign)) or (kind=="df" and sign==1)
        need(good or len(attempts)==len(precision),"precision ladder ended before its criterion")
        return ident,envelope

    def done(self):
        need(next(self.rows,None) is None,"unused evaluation records")


def expected_cell(low,high,status):
    e0,r0,i0 = low
    e1,r1,i1 = high
    return {"box":[str(e0),str(e1)],"interval":[str(i0[0]),str(i1[1])],
            "status":status,"method":"mpfr_endpoints_monotonicity",
            "left_eval":r0,"right_eval":r1,"left_open":False,"right_open":False}


def tails(cfg):
    left,right = cfg["central"]
    return [
        {"box":["0",left],"interval":cfg["small_e_bounds"],"status":"NEGATIVE",
         "method":"small_e_remainder","left_open":True,"right_open":False},
        {"box":[right,"1"],"interval":cfg["small_q_bounds"],"status":"POSITIVE",
         "method":"small_q_remainder","left_open":False,"right_open":True},
    ]


def verify_math(path,cfg,second):
    result = read_json(path/"RESULT.json")
    need(result["status"]=="RECORDED" and result["grade"]=="DIAGNOSTIC_ONLY",
         "no complete numerical record to check")
    tape = Tape(read_jsonl(path/"EVALUATIONS.jsonl"),cfg,second)
    target = Q(cfg["target_width"])
    a,b = map(Q,cfg["central"])
    anchor_l,anchor_r = result["anchors"]
    left,right = (a,*tape.take(anchor_l,"f",(a,a))),(b,*tape.take(anchor_r,"f",(b,b)))
    need(read_sign(left[2])==-1 and read_sign(right[2])==1,"anchor signs")
    expected = tails(cfg)
    steps = 0
    for record in read_jsonl(path/"STEPS.jsonl"):
        steps += 1
        a,b = left[0],right[0]
        need(steps==record["step"]<=cfg["max_steps"] and two(record["before"])==(a,b)
             and b-a>target,"inconsistent step or stop criterion")
        mid = (a+b)/2
        attempts = record["probes"]
        m = (mid,*tape.take(attempts[0],"f",(mid,mid)))
        expected_probes = [m]
        if read_sign(m[2])==0:
            need(len(attempts)==3,"indeterminate midpoint requires both quarter points")
            for x,trial in zip((a+(b-a)/4,b-(b-a)/4),attempts[1:]):
                expected_probes.append((x,*tape.take(trial,"f",(x,x))))
        else:
            need(len(attempts)==1,"decisive midpoint must finish the step")
        new_l,new_r = left,right
        for item in sorted(expected_probes):
            s = read_sign(item[2])
            if s==-1 and item[0]>new_l[0]:
                new_l=item
            elif s==1 and item[0]<new_r[0]:
                new_r=item
        l,r = new_l[0],new_r[0]
        need((l,r)==two(record["after"]) and a<=l<r<=b and r-l<b-a,
             "recorded child is not the strict retained bracket")
        if l>a:
            expected.append(expected_cell(left,new_l,"NEGATIVE"))
        if r<b:
            expected.append(expected_cell(new_r,right,"POSITIVE"))
        left,right = new_l,new_r
    lo,hi = left[0],right[0]
    need(hi-lo<=target and Q(result["width"])==hi-lo and two(result["root"])==(lo,hi)
         and result["left_eval"]==left[1] and result["right_eval"]==right[1],
         "root bracket summary or width differs")
    expected.append(expected_cell(left,right,"ROOT_BRACKET"))
    _,df = tape.take(result["derivative_checks"],"df",(lo,hi))
    need(df[0]>0 and df==two(result["df_interval"]),"root derivative is not strictly positive")
    _,rotation = tape.take(result["omega_checks"],"omega",(lo,hi))
    need(rotation==two(result["omega_mpfr"]),"rotation summary differs")
    tape.done()
    expected.sort(key=lambda c:Q(c["box"][0]))
    rows = list(read_jsonl(path/"SIGN_LEDGER.jsonl"))
    need(expected==rows,"signed ledger differs from the reconstructed cover")
    end = Q(0)
    for k,row in enumerate(rows):
        l,r = two(row["box"])
        need(l==end and l<r and row["left_open"]==(k==0) and
             row["right_open"]==(k==len(rows)-1),"gap, overlap or wrong endpoint inclusion")
        end = r
        sign = read_sign(two(row["interval"]))
        need(sign=={"NEGATIVE":-1,"POSITIVE":1,"ROOT_BRACKET":0}[row["status"]],
             "cell enclosure does not have its declared sign")
    need(end==1,"cover did not reach one")
    independent_omega = tape.cache["omega",(lo,hi)]
    hull = (min(rotation[0],independent_omega[0]),max(rotation[1],independent_omega[1]))
    digits = cfg["display_digits"]
    displayed_e = decimal_box((lo,hi),digits)
    a,b = two(displayed_e)
    need(a<=lo<hi<=b and b-a<=Q(1,10**15),"outward decimal root bracket exceeded 1e-15")
    return {"grade":"DIAGNOSTIC_ONLY","status":"CHECKS_RECORDED","unique_root":True,
            "e_interval_exact":list(map(str,(lo,hi))),"e_interval_display":displayed_e,
            "e_display_width":str(b-a),"omega_interval_display":decimal_box(hull,digits),
            "omega_mpfr":list(map(str,rotation)),
            "omega_series":list(map(str,independent_omega)),
            "derivative_mpfr":list(map(str,df)),
            "derivative_series":list(map(str,tape.cache["df",(lo,hi)])),
            "steps":steps,"raw_evaluations":tape.index,"cover_boxes":len(rows)}


def verify_manifest(path,cfg):
    data = read_json(path/"MANIFEST.json")
    require = re.compile("[0-9a-f]{40}").fullmatch
    need(require(data["execution_approval"]) and require(data["bundle_commit"]) and
         data["execution_approval"]!=data["bundle_commit"],"missing execution provenance")
    start = datetime.fromisoformat(data["started_utc"])
    minimum = datetime.fromisoformat(cfg["research_pc_not_before"])
    end = datetime.fromisoformat(data["candidate_b_v2_ended_at"])
    need(start>=minimum and start>=end and data["candidate_b_v2_end_record"].strip(),
         "execution did not follow Candidate B v2 and the allowed time")
    build = read_json(path/"BUILD.json")
    need(data["build"]==build and build["gmp_limb_bits"]==64 and
         build["compile_log_sha256"]==sha(path/"compile.log") and
         build["k1_sha256"]==sha(path/"K1.log"),"build receipt mismatch")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_hashes(path):
    rows = [(name,digest) for digest,name in (s.split("  ",1) for s in
                                             (path/"RESULT_SHA256SUMS.txt").read_text().splitlines())]
    names = {x.name for x in path.iterdir() if x.is_file()}-{"RESULT_SHA256SUMS.txt"}
    need(len(rows)==len(names) and {name for name,_ in rows}==names,"checksum file set differs")
    for name,digest in rows:
        need(sha(path/name)==digest,f"result digest mismatch: {name}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--unsealed",action="store_true")
    parser.add_argument("output",type=Path)
    args = parser.parse_args()
    try:
        frozen = HERE/"PLAN_INPUTS.json"
        need(frozen.read_bytes()==(args.output/frozen.name).read_bytes(),"frozen inputs differ")
        cfg = read_json(frozen)
        if not args.unsealed:
            verify_hashes(args.output)
        verify_manifest(args.output,cfg)
        series = Series(cfg["fixed_grid_bits"],cfg["series_terms"])
        verified = verify_math(args.output,cfg,series)
        if not args.unsealed:
            need(read_json(args.output/"INDEPENDENT_CHECK.json")==verified,
                 "sealed verification output differs from this reading")
    except (OSError,ValueError,KeyError,TypeError,IndexError,ArithmeticError) as error:
        print(json.dumps(dict(grade="DIAGNOSTIC_ONLY",status="UNRESOLVED",reason=str(error))))
        return 2
    print(json.dumps(verified,indent=2))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
