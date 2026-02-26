# 🤖 AI News Aggregator - Quick Start Guide

## 5-Minute Setup for Daily Email/Slack Notifications

### What You'll Get

Every morning at 9 AM (customizable), you'll receive:
- **Email** with formatted AI news digest (HTML + text)
- **Slack message** with AI news summary (optional)
- Both sent automatically while you sleep! 😴

---

## Step 1: Choose Your Notification Method

### Option A: Gmail (Most Popular)
- ✅ Works with existing Gmail account
- ✅ No signup needed
- ✅ Free forever
- ⏱️ Setup time: 5 minutes

### Option B: Slack (Best for Teams)
- ✅ Posts to your Slack channel
- ✅ Integrates with team workflow
- ✅ Free webhook
- ⏱️ Setup time: 5 minutes

### Option C: SendGrid (Most Reliable)
- ✅ Professional email service
- ✅ Better deliverability
- ✅ 100+ emails/day free
- ⏱️ Setup time: 10 minutes

### Recommend: Gmail + Slack for best experience!

---

## Step 2A: Setup Gmail (5 minutes)

**2A.1 - Enable App Password**

1. Go to https://myaccount.google.com/apppasswords
2. Sign in if needed
3. Select:
   - App: **Mail**
   - Device: **Windows Computer**
