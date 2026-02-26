# GitHub Actions Setup Guide

Run your AI News Aggregator daily on GitHub's servers - **completely free** and independent of your PC!

## Overview

This setup uses GitHub Actions to automatically run your news aggregator at 9:00 AM daily. The workflow runs on GitHub's servers, so your personal computer doesn't need to be on.

## Quick Start

### 1. Create a GitHub Repository

1. Go to [GitHub.com](https://github.com) and create a new repository (can be private)
2. Name it something like `ai-news-aggregator`
3. Don't initialize with README (we'll push existing code)

### 2. Push Your Code to GitHub

Open PowerShell in your project folder and run:

```powershell
# Initialize git repository (if not already done)
git init

# Add all files
git add .

# Create first commit
git commit -m "Initial commit: AI News Aggregator"

# Add your GitHub repository as remote (replace with your repo URL)
git remote add origin https://github.com/YOUR_USERNAME/ai-news-aggregator.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### 3. Configure GitHub Secrets

Secrets keep your API keys and passwords secure. Never commit real credentials to your repository!

#### Setting Up Secrets:

1. Go to your repository on GitHub
2. Click **Settings** tab
3. In the left sidebar, click **Secrets and variables** → **Actions**
4. Click **New repository secret**

#### Required Secrets:

Choose Slack OR Email (or both):

##### For Slack Notifications:
- `SLACK_ENABLED` = `true`
- `SLACK_WEBHOOK_URL` = `https://hooks.slack.com/services/YOUR/WEBHOOK/URL`

##### For Email (SMTP - Gmail/Outlook):
- `EMAIL_ENABLED` = `true`
- `EMAIL_METHOD` = `smtp`
- `EMAIL_SMTP_SERVER` = `smtp.gmail.com` (or `smtp-mail.outlook.com`)
- `EMAIL_SMTP_PORT` = `587`
- `EMAIL_USER` = `your-email@gmail.com`
- `EMAIL_PASSWORD` = `your-app-password` (NOT your regular password!)
- `EMAIL_FROM` = `your-email@gmail.com`
- `EMAIL_TO` = `your-email@gmail.com`

##### For Email (SendGrid API):
- `EMAIL_ENABLED` = `true`
- `EMAIL_METHOD` = `sendgrid`
- `SENDGRID_API_KEY` = `SG.xxxxxxxxxxxxx`
- `EMAIL_FROM` = `your-verified-sender@example.com`
- `EMAIL_TO` = `your-email@example.com`

##### For Email (Mailgun API):
- `EMAIL_ENABLED` = `true`
- `EMAIL_METHOD` = `mailgun`
- `MAILGUN_API_KEY` = `your-mailgun-api-key`
- `MAILGUN_DOMAIN` = `your-domain.mailgun.org`
- `EMAIL_FROM` = `news@your-domain.mailgun.org`
- `EMAIL_TO` = `your-email@example.com`

### 4. Adjust Timezone (Optional)

The workflow runs at 9:00 AM UTC by default. To change timezone:

1. Open [.github/workflows/daily-news.yml](.github/workflows/daily-news.yml)
2. Find the `cron:` line
3. Adjust the time:
   - Current: `'0 9 * * *'` = 9:00 AM UTC
   - For 9 AM EST: `'0 14 * * *'` (UTC+5)
   - For 9 AM PST: `'0 17 * * *'` (UTC+8)
   - For 9 AM CET: `'0 8 * * *'` (UTC-1)

Cron format: `minute hour day month day-of-week`

### 5. Test the Workflow

#### Manual Test (Before Waiting for 9 AM):

1. Go to your repository on GitHub
2. Click **Actions** tab
3. Click **Daily AI News Aggregator** workflow
4. Click **Run workflow** → **Run workflow** button
5. Wait 1-2 minutes and watch it run!

#### Check Results:

- **Logs**: Click on the workflow run to see detailed logs
- **Artifacts**: Download generated digests (HTML/TXT files) from the workflow run
- **Email/Slack**: Check your inbox or Slack channel
- **Commit History**: The workflow commits updates to `data/seen_items.json` automatically

### 6. Monitor and Maintain

#### View Workflow History:
- Go to **Actions** tab to see all runs (success/failure status)

