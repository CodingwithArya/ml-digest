# ml-digest

Very vibecoded daily AI/ML digest — scrapes arXiv, lab blogs, and industry sources every morning. Scores by relevance and sends a clean HTML email tagged **(read)**, **(podcast)**, or **(skim)** so you know exactly what to do with each link.

## Setup

1. Install deps:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Copy and fill in credentials:
```bash
cp .env.example .env
```

3. Get a Gmail App Password:
   - Go to myaccount.google.com/apppasswords
   - Create one named `ml-digest`
   - Paste it into `GMAIL_APP_PASSWORD` in your `.env`

4. Test run:
```bash
python3 digest.py
```

5. Schedule daily at 8am:
```bash
crontab -e
# add this line (update path to match yours):
0 8 * * * /Users/YOUR_NAME/ml-digest/venv/bin/python3 /Users/YOUR_NAME/ml-digest/digest.py
```

## Sources

**Research** — arXiv (Speech, NLP, AI, ML, CV)

**ML & AI** — HuggingFace Blog, BAIR Blog, CMU ML Blog, Google Research, MIT News AI, The Gradient, Ahead of AI, Interconnects, Chip Huyen, Eugene Yan, One Useful Thing

**Security & Systems** — arXiv Security, AI Alignment Forum

**Industry** — DeepMind, OpenAI, Anthropic, Meta AI, Import AI, Pragmatic Engineer, Uber Engineering

## Customization

- **Keywords** — edit the keyword lists at the top of `digest.py` to match your research domain
- **Sources** — add/remove from the source lists to pull from different feeds
- **Link counts** — adjust `top_n_deduped(n=...)` to get more or fewer links per section
- **Send time** — change `0 8` in crontab to your preferred hour

Hope you enjoy :)
