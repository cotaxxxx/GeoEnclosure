#include <assert.h>
#include <gmp.h>
#include <mpfr.h>
#include <stddef.h>

typedef struct { mpfr_t lo,hi; } Interval;
typedef struct {
    Interval buf[64];
    size_t used;
    mpfr_prec_t precision;
    mpfr_t temporary;
    int invalid;
} Arithmetic;
typedef struct {
    char lo[192],hi[192];
    long lo_exp,hi_exp;
} Bounds;

static void setup(Arithmetic *a, mpfr_prec_t precision) {
    a->used = 0;
    a->precision = precision;
    a->invalid = 0;
    mpfr_init2(a->temporary,precision);
}

static void release(Arithmetic *a) {
    for (size_t k=0;k<a->used;k++) {
        mpfr_clear(a->buf[k].lo);
        mpfr_clear(a->buf[k].hi);
    }
    mpfr_clear(a->temporary);
}

static Interval *slot(Arithmetic *a) {
    assert(a->used<sizeof(a->buf)/sizeof(a->buf[0]));
    Interval *v = &a->buf[a->used++];
    mpfr_init2(v->lo,a->precision);
    mpfr_init2(v->hi,a->precision);
    return v;
}

static Interval *integer(Arithmetic *a, long k) {
    Interval *v = slot(a);
    mpfr_set_si(v->lo,k,MPFR_RNDD);
    mpfr_set_si(v->hi,k,MPFR_RNDU);
    return v;
}

static Interval *rational_box(Arithmetic *a, mpq_srcptr lo, mpq_srcptr hi) {
    Interval *v = slot(a);
    mpfr_set_q(v->lo,lo,MPFR_RNDD);
    mpfr_set_q(v->hi,hi,MPFR_RNDU);
    return v;
}

static Interval *add(Arithmetic *a, const Interval *x, const Interval *y) {
    Interval *v = slot(a);
    mpfr_add(v->lo,x->lo,y->lo,MPFR_RNDD);
    mpfr_add(v->hi,x->hi,y->hi,MPFR_RNDU);
    return v;
}

static Interval *sub(Arithmetic *a, const Interval *x, const Interval *y) {
    Interval *v = slot(a);
    mpfr_sub(v->lo,x->lo,y->hi,MPFR_RNDD);
    mpfr_sub(v->hi,x->hi,y->lo,MPFR_RNDU);
    return v;
}

static Interval *corners(Arithmetic *a, const Interval *x, const Interval *y, int divide) {
    Interval *v = slot(a);
    if (divide && mpfr_sgn(y->lo)<=0) {
        a->invalid = 1;
        mpfr_set_zero(v->lo,1);
        mpfr_set_zero(v->hi,1);
        return v;
    }
    mpfr_srcptr xx[] = {x->lo,x->hi};
    mpfr_srcptr yy[] = {y->lo,y->hi};
    int (*operation)(mpfr_ptr,mpfr_srcptr,mpfr_srcptr,mpfr_rnd_t) = divide ? mpfr_div : mpfr_mul;
    operation(v->lo,xx[0],yy[0],MPFR_RNDD);
    operation(v->hi,xx[0],yy[0],MPFR_RNDU);
    for (int k=1;k<4;k++) {
        operation(a->temporary,xx[k/2],yy[k%2],MPFR_RNDD);
        if (mpfr_cmp(a->temporary,v->lo)<0) mpfr_set(v->lo,a->temporary,MPFR_RNDD);
        operation(a->temporary,xx[k/2],yy[k%2],MPFR_RNDU);
        if (mpfr_cmp(a->temporary,v->hi)>0) mpfr_set(v->hi,a->temporary,MPFR_RNDU);
    }
    return v;
}

static Interval *mul(Arithmetic *a, const Interval *x, const Interval *y) {
    return corners(a,x,y,0);
}

static Interval *div_positive(Arithmetic *a, const Interval *x, const Interval *y) {
    return corners(a,x,y,1);
}

static Interval *scale(Arithmetic *a, long k, const Interval *x) {
    return mul(a,integer(a,k),x);
}

static Interval *sqrt_interval(Arithmetic *a, const Interval *x) {
    Interval *v = slot(a);
    if (mpfr_sgn(x->lo)<0) {
        a->invalid = 1;
        mpfr_set_zero(v->lo,1);
        mpfr_set_zero(v->hi,1);
        return v;
    }
    mpfr_sqrt(v->lo,x->lo,MPFR_RNDD);
    mpfr_sqrt(v->hi,x->hi,MPFR_RNDU);
    return v;
}

