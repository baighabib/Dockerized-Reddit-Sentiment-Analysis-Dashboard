import pandas as pd
from textblob import TextBlob
import psycopg2
import schedule
import time

def connect_to_db():
    """Establishes a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            dbname="reddit_db",
            user="postgres",
            password="Mujhenahipata123.",  
            host="postgres",
            port="5432"
        )
        return conn
    except (Exception, psycopg2.Error) as error:
        print("Error connecting to PostgreSQL database:", error)
        return None

def create_table():
    """Drops and recreates the 'reddit_sentiment_analysis' table."""
    conn = connect_to_db()
    if conn is None:
        return

    try:
        with conn.cursor() as cur:
            cur.execute("""
                DROP TABLE IF EXISTS reddit_sentiment_analysis;
                CREATE TABLE reddit_sentiment_analysis (
                    id SERIAL PRIMARY KEY,
                    post_id INT UNIQUE,
                    subreddit TEXT,
                    title TEXT,
                    description TEXT,
                    sentiment_title TEXT,
                    polarity_title FLOAT,
                    subjectivity_title FLOAT,
                    sentiment_description TEXT,
                    polarity_description FLOAT,
                    subjectivity_description FLOAT
                )
            """)
            conn.commit()
        print("Recreated the 'reddit_sentiment_analysis' table.")
    except (Exception, psycopg2.Error) as error:
        print("Error creating table:", error)
    finally:
        conn.close()

def fetch_data_from_db():
    """Fetches data from the 'reddit_posts' table."""
    conn = connect_to_db()
    if conn is None:
        return None

    try:
        with conn.cursor() as cur:
            # Check if the table exists
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'reddit_posts'
                );
            """)
            if not cur.fetchone()[0]:
                print("The 'reddit_posts' table does not exist.")
                return None

            # Fetch data from the table
            cur.execute("SELECT * FROM reddit_posts")
            data = cur.fetchall()
            if not data:
                print("The 'reddit_posts' table is empty.")
                return None

        return data
    except (Exception, psycopg2.Error) as error:
        print("Error fetching data from database:", error)
        return None
    finally:
        conn.close()

def insert_data_into_db(data):
    """Inserts sentiment analysis results into the database."""
    conn = connect_to_db()
    if conn is None:
        return

    try:
        with conn.cursor() as cur:
            for _, row in data.iterrows():
                cur.execute("""
                    INSERT INTO reddit_sentiment_analysis (
                        post_id, subreddit, title, description,
                        sentiment_title, polarity_title, subjectivity_title,
                        sentiment_description, polarity_description, subjectivity_description
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (post_id) DO NOTHING;
                    """, (
                    row['id'], row['subreddit'], row['title'], row['description'],
                    row['sentiment_title'], row['polarity_title'], row['subjectivity_title'],
                    row['sentiment_description'], row['polarity_description'], row['subjectivity_description']
                    ))

            conn.commit()
        print("Data inserted into 'reddit_sentiment_analysis' table.")
    except (Exception, psycopg2.Error) as error:
        print("Error inserting data into database:", error)
    finally:
        conn.close()

def analyze_sentiment(text):
    """Analyzes the sentiment of the given text."""
    if not text:
        return "No Sentiment", 0.0, 0.0
    blob = TextBlob(text)
    sentiment = "Positive" if blob.sentiment.polarity > 0 else (
        "Negative" if blob.sentiment.polarity < 0 else "Neutral"
    )
    polarity = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity
    return sentiment, polarity, subjectivity

def run_sentiment_analysis():
    """Fetches data from the database, performs sentiment analysis, and stores results in PostgreSQL."""
    print("Running sentiment analysis...")
    create_table()  # Ensure the sentiment table exists
    data = fetch_data_from_db()

    if not data:
        print("No data fetched from the database.")
        return

    df = pd.DataFrame(data, columns=["id", "subreddit", "title", "description"])

    # Handle potential missing data
    df = df.dropna(subset=["title", "description"])

    # Perform sentiment analysis on titles and descriptions
    df["sentiment_title"], df["polarity_title"], df["subjectivity_title"] = zip(
        *df["title"].apply(analyze_sentiment)
    )
    df["sentiment_description"], df["polarity_description"], df["subjectivity_description"] = zip(
        *df["description"].apply(analyze_sentiment)
    )

    # Insert sentiment analysis results into the database
    insert_data_into_db(df)
    print("Sentiment analysis results saved to the database.")

# Main Execution
if __name__ == "__main__":
    # Run the sentiment analysis immediately at start
    run_sentiment_analysis()

    # Schedule the task to run every 10 minutes
    schedule.every(10).minutes.do(run_sentiment_analysis)

    print("Starting scheduled job...")
    # Run the scheduler
    while True:
        schedule.run_pending()
        time.sleep(1)  # Sleep for 1 second to prevent CPU overuse
