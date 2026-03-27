import os
import json
import datetime
import re

def save_news_json(news_data: dict) -> str:
    """
    将新闻数据保存到 data/news/ 目录下，文件名为 {date}-{slug}.json
    返回保存的文件路径，失败时返回空字符串
    """
    # 确保目录存在
    news_dir = 'data/news'
    os.makedirs(news_dir, exist_ok=True)

    # 生成安全的文件名
    title = news_data.get('title', 'untitled')
    slug = re.sub(r'[^\w\-_]+', '-', title.lower())
    date = news_data.get('date', datetime.date.today().isoformat())
    filename = f"{date}-{slug}.json"
    filepath = os.path.join(news_dir, filename)

    # 添加保存时间戳
    news_data['_saved_at'] = datetime.datetime.now().isoformat()

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(news_data, f, ensure_ascii=False, indent=2)
        return filepath
    except Exception as e:
        print(f"保存新闻失败: {e}")
        return ""

def read_json(filepath: str) -> dict:
    """读取 JSON 文件并返回字典"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)