static Interval *asin_interval(Arithmetic *a, const Interval *x) {
    Interval *v = slot(a);
    mpfr_asin(v->lo,x->lo,MPFR_RNDD);
    mpfr_asin(v->hi,x->hi,MPFR_RNDU);
    return v;
}

static int encode(mpfr_srcptr value, char *out, long *exp) {
    if (!mpfr_number_p(value)) return 0;
    if (mpfr_zero_p(value)) {
        out[0] = '0';
        out[1] = '\0';
        *exp = 0;
        return 1;
    }
    mpz_t z;
    mpz_init(z);
    *exp = mpfr_get_z_2exp(z,value);
    int ok = mpz_sizeinbase(z,10)+2<=192;
    if (ok) mpz_get_str(out,10,z);
    mpz_clear(z);
    return ok;
}

static int finish(const Arithmetic *a, const Interval *v, Bounds *out) {
    return (!a->invalid && mpfr_number_p(v->lo) && mpfr_number_p(v->hi) &&
            mpfr_cmp(v->lo,v->hi)<=0 &&
            encode(v->lo,out->lo,&out->lo_exp) &&
            encode(v->hi,out->hi,&out->hi_exp)) ? 0 : 3;
}

static int read_rational(mpq_ptr v, const char *s) {
    if (mpq_set_str(v,s,10)!=0 || mpz_sgn(mpq_denref(v))==0) return 0;
    mpq_canonicalize(v);
    return 1;
}

static Interval *formula(Arithmetic *a, int mode, const Interval *e) {
    const Interval *one = integer(a,1);
    const Interval *three = integer(a,3);
    const Interval *s = mul(a,e,e);
    const Interval *q2 = sub(a,one,s);
    const Interval *q = sqrt_interval(a,q2);
    const Interval *alpha = asin_interval(a,e);
    if (mode==2) {
        const Interval *shape = sub(a,three,scale(a,2,s));
        const Interval *first = scale(a,2,mul(a,mul(a,q,shape),alpha));
        const Interval *second = scale(a,6,q2);
        return sub(a,div_positive(a,first,mul(a,e,s)),div_positive(a,second,s));
    }
    const Interval *P = add(a,three,scale(a,8,mul(a,s,q2)));
    const Interval *Q = mul(a,e,add(a,three,scale(a,10,s)));
    const Interval *N = sub(a,mul(a,P,alpha),mul(a,q,Q));
    const Interval *e4 = mul(a,s,s);
    if (mode==0) return div_positive(a,N,scale(a,4,mul(a,e4,e)));
    const Interval *dP = scale(a,16,mul(a,e,sub(a,one,scale(a,2,s))));
    const Interval *dQ = add(a,three,scale(a,30,s));
    const Interval *base = add(a,mul(a,dP,alpha),div_positive(a,P,q));
    const Interval *moving = sub(a,div_positive(a,mul(a,e,Q),q),mul(a,q,dQ));
    const Interval *dN = add(a,base,moving);
    const Interval *value = sub(a,mul(a,e,dN),scale(a,5,N));
    return div_positive(a,value,scale(a,4,mul(a,e4,s)));
}

/* Modes: 0 F, 1 dF/de, 2 Omega^2/(pi G rho). */
int mjb_enclose(int mode, int bits, const char *lower, const char *upper, Bounds *out) {
    if (mode<0 || mode>2 || (bits!=128 && bits!=256 && bits!=512)) return 2;
    mpq_t lo,hi;
    mpq_inits(lo,hi,(mpq_ptr)0);
    int valid = read_rational(lo,lower) && read_rational(hi,upper) &&
        mpq_cmp(lo,hi)<=0 && mpq_cmp_ui(lo,1,8)>=0 && mpq_cmp_ui(hi,63,64)<=0;
    if (!valid) {
        mpq_clears(lo,hi,(mpq_ptr)0);
        return 2;
    }
    Arithmetic a;
    setup(&a,bits);
    Interval *input = rational_box(&a,lo,hi);
    mpq_clears(lo,hi,(mpq_ptr)0);
    Interval *value = formula(&a,mode,input);
    int status = finish(&a,value,out);
    release(&a);
    return status;
}

/* An arithmetic fixture with no call to formula(). */
int mjb_arithmetic_fixture(Bounds *out) {
    Arithmetic a;
    setup(&a,128);
    const Interval *r = div_positive(&a,sqrt_interval(&a,integer(&a,2)),integer(&a,3));
    const Interval *half = div_positive(&a,integer(&a,1),integer(&a,2));
    const Interval *zero = asin_interval(&a,integer(&a,0));
    const Interval *value = sub(&a,add(&a,r,zero),half);
    int status = finish(&a,value,out);
    release(&a);
    return status;
}
