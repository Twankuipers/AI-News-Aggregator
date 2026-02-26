# Email & Slack Notifications Setup Guide

This guide shows you how to set up automatic email and/or Slack notifications for your AI News Digest.

## Quick Start

To send emails or Slack messages every morning:

1. Choose your notification method (Email, Slack, or both)
2. Configure the appropriate service (see sections below)
3. Update `config.json` with your credentials
4. Set up Windows Task Scheduler for daily execution
5. Test it!

---

## Option 1: Email via Gmail (SMTP)

### Setup (Takes 5 minutes)

**Step 1: Enable 2-Factor Authentication**
1. Go to https://myaccount.google.com/security
2. Enable 2-Step Verification if not already enabled

**Step 2: Create an App Password**
1. Go to https://myaccount.google.com/apppasswords
2. Select: App = "Mail", Device = "Windows Computer" (or your device)
3. Click "Generate"
4. Copy the generated 16-character password

**Step 3: Update config.json**
```json
{
  "email_config": {
    "enabled": true,
    "method": "smtp",
    "smtp": {
      "host": "smtp.gmail.com",
      "port": 587,
      "username": "your-email@gmail.com",
      "password": "your-16-character-app-password",
      "from_email": "your-email@gmail.com",
      "to_email": "your-email@gmail.com"
    }
  }
}
```

**Step 4: Test it**
```bash
python ai_news_agent.py
```

You should receive an email within a few seconds!

### Common Issues

**"Login failed"**
- Make sure you created an App Password (not your regular password)
- Verify 2-Factor Authentication is enabled

**"Port 587 connection refused"**
- Try port 465 instead
- Change `"host": "smtp.gmail.com"` to `"smtp.gmail.com:465"`

---

## Option 2: Email via Outlook (SMTP)

### Setup (Takes 3 minutes)

**Step 1: Update config.json**
```json
{
  "email_config": {
    "enabled": true,
    "method": "smtp",
    "smtp": {
      "host": "smtp-mail.outlook.com",
      "port": 587,
      "username": "your-email@outlook.com",
      "password": "your-outlook-password",
      "from_email": "your-email@outlook.com",
      "to_email": "recipient@example.com"
    }
  }
}
```

**Step 2: Test it**
```bash
python ai_news_agent.py
```

---

## Option 3: Email via SendGrid API

### Setup (Takes 10 minutes)

**Step 1: Create SendGrid Account**
1. Sign up at https://sendgrid.com
2. Verify your email address
3. Set up a Single Sender (your email address)

**Step 2: Create API Key**
1. Go to https://app.sendgrid.com/settings/api_keys
2. Click "Create API Key"
3. Give it a name like "AI News Aggregator"
4. Copy the API key

**Step 3: Update config.json**
```json
{
  "email_config": {
    "enabled": true,
    "method": "api",
    "api": {
      "provider": "sendgrid",
      "api_key": "SG.your-api-key-here",
      "from_email": "your-verified-sender@example.com",
      "to_email": "recipient@example.com"
    }
  }
}
```

**Step 4: Test it**
```bash
python ai_news_agent.py
```

### Benefits vs Gmail
- No app password needed (more secure)
- Can send up to 100+ emails/day (free tier)
- Better deliverability

---

## Option 4: Email via Mailgun API

### Setup (Takes 10 minutes)

**Step 1: Create Mailgun Account**
1. Sign up at https://www.mailgun.com
2. Create a free account

**Step 2: Get API Credentials**
1. Go to https://app.mailgun.com/app/account/security/api_keys
2. Copy your API Key
3. Go to https://app.mailgun.com/app/dashboard and find your domain (e.g., `sandbox1234.mailgun.org`)

**Step 3: Update config.json**
```json
{
  "email_config": {
    "enabled": true,
    "method": "api",
    "api": {
      "provider": "mailgun",
      "api_key": "your-api-key-here",
      "from_email": "noreply@yourdomain.com",
      "to_email": "your-email@example.com",
      "domain": "sandboxxxxxxx.mailgun.org"
    }
  }
}
```

