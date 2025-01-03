import praw
import psycopg2
import os
import schedule
import time
from flask import Flask

# Flask Application
app = Flask(__name__)

# Reddit API Configuration
reddit = praw.Reddit(
    client_id=os.getenv('REDDIT_CLIENT_ID', '1IZObZfK2ueN2QXd0ZQizA'),
    client_secret=os.getenv('REDDIT_CLIENT_SECRET', 'asNUjE3hQ2hiI-PSEwacmTd7esYciw'),
    user_agent=os.getenv('REDDIT_USER_AGENT', 'Shaheer')
)

# PostgreSQL Connection
def get_db_connection():
    """Establish a database connection."""
    conn = psycopg2.connect(
        dbname="reddit_db",
        user="postgres",
        password="Mujhenahipata123.",  
        host="postgres",
        port=5432
    )
    return conn


def ensure_table_exists():
    """Create the reddit_posts table if it doesn't already exist."""
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS reddit_posts (
                id SERIAL PRIMARY KEY,
                subreddit TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                CONSTRAINT unique_subreddit_title UNIQUE (subreddit, title)
            );
            """)
            conn.commit()
    print("Ensured that the reddit_posts table exists without dropping existing data.")


def fetch_and_store():
    """Fetch Reddit posts and store results in the database."""
    subreddits = ['python', 'gaming', 'USA', 'History', 'Sports', 'Family', 'Programming']
    limit = 200
    print(f"Fetching {limit} posts for each subreddit: {', '.join(subreddits)}")
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                for subreddit_name in subreddits:
                    print(f"Fetching posts from subreddit: {subreddit_name}")
                    subreddit = reddit.subreddit(subreddit_name)

                    for post in subreddit.hot(limit=limit):
                        title = post.title
                        description = post.selftext.strip() if post.selftext else "No description available"

                        cursor.execute("""
                            INSERT INTO reddit_posts (subreddit, title, description)
                            VALUES (%s, %s, %s)
                            ON CONFLICT (subreddit, title) DO UPDATE SET description = EXCLUDED.description;
                        """, (subreddit_name, title, description))
                conn.commit()
        print(f"Data successfully stored in the database for all subreddits.")
    except Exception as e:
        print(f"Error occurred during data fetch or storage: {e}")

# Function to Run Periodically
def run_reddit_scraper():
    """Main execution function."""
    print("Starting Reddit scraper...")
    ensure_table_exists()
    fetch_and_store()
    print("Reddit scraper run completed.")

# Main Execution
if __name__ == '__main__':
    # Run the scraper immediately at start
    print("Running the scraper immediately on start...")
    run_reddit_scraper()

    # Schedule the task to run every 10 minutes
    schedule.every(10).minutes.do(run_reddit_scraper)

    print("Starting scheduled job...")
    # Run the scheduler
    while True:
        schedule.run_pending()
        time.sleep(1)  # Sleep for 1 second to prevent CPU overuse
