# ─────────────────────────────────────────────────────────────
# NOTE: This was mainly vibecoded! Small project to stay updated on news
# ml-digest — daily AI/ML research digest via email
#
# Scrapes arXiv, lab blogs, and industry sources every morning.
# Scores entries against keyword sets tailored to:
#   - Earable proactive agent research (turn-taking, interrupt timing)
#   - ML & AI engineering (models, evals, systems)
#   - Security & distributed systems (identity, auth, infra)
#   - Industry (lab drops, Uber engineering, launches)
#
# Sends a clean HTML email tagged (read) / (podcast) / (skim)
# so you know exactly what to do with each link.
#
# Setup: copy .env.example → .env, fill in Gmail credentials.
# Schedule: crontab -e → 0 8 * * * python3 /path/to/digest.py
# ─────────────────────────────────────────────────────────────
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from dotenv import load_dotenv
import requests
import xml.etree.ElementTree as ET
import random

load_dotenv()

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
EMAIL_TO = os.getenv("EMAIL_TO")

NEWS_KEYWORDS = [
    "breaking", "latest", "today", "report", "says", "new",
]
RESEARCH_KEYWORDS = [
    "earable", "earables", "in-ear", "wearable assistant", "proactive agent",
    "interrupt timing", "interruption detection", "turn-taking", "barge-in",
    "opportune moment", "conversational agent timing", "dialogue timing",
    "full duplex", "full-duplex", "simultaneous speech",
    "acoustic features", "pitch detection", "speech prosody", "voice activity",
    "energy detection", "speaking rate", "speech rate", "disfluency detection",
    "hesitation detection", "silence token", "speech segmentation",
    "acoustic modeling", "prosodic features",
    "rlhf dialogue", "rlhf personalization", "reinforcement learning human feedback",
    "preference learning conversation", "personalized timing", "user preference learning",
    "reward modeling conversation", "human feedback dialogue",
    "context aware", "context-aware", "situation awareness", "user state detection",
    "cognitive load detection", "attention detection", "interruptibility",
    "just in time", "just-in-time", "information delivery timing",
    "moshi", "llamapie", "syncllm", "freeze-omni", "ct-sdlm",
    "speech language model", "speech llm", "audio llm",
    "real-time speech", "on-device speech", "streaming speech",
    "spoken language understanding", "intent detection speech",
    "slot filling conversation", "semantic understanding dialogue",
    "speech recognition personalization",
    "dialogue benchmark", "turn-taking benchmark", "conversation corpus",
    "interview dataset", "customer service dialogue", "language learning dialogue",
    "annotated dialogue corpus", "human evaluation dialogue",
]

ML_KEYWORDS = [
    "llm", "large language model", "transformer", "foundation model",
    "multimodal", "speech text", "audio language",
    "agent", "agentic", "multi-agent", "tool use",
    "reasoning", "chain-of-thought", "in-context learning",
    "fine-tun", "rlhf", "rlaif", "dpo", "preference learning",
    "instruction tuning", "adapter", "lora", "peft",
    "personalization", "user modeling", "adaptive systems",
    "inference", "serving", "latency", "on-device", "edge inference",
    "quantization", "distillation", "model compression",
    "streaming inference", "real-time", "low latency",
    "benchmark", "evaluation", "human evaluation",
    "inter-annotator agreement", "inter-rater reliability",
    "safety", "alignment", "interpretability", "mechanistic",
]

SECURITY_KEYWORDS = [
    "agent security", "agent authorization", "agent identity",
    "agent timing attack", "interrupt injection", "prompt injection",
    "adversarial agent", "agent robustness",
    "privacy", "differential privacy", "federated learning",
    "user data", "personal information", "on-device", "local processing",
    "distributed systems", "edge computing", "fog computing",
    "device to cloud", "sync", "offline first",
    "audio security", "voice biometric", "speaker verification",
    "adversarial audio", "audio attack", "model poisoning",
]

