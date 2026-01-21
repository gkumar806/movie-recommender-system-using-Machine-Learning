import streamlit as st
import pickle
import pandas as pd
import requests
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer


# ------------------ FETCH POSTER ------------------
@st.cache_data(show_spinner=False, ttl=3600)
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=7b7d85ccff8c6b0ee8638d34b633b35e"

    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if data.get('poster_path'):
            return "https://image.tmdb.org/t/p/w342/" + data['poster_path']
    except:
        pass

    return "https://via.placeholder.com/342x513?text=No+Image"


# ------------------ RECOMMEND FUNCTION ------------------
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]

    movies_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )

    recommended_movies = []
    recommended_movies_posters = []

    for i in movies_list:
        if len(recommended_movies) == 11:
            break

        movie_id = movies.iloc[i[0]].movie_id
        poster = fetch_poster(movie_id)

        # Skip movies without poster
        if "placeholder" in poster:
            continue

        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movies_posters.append(poster)

    return recommended_movies, recommended_movies_posters


# ------------------ LOAD DATA ------------------
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)


# ------------------ OPTIMIZED SIMILARITY (NO PKL FILE) ------------------
@st.cache_data(show_spinner="Computing movie similarity (one-time)...")
def compute_similarity(movies):
    cv = CountVectorizer(
        max_features=3000,
        stop_words='english'
    )
    vectors = cv.fit_transform(movies['tags']).toarray()
    return cosine_similarity(vectors)


similarity = compute_similarity(movies)


# ------------------ STREAMLIT UI ------------------
st.set_page_config(page_title="Movie Recommender", layout="wide")
st.title("🎬 Movie Recommender System")

selected_movie_name = st.selectbox(
    "Select a Movie for Recommendation",
    movies['title'].values
)

if st.button('Recommend'):
    with st.spinner("Fetching recommendations..."):
        names, posters = recommend(selected_movie_name)

    cols_per_row = 5
    num_movies = 10

    for i in range(0, num_movies, cols_per_row):
        cols = st.columns(cols_per_row)
        for col, idx in zip(cols, range(i, i + cols_per_row)):
            with col:
                st.markdown(f"**{names[idx]}**")
                st.image(posters[idx], width=180)
