import streamlit as st
from recommender import recommend_songs

st.set_page_config(page_title="VibeFinder", page_icon="🎵")

# Background gradient + styled elements
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #1a0f2e 0%, #3d1a4a 50%, #6b1e3f 100%);
}

h1 {
    background: linear-gradient(90deg, #ff9a56, #ff6b9d, #c86dd7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 3rem !important;
}

.stTextInput > div > div > input {
    background-color: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 154, 86, 0.4);
    border-radius: 10px;
    color: white;
}

.stButton > button {
    background: linear-gradient(90deg, #ff6b9d, #c86dd7);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0.5rem 2rem;
    font-weight: 600;
}

.stButton > button:hover {
    background: linear-gradient(90deg, #ff9a56, #ff6b9d);
    color: white;
}

.stMarkdown {
    background-color: rgba(255, 255, 255, 0.05);
    border-radius: 10px;
    padding: 0.8rem;
    margin-bottom: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

# Floating music note icons
st.markdown("""
<style>
.floating-notes {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    z-index: 0;
    overflow: hidden;
}
.note {
    position: absolute;
    opacity: 0.15;
    font-size: 2.5rem;
    animation: float 8s ease-in-out infinite;
}
.note:nth-child(1) { top: 8%; left: 5%; animation-delay: 0s; font-size: 3rem; }
.note:nth-child(2) { top: 20%; left: 85%; animation-delay: 1.5s; font-size: 2rem; }
.note:nth-child(3) { top: 45%; left: 12%; animation-delay: 3s; font-size: 4rem; }
.note:nth-child(4) { top: 65%; left: 80%; animation-delay: 2s; font-size: 2.5rem; }
.note:nth-child(5) { top: 80%; left: 20%; animation-delay: 4s; font-size: 3rem; }
.note:nth-child(6) { top: 30%; left: 50%; animation-delay: 1s; font-size: 2rem; }
.note:nth-child(7) { top: 5%; left: 60%; animation-delay: 3.5s; font-size: 2.5rem; }
.note:nth-child(8) { top: 90%; left: 60%; animation-delay: 2.5s; font-size: 2rem; }

@keyframes float {
    0%, 100% { transform: translateY(0px) rotate(0deg); }
    50% { transform: translateY(-25px) rotate(10deg); }
}
</style>

<div class="floating-notes">
    <span class="note">🎵</span>
    <span class="note">🎶</span>
    <span class="note">🎧</span>
    <span class="note">🎤</span>
    <span class="note">🎼</span>
    <span class="note">🥁</span>
    <span class="note">🎸</span>
    <span class="note">💿</span>
</div>
""", unsafe_allow_html=True)

st.title("🎵 VibeFinder")
st.caption("Bollywood music recommendations based on your mood")

# Optional background music player (user must click play)
try:
    with open("app/assets/background.mp3", "rb") as f:
        audio_bytes = f.read()
    st.audio(audio_bytes, format="audio/mp3", loop=True)
except FileNotFoundError:
    pass  # no background track added yet, skip silently

user_input = st.text_input(
    "Describe your mood or vibe:",
    placeholder="e.g. I want something chill and romantic"
)

find_clicked = st.button("Find Songs")

if find_clicked:
    if not user_input:
        st.warning("Please describe your mood first.")
    else:
        with st.spinner("Finding your vibe..."):
            try:
                results = recommend_songs(user_input, top_n=5)
                st.subheader("Your recommendations")
                for song in results:
                    st.markdown(
                        f"**{song['title']}** — {song['artist']}  \n"
                        f"Genre: {song['genre']} | Mood: {song['mood']} | Match score: {song['match_score']}"
                    )
            except Exception as e:
                st.error(f"Something went wrong: {e}")
