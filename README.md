# 🎵 VibeFinder — AI-Powered Music Recommender with Reliability Testing

VibeFinder is a Bollywood music recommendation system that takes free-text mood descriptions (e.g. "I want something chill and romantic") and returns ranked song matches using LLM-based intent parsing and rule-based scoring. It includes a fully integrated **reliability/testing engine** that evaluates the system's consistency, sensitivity, and robustness to adversarial input — live, inside the app.

Built as a CodePath AI110 capstone project (Option A: Reliability/Testing System).

## Features

- **Free-text mood input** — powered by Groq's `llama-3.3-70b-versatile` to extract genre, mood, and energy tags from natural language
- **Rule-based scoring engine** — additive scoring across genre, mood, and energy closeness
- **Reliability Suite** (the core AI feature):
  - **Sensitivity check** — tests whether small changes to input flip the top recommendation (fragility detection)
  - **Consistency check** — verifies repeated identical input produces stable output
  - **Adversarial check** — confirms the system handles empty, garbage, and malicious input without crashing
- **Guardrails** — try/except wrapping around all LLM calls and file I/O, with a safe default fallback if parsing fails
- **Logging** — all parsing attempts, recommendations, and reliability check results are logged to `logs/app.log`

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/Lovina06/applied-ai-system-project.git
cd applied-ai-system-project
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up your API key

Copy `.env.example` to `.env` and add your Groq API key:

```bash
cp .env.example .env
```

Then edit `.env`:
GROQ_API_KEY=your_groq_api_key_here
Get a free key at [console.groq.com](https://console.groq.com).

### 4. Run the app

```bash
python3 -m streamlit run app/main.py
```

Open the app in **Chrome** (Safari has known audio playback issues with Streamlit's audio widget).

## Project Structure

applied-ai-system-project/
├── app/
│ ├── main.py # Streamlit UI (Find Songs + Reliability tabs)
│ ├── recommender.py # Mood parsing + scoring logic
│ ├── data/songs.json # Bollywood song dataset
│ └── assets/ # Background music, images
├── evaluation/
│ ├── eval_runner.py # Reliability check implementations
│ └── results/ # Saved check outputs (JSON)
├── tests/
│ └── test_recommender.py
├── logs/app.log
└── requirements.txt

## Running the Reliability Suite Standalone

You can also run the checks directly from the terminal without the UI:

```bash
python3 evaluation/eval_runner.py
```

This prints results to the console and saves them to `evaluation/results/`.

## Known Findings

The reliability suite has already surfaced a real limitation: the scoring system's top recommendation is sensitive to small changes in energy weighting (see `evaluation/results/sensitivity_check.json`). This is documented and discussed further in the project's model card.

## Tech Stack

- Python 3.9
- Streamlit (UI)
- Groq API (`llama-3.3-70b-versatile`) for mood parsing
- pytest (unit testing)
