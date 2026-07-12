import os
import json
import logging
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    filename="logs/app.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

VALID_GENRES = ["romantic", "party", "rock", "travel",
                "wedding", "motivational", "pop", "hip-hop", "folk"]
VALID_MOODS = ["chill", "energetic", "sad",
               "happy", "motivational", "reflective"]

DEFAULT_TAGS = {"genre": "pop", "mood": "chill", "energy": 0.5}


def parse_mood_input(user_text: str) -> dict:
    """
    Takes free-text mood description and returns structured tags
    using an LLM. Falls back to DEFAULT_TAGS on any failure.
    """
    if not user_text or not user_text.strip():
        logging.warning("Empty input received, using default tags")
        return DEFAULT_TAGS

    prompt = f"""Analyze this music mood request and respond with ONLY valid JSON, no other text.

Request: "{user_text}"

Return JSON in exactly this format:
{{"genre": "<one of: {', '.join(VALID_GENRES)}>", "mood": "<one of: {', '.join(VALID_MOODS)}>", "energy": <float between 0.0 and 1.0>}}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=100,
        )
        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        tags = json.loads(raw)

        # Validate shape
        if not all(k in tags for k in ("genre", "mood", "energy")):
            raise ValueError("Missing required keys in LLM response")

        tags["energy"] = max(0.0, min(1.0, float(tags["energy"])))

        logging.info(f"Parsed input '{user_text}' -> {tags}")
        return tags

    except Exception as e:
        logging.error(f"Failed to parse mood input '{user_text}': {e}")
        return DEFAULT_TAGS


load_dotenv()

logging.basicConfig(
    filename="logs/app.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

VALID_GENRES = ["romantic", "party", "rock", "travel",
                "wedding", "motivational", "pop", "hip-hop", "folk"]
VALID_MOODS = ["chill", "energetic", "sad",
               "happy", "motivational", "reflective"]

DEFAULT_TAGS = {"genre": "pop", "mood": "chill", "energy": 0.5}


def parse_mood_input(user_text: str) -> dict:
    """
    Takes free-text mood description and returns structured tags
    using an LLM. Falls back to DEFAULT_TAGS on any failure.
    """
    if not user_text or not user_text.strip():
        logging.warning("Empty input received, using default tags")
        return DEFAULT_TAGS

    prompt = f"""Analyze this music mood request and respond with ONLY valid JSON, no other text.

Request: "{user_text}"

Return JSON in exactly this format:
{{"genre": "<one of: {', '.join(VALID_GENRES)}>", "mood": "<one of: {', '.join(VALID_MOODS)}>", "energy": <float between 0.0 and 1.0>}}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=100,
        )
        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        tags = json.loads(raw)

        # Validate shape
        if not all(k in tags for k in ("genre", "mood", "energy")):
            raise ValueError("Missing required keys in LLM response")

        tags["energy"] = max(0.0, min(1.0, float(tags["energy"])))

        logging.info(f"Parsed input '{user_text}' -> {tags}")
        return tags

    except Exception as e:
        logging.error(f"Failed to parse mood input '{user_text}': {e}")
        return DEFAULT_TAGS


def load_songs(path="app/data/songs.json") -> list:
    """Load the song dataset from disk. Raises a clear error if missing/corrupt."""
    try:

        with open(path, "r") as f:
            songs = json.load(f)
        if not songs:
            raise ValueError("Song dataset is empty")
        return songs
    except FileNotFoundError:
        logging.error(f"Song dataset not found at {path}")
        raise
    except json.JSONDecodeError as e:
        logging.error(f"Song dataset is corrupt: {e}")
        raise


def score_song(song: dict, tags: dict) -> float:
    """
    Additive scoring: genre match, mood match, energy closeness.
    Mirrors the logic validated in the Module 3 prototype.
    """
    score = 0.0

    if song["genre"] == tags["genre"]:
        score += 2.0

    if song["mood"] == tags["mood"]:
        score += 1.0

    energy_diff = abs(song["energy"] - tags["energy"])
    score += max(0.0, 2.0 - (energy_diff * 2))

    if song.get("acousticness", 0) > 0.5 and tags["mood"] == "chill":
        score += 1.0

    return round(score, 2)


def recommend_songs(user_text: str, top_n: int = 3) -> list:
    """
    Full pipeline: parse free-text input, score all songs, return top N.
    """
    tags = parse_mood_input(user_text)
    songs = load_songs()

    scored = [
        {**song, "match_score": score_song(song, tags)}
        for song in songs
    ]
    scored.sort(key=lambda s: s["match_score"], reverse=True)

    logging.info(
        f"Recommended top {top_n} for '{user_text}': {[s['title'] for s in scored[:top_n]]}")
    return scored[:top_n]
