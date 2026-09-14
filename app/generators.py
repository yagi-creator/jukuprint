import random
from fractions import Fraction

NZ = [i for i in range(-9, 10) if i != 0]

def _p(n): return f"({n})" if n < 0 else f"{n}"
def _lin(a, b, var="x"):
    parts = []
    if a != 0:
        if a == 1: parts.append(var)
        elif a == -1: parts.append(f"-{var}")
        else: parts.append(f"{a}{var}")
    if b != 0 or not parts:
        if not parts: parts.append(str(b))
        else: parts.append(f"+ {b}" if b > 0 else f"- {abs(b)}")
    return " ".join(parts)
def _quad(b, c, var="x"):
    s = f"{var}^2"
    if b != 0:
        coef = "" if abs(b) == 1 else str(abs(b))
        s += f" + {coef}{var}" if b > 0 else f" - {coef}{var}"
    if c != 0:
        s += f" + {c}" if c > 0 else f" - {abs(c)}"
    return s
def _frac(f: Fraction):
    if f.denominator == 1: return str(f.numerator)
    if f < 0: return f"-\\frac{{{abs(f.numerator)}}}{{{f.denominator}}}"
    return f"\\frac{{{f.numerator}}}{{{f.denominator}}}"
def _simp_sqrt(n):
    out, i = 1, 2
    while i * i <= n:
        while n % (i * i) == 0:
            n //= i * i
            out *= i
        i += 1
    return out, n
def _sqrt_tex(out, rest):
    if rest == 1: return str(out)
    if out == 1: return f"\\sqrt{{{rest}}}"
    return f"{out}\\sqrt{{{rest}}}"

def seifu_shisoku(rng):
    a, b, c = rng.choice(NZ), rng.choice(NZ), rng.choice(NZ)
    op = rng.choice(["+", "-"])
    ans = a + b * c if op == "+" else a - b * c
    return f"{a} {op} {_p(b)} \\times {_p(c)}", str(ans)

def bunsuu_kagen(rng):
    d1, d2 = rng.choice([2, 3, 4, 6]), rng.choice([2, 3, 4, 6])
    n1, n2 = rng.randint(1, d1 * 2), rng.randint(1, d2 * 2)
    f1, f2 = Fraction(n1, d1), Fraction(n2, d2)
    op = rng.choice(["+", "-"])
    ans = f1 + f2 if op == "+" else f1 - f2
    return f"{_frac(f1)} {op} {_frac(f2)}", _frac(ans)

def moji_shiki(rng):
    a, b, c, d = rng.choice(NZ), rng.choice(NZ), rng.choice(NZ), rng.choice(NZ)
    return f"({_lin(a, b)}) - ({_lin(c, d)})", _lin(a - c, b - d)

def ichiji_houteishiki(rng):
    x0 = rng.choice(NZ)
    a, c = rng.choice(NZ), rng.choice(NZ)
    while a == c: c = rng.choice(NZ)
    b = rng.choice(NZ)
    d = a * x0 + b - c * x0
    return f"{_lin(a, b)} = {_lin(c, d)}", f"x = {x0}"

def renritsu(rng):
    x0, y0 = rng.choice(NZ), rng.choice(NZ)
    a1, b1 = rng.choice([1, 2, 3, -1, -2]), rng.choice([1, 2, 3, -1, -2])
    a2, b2 = rng.choice([1, 2, 3, -1, -2]), rng.choice([1, 2, 3, -1, -2])
    while a1 * b2 - a2 * b1 == 0: a2 = rng.choice([1, 2, 3, -1, -2])
    c1, c2 = a1 * x0 + b1 * y0, a2 * x0 + b2 * y0
    e1 = f"{_lin(a1, 0)} {'+' if b1 > 0 else '-'} {abs(b1) if abs(b1) != 1 else ''}y = {c1}"
    e2 = f"{_lin(a2, 0)} {'+' if b2 > 0 else '-'} {abs(b2) if abs(b2) != 1 else ''}y = {c2}"
    return f"\\begin{{cases}} {e1} \\\\ {e2} \\end{{cases}}", f"x = {x0},\\ y = {y0}"

def tenkai(rng):
    p, q_ = rng.choice(NZ), rng.choice(NZ)
    return f"({_lin(1, p)})({_lin(1, q_)})", _quad(p + q_, p * q_)

def insuu_bunkai(rng):
    p, q_ = rng.choice(NZ), rng.choice(NZ)
    return _quad(p + q_, p * q_), f"({_lin(1, p)})({_lin(1, q_)})"

def heihoukon(rng):
    if rng.random() < 0.5:
        a, b = rng.choice([2, 3, 5, 6, 8, 12]), rng.choice([2, 3, 5, 6, 8, 12])
        out, rest = _simp_sqrt(a * b)
        return f"\\sqrt{{{a}}} \\times \\sqrt{{{b}}}", _sqrt_tex(out, rest)
    base = rng.choice([2, 3, 5])
    k, m, n = rng.randint(2, 6), rng.randint(2, 6), rng.randint(1, 5)
    coef = k + m - n
    return f"{k}\\sqrt{{{base}}} + {m}\\sqrt{{{base}}} - {n}\\sqrt{{{base}}}", ("0" if coef == 0 else _sqrt_tex(coef, base))

def niji_houteishiki(rng):
    p, q_ = rng.choice(NZ), rng.choice(NZ)
    b, c = -(p + q_), p * q_
    ans = f"x = {p}" if p == q_ else f"x = {p},\\ {q_}"
    return f"{_quad(b, c)} = 0", ans

GENERATORS = {
    "seifu_shisoku": ("正負の数の四則", seifu_shisoku), "bunsuu_kagen": ("分数の加減", bunsuu_kagen),
    "moji_shiki": ("文字式の計算", moji_shiki), "ichiji_houteishiki": ("一次方程式", ichiji_houteishiki),
    "renritsu": ("連立方程式", renritsu), "tenkai": ("式の展開", tenkai),
    "insuu_bunkai": ("因数分解", insuu_bunkai), "heihoukon": ("平方根の計算", heihoukon),
    "niji_houteishiki": ("二次方程式", niji_houteishiki),
}

def build(sections, seed=None):
    rng = random.Random(seed)
    result = []
    for sec in sections:
        key = sec.get("type")
        if key not in GENERATORS: continue
        label, gen = GENERATORS[key]
        items, seen = [], set()
        for _ in range(int(sec.get("count", 4))):
            for _try in range(50):
                q, a = gen(rng)
                if q not in seen:
                    seen.add(q); break
            items.append({"q": q, "a": a})
        result.append({"label": label, "items": items})
    return result
