import sys
import os
import json
import pytest
from unittest.mock import patch, MagicMock

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "app"))

from recommender import score_song, load_songs, parse_mood_input, DEFAULT_TAGS  # noqa: E402


def test_score_song_exact_match():
    """A song matching genre, mood, and energy exactly should score highest."""
    song = {"genre": "party", "mood": "energetic", "energy": 0.9, "acousticness": 0.1}
    tags = {"genre": "party", "mood": "energetic", "energy": 0.9}
    score = score_song(song, tags)
    assert score == pytest.approx(5.0, abs=0.01)


def test_score_song_no_match():
    """A song matching nothing should score based only on energy closeness."""
    song = {"genre": "folk", "mood": "reflective", "energy": 0.1, "acousticness": 0.6}
    tags = {"genre": "party", "mood": "energetic", "energy": 0.9}
    score = score_song(song, tags)
    assert score < 1.0


def test_score_song_partial_match():
    """A song matching only genre should score higher than one matching nothing."""
    song_genre_match = {"genre": "party", "mood": "sad", "energy": 0.5, "acousticness": 0.1}
    song_no_match = {"genre": "folk", "mood": "sad", "energy": 0.5, "acousticness": 0.1}
    tags = {"genre": "party", "mood": "energetic", "energy": 0.5}

    score_genre = score_song(song_genre_match, tags)
    score_none = score_song(song_no_match, tags)
    assert score_genre > score_none


def test_score_song_acoustic_chill_bonus():
    """An acoustic song should get a bonus when mood is chill."""
    song = {"genre": "pop", "mood": "sad", "energy": 0.5, "acousticness": 0.8}
    tags_chill = {"genre": "rock", "mood": "chill", "energy": 0.5}
    tags_not_chill = {"genre": "rock", "mood": "energetic", "energy": 0.5}

    score_chill = score_song(song, tags_chill)
    score_not_chill = score_song(song, tags_not_chill)
    assert score_chill > score_not_chill


def test_load_songs_returns_list():
    songs = load_songs()
    assert isinstance(songs, list)
    assert len(songs) > 0


def test_load_songs_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        load_songs(path="app/data/nonexistent_file.json")


def test_load_songs_corrupt_file_raises(tmp_path):
    bad_file = tmp_path / "corrupt.json"
    bad_file.write_text("{not valid json")
    with pytest.raises(json.JSONDecodeError):
        load_songs(path=str(bad_file))


def test_load_songs_empty_file_raises(tmp_path):
    empty_file = tmp_path / "empty.json"
    empty_file.write_text("[]")
    with pytest.raises(ValueError):
        load_songs(path=str(empty_file))


def test_parse_mood_input_empty_string_returns_default():
    result = parse_mood_input("")
    assert result == DEFAULT_TAGS


def test_parse_mood_input_whitespace_only_returns_default():
    result = parse_mood_input("   ")
    assert result == DEFAULT_TAGS


@patch("recommender.client")
def test_parse_mood_input_valid_response(mock_client):
    """Mocks a successful Groq response and checks it's parsed correctly."""
    mock_response = MagicMock()
    mock_response.choices[0].message.content = '{"genre": "romantic", "mood": "chill", "energy": 0.4}'
    mock_client.chat.completions.create.return_value = mock_response

    result = parse_mood_input("something chill and romantic")
    assert result["genre"] == "romantic"
    assert result["mood"] == "chill"
    assert result["energy"] == 0.4


@patch("recommender.client")
def test_parse_mood_input_malformed_response_falls_back(mock_client):
    """If the LLM returns invalid JSON, the function should fall back to defaults."""
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "not valid json at all"
    mock_client.chat.completions.create.return_value = mock_response

    result = parse_mood_input("some input")
    assert result == DEFAULT_TAGS


@patch("recommender.client")
def test_parse_mood_input_energy_out_of_range_clamped(mock_client):
    """Energy values outside 0-1 should be clamped."""
    mock_response = MagicMock()
    mock_response.choices[0].message.content = '{"genre": "pop", "mood": "happy", "energy": 1.5}'
    mock_client.chat.completions.create.return_value = mock_response

    result = parse_mood_input("very very happy")
    assert result["energy"] == 1.0
