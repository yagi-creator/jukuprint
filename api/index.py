from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse
import google.generativeai as genai
import json
import os
import random
from fractions import Fraction

# --- analyzer.py の中身 ---
genai.configure(api_key=os.environ.get("GEMINI_API_KEY", ""))

TYPES = """
seifu_shisoku(正負の数の四則) / bunsuu_kagen(分数の加減) /
moji_shiki(文字式の計算) / ichiji_houteishiki(一次方程式) /
renritsu(連立方程式) / tenkai(式の展開) /
insuu_bunkai(因数分解) / heihoukon(平方根の計算) /
niji_houteishiki(二次方程式)
"""

PROMPT = f"""この画像は中学数学の計算問題のページです。
問題の「構成」だけを読み取り、JSONで返してください。
- 大問ごとに1つのsectionとし、その大問に含まれる小問の数をcountに入れます。
- 各大問がどの問題タイプかを、次の一覧から必ず選んでください。
{TYPES}
- 一覧に該当しないもの(文章題・図形など)は無視してください。
- JSONのみを出力してください。

出力形式:
{{"sections":[{{"type":"ichiji_houteishiki","count":4}}]}}
"""

def analyze(image_bytes: bytes, media_type: str = "image/jpeg"):
    model = genai.GenerativeModel('gemini-2.5-flash')
    image_parts = [{"mime_type": media_type, "data": image_bytes}]
    response = model.generate_content([PROMPT, image_parts[0]])
    del image_bytes
    text = response.text.strip()
    if text.startswith("```"):
        text = text.split("```")[1].lstrip("json").strip()
    try:
        return json.loads(text).get("sections", [])
    except json.JSONDecodeError:
        return []


# --- generators.py の中身 ---
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

def build_questions(sections, seed=None):
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


# --- render.py の中身 ---
CSS = """
@page { size: A4; margin: 15mm 12mm; }
body { font-family: "Hiragino Mincho ProN","Yu Mincho",serif; margin:0; }
.head { display:flex; justify-content:space-between; align-items:flex-end;
        border-bottom:2px solid #000; padding-bottom:4mm; margin-bottom:6mm; }
.head-left { display: flex; flex-direction: column; }
.juku-name { font-size: 10pt; color: #555; margin-bottom: 4px; }
.title { font-size:16pt; font-weight:bold; }
.fields { font-size:11pt; }
.fields span { display:inline-block; border-bottom:1px solid #000;
               width:40mm; margin-left:3mm; }
.sec-title { font-size:12pt; font-weight:bold; margin: 8mm 0 6mm 0; }
.cols { column-count:2; column-gap:12mm; }
.item { break-inside:avoid; margin-bottom: 25mm; font-size:13pt; display:flex; gap:3mm; }
.no { min-width:8mm; font-weight:bold; }
.page-break { break-before:page; }
.ans .item { margin-bottom: 6mm; font-size:11pt; }
.ans .sec-title { margin: 5mm 0 3mm 0; }

@media screen {
    body { background: transparent; padding: 0; }
    .sheet { background: white; width: 100%; min-height: 297mm; padding: 15mm 12mm; box-sizing: border-box; margin: 0 auto 20px; }
    .page-break { break-before: auto; border-top: 2px dashed #ccc; margin-top: 20px; padding-top: 20px; }
}
@media print {
    body { background: white; padding: 0; }
    .sheet { box-shadow: none; margin: 0; }
}
"""

HTML_TEMPLATE = """<!doctype html><html><head><meta charset="utf-8">
<script>window.MathJax={{tex:{{inlineMath:[['\\\\(','\\\\)']]}}}};</script>
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
<style>{css}</style></head><body>{body}</body></html>"""

def _sheet(title, sections, juku_name, answer=False):
    h = f"""<div class="head">
    <div class="head-left">
        <div class="juku-name">{juku_name}</div>
        <div class="title">{title}</div>
    </div>
<div class="fields">日付<span></span>氏名<span></span></div></div>"""
    parts = [h]
    
    daimon_no = 1
    for sec in sections:
        lead_text = "次の方程式を解きなさい。" if "方程式" in sec["label"] else "次の計算をしなさい。"
        parts.append(f'<div class="sec-title">{daimon_no}. {lead_text}</div>')
        
        parts.append('<div class="cols">')
        shomon_no = 1
        for it in sec["items"]:
            body = it["a"] if answer else it["q"]
            parts.append(
                f'<div class="item"><span class="no">({shomon_no})</span>'
                f'<span>\\({body}\\)</span></div>')
            shomon_no += 1
        parts.append("</div>")
        daimon_no += 1
        
    return "".join(parts)

def to_html(title, sections, juku_name="進学塾テスト教室") -> str:
    body = (f'<div class="sheet">{_sheet(title, sections, juku_name)}</div>'
            f'<div class="sheet page-break ans">'
            f'{_sheet(title + " 【解答】", sections, juku_name, answer=True)}</div>')
    return HTML_TEMPLATE.format(css=CSS, body=body)


# --- メインのAPI処理 (main.py の中身) ---
app = FastAPI()