**Step 4: Test it**
```bash
python ai_news_agent.py
```

---

## Option 5: Slack Notifications

### Setup (Takes 5 minutes)

**Step 1: Create Slack Channel (Optional)**
- Create a channel in your Slack workspace for notifications
- Name it something like `#ai-news-digest`

**Step 2: Create Incoming Webhook**
1. Go to https://api.slack.com/messaging/webhooks
2. Click "Create New App"
3. Choose "From scratch"
4. App Name: "AI News Digest", Workspace: select your workspace
5. Click "Create App"
6. Go to "Incoming Webhooks" in the left menu
7. Toggle "Activate Incoming Webhooks" to "On"
8. Click "Add New Webhook to Workspace"
9. Select your channel and click "Allow"
10. Copy the Webhook URL

**Step 3: Update config.json**
```json
{
  "slack_config": {
    "enabled": true,
    "webhook_url": "https://hooks.slack.com/services/XXXXXX/XXXXXX/XXXXXX"
  }
}
```

**Step 4: Test it**
```bash
python ai_news_agent.py
```

You should see a message in your Slack channel!

### Example Slack Message

```
🤖 *AI News Digest* - February 26, 2026

*ArXiv AI Papers*
• <https://arxiv.org/abs/2602.22067|Semantic Partial Grounding via LLMs>
• <https://arxiv.org/abs/2602.22055|Physics-Informed Machine Learning>

*OpenAI Blog*
• <https://openai.com/blog/gpt-5|GPT-5 Release Announcement>

[... more items ...]
```

---

## Step-by-Step: Schedule for Daily Morning Emails

### Windows Task Scheduler Setup

**Step 1: Open Task Scheduler**
```
Press: Win + R
Type: taskschd.msc
Press: Enter
```

**Step 2: Create Basic Task**
1. Right-click "Task Scheduler Library" → "Create Basic Task"
2. **Name:** `AI News Digest Daily`
3. **Description:** `Fetch AI news and send morning digest`
4. Click "Next"

