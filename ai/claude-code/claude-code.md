# Claude Code 安装指南

Claude Code 对于中国大陆用户，直接使用面临网络与账号双重门槛。但可以通过本地部署 + 国产大模型兼容层（GLM/DeepSeek）方案，实现无障碍安装使用。
**操作起来很简单，只需要3个步骤即可。**

## 1. 基础环境与工具安装

Claude Code 依赖 Node.js 环境运行。**请确保已安装 [Node.js](https://nodejs.org/)**。
下载Nodejs之后，双击安装即可。

打开终端（Windows 推荐 PowerShell/CMD，Mac 使用 Terminal），按顺序执行以下命令完成从检查到安装的全流程：

1. 检查 Node.js 环境（必须有版本号返回）
```bash
node -v
npm -v
```
2. 安装 Claude Code（使用 -g 进行全局安装）
```bash
npm install -g @anthropic-ai/claude-code
```
3. 验证安装
```bash
claude --version
```
看到版本号即安装成功。输出示例：2.1.2 (Claude Code) 

如果在npm install这一步遇到卡顿，建议搜索watt toolkit加速器（windows应用商店搜索然后安装），或者使用国内npm中转，具体做法是在npm install命令后面添加参数：

```bash
npm install -g @anthropic-ai/claude-code --registry=https://registry.npmmirror.com
```


## 2. Claude账号问题

安装完成后，需要解决“谁来驱动”的问题，**根据你的网络与账号情况**选择路径：

*   **路径 A：标准模式（美国、欧洲等支持地区）**
    **如果你身处海外环境且有 Anthropic 账号**，直接运行 `claude login`，系统会打开浏览器，让你登录Claude，进行 OAuth 授权。登录完成后即可顺畅使用Claude Code。那么对于你来说，现在已经安装成功了。

*   **路径 B：兼容模式（中国大陆推荐）**
    国内用户无需注册 Anthropic 账号，可直接使用**智谱 GLM**或**DeepSeek**的 API 来驱动 Claude Code。这两者均提供了官方兼容接口。具体看第三步。

## 3. 核心配置：使用兼容模型，绕过Claude登录验证

为了让 Claude Code 连接到兼容模型（智谱GLM, DeepSeek)。

- 请求 / 响应结构与 Anthropic 基本一致
- 可直接作为 Claude Code 的后端
- 不需要登录 Anthropic 官网账号

### 方案一：通过命令行设置环境变量

我们需要配置 `BASE_URL` 和 `API_KEY`
为了避免每次重启终端丢失配置，以下命令将直接写入系统**永久环境变量**。

*   **智谱 GLM Base URL**: `https://open.bigmodel.cn/api/anthropic`
*   **DeepSeek Base URL**: `https://api.deepseek.com/anthropic`

请根据你的系统，复制对应的命令块运行（只需运行一次）：

#### Windows 用户 (CMD 命令提示符)
使用 setx 命令写入用户级永久变量
```cmd
setx ANTHROPIC_BASE_URL "https://open.bigmodel.cn/api/anthropic"
setx ANTHROPIC_AUTH_TOKEN "你的_GLM_API_KEY"
setx ANTHROPIC_MODEL "glm-4.6"
```

注意：运行后需重启 CMD 窗口才会生效

#### macOS / Linux 用户 (Shell)
```bash
echo 'export ANTHROPIC_BASE_URL="https://open.bigmodel.cn/api/anthropic"' >> ~/.zshrc
echo 'export ANTHROPIC_AUTH_TOKEN="你的_GLM_API_KEY"' >> ~/.zshrc
echo 'export ANTHROPIC_MODEL=glm-4.6' >> ~/.zshrc

source ~/.zshrc
```

如果使用DeepSeek则使用DeepSeek的url和api key，模型名则是deepseek-chat。

### 方案二：通过配置文件修改环境变量

通过修改本地配置文件，可以强制 Claude Code (CLI) 连接到 DeepSeek 或其他兼容 Anthropic 协议的模型，并跳过官方的浏览器登录验证。

#### 1. 文件结构总览
需要修改的文件位于用户根目录下。请确保文件位置和层级完全一致：

```text
C:\Users\用户名\
│
├── 📄 .claude.json                 <-- 【状态文件】 修改这个文件内容，添加"hasCompletedOnboarding": true,
│
└── 📂 .claude\                     <-- 【配置文件夹】 这是claude全局文件夹
    └── ⚙️ settings.json            <-- 【配置文件】 新建这个settings.json文件，并添加环境变量
```

#### 2. 详细配置指南

1. 配置 API 连接 (`.claude\settings.json`)
此文件用于接管网络请求，将其重定向到第三方服务（如 GLM/DeepSeek）。
*   **路径**: `C:\Users\你的用户名\.claude\settings.json`
*   **内容**: 新建这个setting.json文件，用记事本打开，在里面添加下面这段内容：

```json
{
    "env": {
        // 将地址改为 DeepSeek 或 GLM 的 Anthropic 兼容接口
        "ANTHROPIC_BASE_URL": "https://api.deepseek.com/anthropic",
        // 填写对应的 API Key
        "ANTHROPIC_AUTH_TOKEN": "你的API Key",
        // 禁用遥测和联网检查，防止因地区问题导致的报错
        "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"
    }
}
```

2. 绕过登录验证 (`.claude.json`)
此文件用于伪造“老用户”状态，防止 CLI 启动时弹出浏览器进行 OAuth 验证。
*   **路径**: `C:\Users\你的用户名\.claude.json` 
*   **内容**: 用记事本打开这个文件，在其中添加一项

```json
	"hasCompletedOnboarding": true,  // 核心：告诉程序已完成新手引导，直接进入对话
```



## 4. 启动与常用指令

环境变量配置完毕后，无需登录，直接启动即可。

*   **启动程序**：在命令行中输入 `claude`，然后回车。
    *   *成功标志*：出现 "Welcome to Claude Code" 欢迎语，且未弹出浏览器。
*   **退出程序**：在交互界面输入`exit`，回车。

**常用交互指令**：
*   `/clear`：清除上下文记忆（节省 Token，开启新任务时推荐）。
*   `/compact`：压缩上下文（处理长任务时使用）。
*   `/help`：查看所有可用命令。
*   `Alt + Enter` (Win) / `Opt + Enter` (Mac)：在对话框中换行。