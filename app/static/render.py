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
/* 大問のリード文 */
.sec-title { font-size:12pt; font-weight:bold; margin: 8mm 0 6mm 0; }
.cols { column-count:2; column-gap:12mm; }
/* 問題の余白を広く取る */
.item { break-inside:avoid; margin-bottom: 25mm; font-size:13pt; display:flex; gap:3mm; }
.no { min-width:8mm; font-weight:bold; }
.page-break { break-before:page; }
/* 解答ページは余白を詰める */
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

HTML = """<!doctype html><html><head><meta charset="utf-8">
<script>window.MathJax={{tex:{{inlineMath:[['\\\\(','\\\\)']]}}}};</script>
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
<style>{css}</style></head><body>{body}</body></html>"""

def _sheet(title, sections, juku_name, answer=False):
    # ヘッダーに塾名を追加
    h = f"""<div class="head">
    <div class="head-left">
        <div class="juku-name">{juku_name}</div>
        <div class="title">{title}</div>
    </div>
<div class="fields">日付<span></span>氏名<span></span></div></div>"""
    parts = [h]
    
    daimon_no = 1
    for sec in sections:
        # 単元名ではなく、汎用的なリード文にする
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

def to_html(title, sections, juku_name) -> str:
    # 印刷時に解答ページが崩れないように枠で囲む
    body = (f'<div class="sheet">{_sheet(title, sections, juku_name)}</div>'
            f'<div class="sheet page-break ans">'
            f'{_sheet(title + " 【解答】", sections, juku_name, answer=True)}</div>')
    return HTML.format(css=CSS, body=body)
