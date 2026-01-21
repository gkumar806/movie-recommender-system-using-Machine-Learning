import streamlit as st
import pickle
import pandas as pd
import requests
from concurrent.futures import ThreadPoolExecutor

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


# ------------------ RECOMMEND ------------------
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
        if len(recommended_movies) == 5:
            break

        movie_id = movies.iloc[i[0]].movie_id
        poster = fetch_poster(movie_id)

        # 🚀 SKIP movies without poster
        if "placeholder" in poster:
            continue

        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movies_posters.append(poster)

    return recommended_movies, recommended_movies_posters


# ------------------ LOAD DATA ------------------
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

similarity = pickle.load(open('similarity.pkl', 'rb'))


# ------------------ STREAMLIT UI ------------------
st.title('Movie Recommender System')

selected_movie_name = st.selectbox(
    "select a movie",
    movies['title'].values
)

if st.button('Recommend'):
    with st.spinner("Fetching recommendations..."):
        names, posters = recommend(selected_movie_name)

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.text(names[0])
        st.image(posters[0],width=180)
    with col2:
        st.text(names[1])
        st.image(posters[1],width=180)
    with col3:
        st.text(names[2])
        st.image(posters[2],width=180)
    with col4:
        st.text(names[3])
        st.image(posters[3],width=180)
    with col5:
        st.text(names[4])
        st.image(posters[4],width=180)
