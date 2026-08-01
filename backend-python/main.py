import json
import os
import re
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from rank_bm25 import BM25Okapi
from janome.tokenizer import Tokenizer

load_dotenv()

app = FastAPI(
    title="Campus Hub - AI Syllabus Search API",
    description="Python FastAPI backend for AI-powered syllabus search",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  #本番時には修正
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# シラバスデータ
SYLLABUS_FILE = os.path.join(os.path.dirname(__file__), "syllabuses.json")

def load_syllabuses():
    if os.path.exists(SYLLABUS_FILE):
        with open(SYLLABUS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# データモデル定義

#フロントから受け取るデータ
class SearchRequest(BaseModel):
    query: str
    university: Optional[str] = None

class Course(BaseModel):
    id: str
    university: str
    title: str
    instructor: str
    term: str
    day_period: str
    credits: int
    category: str
    summary: str
    grading: dict
    tags: List[str]
    prerequisites: str

#フロントに返すデータ
class SearchResponse(BaseModel):
    answer: str
    recommended_courses: List[Course]


# ルート
@app.get("/")
def read_root():
    return {"message": "Campus Hub AI Syllabus Search API is running"}


# ヘルスチェックAPI
@app.get("/api/health")
def health_check():
    return {"status": "ok", "total_courses": len(load_syllabuses())}


# シラバス一覧取得API
@app.get("/api/syllabuses", response_model=List[Course])
def get_all_syllabuses():
    return load_syllabuses()


# 形態素解析
janome_tokenizer = Tokenizer()

def tokenize_text(text: str) -> List[str]:
    text = text.lower()
    tokens = []
    for token in janome_tokenizer.tokenize(text):
        pos = token.part_of_speech.split(',')[0] 
        if pos in ['名詞', '動詞', '形容詞']:
            word = token.surface.strip()
            if len(word) > 1 or word.isalnum():
                tokens.append(word)
    return tokens


# 検索API
@app.post("/api/search", response_model=SearchResponse)
async def search_syllabus(request: SearchRequest):

    syllabuses = load_syllabuses()

    if not syllabuses:
        raise HTTPException(status_code=500, detail="シラバスデータが見つかりません。")

    user_query = request.query.strip()
    if not user_query:
        raise HTTPException(status_code=400, detail="検索キーワードを入力してください。")

    # 大学フィルターが指定されている場合
    target_syllabuses = syllabuses
    if request.university:
        target_syllabuses = [s for s in syllabuses if s.get("university") == request.university]


    # --- 1. BM25 アルゴリズムによるスコアリング ---
    corpus_tokens = []
    for course in target_syllabuses:
        full_text = (
            course["title"] + " " +
            course["summary"] + " " +
            course["category"] + " " +
            " ".join(course["tags"])
        )
        tokens = tokenize_text(full_text)
        corpus_tokens.append(tokens)

    # BM25検索エンジンの構築とスコア計算
    bm25 = BM25Okapi(corpus_tokens)
    query_tokens = tokenize_text(user_query)
    doc_scores = bm25.get_scores(query_tokens)

    # スコアが高い上位3件を取得
    pairs = zip(doc_scores, target_syllabuses)
    sorted_pairs = sorted(pairs, key=lambda x: x[0], reverse=True)
    matched_courses = [course for score, course in sorted_pairs[:3]]


    # 該当なしの場合はスコアに関わらず上位3件を表示
    if not matched_courses:
        matched_courses = target_syllabuses[:3]


    # --- 2. Gemini API によるAI回答生成 ---
    api_key = os.environ.get("GEMINI_API_KEY")
    ai_answer = ""

    if api_key:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)

            # シラバスのテキスト情報を構築
            context_text = ""
            for idx, c in enumerate(matched_courses, 1):
                context_text += f"\n【講義{idx}】 {c['title']} ({c['university']} / {c['day_period']})\n"
                context_text += f"概要: {c['summary']}\n"
                context_text += f"評価方法: 試験{c['grading'].get('exam', 0)}%, レポート{c['grading'].get('report', 0)}%, 出席/その他{c['grading'].get('attendance', 0) + c['grading'].get('group_work', 0) + c['grading'].get('presentation', 0)}%\n"
                context_text += f"タグ: {', '.join(c['tags'])}\n"

            prompt = f"""
あなたは大学の親切な履修登録アドバイザーAIです。
以下の学生の希望・質問に対して、提示されたシラバス情報を踏まえてわかりやすくアドバイスを行ってください。

【学生の希望・質問】
{user_query}

【検索された関連講義】
{context_text}

【回答のルール】
- なぜその講義が学生の希望に合っているのか、ポイント（評価基準や講義内容）を具体的に説明してください。
- 簡潔に200〜300文字程度でまとめてください。
"""

            response = client.models.generate_content(
                model='gemini-3.5-flash',
                contents=prompt,
            )
            ai_answer = response.text.strip()
        except Exception as e:
            ai_answer = f"「{user_query}」に合わせたおすすめ講義の検索結果です。以下の講義のシラバス・評価方法をご確認ください。（※AI生成エラー: {str(e)}）"
    else:
        course_names = "、".join([f"「{c['title']}」" for c in matched_courses])
        ai_answer = f"「{user_query}」のご相談ですね！ご希望の条件に合う講義として {course_names} をピックアップしました。評価割合やタグを参考に履修を検討してみてください"

    return SearchResponse(
        answer=ai_answer,
        recommended_courses=[Course(**c) for c in matched_courses]
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
