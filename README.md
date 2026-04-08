# 智能数据分析系统

基于自然语言的数据库查询与可视化应用：在对话中描述需求，由大模型理解意图、生成并执行 SQL，并将结果以表格与图表形式呈现。

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | React 19、TypeScript、Vite、Ant Design、ECharts、Zustand、Axios |
| 后端 | Python、FastAPI、Uvicorn |
| AI / 数据 | LangChain、LangGraph、兼容 OpenAI 的 DashScope（通义千问）接口 |
| 存储 | SQLite（业务库与会话等，路径见环境变量） |

## 架构（一句话）

**浏览器中的 React 界面通过 HTTP/SSE 调用 FastAPI；后端使用 LangChain/LangGraph 与 Qwen 模型完成 NL2SQL 与多轮对话，读写本地 SQLite，前端用 ECharts 渲染可视化。**

<!-- 可选：在此下方插入界面或架构截图 -->
<!-- ![架构或界面截图](./docs/screenshot.png) -->

## 环境要求

- **Node.js** 18+（推荐 LTS）
- **Python** 3.10+

## 安装与运行

### 1. 后端（Python）

在仓库根目录进入 `backend`，创建虚拟环境并安装依赖（首次克隆后执行一次）：

```bash
cd backend
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# Windows CMD:  .venv\Scripts\activate.bat
# macOS / Linux: source .venv/bin/activate

pip install -r requirements.txt
```

复制环境变量模板并按说明填写（详见下文「环境变量」）：

```bash
copy .env.example .env
# macOS / Linux: cp .env.example .env
```

**启动后端（默认 <http://127.0.0.1:8000>）：**

```bash
uvicorn main:app --reload --port 8000
```

健康检查：<http://127.0.0.1:8000/api/health>

### 2. 前端（React）

```bash
cd frontend
npm install
```

**启动前端开发服务器：**

```bash
npm run dev
```

浏览器访问终端中提示的本地地址（Vite 默认为 `http://localhost:5173`）。前端默认请求后端 `http://127.0.0.1:8000/api`（见 `frontend/src/services/api.ts`），请先启动后端。

生产构建：`npm run build`，产物在 `frontend/dist`。

## 环境变量

后端从 **`backend/.env`** 读取配置。请勿将真实密钥提交到 Git；以 **`backend/.env.example`** 为模板创建 `.env`。

| 变量 | 说明 |
|------|------|
| `DASHSCOPE_API_KEY` | 阿里云 DashScope API Key（通义千问等） |
| `MODEL_NAME` | 模型名称，如 `qwen3.6-plus` |
| `DASHSCOPE_BASE_URL` | 兼容 OpenAI 的 API 根地址 |
| `BUSINESS_DB_PATH` | 业务 SQLite 数据库文件路径 |
| `SESSION_DB_PATH` | 会话相关 SQLite 路径 |
| `MEMORY_WINDOW_SIZE` | 对话记忆窗口大小 |
| `ENABLE_THINKING` | 是否启用思考链等（`true` / `false`） |
| `TEMPERATURE` | 采样温度 |

完整示例见：**[backend/.env.example](backend/.env.example)**。

## 仓库信息

远程仓库（示例）：`https://github.com/HaoYu-4B11/VibeCodingProject_V1`
