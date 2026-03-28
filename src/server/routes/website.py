import os
from flask import Blueprint, send_from_directory

website_bp = Blueprint('website', __name__)

# 计算绝对路径：假设项目结构是 ~/openclaw/web/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WEB_ROOT = os.path.join(BASE_DIR, 'web')

print(f"[DEBUG] WEB_ROOT = {WEB_ROOT}")

@website_bp.route('/')
def index():
    print(f"[DEBUG] Serving index from {WEB_ROOT}")
    return send_from_directory(WEB_ROOT, 'index.html')

@website_bp.route('/<path:filename>')
def static_files(filename):
    print(f"[DEBUG] Serving static file {filename} from {WEB_ROOT}")
    return send_from_directory(WEB_ROOT, filename)