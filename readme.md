# TeleMonit_bot

A telegram bot project integrated with Monit, you can monitor the system easily and get an alarm if there is a problem on the server directly with the telegram bot.

## Feature

- Realtime monitoring
- Multiple Server
- Monitoring Event (Service running, uptime, CPU usage, memory usage)
- Alert (Timeout, server down, high CPU, high memory)
- Settings (interval, cpu and memory usage)

## How to Install

```bash
# Pull reposiroty
git pull https://github.com/tresnax/telemonit_bot.git | cd telemonit_bot

# Create .env file and insert below
TELEGRAM_BOT_TOKEN=yourbottoken
TELEGRAM_CHAT_ID=yourchatid

# Create venv
python venv .venv
source .venv/bin/activate

# Install Dependency
pip install -r requirements.txt

# Create Database
python createdb.py

# Running Apps
nohup python app.py &
```

## Install with Docker

```bash
# Create Volume
docker volume create telemonit_bot

# Run Docker
docker run -d --name telemonit_bot \
-e TELEGRAM_BOT_TOKEN=yourtokenbot \
-e TELEGRAM_CHAT_ID=yourchatid \
-v telemonit_bit:/app \
tresnax/telemonit_bot:latest
```

## Screenshoots
<img src="img/Screenshot_from_2024-09-04_16-28-11.png" alt="Screenshot" width="30%">
<img src="img/Screenshot_from_2024-09-04_16-27-14.png" alt="Screenshot" width="30%">
<img src="img/Screenshot_from_2024-09-04_16-27-50.png" alt="Screenshot" width="30%">