#### Debugging Failed Runs:
- Click on failed workflow run
- Expand each step to see error messages
- Common issues:
  - Invalid API keys → Check secrets are correct
  - Rate limiting → Sources may temporarily block requests
  - Network errors → Usually self-resolving on next run

#### Update Configuration:
- Edit `config.json` to add/remove sources or keywords
- Commit and push changes: `git add config.json; git commit -m "Update config"; git push`
- Changes take effect on next scheduled run

## How It Works

1. **Scheduled Trigger**: GitHub Actions runs at 9:00 AM daily
2. **Environment Setup**: Installs Python and dependencies
3. **Run Aggregator**: Executes `ai_news_agent.py` with secrets as environment variables
4. **Send Notifications**: Emails and/or Slack messages sent automatically
5. **Save State**: Commits `data/seen_items.json` back to repo (prevents duplicates)
6. **Store Artifacts**: Uploads digest files for 30 days

## Cost

**100% FREE** on GitHub!

- Public repositories: Unlimited Actions minutes
- Private repositories: 2,000 minutes/month free (this workflow uses ~2-3 minutes/day)

## Benefits Over Task Scheduler

✅ **No PC required** - Runs on GitHub's servers  
✅ **Never miss a run** - Even when traveling or computer is off  
✅ **Free forever** - No hosting costs  
✅ **Automatic backups** - All outputs committed to git history  
✅ **Easy debugging** - Full logs available in GitHub UI  
✅ **Accessible anywhere** - Check workflow from any device  
✅ **Version controlled** - All changes tracked  

## Hybrid Approach

You can use BOTH:
- **GitHub Actions**: Reliable daily runs when PC is off  
- **Task Scheduler**: Backup/testing on your local machine  

No conflicts - they both update the same `seen_items.json` via git sync.

## Disabling GitHub Actions

If you want to stop automated runs:

1. Go to **Actions** tab
2. Click **Daily AI News Aggregator**
3. Click **⋯** (three dots) → **Disable workflow**

Or simply delete [.github/workflows/daily-news.yml](.github/workflows/daily-news.yml)

## Troubleshooting

### "Workflow not running at 9 AM"
- Scheduled workflows may have 5-15 minute delay during high GitHub traffic
- Use manual trigger to test functionality while waiting

### "Permission denied" when committing
- The workflow uses built-in `GITHUB_TOKEN` which has appropriate permissions
- If using private repo, ensure Actions has write permissions:
  - Settings → Actions → General → Workflow permissions → "Read and write permissions"

### "Email not sending"
- Verify secrets are spelled exactly as shown above (case-sensitive)
- For Gmail: Use App Password, not regular password (see [SETUP_NOTIFICATIONS.md](SETUP_NOTIFICATIONS.md))
- Check workflow logs for specific error messages

### "Duplicate news items"
- The workflow commits `seen_items.json` after each run
- If commit fails, duplicates may occur on next run
- Check that workflow has write permissions (see above)

## Advanced Configuration

### Run Multiple Times Per Day
Edit the `cron` line in [.github/workflows/daily-news.yml](.github/workflows/daily-news.yml):

```yaml
schedule:
  - cron: '0 9 * * *'   # 9 AM
  - cron: '0 17 * * *'  # 5 PM
```

### Notification on Failure
Add to workflow after "Run AI News Aggregator" step:

```yaml
- name: Notify on failure
  if: failure()
  run: |
    curl -X POST ${{ secrets.SLACK_WEBHOOK_URL }} \
      -H 'Content-Type: application/json' \
      -d '{"text":"⚠️ AI News Aggregator failed! Check Actions logs."}'
```

### Skip Weekends
Change cron to run only Monday-Friday:

```yaml
schedule:
  - cron: '0 9 * * 1-5'  # Monday=1, Friday=5
```

## Next Steps

1. ✅ Push code to GitHub
2. ✅ Configure secrets
3. ✅ Test with manual trigger
4. ✅ Wait for first scheduled run at 9 AM
5. ✅ Check your email/Slack for the digest!

For local setup and email provider configuration, see:
- [SETUP_NOTIFICATIONS.md](SETUP_NOTIFICATIONS.md) - Email and Slack configuration
- [agent.md](agent.md) - Full agent documentation
- [QUICK_START.md](QUICK_START.md) - Local usage guide
