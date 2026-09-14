import google.generativeai as genai
import json
import os

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

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
    model = genai.GenerativeModel('gemini-1.5-flash')
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
