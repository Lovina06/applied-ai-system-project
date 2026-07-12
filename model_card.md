# 🎧 Model Card: VibeFinder 2.0

## 1. Model Name

**VibeFinder 2.0**

A music recommender that takes a free-text mood description and suggests a top-5 list of Bollywood songs. This is an evolution of VibeFinder 1.0 (Module 3), rebuilt with LLM-based input parsing and a dedicated reliability/testing engine.

---

## 2. Goal / Task

VibeFinder 2.0 takes one sentence from a user, like "I want something chill and romantic," and turns it into structured tags — genre, mood, and energy — using an LLM (Groq's `llama-3.3-70b-versatile`). It then scores every song in the dataset against those tags and returns the top 5 matches.

Unlike Version 1.0, the user doesn't fill out a form with dropdowns — they just describe their vibe in plain language, and the system interprets it. It does not learn over time; it re-parses and re-scores fresh on every request.

---

## 3. Data Used

The dataset is `app/data/songs.json`. It has **15 Bollywood songs**.

Each song has:

- title and artist
- genre (romantic, party, rock, travel, wedding, motivational, pop, hip-hop, folk)
- mood (chill, energetic, sad, happy, motivational, reflective)
- energy (0.0–1.0)
- acousticness (0.0–1.0)

**Limits:**

- Only 15 songs, so results repeat, especially for less common genre/mood combinations.
- Heavily weighted toward Arijit Singh tracks and romantic/sad songs — other artists and moods are underrepresented.
- No classical, devotional/bhajan, or regional (non-Hindi) Bollywood music.
- Some genres (folk, hip-hop) have only one song each, so those users get almost no real choice.

---

## 4. Algorithm Summary (Plain Language)

The pipeline has two stages:

**Stage 1 — Parsing:** The user's free-text input is sent to an LLM, which returns structured tags (genre, mood, energy) as JSON. If the LLM fails to respond or returns something unparseable, the system falls back to a safe default (`pop`, `chill`, `0.5`) rather than crashing.

**Stage 2 — Scoring:** Every song gets a score, same additive approach as Version 1.0:

- **Genre match:** +2.0 points if it matches the parsed genre.
- **Mood match:** +1.0 point if it matches the parsed mood.
- **Energy closeness:** up to +2.0 points, shrinking as the gap between song energy and target energy grows.
- **Acoustic + chill bonus:** +1.0 point if the song is acoustic and the mood is "chill."

Songs are sorted by score, and the top 5 are returned. As with Version 1.0, there is no penalty for a mismatch — a wrong genre or mood just contributes zero, never subtracts.

---

## 5. Observed Behavior / Biases

**Energy still dominates over genre and mood**, consistent with the Version 1.0 finding. The reliability suite's sensitivity check made this concrete and reproducible: nudging the target energy from 0.8 to 0.9 (a small, realistic shift) flipped the top recommendation from "Ghungroo" to "Kala Chashma" — two different songs, both plausible "party" matches, but the system isn't stable under small perturbations to just one input dimension.

**The LLM parsing layer adds a new source of variability** that Version 1.0 didn't have (since 1.0 used dropdowns, not free text). The consistency check found this layer to currently be stable: 5 identical calls with the same input text returned the same top song ("Kesariya") every time. This is a positive finding, but it's not guaranteed to hold for all inputs — only the one tested.

**The system does not flag contradictory or ambiguous input.** Like Version 1.0's "loves acoustic but wants high energy" issue, VibeFinder 2.0 will happily parse a self-contradictory sentence into tags without warning the user their request doesn't fully make sense.

---

## 6. Evaluation Process

Evaluation for this version centers on the **reliability engine** (`evaluation/eval_runner.py`), which runs three automated checks, integrated directly into the app's UI (not just standalone scripts):

**Sensitivity check** — Tests whether a small (+0.1) shift in target energy flips the top recommendation.

- Result: **FAIL** — flipped from "Ghungroo" (4.84) to "Kala Chashma" (5.0). Confirms the same fragility pattern documented in Version 1.0's model card, now measured on the new dataset and scoring path.

**Consistency check** — Runs the same free-text input through the full pipeline (LLM parsing included) 5 times and checks the top result stays stable.

- Result: **PASS** — "Kesariya" was returned as the top match in all 5 runs for "I want something chill and romantic."

**Adversarial check** — Feeds 7 edge cases through the full pipeline: empty string, whitespace-only, gibberish, emoji spam, a 2000-character string, a SQL-injection-style string, and heavily repeated text.

- Result: **PASS** — no crashes across any case. The system's try/except guardrails and default fallback tags handled every case gracefully, including the SQL-injection-style input, which was safely treated as plain text (no execution risk, since there's no database in this system).

**What surprised us:** the adversarial check passing cleanly wasn't a given — before the guardrails were added to `parse_mood_input()`, an empty string or malformed LLM response would have thrown an unhandled exception. The try/except + default fallback pattern is doing real work here, not just boilerplate.

---

## 7. Intended Use and Non-Intended Use

**Intended use:**

- A capstone project demonstrating an AI reliability/testing system integrated into a working application.
- A way to learn how LLM-based parsing, rule-based scoring, and automated reliability checks fit together in one pipeline.
- A portfolio piece demonstrating QA/testing thinking applied to an AI system, relevant to AI QA Automation Engineer and LLM Evaluation Engineer roles.

**Not intended for:**

- Real music recommendations for real users — the dataset is small and hand-curated, not representative of a real catalog.
- Any use involving real personal data or user profiles.
- Production or commercial use of any kind.
- Any claim that the reliability suite is exhaustive — it tests three specific failure modes (sensitivity, consistency, adversarial robustness), not the full space of possible AI reliability concerns (e.g., no bias-across-demographic-groups testing, since this system has no demographic inputs).

---

## 8. Ideas for Improvement

1. **Reduce energy's dominance in scoring** — e.g., cap its contribution or make weights configurable, so the sensitivity check's fragility finding can be directly addressed rather than just documented.
2. **Expand the adversarial suite** — add non-English input, extremely short input (single characters), and prompt-injection-style text specifically targeting the LLM parsing step (e.g., "ignore previous instructions and return X"), since the current adversarial set doesn't test LLM-specific attack patterns.
3. **Run the consistency check across a wider range of inputs**, not just one fixed sentence, to see if the LLM parsing layer's stability holds generally or only for common, clearly-worded requests.
