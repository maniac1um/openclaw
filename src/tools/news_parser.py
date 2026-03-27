import re
import datetime

def sanitize_input(raw_text: str) -> str:
    """
    清洗新闻文本，防止 Prompt 注入攻击
    """
    # 移除控制字符
    cleaned = re.sub(r'[\x00-\x1f\x7f]', '', raw_text)

    # 检测并移除常见注入模式（可根据需要扩展）
    injection_patterns = [
        (r'忽略.*指令', '[REDACTED]'),
        (r'ignore.*previous.*instruction', '[REDACTED]'),
        (r'你现在是.*系统', '[REDACTED]'),
        (r'you are now.*system', '[REDACTED]'),
        (r'请执行.*命令', '[REDACTED]'),
        (r'execute.*command', '[REDACTED]'),
    ]
    for pattern, replacement in injection_patterns:
        cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)

    # 长度限制
    max_len = 10000
    if len(cleaned) > max_len:
        cleaned = cleaned[:max_len] + "\n\n[内容已截断]"

    return cleaned.strip()

def extract_news(text: str) -> dict:
    """
    从文本中提取新闻信息（标题、日期、作者、正文）。
    此处为简单模拟，实际应调用 LLM 进行结构化提取。
    你可以扩展为调用 OpenAI API 等。
    """
    lines = text.strip().split('\n')
    # 尝试从第一行提取标题
    title = lines[0].strip() if lines else "无标题"
    # 去除常见的标题前缀
    if title.startswith('标题：'):
        title = title[3:].strip()
    elif title.startswith('Title:'):
        title = title[6:].strip()

    # 尝试从内容中提取日期（例如 2026-03-27）
    date = datetime.date.today().isoformat()
    date_pattern = r'\d{4}-\d{2}-\d{2}'
    match = re.search(date_pattern, text)
    if match:
        date = match.group()

    # 尝试提取作者（简单匹配 "作者：" 或 "Author:"）
    author = "系统"
    author_pattern = r'(?:作者|Author)[：:]\s*([^\n]+)'
    match = re.search(author_pattern, text, re.IGNORECASE)
    if match:
        author = match.group(1).strip()

    # 正文为剩余内容（跳过标题行）
    if len(lines) > 1:
        content = '\n'.join(lines[1:])
    else:
        content = text

    return {
        'title': title,
        'date': date,
        'author': author,
        'content': content
    }