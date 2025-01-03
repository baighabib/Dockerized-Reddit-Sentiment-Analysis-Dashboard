import pandas as pd
import streamlit as st
import plotly.express as px
import psycopg2
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import time

# Database Connection Function
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
        st.error(f"Error connecting to PostgreSQL database: {error}")
        return None

# Fetch Data Function
def fetch_data_from_db():
    """Fetches data from the 'reddit_sentiment_analysis' table."""
    conn = connect_to_db()
    if conn is None:
        return None

    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM reddit_sentiment_analysis")
            data = cur.fetchall()
            colnames = [desc[0] for desc in cur.description] 
        return pd.DataFrame(data, columns=colnames)
    except (Exception, psycopg2.Error) as error:
        st.error(f"Error fetching data from database: {error}")
        return None
    finally:
        conn.close()

# Word Cloud Function
def generate_wordcloud(text, title="Word Cloud"):
    """Generates and displays a word cloud."""
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.title(title)
    st.pyplot(plt)

# Main Streamlit App
def main():
    """Streamlit app for Reddit Sentiment Analysis."""
    st.title("Reddit Sentiment Analysis Dashboard")

    # Fetch data from database
    df = fetch_data_from_db()
    if df is None or df.empty:
        st.warning("No data available to display.")
        return

    # Sidebar Navigation
    st.sidebar.title("Navigation")
    section = st.sidebar.selectbox("Go to", ["Overview", "Sentiment Analysis", "Word Cloud", "Polarity and Subjectivity"])

    st.sidebar.write("The page will automatically refresh every 15 minutes.")

    # Overview Section
    if section == "Overview":
        st.header("Dataset Overview")

        st.subheader("Filterable Table")
        subreddit_options = list(df["subreddit"].unique())
        selected_subreddits = st.multiselect("Filter by Subreddit", subreddit_options, default=subreddit_options)
        keyword_filter = st.text_input("Filter by Keyword in Description")

        filtered_df = df
        if selected_subreddits:
            filtered_df = filtered_df[filtered_df["subreddit"].isin(selected_subreddits)]
        if keyword_filter:
            filtered_df = filtered_df[filtered_df["description"].str.contains(keyword_filter, case=False, na=False)]

        st.dataframe(filtered_df)

    # Sentiment Analysis Section
    elif section == "Sentiment Analysis":
        st.header("Sentiment Analysis")

        subreddit_options = list(df["subreddit"].unique())
        selected_subreddits = st.multiselect("Filter by Subreddit", subreddit_options, default=subreddit_options, key="sentiment_filter")
        filtered_df = df
        if selected_subreddits:
            filtered_df = filtered_df[filtered_df["subreddit"].isin(selected_subreddits)]

        st.subheader("Sentiment Distribution")
        sentiment_counts = filtered_df["sentiment_description"].value_counts()
        st.bar_chart(sentiment_counts)

    # Word Cloud Section
    elif section == "Word Cloud":
        st.header("Word Cloud")

        subreddit_options = list(df["subreddit"].unique())
        selected_subreddits = st.multiselect("Filter by Subreddit", subreddit_options, default=subreddit_options, key="wordcloud_filter")
        filtered_df = df
        if selected_subreddits:
            filtered_df = filtered_df[filtered_df["subreddit"].isin(selected_subreddits)]

        st.subheader("Word Cloud")
        all_text = " ".join(filtered_df["description"].dropna().astype(str))
        generate_wordcloud(all_text, title="Word Cloud")

        st.subheader("Average Description and Title Length")
        avg_description_length = filtered_df["description"].dropna().str.len().mean()
        avg_title_length = filtered_df["title"].dropna().str.len().mean()
        st.write(f"Average Description Length: {avg_description_length:.2f}")
        st.write(f"Average Title Length: {avg_title_length:.2f}")

    # Polarity and Subjectivity Section
    elif section == "Polarity and Subjectivity":
        st.header("Polarity and Subjectivity Analysis")

        subreddit_options = list(df["subreddit"].unique())
        selected_subreddits = st.multiselect("Filter by Subreddit", subreddit_options, default=subreddit_options, key="polarity_filter")
        filtered_df = df
        if selected_subreddits:
            filtered_df = filtered_df[filtered_df["subreddit"].isin(selected_subreddits)]

        st.subheader("Polarity Distribution")
        fig1 = px.histogram(filtered_df, x="polarity_description", title="Polarity Distribution")
        st.plotly_chart(fig1)

        st.subheader("Subjectivity Distribution")
        fig2 = px.histogram(filtered_df, x="subjectivity_description", title="Subjectivity Distribution")
        st.plotly_chart(fig2)

        st.subheader("Polarity vs Subjectivity Scatter Plot")
        fig3 = px.scatter(filtered_df, x="polarity_description", y="subjectivity_description", color="sentiment_description", title="Polarity vs Subjectivity")
        st.plotly_chart(fig3)

    # Automatically refresh the page every 15 minutes
    time.sleep(900)  # Sleep for 900 seconds (15 minutes)
    st.experimental_rerun()  # Rerun the app

if __name__ == "__main__":
    main()
