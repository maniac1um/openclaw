# OpenClaw 自动化新闻发布系统

本项目是一个基于 Flask 的本地服务器，用于支持 OpenClaw Agent 的自动化新闻发布功能。服务器接收来自 Agent 的新闻稿文本，自动提取信息、保存数据、生成静态网站并执行 Git 操作，实现全流程自动化。

## 功能特点

- **Webhook 接口**：接收 POST 请求，处理新闻稿发布
- **安全清洗**：防止 Prompt 注入攻击，输入数据安全处理
- **信息提取**：自动解析新闻标题、内容、作者、日期
- **数据存储**：以 JSON 格式保存新闻到 `data/news/` 目录
- **网站生成**：使用 Jinja2 模板动态生成静态 HTML 页面
- **版本管理**：自动 Git 提交和推送，仅操作指定目录
- **静态服务**：提供网站访问服务

## 系统架构

```
用户输入 → OpenClaw Agent → POST /api/webhook → Flask 服务器
    ↓
1. 清洗输入（防注入）
2. 提取新闻信息（标题、内容、作者、日期）
3. 保存为 data/news/YYYY-MM-DD-slug.json
4. 调用 generate_site.py 重新生成 web/index.html
5. Git 操作：add web/ → commit → push
    ↓
返回响应 → Agent → 用户反馈
```

## 目录结构

```
openclaw/
├── README.md
├── REQUIRMENTS.txt
├── config/
├── data/
│   ├── index.json
│   └── news/          # 新闻 JSON 文件存储目录
│       ├── test.json
│       └── ...
├── openclaw config/   # OpenClaw 配置（待补充）
├── scripts/
│   ├── generate_site.py  # 网站生成脚本
│   ├── init_repo.sh      # 仓库初始化脚本
│   └── start_server.sh  # 服务器启动脚本
├── src/
│   ├── __init__.py
│   ├── server/
│   │   ├── __init__.py
│   │   ├── app.py           # Flask 应用入口
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── webhook.py   # Webhook 接口路由
│   │       └── website.py   # 网站服务路由
│   └── templates/
│       └── index.html       # 网站首页模板
│   └── tools/
│       ├── __init__.py
│       ├── file_tools.py    # 文件操作工具
│       ├── git_tools.py     # Git 操作工具
│       └── news_parser.py   # 新闻解析工具
├── tests/
├── web/
│   └── index.html           # 生成的静态网站首页
└── ...
```

## 环境要求

- Python 3.10+
- Git（用于版本管理）
- Linux/Windows/macOS

## 安装步骤

1. **克隆或下载项目**
   ```bash
   cd /path/to/openclaw
   ```

2. **创建虚拟环境**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   # 或
   .venv\Scripts\activate     # Windows
   ```

3. **安装依赖**
   ```bash
   pip install -r REQUIRMENTS.txt
   ```

4. **初始化 Git 仓库**
   ```bash
   ./scripts/init_repo.sh
   # 如果需要设置远程仓库：
   # ./scripts/init_repo.sh https://github.com/username/repo.git
   ```

5. **创建必要目录**
   ```bash
   mkdir -p data/news web
   ```

## 运行服务器

### 方式一：直接运行 Python
```bash
# 设置环境变量（可选）
export PORT=5000
export DEBUG=True
export REPO_PATH=.

# 运行服务器
python3 -m src.server.app
```

### 方式二：使用启动脚本（推荐）
```bash
./scripts/start_server.sh
```

服务器将在 `http://localhost:5000` 启动，提供以下服务：
- Webhook 接口：`POST http://localhost:5000/api/webhook`
- 网站访问：`http://localhost:5000/`

## API 文档

### POST /api/webhook

接收新闻稿发布请求。

**请求格式：**
```json
{
  "news_text": "新闻标题\n\n新闻内容\n\n作者：张三\n\n日期：2026-04-01"
}
```

**响应格式：**
```json
{
  "status": "ok",
  "news": {
    "title": "新闻标题",
    "content": "新闻内容",
    "author": "张三",
    "date": "2026-04-01",
    "_saved_at": "2026-04-01T12:00:00"
  },
  "commit": "abc1234"
}
```

**错误响应：**
```json
{
  "error": "错误信息"
}
```

**新闻稿格式说明：**
- 支持标准格式：标题 + 内容 + 作者 + 日期（每行一个）
- 支持简化格式：至少标题和内容
- 作者行：`作者：姓名` 或 `记者：姓名`
- 日期行：`日期：YYYY-MM-DD` 或直接日期字符串
- 自动提取日期格式 `YYYY-MM-DD`

## 使用流程

1. **启动服务器**
   ```bash
   python3 -m src.server.app
   ```

2. **发送测试请求**
   ```bash
   curl -X POST http://localhost:5000/api/webhook \
        -H "Content-Type: application/json" \
        -d '{"news_text": "测试新闻\n\n这是测试内容\n\n作者：测试者\n\n日期：2026-04-01"}'
   ```

3. **查看结果**
   - 新闻 JSON 文件保存在 `data/news/`
   - 网站更新在 `web/index.html`
   - Git 提交历史记录发布操作

4. **访问网站**
   打开浏览器访问 `http://localhost:5000/` 查看生成的新闻网站

## 安全特性

- **输入清洗**：移除控制字符，检测并过滤注入模式
- **路径安全**：Git 操作仅允许指定目录，防止路径遍历
- **命令验证**：Commit 消息过滤危险字符
- **不提交 `web/index.html`**：Webhook 提交排除 `web/index.html`，仅对其他已暂存内容生效
- **长度限制**：输入文本最大长度 10000 字符

## 扩展开发

- **自定义解析器**：修改 `src/tools/news_parser.py` 中的 `extract_news` 函数
- **更换模板**：编辑 `src/templates/index.html` 自定义网站样式
- **添加工具**：在 `src/tools/` 下添加新的工具模块
- **扩展路由**：在 `src/server/routes/` 下添加新的 API 接口

## OpenClaw Agent 集成

[待补充：OpenClaw 本体部署过程]

## Skill 部署过程

[待补充：自动化新闻发布 Skill 的部署和配置过程]

---

*本项目由 OpenClaw Agent 驱动，实现自动化新闻发布工作流。*
- OpenClaw (最新版)
- Git 2.40+
- Ubuntu / macOS / Windows WSL2
