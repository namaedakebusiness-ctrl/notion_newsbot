import requests
import feedparser
from datetime import datetime, timedelta
import os

NOTION_API_KEY = os.environ.get('NOTION_API_KEY')
DATABASE_ID = os.environ.get('DATABASE_ID')
NOTION_VERSION = "2022-06-28"

SOURCES = {
    "OpenAI": {"url": "https://openai.com/blog/rss.xml", "keywords": None},
    "DeepMind": {"url": "https://deepmind.google/discover/blog/rss.xml", "keywords": None},
    "日経クロステック": {"url": "https://xtech.nikkei.com/rss/xtech_it.rdf", "keywords": ["生成AI", "CNN", "RNN", "transformer", "エージェント型", "自動化"]},
    "ITmedia": {"url": "https://rss.itmedia.co.jp/rss/2.0/news_bursts.xml", "keywords": ["生成AI", "CNN", "RNN", "transformer", "エージェント型", "自動化"]},
    "Ledge.ai": {"url": "https://ledge.ai/feed/", "keywords": ["生成AI", "CNN", "RNN", "transformer", "エージェント型", "自動化"]},
    "MIT Tech": {"url": "https://www.technologyreview.jp/feed/", "keywords": ["生成AI", "CNN", "RNN", "transformer", "エージェント型", "自動化"]}
}

COMMON_KEYWORDS = ["提携", "買収", "規制"]

def get_filtered_news():
    all_news = []
    yesterday = datetime.utcnow() - timedelta(days=1)
    
    for source_name, info in SOURCES.items():
        try:
            feed = feedparser.parse(info["url"])
            count = 0
            for entry in feed.entries:
                if count >= 3: break
                
                title = entry.get('title', '')
                link = entry.get('link', '')
                summary = entry.get('summary', entry.get('description', ''))
                
                # 公開日時のチェック
                is_new = True
                pub_parsed = entry.get('published_parsed')
                if pub_parsed:
                    pub_date = datetime(*pub_parsed[:6])
                    if pub_date < yesterday:
                        is_new = False
                
                if not is_new: continue

                # 判定ロジック
                if info["keywords"] is None:
                    all_news.append({"source": source_name, "title": title, "link": link})
                    count += 1
                else:
                    target_keywords = info["keywords"] + COMMON_KEYWORDS
                    content_text = (title + summary).lower()
                    if any(k.lower() in content_text for k in target_keywords):
                        all_news.append({"source": source_name, "title": title, "link": link})
                        count += 1
        except Exception as e:
            print(f"⚠️ {source_name} 取得失敗: {e}")
            
    return all_news[:15]

def create_notion_page(news_items):
    if not news_items:
        print("💡 新着ニュースなし")
        return

    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_VERSION
    }
    
    today_str = datetime.now().strftime('%Y-%m-%d')
    children = []
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
                    {"text": {"content": "👉 記事をチェック", "link": {"url": item['link']}}, "annotations": {"bold": True, "color": "blue"}}
                ]
            }
        })

    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {"Name": {"title": [{"text": {"content": today_str}}]}},
        "children": children
    }
    
    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        print(f"❌ Notion投稿失敗: {response.text}")
    else:
        print(f"✅ {today_str} 投稿成功")

if __name__ == "__main__":
    news = get_filtered_news()
    create_notion_page(news)
