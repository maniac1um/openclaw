import re
import datetime
from typing import Dict

def sanitize_input(raw_text: str) -> str:
    """
    清洗新闻文本，防止 Prompt 注入攻击
    """
    # 移除控制字符（但保留换行符 \n 和回车符 \r）
    # \x00-\x08: 控制字符
    # \x0b-\x0c: 垂直制表符、换页符
    # \x0e-\x1f: 控制字符
    # \x7f: 删除字符
    cleaned = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]', '', raw_text)

    # 检测并移除常见注入模式
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

def extract_news(text: str) -> Dict[str, str]:
    """
    从文本中提取新闻信息（标题、日期、作者、正文）。
    简单有效的解析器，支持标准格式。
    """
    # 清洗输入
    cleaned_text = sanitize_input(text)
    
    # 获取所有行并去除空白
    lines = [line.strip() for line in cleaned_text.strip().split('\n')]
    
    # 移除空行，保留非空行
    non_empty_lines = [line for line in lines if line]
    
    # 初始化结果
    result = {
        'title': '',
        'content': '',
        'author': '系统',
        'date': datetime.date.today().isoformat(),
        '_saved_at': datetime.datetime.now().isoformat()
    }
    
    if len(non_empty_lines) >= 4:
        # 标准格式：标题、正文、作者、日期（每行一个）
        result['title'] = non_empty_lines[0]
        result['content'] = non_empty_lines[1]
        
        # 处理作者行
        author_line = non_empty_lines[2]
        if author_line.startswith('作者：'):
            result['author'] = author_line[3:].strip()
        elif author_line.startswith('记者：'):
            result['author'] = author_line[3:].strip()
        else:
            result['author'] = author_line
        
        # 处理日期行
        date_line = non_empty_lines[3]
        if date_line.startswith('日期：'):
            date_str = date_line[3:].strip()
        else:
            date_str = date_line
        
        # 提取标准日期格式
        date_match = re.search(r'\d{4}-\d{2}-\d{2}', date_str)
        if date_match:
            result['date'] = date_match.group()
    
    elif len(non_empty_lines) >= 2:
        # 简化格式：至少标题和内容
        result['title'] = non_empty_lines[0]
        
        # 剩余行作为内容，但尝试提取作者和日期
        content_lines = []
        for line in non_empty_lines[1:]:
            # 检查是否是作者行
            if line.startswith('作者：'):
                result['author'] = line[3:].strip()
            elif line.startswith('记者：'):
                result['author'] = line[3:].strip()
            # 检查是否是日期行
            elif line.startswith('日期：'):
                date_str = line[3:].strip()
                date_match = re.search(r'\d{4}-\d{2}-\d{2}', date_str)
                if date_match:
                    result['date'] = date_match.group()
            elif re.match(r'^\d{4}-\d{2}-\d{2}$', line):
                result['date'] = line
            else:
                content_lines.append(line)
        
        result['content'] = '\n'.join(content_lines)
    
    else:
        # 单行或空文本
        if non_empty_lines:
            result['title'] = non_empty_lines[0]
            result['content'] = cleaned_text
    
    # 如果没有找到日期，从整个文本中搜索
    if result['date'] == datetime.date.today().isoformat():
        date_match = re.search(r'\d{4}-\d{2}-\d{2}', cleaned_text)
        if date_match:
            result['date'] = date_match.group()
    
    # 清理作者字段（移除可能包含的日期）
    if result['author'] and re.search(r'\d{4}', result['author']):
        result['author'] = re.sub(r'\s*\d{4}-\d{2}-\d{2}\s*', '', result['author']).strip()
    
    # 确保标题不超过合理长度
    if len(result['title']) > 100:
        result['title'] = result['title'][:97] + '...'
    
    return result