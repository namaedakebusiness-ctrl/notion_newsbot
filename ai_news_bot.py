import requests
import feedparser
from datetime import datetime, timedelta
import os

NOTION_API_KEY = os.environ.get('NOTION_API_KEY')
DATABASE_ID = os.environ.get('DATABASE_ID')
NOTION_VERSION = "2022-06-28"

# --- 設定：サイトごとのURLとキーワード ---
# keywordsをNoneにすると無条件取得。リストを入れるとフィルタリングします。
SOURCES = {
    "OpenAI": {
        "url": "https://openai.com/blog/rss.xml",
        "keywords": None  # すべての記事を取得
    },
    "DeepMind": {
        "url": "https://deepmind.google/discover/blog/rss.xml",
        "keywords": None  # すべての記事を取得
    },
    "日経クロステック": {
        "url": "https://xtech.nikkei.com/rss/xtech_it.rdf",
        "keywords": ["生成AI", "CNN", "RNN", "transformer", "エージェント型", "自動化"]
    },
    "ITmedia": {
        "url": "https://rss.itmedia.co.jp/rss/2.0/news_bursts.xml",
        "keywords": ["生成AI", "CNN", "RNN", "transformer", "エージェント型", "自動化"]
    },
    "Ledge.ai": {
        "url": "https://ledge.ai/feed/",
        "keywords": ["生成AI", "CNN", "RNN", "transformer", "エージェント型", "自動化"]
    },
    "MIT Tech": {
        "url": "https://www.technologyreview.jp/feed/",
        "keywords": ["生成AI", "CNN", "RNN", "transformer", "エージェント型", "自動化"]
    }
}

# 全サイト共通でチェックしたい重要なキーワード（もしあれば追加してください）
COMMON_KEYWORDS = ["提携", "買収", "規制"]

def get_filtered_news():
    all_news = []
    # 過去24時間以内の記事を対象（実行時刻の24時間前〜現在）
    yesterday = datetime.utcnow() - timedelta(days=1)
    
    for source_name, info in SOURCES.items():
        try:
            feed = feedparser.parse(info["url"])
            
            count = 0
            for entry in feed.entries:
                if count >= 3: break # 1サイト最大3件
                
                title = entry.get('title', '')
                link = entry.get('link', '')
                summary = entry.get('summary', entry.get('description', ''))
                
                # 24時間以内かチェック
                published_parsed = entry.get('published_
