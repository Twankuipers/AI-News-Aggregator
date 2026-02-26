# AI News Agent

This README covers only setup and how to run the news agent.

## Requirements

- Python 3.10+
- Internet access

## Install dependencies

```bash
pip install -r requirements.txt
```

## Configure sources and notifications

Edit `config.json` to enable sources and set notifications.

### Email via Gmail SMTP

```json
{
  "email_config": {
    "enabled": true,
    "method": "smtp",
    "smtp": {
      "host": "smtp.gmail.com",
      "port": 587,
      "username": "your-email@gmail.com",
      "password": "YOUR-16-CHAR-APP-PASSWORD",
      "from_email": "your-email@gmail.com",
      "to_email": "your-email@gmail.com"
    }
  }
}
```

### Slack webhook

```json
{
  "slack_config": {
    "enabled": true,
    "webhook_url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
  }
}
```

### Optional local overrides

For local secrets, you can create a `config.local.json` file. It is loaded automatically and deep-merged over `config.json`. Keep this file out of version control.

## Run the agent

```bash
python ai_news_agent.py
```

Outputs:
- `output/` contains the daily digest files
- `logs/` contains the daily log file
- `data/seen_items.json` tracks deduplication state

## Schedule on Windows

Run the provided PowerShell script as Administrator:

```bash
pwsh -ExecutionPolicy Bypass -File setup_scheduler.ps1
```

## Run daily on GitHub Actions

The workflow in `.github/workflows/daily-news.yml` runs the agent on a schedule.

Set these GitHub Actions secrets (Slack or Email, or both):

Slack:
- `SLACK_ENABLED` = `true`
- `SLACK_WEBHOOK_URL` = `https://hooks.slack.com/services/YOUR/WEBHOOK/URL`

Email (SMTP):
- `EMAIL_ENABLED` = `true`
- `EMAIL_METHOD` = `smtp`
- `EMAIL_SMTP_SERVER` = `smtp.gmail.com`
- `EMAIL_SMTP_PORT` = `587`
- `EMAIL_USER` = `your-email@gmail.com`
- `EMAIL_PASSWORD` = `your-app-password`
- `EMAIL_FROM` = `your-email@gmail.com`
- `EMAIL_TO` = `your-email@gmail.com`

To change the run time, edit the `cron:` line in the workflow.
