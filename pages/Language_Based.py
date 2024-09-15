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

# Delete missing values
df2 = pd.DataFrame(df1.dropna())

# Clean 'all_reviews' column
df2['all_reviews'] = df2['all_reviews'].fillna('No reviews')  # Handle missing reviews
df2['all_reviews'] = df2['all_reviews'].apply(lambda x: re.sub(r'[^\x00-\x7F]+',' ', x))  # Remove special characters
df2['all_reviews'] = df2['all_reviews'].apply(lambda x: x if len(x) <= 50 else x[:50] + '...')  # Truncate long reviews

# Add a column to format the languages with spacing and brackets for the searched language
def format_languages(languages, searched_language):
    # Split languages by commas and format with brackets around the searched language
    formatted = []
    for lang in languages.split(','):
        lang = lang.strip()
        if lang.lower() == searched_language:
            formatted.append(f"[{lang}]")
        else:
            formatted.append(lang)
    return ', '.join(formatted)

# Streamlit app
st.title("🎮Game Recommender with Reviews🎮")
st.write("🔎 Find games based on language and user reviews 🔎")

# Asking for user input via Streamlit for language search
language = st.text_input("Please enter a language to find games with that language:").lower()

# Ensure all languages in the dataset are lowercase for comparison
df2['languages'] = df2['languages'].str.lower()

# Add a dropdown for filtering by user reviews
reviews_filter = st.selectbox("Select review category:", ["All reviews", "Mostly Positive", "Very Positive", "Overwhelmingly Positive"])

# If the user has entered a language, proceed with the recommendation
if language:
    # Filter games that contain the specified language
    matching_games = df2[df2['languages'].str.contains(language, na=False)]

    # Check if a review filter was selected and apply it
    if reviews_filter != "All reviews":
        # Look for partial matches for the selected review filter (e.g., "Mostly Positive" anywhere in the text)
        matching_games = matching_games[matching_games['all_reviews'].str.contains(reviews_filter, case=False, na=False)]

    # Add formatted languages with brackets
    matching_games['formatted_languages'] = matching_games['languages'].apply(lambda langs: format_languages(langs, language))
    
    # Display total number of matches
    total_matches = len(matching_games)
    st.write(f"Total number of games found that support the language '{language}': {total_matches}")

    # Display results
    if not matching_games.empty:
        matching_games = matching_games.reset_index(drop=True)  # Reset index to start from 0
        matching_games.index += 1  # Set index to start from 1

        if reviews_filter == "All reviews":
            st.write(f"Games that support the language '{language}':")
            st.table(matching_games[['name', 'formatted_languages', 'all_reviews']].head(20))  # Display full info if showing all reviews
        else:
            st.write(f"Games that support the language '{language}' with '{reviews_filter}' reviews:")
            st.table(matching_games[['name', 'formatted_languages', 'all_reviews']].head(20))  # Display full info if review filter is applied
    else:
        st.write(f"No games found that support the language '{language}' with '{reviews_filter}' reviews.")
