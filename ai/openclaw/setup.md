## What is OpenClaw

OpenClaw is an open-source, self-hosted AI agent gateway. It runs locally and bridges messaging apps (Telegram, WhatsApp, Discord, Feishu, etc.) to AI models (Claude, GPT, Gemini, MiniMax, local models). All data stays on your hardware.

Key features:
- Filesystem and shell access, browser automation
- Persistent memory, scheduled jobs (cron), webhooks
- 50+ integrations via ClawHub (Gmail, GitHub, Obsidian, etc.)
- Multi-channel: WhatsApp, Telegram, Discord, Slack, Feishu/Lark, iMessage, Signal, Teams, LINE, and more

---

## Preparation

### Local machine requirements
- macOS / Linux / WSL2 (Windows native has limited support)
- Node.js v22+ — check with `node --version`
- brew (macOS)

### 3rd party platforms

#### Model API token

Recommended: **MiniMax**

> Caution: MiniMax has CN and international versions with different API endpoints.

| Version | API Endpoint |
|---|---|
| International | `https://api.minimax.io/anthropic` |
| China (CN) | `https://api.minimaxi.com/anthropic` |

Both use Anthropic-compatible API format. The CN endpoint requires `Authorization: Bearer` header (not `x-api-key` — a common source of 401 errors).

Supported models: `MiniMax-M2.5`, `MiniMax-M2.5-highspeed`

#### Telegram bot

1. Message `@BotFather` on Telegram
2. Send `/newbot` and follow prompts → copy the bot token (`123456789:AABBccdd...`)
3. Optional BotFather settings:
   - `/setprivacy` → **Disabled** (if bot needs to see all group messages, not just mentions)
   - `/setjoingroups` → **Enabled** (to allow adding to groups)
4. In groups where the bot needs full message access: grant it **admin status**

Reference: https://apps.make.com/telegram

#### Feishu / Lark bot

1. Create app at https://open.feishu.cn/app (CN) or https://open.larksuite.com/app (international)
2. From **Credentials & Basic Info**: copy **App ID** (`cli_xxx`) and **App Secret**
3. Under **Permissions**, batch import these scopes:
   ```json
   {
     "scopes": {
       "tenant": [
         "im:message", "im:message:send_as_bot", "im:message:readonly",
         "im:message.p2p_msg:readonly", "im:message.group_at_msg:readonly",
         "im:chat.members:bot_access", "im:chat.access_event.bot_p2p_chat:read",
         "im:resource", "contact:user.employee_id:readonly",
         "cardkit:card:read", "cardkit:card:write",
         "aily:file:read", "aily:file:write"
       ],
       "user": ["aily:file:read", "aily:file:write", "im:chat.access_event.bot_p2p_chat:read"]
     }
   }
   ```
4. **App Capability > Bot**: enable bot, set a bot name
5. **Event Subscription**: select "Use long connection to receive events" (WebSocket — no public URL needed)
6. Add event: `im.message.receive_v1`
7. **Version Management & Release**: create version, submit for review, publish

Reference: https://docs.openclaw.ai/channels/feishu

---

## OpenClaw Install

```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

What the script does:
1. Detects OS and Node.js version, installs Node.js v22+ if needed
2. Installs the `openclaw` npm package globally
3. Launches interactive onboarding wizard
4. Registers gateway as a background service (launchd on macOS, systemd on Linux)

**Verify installation:**
```bash
openclaw doctor          # diagnose config issues
openclaw status          # check gateway and channels
openclaw dashboard       # open browser UI at http://127.0.0.1:18789/
```

**Alternative installs:**
```bash
# npm manual
npm install -g openclaw@latest
openclaw onboard --install-daemon

# pnpm
pnpm add -g openclaw@latest
pnpm approve-builds -g
openclaw onboard --install-daemon

# from source
git clone https://github.com/openclaw/openclaw.git
cd openclaw && pnpm install && pnpm ui:build && pnpm build
pnpm link --global && openclaw onboard --install-daemon
```

---

## Configuration

Config file: `~/.openclaw/openclaw.json` (JSON5 format — comments and trailing commas allowed)

**Minimum working config:**
```json5
{
  agent: { workspace: "~/.openclaw/workspace" },
  channels: { telegram: { botToken: "YOUR_TOKEN", allowFrom: ["123456789"] } },
}
```

**Config with MiniMax (international):**
```json5
{
  agent: {
    workspace: "~/.openclaw/workspace",
    model: { primary: "minimax/MiniMax-M2.5" },
  },
  models: {
    providers: {
      minimax: {
        baseUrl: "https://api.minimax.io/anthropic",  // use api.minimaxi.com for CN
        api: "anthropic-messages",
        apiKey: "${MINIMAX_API_KEY}",
      },
    },
  },
  channels: {
    telegram: {
      enabled: true,
      botToken: "${TELEGRAM_BOT_TOKEN}",
      dmPolicy: "pairing",
      groups: { "*": { requireMention: true } },
    },
    feishu: {
      enabled: true,
      dmPolicy: "pairing",
      accounts: {
        main: { appId: "cli_xxx", appSecret: "xxx", botName: "My AI" }
      },
    },
  },
}
```

**Set secrets via env or `~/.openclaw/.env`:**
```bash
export MINIMAX_API_KEY="your-key-here"
export TELEGRAM_BOT_TOKEN="123:abc"
```

**Config management commands:**
```bash
openclaw config get channels.telegram.botToken
openclaw config set channels.telegram.enabled true --json
openclaw config validate
```

---

## Running

```bash
# Foreground (testing)
openclaw gateway

# Background daemon
openclaw gateway install
openclaw gateway start
openclaw gateway status

# Web dashboard
openclaw dashboard    # http://127.0.0.1:18789/

# Terminal UI
openclaw tui
```

**After starting, pair users:**
```bash
openclaw pairing list telegram          # see pending pairing codes
openclaw pairing approve telegram <CODE>
```

---

## Key CLI Commands

```bash
# Status & health
openclaw status [--all]
openclaw gateway status
openclaw logs --follow
openclaw doctor [--fix]

# Channels
openclaw channels list
openclaw channels status --probe
openclaw channels login --channel whatsapp    # QR code login

# Models
openclaw models list
openclaw models set <model>

# Agents
openclaw agents list
openclaw agent --message "text"

# Gateway lifecycle
openclaw gateway start / stop / restart / install / uninstall

# Update
openclaw update [--channel stable|beta|dev]
```

---

## Troubleshooting

**Bot not responding:**
```bash
openclaw pairing list --channel <channel>   # check pending approvals
openclaw logs --follow                       # watch for "drop", "blocked", "pairing request"
```

**MiniMax 401 error (CN endpoint):**
- Use `api.minimaxi.com` (not `api.minimax.io`) for CN
- Dashboard: Config → models → enable "Auth Header" toggle

**Gateway won't start:**
- `EADDRINUSE`: port conflict — change port or use `--force`
- `"refusing to bind without auth"`: add token or password auth before binding to non-loopback

**Messages arrive but no reply in groups:**
- `requireMention: true` is set — must `@mention` the bot
- Check: `openclaw config get channels.<name>.groups`

**Full diagnostic sequence:**
```bash
openclaw status --all
openclaw gateway probe
openclaw doctor
openclaw channels status --probe
```
