import os
from flask import Blueprint, send_from_directory

website_bp = Blueprint('website', __name__)

# 获取项目根目录：从当前文件 (src/server/routes/website.py) 向上三级到项目根
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
WEB_ROOT = os.path.join(BASE_DIR, 'web')

print(f"[DEBUG] WEB_ROOT = {WEB_ROOT}")

@website_bp.route('/')
def index():
    return send_from_directory(WEB_ROOT, 'index.html')

@website_bp.route('/<path:filename>')
def static_files(filename):
    return send_from_directory(WEB_ROOT, filename)