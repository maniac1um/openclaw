import os
import json
from jinja2 import Environment, FileSystemLoader

def regenerate_website():
    data_dir = 'data/news'
    web_dir = 'web'
    template_path = 'src/templates/index.html'

    # 读取所有新闻
    news_list = []
    if os.path.exists(data_dir):
        for filename in os.listdir(data_dir):
            if filename.endswith('.json'):
                with open(os.path.join(data_dir, filename), 'r', encoding='utf-8') as f:
                    try:
                        news_list.append(json.load(f))
                    except json.JSONDecodeError:
                        continue

    # 按日期倒序排序
    news_list.sort(key=lambda x: x.get('date', ''), reverse=True)

    # 渲染模板
    env = Environment(loader=FileSystemLoader(os.path.dirname(template_path)))
    template = env.get_template(os.path.basename(template_path))
    rendered = template.render(news=news_list)

    # 写入 web/index.html
    os.makedirs(web_dir, exist_ok=True)
    with open(os.path.join(web_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(rendered)

if __name__ == '__main__':
    regenerate_website()