# AI Research Agent

A minimal Streamlit starter app for topic-based research workflows.

## Features

- Sidebar with app title and description
- Text input for a research topic
- Submit button
- Results placeholder powered by a `run_research()` hook

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

## Next Step

Replace `run_research()` in `app.py` with your real pipeline (search APIs, LLM calls, retrieval, ranking, summarization).
