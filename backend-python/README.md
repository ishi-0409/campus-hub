# Python Backend (AI Syllabus Search API)

Python (FastAPI) を用いた AIシラバス検索のバックエンド API です。

---

## 起動方法

### 1. 依存ライブラリのインストール
```bash
cd backend-python
pip install -r requirements.txt
```

### 2. 環境変数の設定 (任意)
Gemini API を使用する場合は、`.env` ファイルを作成して API キーを設定します。

```bash
# Windows (PowerShell)
Copy-Item .env.example .env

# Mac / Linux
cp .env.example .env
```
`.env` 内の `GEMINI_API_KEY` に自身の API キーを設定してください。  
※ API キーが未設定の場合でも、ローカルテスト用にモック（ダミー）応答で動作します。

### 3. API サーバーの起動
```bash
uvicorn main:app --reload --port 8000
```

起動後、ブラウザで以下のURLにアクセスできます：
* **ヘルスチェック**: `http://localhost:8000/api/health`
* **Swagger UI (APIドキュメント＆テスト画面)**: `http://localhost:8000/docs`

---

##  提供 API エンドポイント

### 1. `POST /api/search` (AIシラバス検索)
* **リクエスト例**:
  ```json
  {
    "query": "レポート中心で未経験でも単位が取りやすいプログラミングの授業",
    "university": "A大学"
  }
  ```
* **レスポンス例**:
  ```json
  {
    "answer": "「未経験でも〜」ですね！おすすめの講義として「プログラミング基礎」をピックアップしました。この授業は試験がなくレポートと出席で評価されます。",
    "recommended_courses": [
      {
        "id": "CS101",
        "title": "プログラミング基礎 (Python)",
        "instructor": "山田 太郎",
        "term": "前期",
        "day_period": "水曜3限",
        "credits": 2,
        "category": "専門基礎",
        "summary": "...",
        "grading": { "exam": 0, "report": 70, "attendance": 30 },
        "tags": ["未経験者歓迎", "レポート重視", "テストなし"]
      }
    ]
  }
  ```

### 2. `GET /api/syllabuses` (シラバス全件取得)
登録されているシラバスデータ一覧を返却します。
