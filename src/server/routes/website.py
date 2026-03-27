import os
from flask import Blueprint, send_from_directory

website_bp = Blueprint('website', __name__)

# 网站静态文件目录（相对于项目根目录）
WEB_ROOT = os.getenv('WEB_ROOT', 'web')

@website_bp.route('/')
def index():
    """提供生成的网站首页"""
    return send_from_directory(WEB_ROOT, 'index.html')

@website_bp.route('/<path:filename>')
def static_files(filename):
    """提供其他静态资源（CSS、JS等）"""
    return send_from_directory(WEB_ROOT, filename)