4. Google will generate a **16-character password**
5. **Copy this password** (you'll need it in Step 3)

If you don't see "App passwords" option:
- Go to https://myaccount.google.com/security
- Enable "2-Step Verification" first, then try again

**Done! ✓ Move to Step 3**

---

## Step 2B: Setup Slack (5 minutes)

**2B.1 - Create Slack Webhook**

1. Go to https://api.slack.com/messaging/webhooks
2. Click **"Create New App"**
3. Select **"From scratch"**
4. App name: `AI News Digest`
5. Pick your workspace → **Create App**
6. Go to **"Incoming Webhooks"** (left menu)
7. Toggle to **"On"**
8. Click **"Add New Webhook to Workspace"**
9. Select your channel → **Allow**
10. **Copy the Webhook URL** (you'll need it in Step 3)

**Done! ✓ Move to Step 3**

---

## Step 3: Configure config.json

Open `config.json` in the workshop folder and update:

### For Gmail:

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

Replace:
- `your-email@gmail.com` → Your actual Gmail
- `YOUR-16-CHAR-APP-PASSWORD` → The password from Step 2A

### For Slack:

```json
{
  "slack_config": {
    "enabled": true,
    "webhook_url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
  }
}
```

Replace:
- `YOUR/WEBHOOK/URL` → The URL from Step 2B

### For Both Gmail + Slack:

Combine both sections above in `config.json`

---

## Step 4: Test It Works

Open PowerShell in the workshop folder and run:

```bash
python ai_news_agent.py
```

**Expected output:**
```
2026-02-26 10:53:37 - INFO - Starting AI News Aggregator...
2026-02-26 10:53:41 - INFO - Fetched 10 papers from ArXiv
2026-02-26 10:53:42 - INFO - Fetched 5 Hugging Face blog posts
...
✓ Digest generated with 10 news items
```

**Check:**
- ✉️ Did you get an email?
- 💬 Did you see a Slack message?
- 📁 Check `output/digest_2026-02-26.html` in browser

If **email/Slack didn't arrive**:
- Check `logs/agent_2026-02-26.log` for errors
- Verify credentials in `config.json`
- Make sure Gmail two-factor auth is enabled
- Make sure Slack webhook is current

---

## Step 5: Schedule for Daily 9 AM

### Windows Task Scheduler (Easiest)

**Option A: Use PowerShell Script (Recommended)**

1. Right-click **PowerShell**
2. Select **"Run as administrator"**
3. Navigate to workshop folder:
   ```bash
   cd C:\Users\twank\Topicus-Local\workshop
   ```
4. Run:
   ```bash
   pwsh -ExecutionPolicy Bypass -File setup_scheduler.ps1
   ```
5. Follow the prompts
6. **Done!** ✓ Task scheduler is configured

**Option B: Manual Setup**

1. Press `Win + R`
2. Type `taskschd.msc` and press Enter
3. Right-click "Task Scheduler Library" → "Create Basic Task"
4. **Name:** `AI News Digest Daily`
5. **Trigger:** Daily at 9:00 AM
6. **Action:** Run `python ai_news_agent.py` from workshop folder
7. Click Finish!

---

## Step 6: Verify It's Scheduled

Open PowerShell and run:

```bash
Get-ScheduledTask -TaskName "AI News Digest Daily"
```

You should see something like:
```
TaskName      : AI News Digest Daily
State         : Ready
Enabled       : True
Triggers      : {Daily at 9:00 AM}
```

**All set!** ✓ You'll get your first digest tomorrow morning at 9 AM!

---

## Customization

### Change Time

Edit scheduled task:
```bash
# Open Task Scheduler (Win + R, taskschd.msc)
# Find "AI News Digest Daily"
# Right-click → Properties → Triggers tab
# Edit the trigger time
```

### Change News Sources

Edit `config.json`:
```json
{
  "keywords": [
    "transformer",
    "LLM",
    "diffusion"
  ],
  "max_items_per_source": 10
}
```

Add keywords you care about, remove ones you don't!

### Change Recipients

Edit `config.json`:
```json
{
  "smtp": {
    "to_email": "your-colleague@example.com"  // Send to them instead
  }
}
```

### Multiple Slack Channels

Create multiple tasks with different webhook URLs:
```bash
setup_scheduler.ps1  # Run again with different name
# Select different Slack channel in Step 2B
```

---

## Troubleshooting

### Email not arriving?

**Gmail:**
- Did you use App Password (16 chars)?
- Did you enable 2-Factor Auth?
- Check: https://myaccount.google.com/security

**Firewall issue:**
- Might be blocking port 587
- Try on different WiFi or contact IT

**Check logs:**
```bash
cat logs/agent_2026-02-26.log
```

### Slack webhook not working?

- Test webhook manually:
  ```bash
  $url = "https://hooks.slack.com/services/..."
  $payload = @{text="Test"} | ConvertTo-Json
  curl -X POST -H 'Content-type: application/json' --data $payload $url
  ```
- Webhook URLs expire - create a new one
- Check permissions on the channel

### Task not running?

- Verify Python in PATH: `python --version`
- Try running manually: `python ai_news_agent.py`
- Check Task Scheduler history
- Disable "wake only on AC power" in task settings

---

##  Next Steps

1. ✅ You got a digest working locally
2. ✅ You configured email/Slack
3. ✅ You scheduled the task
4. 🎉 Relax! Digests arrive automatically

### Optional Enhancements

- [ ] Add more news sources to `config.json`
- [ ] Filter keywords to your interests
- [ ] Set up multiple tasks for different times
- [ ] Share digest with your team via Slack
- [ ] Customize HTML template in `ai_news_agent.py`

---

## Security Notes

⚠️ **Important: Protect your credentials**

- Never push `config.json` to GitHub with real passwords
- Keep your app password secret
- Rotate every 6 months
- Don't share webhook URLs publicly

---

## Full Documentation

- **Agent Details:** See `agent.md`
- **Advanced Email Setup:** See `SETUP_NOTIFICATIONS.md`
- **Customization:** See `config.json` comments
- **Logs:** Check `logs/agent_YYYY-MM-DD.log`

---

## Success! 🎉

You now have a fully automated AI news digest!

**What happens:**
- Every morning at 9 AM (or time you set):
  - ✓ Fetch latest AI papers from ArXiv
  - ✓ Get trending AI models from Hugging Face
  - ✓ Find popular AI repos from GitHub
  - ✓ Collect OpenAI/Anthropic announcements
  - ✓ Send you an email AND/OR Slack message
  - ✓ All while you sleep! 😴

**You receive:**
- Professional HTML digest
- Plain text version
- Formatted Slack message
- All organized by source

**Total setup time:** 15 minutes ⏱️

---

**Questions?** Check `SETUP_NOTIFICATIONS.md` for detailed setup guides.

**Ready to start?** Run: `python setup_scheduler.ps1`

Enjoy your daily AI news digests! 🚀
