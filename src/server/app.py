import os
from flask import Flask
from src.server.routes.webhook import webhook_bp
from src.server.routes.website import website_bp

# 创建 Flask 应用
app = Flask(__name__, template_folder='../templates')

# 注册蓝图
app.register_blueprint(webhook_bp, url_prefix='/api')
app.register_blueprint(website_bp, url_prefix='')

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    print("Registered routes:")
    for rule in app.url_map.iter_rules():
        print(rule)
    app.run(host='0.0.0.0', port=port, debug=debug)