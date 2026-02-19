# 🛡️ Discord News Bot — Taggart Institute Intel Center

Monitors the [Taggart Institute Intel Center](https://intel.taggartinstitute.org/i/) RSS feed and sends new cybersecurity articles to a Discord channel via webhook.

![Python](https://img.shields.io/badge/python-3.10+-blue)

## What it does

- Polls the FreshRSS feed at `https://intel.taggartinstitute.org/i/?a=rss` on a configurable interval (default: every 5 minutes)
- Detects **new** articles by tracking GUIDs in a local JSON file (`seen_articles.json`)
- Sends a rich Discord **embed** for each new article — with title, link, summary, author, tags, and timestamp
- On the **first run** it records all existing articles without spamming your channel
- Handles Discord rate-limits gracefully

### Sources covered (60+ feeds)

CISA Advisories · BleepingComputer · Krebs on Security · The Record · CyberScoop · Ars Technica · DataBreaches.net · 404 Media · Cisco Talos · Sophos · Huntress · Unit 42 · Schneier on Security · SANS ISC · and many more…

---

## Quick Start

### 1. Create a Discord Webhook

1. Open your Discord server
2. Go to **Server Settings → Integrations → Webhooks**
3. Click **New Webhook**, pick your channel, and copy the **Webhook URL**

### 2. Set up the bot

```bash
cd Discord_News_Bot

# Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create your config
cp .env.example .env
```

### 3. Configure

Edit `.env` and paste your webhook URL:

```
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/1234567890/abcdefg...
```

Optional settings in `.env`:

| Variable             | Default                                                   | Description                    |
| -------------------- | --------------------------------------------------------- | ------------------------------ |
| `DISCORD_WEBHOOK_URL`| *(required)*                                              | Your Discord channel webhook   |
| `RSS_FEED_URL`       | `https://intel.taggartinstitute.org/i/?a=rss`             | RSS feed to monitor            |
| `CHECK_INTERVAL`     | `300`                                                     | Seconds between feed checks    |

### 4. Run

```bash
python bot.py
```

On the **first run**, the bot will silently index all current articles. From then on, it will send a Discord embed for every new article it finds.

---

## Running in the background

### Option A — `nohup`
```bash
nohup python bot.py &
```

### Option B — `systemd` (Linux)

Create `/etc/systemd/system/discord-news-bot.service`:

```ini
[Unit]
Description=Discord News Bot
After=network.target

[Service]
WorkingDirectory=/path/to/Discord_News_Bot
ExecStart=/path/to/Discord_News_Bot/venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable --now discord-news-bot
```

### Option C — `launchd` (macOS)

Create `~/Library/LaunchAgents/com.discord-news-bot.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.discord-news-bot</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/Discord_News_Bot/venv/bin/python</string>
        <string>/path/to/Discord_News_Bot/bot.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>WorkingDirectory</key>
    <string>/path/to/Discord_News_Bot</string>
</dict>
</plist>
```

```bash
launchctl load ~/Library/LaunchAgents/com.discord-news-bot.plist
```

---

## How it looks in Discord

Each article is sent as a rich embed:

> **🛡️  CISA Adds Two Known Exploited Vulnerabilities to Catalog**
>
> CISA has added two new vulnerabilities to its Known Exploited Vulnerabilities (KEV) Catalog…
>
> **Tags:** `Cybersecurity` · `CISA` · `KEV`
>
> *Source: CISA  ·  Feb 18, 2026*

---

## Project Structure

```
Discord_News_Bot/
├── bot.py              # Main bot script
├── requirements.txt    # Python dependencies
├── .env.example        # Config template
├── .env                # Your config (git-ignored)
├── .gitignore
├── seen_articles.json  # Auto-generated article tracker (git-ignored)
└── README.md
```
