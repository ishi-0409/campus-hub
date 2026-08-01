# campus-hub

## 学内ポータルサイト (Campus Hub)
    
学生生活を便利にする各種ミニアプリ（機能）を統合するポータルサイトの開発リポジトリです。
    
--- 
        
## チームのみなさんへ（はじめに）
    
現在、以下のような構成・役割分担のアイデアをメモとして考えています！
**「もっとこうしたら面白そう！」「こんな機能作りたい！」などの案やフィードバックがあれば、Issue やチャットで気軽に教えてください！** みんなで相談しながら進めていきましょう！


## 📁 プロジェクト構成


    campus-hub/ (リポジトリの一番上)
    ├── README.md               # プロジェクトの説明・担当表
    ├── .gitignore              # Git管理から除外する設定
    │
    ├── frontend/               # 🎨 【フロント担当】ポータル画面
    │   ├── src/
    │   └── package.json
    │
    ├── backend-python/         # 🐍 【Python担当】
    │   ├── main.py
    │   └── requirements.txt
    │
    ├── backend-java/           # ☕ 【Java担当】　
    │   ├── src/
    │   └── pom.xml
    │
    ├── backend-c/              # ⚙️ 【C言語担当】
      　├── route_finder.c
        └── Makefile
    

 ## 📌 チーム開発のルール
1. 自分の担当フォルダ（`backend-python/` 等）を中心に作業しましょう。
2. `main` ブランチに直接 Push せず、`feature/機能名` ブランチを作成してPRを送りましょう


