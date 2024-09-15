import streamlit as st
import pandas as pd
import re

# Set Streamlit to a wide layout
st.set_page_config(layout="wide")

# Custom CSS to make the table wider
st.markdown("""
    <style>
    .dataframe {
        width: 100% !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Load CSV data (ensure the path is correct and CSV is accessible)
path = 'games.csv'

column_names = ['name', 'desc_snippet', 'recent_reviews', 'all_reviews', 'release_date',
                'popular_tags', 'game_details', 'languages', 'genre', 'game_description',
                'mature_content', 'original_price', 'discount_price']
df = pd.read_csv(path, names=column_names, encoding='ISO-8859-1', low_memory=True)

# Selecting only relevant columns
df1 = df[['name', 'languages', 'popular_tags', 'genre', 'original_price', 'all_reviews']]

# Drop rows with missing values in relevant columns
df2 = df1.dropna(subset=['languages', 'name'])

# Clean 'all_reviews' column
df2['all_reviews'] = df2['all_reviews'].fillna('No reviews')  # Handle missing reviews
df2['all_reviews'] = df2['all_reviews'].apply(lambda x: re.sub(r'[^\x00-\x7F]+',' ', x))  # Remove special characters
df2['all_reviews'] = df2['all_reviews'].apply(lambda x: x if len(x) <= 50 else x[:50] + '...')  # Truncate long reviews

# Ensure all languages in the dataset are lowercase for comparison
df2['languages'] = df2['languages'].str.lower()

# Streamlit app
st.title("🎮 Game Recommender with Reviews 🎮")
st.write("🔎 Find games based on language and user reviews 🔎")

# Asking for user input via Streamlit for language search
language = st.text_input("Please enter a language to find games with that language:").lower()

# Add a dropdown for filtering by user reviews
reviews_filter = st.selectbox("Select review category:", ["None", "Mostly Positive", "Very Positive", "Overwhelmingly Positive"])

# If the user has entered a language, proceed with the recommendation
if language:
    # Filter games that contain the specified language
    exact_matches = df2[df2['languages'].str.contains(language, na=False)]
    other_matches = df2[~df2['languages'].str.contains(language, na=False)]

    # Check if a review filter was selected and apply it to both exact and other matches
    if reviews_filter != "None":
        exact_matches = exact_matches[exact_matches['all_reviews'].str.contains(reviews_filter, case=False, na=False)]
        other_matches = other_matches[other_matches['all_reviews'].str.contains(reviews_filter, case=False, na=False)]

    # Combine the two sets of results, prioritizing exact language matches
    matching_games = pd.concat([exact_matches, other_matches])

    # Reset index for better readability
    matching_games = matching_games.reset_index(drop=True)
    matching_games.index += 1  # Set index to start from 1 for display

    # Display results
    if not matching_games.empty:
        st.write(f"Games that match your language search: '{language}'")
        st.table(matching_games[['name', 'languages', 'all_reviews']].head(20))
    else:
        st.write(f"No games found for language '{language}' and review filter '{reviews_filter}'.")
