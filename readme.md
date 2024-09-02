# TeleMonit_bot

A project Telegram integrated tools for M/Monit, with our tools you can query event monitoring from M/Monit and reported to Telegram, helping your productivity with alert event if server hape a trouble.

## Feature

- Realtime monitoring (interval set)
- Multiple server monitor
- Monitoring item (Service running, uptime, CPU usage, memory usage)
- Alert (Timeout, server down, high CPU, high memory)


## How to Install

```bash
# Pull reposiroty
git pull https://github.com/tresnax/telemonit_bot.git | cd telemonit_bot

# Create .env file and insert below
TELEGRAM_BOT_TOKEN=yourbottoken
TELEGRAM_CHAT_ID=yourchatid

# Create Database
python createdb.py

# Running Apps
nohup python app.py &
```


### With Docker

```bash
docker run -d --name telemonit_bot \
-e TELEGRAM_BOT_TOKEN=yourtokenbot \
-e TELEGRAM_CHAT_ID=yourchatid \
tresnax/telemonit_bot:latest
```