INDUSTRY_KEYWORDS = [
    "uber", "distributed systems", "microservices", "service mesh",
    "load balancing", "routing", "matching", "real-time", "low latency",
    "infrastructure", "platform", "scale", "performance",
    "authentication", "authorization", "token exchange", "identity",
    "workflow", "cadence", "orchestration", "job scheduling",
    "consensus", "replication", "fault tolerance",
    "tracing", "observability", "monitoring",
    "apple", "apple watch", "airpods", "airpods pro",
    "google", "pixel buds", "pixel", "wear os",
    "samsung", "galaxy buds", "wearable",
    "meta", "ray ban glasses", "smart glasses",
    "amazon", "alexa", "echo buds",
    "openai", "anthropic", "deepmind", "google deepmind",
    "meta ai", "mistral", "cohere", "together",
    "interspeech", "icml", "neurips", "emnlp",
    "acl", "sigir", "chi", "uist",
    "model release", "new model", "launch", "announced",
    "open source", "open-source", "weights released",
    "speech model", "audio model", "agent framework",
]

NEWS_SOURCES = [
    {"name": "AP News",              "url": "https://feeds.apnews.com/rss/topnews"},
    {"name": "Reuters",              "url": "https://feeds.reuters.com/reuters/topNews"},
    {"name": "BBC News",             "url": "http://feeds.bbci.co.uk/news/rss.xml"},
    {"name": "The Guardian",         "url": "https://www.theguardian.com/world/rss"},
    {"name": "Al Jazeera",           "url": "https://www.aljazeera.com/xml/rss/all.xml"},
    {"name": "NPR News",             "url": "https://feeds.npr.org/1001/rss.xml"},
    {"name": "PBS NewsHour",         "url": "https://www.pbs.org/newshour/feeds/rss/headlines"},
    {"name": "Financial Times",      "url": "https://www.ft.com/rss/home"},
    {"name": "The Economist",        "url": "https://www.economist.com/latest/rss.xml"},
    {"name": "WSJ World News",       "url": "https://feeds.a.dj.com/rss/RSSWorldNews.xml"},
    {"name": "WSJ US Business",      "url": "https://feeds.a.dj.com/rss/WSJcomUSBusiness.xml"},
    {"name": "Bloomberg Markets",    "url": "https://feeds.bloomberg.com/markets/news.rss"},
    {"name": "Politico",             "url": "https://rss.politico.com/politics-news.xml"},
    {"name": "The Hill",             "url": "https://thehill.com/rss/syndicator/19110"},
    {"name": "NYT Science",          "url": "https://rss.nytimes.com/services/xml/rss/nyt/Science.xml"},
    {"name": "The Atlantic",         "url": "https://www.theatlantic.com/feed/all/"},
    {"name": "Hacker News",          "url": "https://hnrss.org/frontpage"},
    {"name": "Reddit r/worldnews",   "url": "https://www.reddit.com/r/worldnews/.rss"},
    {"name": "Axios",                "url": "https://www.axios.com/feed/"},
    {"name": "Vox",                  "url": "https://www.vox.com/rss/index.xml"},
    {"name": "ProPublica",           "url": "https://feeds.propublica.org/main"},
    {"name": "The New York Times",   "url": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml"},
    {"name": "Financial Times",      "url": "https://www.ft.com/rss/home"},
    {"name": "The Economist",        "url": "https://www.economist.com/latest/rss.xml"},
    {"name": "WSJ World News",       "url": "https://feeds.a.dj.com/rss/RSSWorldNews.xml"},
    {"name": "Axios",                "url": "https://www.axios.com/feed/"},
]

RESEARCH_SOURCES = [
    {"name": "arXiv Speech",      "url": "https://arxiv.org/rss/eess.AS"},
    {"name": "arXiv NLP",         "url": "https://arxiv.org/rss/cs.CL"},
    {"name": "arXiv AI",          "url": "https://arxiv.org/rss/cs.AI"},
    {"name": "arXiv ML",          "url": "https://arxiv.org/rss/cs.LG"},
    {"name": "arXiv CV",          "url": "https://arxiv.org/rss/cs.CV"},
]

ML_SOURCES = [
    {"name": "HuggingFace Blog",  "url": "https://huggingface.co/blog/feed.xml"},
    {"name": "BAIR Blog",         "url": "https://bair.berkeley.edu/blog/feed.xml"},
    {"name": "CMU ML Blog",       "url": "https://blog.ml.cmu.edu/feed"},
    {"name": "Google Research",   "url": "https://research.google/blog/rss/"},
    {"name": "MIT News AI",       "url": "https://news.mit.edu/rss/topic/artificial-intelligence"},
    {"name": "The Gradient",      "url": "https://thegradient.pub/rss/"},
    {"name": "Ahead of AI",       "url": "https://magazine.sebastianraschka.com/feed"},
    {"name": "Interconnects",     "url": "https://www.interconnects.ai/feed"},
    {"name": "Chip Huyen",        "url": "https://huyenchip.com/feed.xml"},
    {"name": "Eugene Yan",        "url": "https://eugeneyan.com/rss/"},
    {"name": "One Useful Thing",  "url": "https://www.oneusefulthing.org/feed"},
]

SECURITY_SOURCES = [
    {"name": "arXiv Security",    "url": "https://arxiv.org/rss/cs.CR"},
    {"name": "AI Alignment Forum","url": "https://www.alignmentforum.org/feed.xml"},
]

INDUSTRY_SOURCES = [
    {"name": "DeepMind",          "url": "https://deepmind.google/blog/rss.xml"},
    {"name": "OpenAI",            "url": "https://openai.com/news/rss.xml"},
    {"name": "Anthropic Research","url": "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_research.xml"},
    {"name": "Anthropic News",    "url": "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_news.xml"},
    {"name": "Meta AI",           "url": "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_meta_ai.xml"},
    {"name": "Import AI",         "url": "https://jack-clark.net/feed/"},
    {"name": "Pragmatic Engineer","url": "https://newsletter.pragmaticengineer.com/feed"},
    {"name": "Uber Engineering",  "url": "https://www.uber.com/blog/engineering/feed/"},
]

READ_SOURCES = {
    "arXiv Speech", "arXiv NLP", "arXiv AI", "arXiv ML",
    "arXiv Security", "BAIR Blog", "CMU ML Blog", "Google Research",
}
PODCAST_SOURCES = {
    "Interconnects", "Ahead of AI", "Import AI", "Pragmatic Engineer",
    "Chip Huyen", "Eugene Yan", "The Gradient",
    "AI Alignment Forum", "HuggingFace Blog",
}

def parse_rss(xml_text):
    try:
        root = ET.fromstring(xml_text)
        items = []
        for item in root.findall('.//item'):
            title_elem = item.find('title')
            link_elem  = item.find('link')
            summary_elem = item.find('description')
            if title_elem is not None and link_elem is not None:
                items.append({
                    'title':   (title_elem.text or '').strip(),
                    'link':    (link_elem.text or '').strip(),
                    'summary': (summary_elem.text or '').strip() if summary_elem is not None else '',
                })
        return items
    except:
        return []

def reading_mode(source):
    if source in READ_SOURCES:    return "read"
    if source in PODCAST_SOURCES: return "podcast"
    return "skim"

def score(title, summary, keywords):
    text = (title + " " + summary).lower()
    return sum(1 for kw in keywords if kw in text)

def fetch_section(sources, keywords):
    results = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    for source in sources:
        try:
            r = requests.get(source["url"], timeout=5, headers=headers)
            r.raise_for_status()
            items = parse_rss(r.text)
            if not items:
                continue
            # Score all 50, but boost score for entries in top 10 (most recent). helps make sure you read relevant papers but prioritizes
            # new ones :) 
            scored = []
            for idx, e in enumerate(items[:50]):
                s = score(e['title'], e['summary'], keywords)
                recency_boost = 2 if idx < 10 else 0
                scored.append((s + recency_boost, e, s))
            scored.sort(key=lambda x: x[0], reverse=True)
            best_boosted, best_entry, raw_score = scored[0]
            results.append({
                "source": source["name"],
                "title":  best_entry['title'][:110],
                "link":   best_entry['link'],
                "score":  raw_score,
            })
        except:
            pass
    return results

def top_n_deduped(results, n, min_score=1):
    seen, out = set(), []
    for item in sorted(results, key=lambda x: x["score"], reverse=True):
        if item["link"] not in seen and item["score"] >= min_score:
            seen.add(item["link"])
            out.append(item)
        if len(out) >= n:
            break
    return out

TAG_COLORS = {
    "read":    "#2563eb",
    "podcast": "#7c3aed",
    "skim":    "#64748b",
}
TAG_BG = {
    "read":    "#eff6ff",
    "podcast": "#f5f3ff",
    "skim":    "#f8fafc",
}

FOOTERS = [ #these are personalized to me, but you can change these to anything :) 
    # ai generated self-aware
    "you read one paper today. you are basically a professor now.",
    "somewhere out there, a senior engineer is also confused. you're in good company.",
    "papers read: +1. papers fully understood: debatable.",
    "if you read this and then immediately open instagram, that's okay. we don't judge.",
    "knowledge acquired. now go touch grass.",
    "you opened the email. that's already more than yesterday.",
    "a paper a day keeps the 'uh I haven't really looked into that' away.",
    "big brain activities only in this inbox.",
    "reading papers is just adulting with citations.",
    "your future self is nodding approvingly. your current self can go back to sleep.",
    "this is your sign to close 47 browser tabs and read one thing deeply.",
    "certified intellectual (pending).",
    "you didn't have to do this. but here you are. respect.",
    "powered by caffeine, curiosity, and mild anxiety about the future.",
    "less doomscrolling, more doom-reading-papers.",
    "ok smartypants, go learn something.",
    "another day, another opportunity to have opinions about attention mechanisms.",
    "the machine learns. so do you. difference is you get a hojicha latte with caramel.",

    # moto moto
    "big and chunky. just like this paper's appendix.",
    "moto moto likes this digest. moto moto likes it a lot.",
    "you are big. you are chunky. you are reading arxiv. iconic.",
    "the models are large. the ideas are large. you are large. (intellectually.)",

    # boss baby
    "i'm not a regular researcher, i'm a cool researcher.",
    "listen here, tiny intern. the field doesn't stop moving. neither do you.",
    "meeting in 10. you better have read something.",
    "boss baby would have read all of these by 6am. just saying.",
    "you didn't choose the research life. the research life chose you.",
    "this is business. baby business.",

    # sofia the first
    "you've got the knowledge, you've got the vibe, you've got the email digest.",
    "every great researcher started somewhere. today that somewhere is your inbox.",
    "being curious is a superpower. wear the crown.",
    "once upon a time there was a very smart person who read their daily digest. the end.",

    # my little pony
    "friendship is magic. so is a well-timed arxiv paper.",
    "today's element of harmony: staying up to date on the literature.",
    "you're doing amazing sweetie (twilight sparkle voice).",
    "the magic was inside you all along. also it was in this email.",
    "20% cooler than you were yesterday. keep going.",
]
def build_html(sections_data, total, date_str, footer_line):
    def item_html(item):
        mode = reading_mode(item["source"])
        color  = TAG_COLORS[mode]
        bg     = TAG_BG[mode]
        return f"""
        <div style="margin-bottom:20px; padding-bottom:20px; border-bottom:1px solid #f1f5f9;">
            <div style="margin-bottom:6px;">
                <span style="
                    display:inline-block;
                    background:{bg};
                    color:{color};
                    font-size:11px;
                    font-weight:600;
                    letter-spacing:0.5px;
                    text-transform:uppercase;
                    padding:2px 8px;
                    border-radius:4px;
                ">{mode}</span>
                <span style="font-size:11px; color:#94a3b8; margin-left:8px;">{item['source']}</span>
            </div>
            <a href="{item['link']}" style="
                font-size:15px;
                font-weight:500;
                color:#0f172a;
                text-decoration:none;
                line-height:1.4;
                display:block;
                margin-bottom:4px;
            ">{item['title']}</a>
            <a href="{item['link']}" style="font-size:12px; color:#3b82f6; text-decoration:none;">{item['link'][:60]}...</a>
        </div>"""

    def section_html(emoji, title, items):
        if not items:
            return ""
        items_html = "".join(item_html(i) for i in items)
        return f"""
        <div style="margin-bottom:36px;">
            <div style="
                font-size:13px;
                font-weight:600;
                letter-spacing:1px;
                text-transform:uppercase;
                color:#64748b;
                margin-bottom:16px;
                padding-bottom:8px;
                border-bottom:2px solid #e2e8f0;
            ">{emoji}&nbsp; {title}</div>
            {items_html}
        </div>"""

    sections_html = ""
    for emoji, title, items in sections_data:
        sections_html += section_html(emoji, title, items)

    return f"""
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0; padding:0; background:#f8fafc; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
<div style="max-width:580px; margin:0 auto; background:#ffffff; padding:40px 36px; border-radius:8px;">

    <div style="margin-bottom:32px; padding-bottom:24px; border-bottom:2px solid #e2e8f0;">
        <div style="font-size:22px; font-weight:700; color:#0f172a; margin-bottom:4px;">ML Digest</div>
        <div style="font-size:13px; color:#64748b;">{date_str} &nbsp;·&nbsp; {total} links</div>
        <div style="margin-top:12px; font-size:12px; color:#94a3b8; line-height:1.8;">
            <span style="color:#2563eb; font-weight:600;">read</span> → open in browser &nbsp;
            <span style="color:#7c3aed; font-weight:600;">podcast</span> → NotebookLM &nbsp;
            <span style="color:#64748b; font-weight:600;">skim</span> → 30 sec
        </div>
    </div>

    {sections_html}

    <div style="
        margin-top:16px;
        padding-top:24px;
        border-top:1px solid #e2e8f0;
        font-size:12px;
        color:#94a3b8;
        line-height:1.8;
    ">
        {footer_line}
    </div>

</div>
</body>
</html>"""

def send_email(subject, html):
    if not all([GMAIL_USER, GMAIL_APP_PASSWORD, EMAIL_TO]):
        print("\n[PREVIEW — no credentials]\n")
        print(html[:500])
        return
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = GMAIL_USER
    msg["To"]      = EMAIL_TO
    msg.attach(MIMEText(html, "html"))
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_USER, EMAIL_TO, msg.as_string())
    print("✓ Email sent")

