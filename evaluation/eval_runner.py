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


if __name__ == "__main__":
    os.makedirs(RESULTS_DIR, exist_ok=True)
    result = run_sensitivity_check()
    print(json.dumps(result, indent=2))

    with open(os.path.join(RESULTS_DIR, "sensitivity_check.json"), "w") as f:
        json.dump(result, f, indent=2)
