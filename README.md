# RSSNotify

This project is an automated RSS feed notifier that sends email updates whenever a new post is published in specified RSS feeds. It uses SendGrid to send emails and GitHub Actions to run the script every 3 hours.(you can change this) 

## Prerequisites

- A GitHub account and repository where the notifier will run.
- A [SendGrid account](https://sendgrid.com/) and an API key to send emails.
- Python dependencies: `feedparser` and `sendgrid`.

## Setup Guide

### Step 1: Clone the Repository

In a new repository create: rss_notifier.py , seen_post.txt files


### Step 2: Set Up SendGrid

1. Sign up at [SendGrid](https://sendgrid.com/) if you don’t have an account.
2. Once logged in, go to **Settings > API Keys** in the SendGrid dashboard.
3. Click **Create API Key**, give it a name, select **Full Access**, and then click **Create & View**.
4. Copy the generated API key. You will use this in your GitHub repository secrets.

   - **Note**: You will need a verified sender email on SendGrid to be able to send emails.
     - Navigate to **Sender Authentication** and follow the steps to verify your email address.

### Step 3: Add Environment Variables in GitHub Secrets

To keep your API key and email addresses secure, store them as GitHub repository secrets. Follow these steps:

1. Go to your GitHub repository.
2. Navigate to **Settings > Secrets and variables > Actions**.
3. Click **New repository secret** and add the following secrets:

   - `SENDGRID_API_KEY`: Your SendGrid API key.
   - `SENDER_EMAIL`: The verified email address from which you will send the notifications.
   - `RECEIVER_EMAIL`: The email address that will receive the notifications.

### Step 4: Update the RSS Feed URLs (Optional)

In `rss_notifier.py`, there is a list of RSS feed URLs that the notifier checks. You can modify or add more URLs to the `RSS_FEED_URLS` list based on your needs.

```python
# List of RSS feed URLs
RSS_FEED_URLS = [
    "https://example.com/feed1/rss",
    "https://example.com/feed2/rss",
    ...
]
```
### Step 5: Modify the Email Subject

To customize the email subject based on the course name, update the get_course_name function in rss_notifier.py:

```python
def get_course_name(feed_url):
    if "CCU" in feed_url:
        return "IST - CCU Announcement"
    elif "SIRS" in feed_url:
        return "IST - SIRS Announcement"
    # Add more conditions for other courses as needed
```
This will allow you to have different subjects for each feed.

### Step 6: Configure GitHub Actions Workflow

Create .github/workflows/rss_notifier.yml file that configures GitHub Actions to run the notifier script on a schedule.


```yaml
name: RSS Feed Notifier

on:
  schedule:
    - cron: "*/30 * * * *"  # Runs every 30 minutes
  workflow_dispatch:  # Allows manual trigger

permissions:
  contents: write  # Grants read and write permissions for repository contents

jobs:
  check_rss_feed:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v3
        with:
          persist-credentials: true  # Ensures credentials are available for pushing changes

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.x'

      - name: Install dependencies
        run: pip install feedparser sendgrid

      - name: Run RSS notifier
        env:
          SENDGRID_API_KEY: ${{ secrets.SENDGRID_API_KEY }}
          SENDER_EMAIL: ${{ secrets.SENDER_EMAIL }}
          RECEIVER_EMAIL: ${{ secrets.RECEIVER_EMAIL }}
        run: python rss_notifier.py

      - name: Upload seen posts
        uses: actions/upload-artifact@v3
        with:
          name: seen_posts
          path: seen_posts.txt
          if-no-files-found: warn

      - name: Commit and push updates to seen_posts.txt (if changes detected)
        run: |
          # Check if there are changes to seen_posts.txt
          git diff --exit-code seen_posts.txt || (git config --global user.email "github-actions[bot]@users.noreply.github.com" && git config --global user.name "github-actions[bot]" && git add seen_posts.txt && git commit -m "Update seen_posts.txt with new entries" && git push)


```
- In the YAML file:

The cron schedule defines that the workflow will run every 30 minutes. You can adjust this as needed.

The workflow checks for new RSS posts, sends email notifications, and uploads the seen_posts.txt file as an artifact.

It will commit and push the seen_posts.txt file only if there are new entries to be added, skipping the commit if no changes are detected.


- Configure GitHub Actions Permissions:

Ensure that the GitHub Actions workflow has the necessary permissions to commit and push changes back to the repository. In this YAML file, the contents: write permission is enabled to allow GitHub Actions to commit changes to seen_posts.txt.

If you want to run it manually, you can trigger the workflow by clicking Run workflow in the Actions tab on GitHub.

### Step 7: Test the Setup

1. Once the repository and workflow are set up, you can manually trigger the workflow from the Actions tab in your GitHub repository.
2. Check the email address specified in RECEIVER_EMAIL to verify if you receive email notifications when a new post is published in any of the RSS feeds.

### Troubleshooting

If you run into issues, here are a few things to check:

- Make sure the SendGrid API key is correctly set in your GitHub secrets.
- Verify that your sender email is correctly verified with SendGrid.
- Ensure the RSS feed URLs are correct and returning valid data.
- Check the GitHub Actions logs to troubleshoot any errors related to the workflow execution.

### Usage

Once everything is set up, the workflow will automatically check the RSS feeds at the interval specified (e.g., every 15 minutes) and send an email notification to the RECEIVER_EMAIL address whenever there’s a new post in the feed.
