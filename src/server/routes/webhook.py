import os
import json
from flask import Blueprint, request, jsonify
from src.tools.news_parser import sanitize_input, extract_news
from src.tools.file_tools import save_news_json
from src.tools.git_tools import GitTools
from scripts.generate_site import regenerate_website

webhook_bp = Blueprint('webhook', __name__)

# 加载环境变量
REPO_PATH = os.getenv('REPO_PATH', '.')
git = GitTools(repo_path=REPO_PATH)

@webhook_bp.route('/webhook', methods=['POST'])
def handle_webhook():
    """
    接收来自 OpenClaw 的新闻稿，完成自动化发布
    期望 JSON 格式：{"news_text": "..."}
    """
    data = request.get_json()
    if not data or 'news_text' not in data:
        return jsonify({'error': 'Missing news_text'}), 400

    raw_text = data['news_text']

    # 1. 清洗输入（防止注入）
    cleaned_text = sanitize_input(raw_text)

    # 2. 提取新闻结构化信息
    news_data = extract_news(cleaned_text)

    # 3. 保存为 JSON 文件
    json_path = save_news_json(news_data)
    if not json_path:
        return jsonify({'error': 'Failed to save news JSON'}), 500

    # 4. 重新生成静态网站
    try:
        regenerate_website()
    except Exception as e:
        return jsonify({'error': f'Site regeneration failed: {str(e)}'}), 500

    # 5. Git 提交并推送
    commit_msg = f"发布新闻：{news_data['title']}"
    result = git.commit_and_push(commit_msg, patterns=['web/'])
    if not result['success']:
        return jsonify({'error': result['error']}), 500

    return jsonify({
        'status': 'ok',
        'commit': result['commit_hash'],
        'news': news_data
    }), 200