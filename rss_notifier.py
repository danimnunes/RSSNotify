import feedparser
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os
from datetime import datetime, timedelta, timezone
import time

# RSS feed URL mapping to course names
RSS_FEED_URLS = {
    "https://fenix.tecnico.ulisboa.pt/disciplinas/CCU11/2024-2025/1-semestre/rss/announcement": "CCU",
    "https://fenix.tecnico.ulisboa.pt/disciplinas/SIRS11/2024-2025/1-semestre/rss/announcement": "SIRS",
    "https://fenix.tecnico.ulisboa.pt/disciplinas/SSof11/2024-2025/1-semestre/rss/announcement": "SSof",
    "https://fenix.tecnico.ulisboa.pt/disciplinas/CSF211/2024-2025/1-semestre/rss/announcement": "CSF",
    "https://fenix.tecnico.ulisboa.pt/disciplinas/PADI11/2024-2025/1-semestre/rss/announcement": "PADI",
    "https://fenix.tecnico.ulisboa.pt/disciplinas/CCEIC11/2024-2025/1-semestre/rss/announcement": "CCEIC",
}

# Email settings
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")
# Track previously seen posts in a temporary file
SEEN_POSTS_FILE = "seen_posts.txt"

def load_seen_posts():
    try:
        with open(SEEN_POSTS_FILE, "r") as f:
            return set(line.strip() for line in f)
    except FileNotFoundError:
        return set()

def save_seen_post(post_id):
    with open(SEEN_POSTS_FILE, "a") as f:
        f.write(post_id + "\n")

def send_email(subject, content):
    message = Mail(
        from_email=SENDER_EMAIL,
        to_emails=RECEIVER_EMAIL,
        subject=subject,
        html_content=content  # Make sure this content is properly formatted as HTML
    )
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print("Email sent successfully, status code:", response.status_code)
    except Exception as e:
        print("Error sending email:", e)

def check_feed(feed_url, course_name):
    # Load previously seen posts
    seen_posts = load_seen_posts()
    feed = feedparser.parse(feed_url)
    
    for entry in feed.entries:
        post_id = entry.id
            
        # Parse the pubDate and calculate the time difference
        pub_date = datetime.strptime(entry.published, '%a, %d %b %Y %H:%M:%S %z')
        
        # Use timezone-aware current time in UTC
        time_difference = datetime.now(timezone.utc) - pub_date
        
        # Skip if the entry was published more than 5 hours ago
        if time_difference > timedelta(hours=5):
            continue
        # Skip if already seen
        if post_id in seen_posts:
            continue

        # Save the post as seen
        save_seen_post(post_id)

        # Get the author, if available
        author = entry.get("author", "No author specified")
        
        # Create a dynamic subject using the entry's title and timestamp for uniqueness
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        subject = f"IST - {course_name} Announcement: {entry.title} ({timestamp})"
        content = f"<p><strong>Author:</strong> {author}</p><p>{entry.description}</p><p><a href='{entry.link}'>Read more</a></p>"

        # Send email
        send_email(subject, content)

if __name__ == "__main__":
    for url, course_name in RSS_FEED_URLS.items():
        check_feed(url, course_name)
