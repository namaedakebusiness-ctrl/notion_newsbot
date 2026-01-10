import requests
from datetime import datetime
import os

NOTION_API_KEY = os.environ.get('NOTION_API_KEY')
DATABASE_ID = os.environ.get('DATABASE_ID')
NOTION_VERSION = "2022-06-28"

headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": NOTION_VERSION
}

def search_ai_news():
    """無料で取得できるAIニュースを検索"""
    news_list = []
    
    # Hugging Face Daily Papers
    try:
        response = requests.get("https://huggingface.co/api/daily_papers")
        papers = response.json()[:5]
        for paper in papers:
            news_list.append(f"📄 {paper['title']}")
    except:
        pass
    
    # Arxivの最新AI論文
    try:
        arxiv_url = "http://export.arxiv.org/api/query?search_query=cat:cs.AI&sortBy=submittedDate&sortOrder=descending&max_results=5"
        response = requests.get(arxiv_url)
        if response.status_code == 200:
            news_list.append("\n🔬 Arxiv最新論文 (AIカテゴリ)")
    except:
        pass
    
    return "\n".join(news_list) if news_list else "本日のニュースはありませんでした。"

def create_notion_page():
    url = "https://api.notion.com/v1/pages"
    today = datetime.now()
    # タイトルを「デイリー」に変更
    title = f"【Daily】AIニュース - {today.strftime('%Y/%m/%d')}"
    content = search_ai_news()
    
    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Name": {
                "title": [{"text": {"content": title}}]
            },
            "Date": {
                "date": {"start": today.date().isoformat()}
            }
        },
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"text": {"content": content}}]
                }
            }
        ]
    }
    
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print("✅ Notionへの投稿成功！")
    else:
        print(f"❌ エラー: {response.text}")

if __name__ == "__main__":
    create_notion_page()
