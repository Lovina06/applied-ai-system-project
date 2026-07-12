import sys
import os
import json
import logging
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "app"))

from recommender import load_songs, score_song, parse_mood_input  # noqa: E402

logging.basicConfig(
    filename="logs/app.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")


def run_sensitivity_check(test_tags: dict = None, weight_shift: float = 0.1) -> dict:
    """
    Nudges the energy target slightly and checks whether the top
    recommendation flips. A fragile scoring system will flip easily;
    a robust one should be stable under small perturbations.
    """
    if test_tags is None:
        test_tags = {"genre": "party", "mood": "energetic", "energy": 0.8}

    songs = load_songs()

    def top_song(tags):
        scored = [{**s, "match_score": score_song(s, tags)} for s in songs]
        scored.sort(key=lambda s: s["match_score"], reverse=True)
        return scored[0]["title"], scored[0]["match_score"]

    baseline_title, baseline_score = top_song(test_tags)

    shifted_tags = {**test_tags,
                    "energy": min(1.0, test_tags["energy"] + weight_shift)}
    shifted_title, shifted_score = top_song(shifted_tags)

    flipped = baseline_title != shifted_title

    result = {
        "check": "sensitivity",
        "timestamp": datetime.now().isoformat(),
        "baseline_input": test_tags,
        "baseline_top_song": baseline_title,
        "baseline_score": baseline_score,
        "shifted_energy": shifted_tags["energy"],
        "shifted_top_song": shifted_title,
        "shifted_score": shifted_score,
        "flipped": flipped,
        "status": "FAIL - fragile ranking" if flipped else "PASS - stable ranking",
    }

    logging.info(f"Sensitivity check: {result['status']}")
    return result


def run_consistency_check(user_text: str = "I want something chill and romantic", runs: int = 5) -> dict:
    """
    Calls the full pipeline multiple times with identical input and
    checks whether the top recommendation stays stable. Flags LLM-level
    non-determinism that could make results feel unreliable to users.
    """
    top_songs = []

    for _ in range(runs):
        tags = parse_mood_input(user_text)
        songs = load_songs()
        scored = [{**s, "match_score": score_song(s, tags)} for s in songs]
        scored.sort(key=lambda s: s["match_score"], reverse=True)
        top_songs.append(scored[0]["title"])

    unique_tops = set(top_songs)
    consistent = len(unique_tops) == 1

    result = {
        "check": "consistency",
        "timestamp": datetime.now().isoformat(),
        "input": user_text,
        "runs": runs,
        "top_songs_per_run": top_songs,
        "unique_top_songs": list(unique_tops),
        "consistent": consistent,
        "status": "PASS - consistent output" if consistent else "FAIL - inconsistent output across runs",
    }

    logging.info(f"Consistency check: {result['status']}")
    return result


def run_adversarial_check() -> dict:
    """
    Feeds edge-case and garbage input through the full pipeline and
    confirms the system degrades gracefully (no crash, sensible fallback)
    instead of failing outright.
    """
    adversarial_inputs = [
        "",
        "   ",
        "asdkfjaslkdfjalskdjf qwoeiruqwoeiru",
        "🎵🎶🎧" * 20,
        "a" * 2000,
        "'; DROP TABLE songs; --",
        "I want something " * 100,
    ]

    case_results = []
    all_passed = True

    for text in adversarial_inputs:
        label = text[:30] + ("..." if len(text) > 30 else "")
        try:
            tags = parse_mood_input(text)
            songs = load_songs()
            scored = [{**s, "match_score": score_song(s, tags)} for s in songs]
            scored.sort(key=lambda s: s["match_score"], reverse=True)
            top_song = scored[0]["title"] if scored else None

            case_results.append({
                "input": label,
                "tags_returned": tags,
                "top_song": top_song,
                "crashed": False,
            })
        except Exception as e:
            all_passed = False
            case_results.append({
                "input": label,
                "error": str(e),
                "crashed": True,
            })

    result = {
        "check": "adversarial",
        "timestamp": datetime.now().isoformat(),
        "total_cases": len(adversarial_inputs),
        "cases": case_results,
        "status": "PASS - no crashes" if all_passed else "FAIL - one or more inputs crashed the system",
    }

    logging.info(f"Adversarial check: {result['status']}")
    return result


if __name__ == "__main__":
    os.makedirs(RESULTS_DIR, exist_ok=True)

    sensitivity_result = run_sensitivity_check()
    print("=== Sensitivity Check ===")
    print(json.dumps(sensitivity_result, indent=2))
    with open(os.path.join(RESULTS_DIR, "sensitivity_check.json"), "w") as f:
        json.dump(sensitivity_result, f, indent=2)

    consistency_result = run_consistency_check()
    print("\n=== Consistency Check ===")
    print(json.dumps(consistency_result, indent=2))
    with open(os.path.join(RESULTS_DIR, "consistency_check.json"), "w") as f:
        json.dump(consistency_result, f, indent=2)

    adversarial_result = run_adversarial_check()
    print("\n=== Adversarial Check ===")
    print(json.dumps(adversarial_result, indent=2))
    with open(os.path.join(RESULTS_DIR, "adversarial_check.json"), "w") as f:
        json.dump(adversarial_result, f, indent=2)