**Step 3: Set Trigger (Time)**
1. Select "Daily"
2. **Start:** [Today's date]
3. **Time:** 9:00:00 AM (or your preferred time)
4. **Recur every:** 1 day
5. Click "Next"

**Step 4: Set Action (What to Run)**
1. Select "Start a program"
2. **Program/script:** `python`
3. **Add arguments:** `ai_news_agent.py`
4. **Start in (optional):** `C:\Users\twank\Topicus-Local\workshop`
5. Click "Next"

**Step 5: Review & Finish**
1. Check "Open the Properties dialog" to set additional options (optional)
2. Click "Finish"

**Step 6: Test the Task**
1. In Task Scheduler, find "AI News Digest Daily"
2. Right-click → "Run"
3. Check your email/Slack for the digest!

### Additional Settings (Optional)

In Task Scheduler properties:
- **General tab:**
  - Check "Run whether user is logged in or not"
  - Check "Run with highest privileges"

- **Triggers tab:**
  - Add another trigger for afternoon (e.g., 2 PM)
  - Add triggers for weekends if desired

- **Conditions tab:**
  - Uncheck "Start the task only if the computer is on AC power" (if on laptop)
  - Uncheck "Stop the task if it runs longer than X hours"

- **Settings tab:**
  - Check "Allow task to be run on demand"
  - Check "If the task fails, restart every: 1 minute"

---

## Combining Email + Slack

You can send BOTH email AND Slack notifications! Just enable both:

```json
{
  "email_config": {
    "enabled": true,
    "method": "smtp",
    "smtp": { ... }
  },
  "slack_config": {
    "enabled": true,
    "webhook_url": "https://hooks.slack.com/services/..."
  }
}
```

Now the agent will send:
- ✉️ Email with formatted HTML digest
- 💬 Slack message with quick summary
- 📁 Files saved in `output/` for reference

---

## Troubleshooting

### Email not sending?

1. **Check the log file:**
   ```
   cat logs/agent_2026-02-26.log
   ```

2. **Verify credentials:**
   - Gmail: Test credentials first at https://myaccount.google.com/security
   - SendGrid: Check API key at https://app.sendgrid.com/settings/api_keys
   - Mailgun: Verify API key and domain match

3. **Check firewall/antivirus:**
   - Some firewalls block SMTP port 587/465
   - Try a different network or contact IT

4. **Gmail specific:**
   - Did you use an App Password (16 chars)?
   - Is 2-Factor Authentication enabled?

### Slack not posting?

1. **Test the webhook:**
   ```bash
   curl -X POST -H 'Content-type: application/json' \
     --data '{"text":"Test message"}' \
     YOUR_WEBHOOK_URL
   ```

2. **Check webhook URL:**
   - Make sure it starts with `https://hooks.slack.com/services/`
   - Verify it's current (webhooks can expire)

3. **Check channel permissions:**
   - Make sure the app has permission to post in the channel
   - Try re-authorizing the webhook

### Task Scheduler not running?

1. **Check if task ran:**
   - Task Scheduler → History tab
   - Look for "AI News Digest Daily"

2. **Check python path:**
   - Open PowerShell and type `python --version`
   - If not recognized, add Python to PATH

3. **Run manually to test:**
   ```bash
   python ai_news_agent.py
   ```

4. **Check logs:**
   - Review `logs/agent_YYYY-MM-DD.log`

---

## Security Notes

### Protecting Your Credentials

⚠️ **Never commit `config.json` to GitHub with real credentials!**

Options:
1. **Option A: Use environment variables**
   ```json
   "password": "${GMAIL_PASSWORD}"
   ```
   Then set in PowerShell:
   ```bash
   $env:GMAIL_PASSWORD = "your-app-password"
   ```

2. **Option B: Use .env file (in .gitignore)**
   ```
   GMAIL_PASSWORD=your-app-password
   SLACK_WEBHOOK=https://hooks.slack.com/...
   ```

3. **Option C: Store separately**
   - Save credentials in a secure location
   - Only reference in config.json

### Best Practices

- Use App Passwords instead of main passwords (Gmail)
- Rotate API keys monthly
- Never share `config.json` with credentials
- Add `config.json` to `.gitignore` if using Git
- Use API keys instead of passwords when available (SendGrid, Mailgun)

---

## Testing

### Test Email Sending:

```bash
python ai_news_agent.py
```

### Test Slack Only:

Temporarily disable email:
```json
{
  "email_config": { "enabled": false },
  "slack_config": { "enabled": true, "webhook_url": "..." }
}
```

### Test Email Only:

Temporarily disable Slack:
```json
{
  "email_config": { "enabled": true, ... },
  "slack_config": { "enabled": false }
}
```

---

## Next Steps

1. ✅ Choose a notification method (Gmail, SendGrid, Mailgun, Slack, or combination)
2. ✅ Configure `config.json` with your credentials
3. ✅ Test: `python ai_news_agent.py`
4. ✅ Schedule with Task Scheduler
5. ✅ Sit back and receive daily AI news digests! 🎉

---

## Support

**Issue with setup?**
- Check the log file in `logs/agent_YYYY-MM-DD.log`
- Verify credentials in `config.json`
- Test manually first: `python ai_news_agent.py`

**Questions?**
- See `agent.md` for full documentation
- Check the specific service's documentation:
  - Gmail: https://support.google.com/accounts
  - SendGrid: https://docs.sendgrid.com
  - Mailgun: https://documentation.mailgun.com
  - Slack: https://api.slack.com

---

**Last Updated:** February 26, 2026
