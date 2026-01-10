import requests
import feedparser
from datetime import datetime
import os
import re

NOTION_API_KEY = os.environ.get('NOTION_API_KEY')
DATABASE_ID = os.environ.get('DATABASE_ID')
NOTION_VERSION = "2022-06-28"

# 収集ソース設定
SOURCES = {
    "OpenAI": "https://openai.com/blog/rss.xml",
    "DeepMind": "https://deepmind.google/discover/blog/rss.xml",
    "Anthropic": "https://www.anthropic.com/newsroom/rss",
    "日経クロステック": "https://xtech.nikkei.com/rss/xtech_it.rdf",
    "ITmedia": "https://rss.itmedia.co.jp/rss/2.0/news_bursts.xml",
    "Ledge.ai": "https://ledge.ai/feed/",
    "MIT Tech": "https://www.technologyreview.jp/feed/"
}

# 収集基準キーワード
KEYWORDS = ["API", "アップデート", "規制", "法", "EU AI Act", "提携", "コスト", "削減", "エージェント", "Agent"]

def get_filtered_news():
    all_news = []
    for source_name, url in SOURCES.items():
        try:
            feed = feedparser.parse(url)
            count = 0
            for entry in feed.entries:
                if count >= 3: break # 各サイト最大3件
                title = entry.get('title', '')
                summary = entry.get('summary', entry.get('description', ''))
                link = entry.get('link', '')
                
                content_text = (title + summary).lower()
                # キーワードのいずれかが含まれているかチェック
                if any(k.lower() in content_text for k in KEYWORDS):
                    all_news.append({"source": source_name, "title": title, "link": link})
                    count += 1
        except Exception as e:
            print(f"⚠️ {source_name} 取得失敗: {e}")
    return all_news

def create_notion_page(news_items):
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_VERSION
    }
    
    today_str = datetime.now().strftime('%Y-%m-%d')
    
    children = []
    if not news_items:
        children.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": [{"text": {"content": "本日の条件に合うニュースはありませんでした。"}}] }
        })
    else:
        for item in news_items:
            children.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {"rich_text": [{"text": {"content": f"【{item['source']}】"}}] }
            })
            children.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {"text": {"content": f"{item['title']}\n"}},
                        {
                            "text": {"content": "👉 記事をチェックする", "link": {"url": item['link']}},
                            "annotations": {"bold": True, "color": "blue"}
                        }
                    ]
                }
            })

    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Name": {
                "title": [{"text": {"content": today_str}}] # Name列に日付のみ記載
            }
        },
        "children": children
    }
    
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print(f"✅ {today_str} の投稿成功！")
    else:
        print(f"❌ エラー: {response.text}")

if __name__ == "__main__":
    news = get_filtered_news()
    create_notion_page(news)