INDEX_HTML = """
<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>類題プリント自動生成システム (Demo)</title>
<style>
  body { font-family: 'Helvetica Neue', Arial, sans-serif; background: #f4f7f6; color: #333; margin: 0; padding: 0; }
  .header { background: #1a4f8a; color: #fff; padding: 16px; text-align: center; font-weight: bold; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
  .container { max-width: 500px; margin: 20px auto; background: #fff; padding: 24px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
  h2 { font-size: 18px; margin-top: 0; border-bottom: 2px solid #1a4f8a; padding-bottom: 8px; }
  label { display: block; margin: 16px 0 6px; font-size: 14px; font-weight: bold; }
  input[type="text"], input[type="password"] { width: 100%; padding: 12px; font-size: 16px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
  input[type="file"] { width: 100%; padding: 10px; background: #f9f9f9; border: 1px dashed #ccc; border-radius: 4px; box-sizing: border-box; }
  button { width: 100%; padding: 14px; font-size: 16px; font-weight: bold; margin-top: 20px; background: #28a745; color: #fff; border: none; border-radius: 6px; cursor: pointer; transition: background 0.2s; }
  button:active { background: #218838; }
  #msg { margin-top: 16px; font-size: 14px; color: #d9534f; font-weight: bold; text-align: center; }
  #preview-container { display: none; margin-top: 30px; border-top: 2px dashed #ccc; padding-top: 20px; }
  .action-btn { background: #1a4f8a; margin-top: 10px; }
  iframe { width: 100%; height: 600px; border: 1px solid #ccc; border-radius: 4px; margin-top: 10px; background: #fff; }
  #app-screen { display: none; }
</style>
</head>
<body>

<div class="header">類題プリントジェネレーター</div>

<div class="container" id="login-screen">
  <h2>システムにログイン</h2>
  <label>合言葉</label>
  <input type="password" id="passcode" placeholder="パスワードを入力">
  <button id="btn-login">ログイン</button>
  <p id="login-msg"></p>
</div>

<div class="container" id="app-screen">
  <h2>問題の読み込み</h2>
  <label>自塾の名称（プリントに印字されます）</label>
  <input type="text" id="juku-name" value="進学塾テスト教室">
  <label>問題ページを撮影</label>
  <input type="file" id="img" accept="image/*" capture="environment">
  <label>プリントのタイトル</label>
  <input type="text" id="title" value="計算復習プリント">
  <button id="go">類題を作成する</button>
  <p id="msg"></p>

  <div id="preview-container">
    <h2>生成結果プレビュー</h2>
    <p style="font-size:12px; color:#666;">※実際の紙面と同じレイアウトです。印刷ボタンからPDF保存が可能です。</p>
    <iframe id="preview-frame"></iframe>
    <button class="action-btn" id="btn-print">このプリントを印刷する</button>
  </div>
</div>

<script>
document.getElementById('btn-login').onclick = () => {
  if (document.getElementById('passcode').value === 'juku2026') {
    document.getElementById('login-screen').style.display = 'none';
    document.getElementById('app-screen').style.display = 'block';
  } else {
    document.getElementById('login-msg').textContent = '合言葉が違います';
  }
};

document.getElementById('go').onclick = async () => {
  const f = document.getElementById('img').files[0];
  const msg = document.getElementById('msg');
  const previewContainer = document.getElementById('preview-container');
  const iframe = document.getElementById('preview-frame');
  
  if (!f) { msg.textContent = '画像を選択してください'; return; }
  
  msg.textContent = '画像をAIで解析し、数値を生成中... (約10秒)';
  msg.style.color = '#1a4f8a';
  previewContainer.style.display = 'none';

  const fd = new FormData();
  fd.append('image', f);
  fd.append('title', document.getElementById('title').value);
  fd.append('juku_name', document.getElementById('juku-name').value);

  try {
    const r = await fetch('/api/generate', {method:'POST', body:fd});
    if (!r.ok) { 
      msg.textContent = 'エラー: ' + (await r.text()); 
      msg.style.color = '#d9534f';
      return; 
    }
    const htmlText = await r.text();
    iframe.srcdoc = htmlText;
    previewContainer.style.display = 'block';
    msg.textContent = '生成が完了しました！';
    msg.style.color = '#28a745';

    document.getElementById('btn-print').onclick = () => {
      iframe.contentWindow.print();
    };
  } catch (e) {
    msg.textContent = '通信エラーが発生しました';
    msg.style.color = '#d9534f';
  }
};
</script>
</body>
</html>
"""

@app.get("/")
def index():
    return HTMLResponse(content=INDEX_HTML)

@app.post("/api/generate")
async def generate(
    image: UploadFile = File(...), 
    title: str = Form("計算演習プリント"),
    juku_name: str = Form("進学塾テスト教室")
):
    data = await image.read()
    try:
        sections = analyze(data, image.content_type or "image/jpeg")
    finally:
        del data
    if not sections:
        raise HTTPException(422, "対応する計算問題を検出できませんでした")
    
    built = build_questions(sections)
    html_content = to_html(title, built, juku_name)
    return HTMLResponse(content=html_content)