def main():
    print(f"\n🔍 ML Digest — {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

    print("  Fetching top news...")
    n_raw = fetch_section(NEWS_SOURCES, NEWS_KEYWORDS)
    print("  Fetching research...")
    r_raw  = fetch_section(RESEARCH_SOURCES, RESEARCH_KEYWORDS)
    print("  Fetching ML/AI...")
    ml_raw = fetch_section(ML_SOURCES,       ML_KEYWORDS)
    print("  Fetching security/systems...")
    s_raw  = fetch_section(SECURITY_SOURCES, SECURITY_KEYWORDS)
    print("  Fetching industry...")
    i_raw  = fetch_section(INDUSTRY_SOURCES, INDUSTRY_KEYWORDS)

    news  = top_n_deduped(n_raw, 4, min_score=0)  # min_score=0 so always show smt
    research = top_n_deduped(r_raw,  2, min_score=1)
    ml       = top_n_deduped(ml_raw, 3, min_score=1)
    security = top_n_deduped(s_raw,  2, min_score=1)
    industry = top_n_deduped(i_raw,  2, min_score=1)

    total = len(news) + len(research) + len(ml) + len(security) + len(industry)
    date_str = datetime.now().strftime("%B %d, %Y")

    sections_data = [
        ("📰", "Top News", news),
        ("🎙️", "Your Research", research),
        ("🤖", "ML & AI", ml),
        ("🔐", "Security & Systems", security),
        ("📡", "Industry", industry),
    ]
    footer_line = random.choice(FOOTERS)
    html = build_html(sections_data, total, date_str, footer_line)
    send_email(f"ML Digest — {datetime.now().strftime('%b %d')}", html)
    print(f"Done. {total} links.")

if __name__ == "__main__":
    main()