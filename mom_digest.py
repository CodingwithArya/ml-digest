# ─────────────────────────────────────────────────────────────
# mom_digest.py — daily digest for Priya
#
# Three sections tailored for a senior data analyst job hunting:
#   - Data & Analytics: SQL, Tableau, BI, data engineering
#   - AI in Business: how companies are actually using AI
#   - Tech Finance: AI revenue, losses, investment, IPOs
#
# Same format as ml-digest. No footers.
# Add MOM_EMAIL_TO to your .env file.
# ─────────────────────────────────────────────────────────────

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from dotenv import load_dotenv
import requests
import xml.etree.ElementTree as ET

load_dotenv()

GMAIL_USER         = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
MOM_EMAIL_TO       = os.getenv("MOM_EMAIL_TO")   # add this line to your .env

# ─── KEYWORDS ──────────────────────────────────────────────────────────────────

ANALYTICS_KEYWORDS = [
    # tools she actually uses day to day
    "sql", "tableau", "power bi", "snowflake", "databricks",
    "dbt", "looker", "data visualization", "dashboard",
    "python", "pandas", "numpy", "matplotlib", "seaborn",
    "jupyter", "data science", "machine learning basics",
    "data analyst", "business analyst", "financial analyst",
    "data warehouse", "business intelligence",
    "predictive analytics", "forecasting", "financial modeling",
    "reporting", "metrics", "kpi",
    # trends in the data industry worth knowing about
    "future of data", "data stack", "modern data stack",
    "analyst role", "data skills", "data career",
]

AI_BUSINESS_KEYWORDS = [
    # big picture AI trends — what's happening, not how to use it
    "ai trend", "ai adoption", "ai strategy", "state of ai",
    "generative ai", "large language model", "foundation model",
    "ai regulation", "ai policy", "ai governance", "ai act",
    "ai impact", "ai workforce", "ai jobs", "future of work",
    # big companies making AI moves
    "microsoft ai", "google ai", "amazon ai", "apple ai", "meta ai",
    "openai", "anthropic", "nvidia", "salesforce ai",
    "ai partnership", "ai deal", "ai acquisition",
    "chatgpt", "gemini", "copilot", "claude",
    # what's actually changing
    "ai replacing", "ai disruption", "ai transformation",
    "enterprise ai", "ai rollout", "ai deployment",
]

FINANCE_KEYWORDS = [
    # big company earnings — exact phrases from earnings coverage
    "earnings", "quarterly earnings", "quarterly results", "q1", "q2", "q3", "q4",
    "revenue", "revenue growth", "net income", "net loss", "operating income",
    "beats expectations", "misses expectations", "guidance",
    "microsoft earnings", "google earnings", "alphabet earnings",
    "amazon earnings", "meta earnings", "nvidia earnings",
    "apple earnings", "tesla earnings", "salesforce earnings",
    # ai-specific financials
    "ai revenue", "cloud revenue", "aws revenue", "azure revenue",
    "google cloud", "ai investment", "capex", "data center",
    "ai spending", "ai infrastructure",
    # ipos + startups going public
    "ipo", "going public", "s-1 filing", "direct listing",
    "profitable", "profitability", "burn rate", "path to profit",
    "openai valuation", "anthropic valuation", "ai unicorn",
    "funding round", "raised", "billion",
]

# ─── SOURCES ───────────────────────────────────────────────────────────────────

ANALYTICS_SOURCES = [
    {"name": "Towards Data Science",  "url": "https://towardsdatascience.com/feed"},
    {"name": "Mode Analytics Blog",   "url": "https://mode.com/blog/rss"},
    {"name": "dbt Blog",              "url": "https://www.getdbt.com/blog/rss"},
    {"name": "Locally Optimistic",    "url": "https://locallyoptimistic.com/feed/"},
    {"name": "Data Elixir",           "url": "https://dataelixir.com/feed/"},
    {"name": "Practical SQL",         "url": "https://blog.sqlauthority.com/feed/"},
    {"name": "Tableau Blog",          "url": "https://www.tableau.com/blog/rss"},
    {"name": "Databricks Blog",       "url": "https://www.databricks.com/blog/feed"},
    {"name": "Real Python",           "url": "https://realpython.com/atom.xml"},
    {"name": "PyData Blog",           "url": "https://pydata.org/feed/"},
]

AI_BUSINESS_SOURCES = [
    {"name": "Harvard Biz Review AI", "url": "https://hbr.org/topics/ai/rss"},
    {"name": "MIT Tech Review",       "url": "https://www.technologyreview.com/feed/"},
    {"name": "VentureBeat AI",        "url": "https://venturebeat.com/category/ai/feed/"},
    {"name": "The Verge AI",          "url": "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml"},
    {"name": "Wired AI",              "url": "https://www.wired.com/feed/tag/ai/rss"},
    {"name": "One Useful Thing",      "url": "https://www.oneusefulthing.org/feed"},
    {"name": "The Batch (DeepLearning.AI)", "url": "https://www.deeplearning.ai/the-batch/rss/"},
]

FINANCE_SOURCES = [
    # best free sources for AI financial news
    {"name": "TechCrunch",            "url": "https://techcrunch.com/feed/"},          # funding rounds, IPOs
    {"name": "TechCrunch Startups",   "url": "https://techcrunch.com/category/startups/feed/"},
    {"name": "Reuters Technology",    "url": "https://feeds.reuters.com/reuters/technologyNews"},  # earnings
    {"name": "Crunchbase News",       "url": "https://news.crunchbase.com/feed/"},     # funding + valuations
    {"name": "Stratechery",           "url": "https://stratechery.com/feed/"},         # deep business analysis
    {"name": "Import AI",             "url": "https://jack-clark.net/feed/"},          # AI industry money moves
    {"name": "The Batch (DeepLearning.AI)", "url": "https://www.deeplearning.ai/the-batch/rss/"},  # weekly AI biz news
    {"name": "Hacker News",           "url": "https://hnrss.org/frontpage"},           # breaks funding/IPO news fast
]

# ─── READ/PODCAST/SKIM TAGS ────────────────────────────────────────────────────

READ_SOURCES = {
    "Harvard Biz Review AI", "MIT Tech Review", "dbt Blog",
    "Locally Optimistic", "Towards Data Science",
}
PODCAST_SOURCES = {
    "One Useful Thing", "Import AI", "Stratechery",
}
# everything else → skim

# ─── SHARED LOGIC (same as digest.py) ─────────────────────────────────────────

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

def parse_rss(xml_text):
    try:
        root  = ET.fromstring(xml_text)
        items = []
        for item in root.findall('.//item'):
            title_elem   = item.find('title')
            link_elem    = item.find('link')
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

# ─── HTML (same structure as digest.py) ───────────────────────────────────────

def build_html(sections_data, total, date_str):
    def item_html(item):
        mode  = reading_mode(item["source"])
        color = TAG_COLORS[mode]
        bg    = TAG_BG[mode]
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

    sections_html = "".join(section_html(e, t, i) for e, t, i in sections_data)

    return f"""
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0; padding:0; background:#f8fafc; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
<div style="max-width:580px; margin:0 auto; background:#ffffff; padding:40px 36px; border-radius:8px;">

    <div style="margin-bottom:32px; padding-bottom:24px; border-bottom:2px solid #e2e8f0;">
        <div style="font-size:22px; font-weight:700; color:#0f172a; margin-bottom:4px;">Daily Digest</div>
        <div style="font-size:13px; color:#64748b;">{date_str} &nbsp;·&nbsp; {total} links</div>
        <div style="margin-top:12px; font-size:12px; color:#94a3b8; line-height:1.8;">
            <span style="color:#2563eb; font-weight:600;">read</span> → open in browser &nbsp;
            <span style="color:#7c3aed; font-weight:600;">podcast</span> → NotebookLM &nbsp;
            <span style="color:#64748b; font-weight:600;">skim</span> → 30 sec
        </div>
    </div>

    {sections_html}

</div>
</body>
</html>"""

# ─── SEND ──────────────────────────────────────────────────────────────────────

def send_email(subject, html):
    if not all([GMAIL_USER, GMAIL_APP_PASSWORD, MOM_EMAIL_TO]):
        print("\n[PREVIEW — add MOM_EMAIL_TO to .env]\n")
        print(html[:500])
        return
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = GMAIL_USER
    msg["To"]      = MOM_EMAIL_TO
    msg.attach(MIMEText(html, "html"))
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_USER, MOM_EMAIL_TO, msg.as_string())
    print("✓ Mom's digest sent")

# ─── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    print(f"\n📊 Mom's Digest — {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

    print("  Fetching data & analytics...")
    a_raw = fetch_section(ANALYTICS_SOURCES,   ANALYTICS_KEYWORDS)
    print("  Fetching AI in business...")
    b_raw = fetch_section(AI_BUSINESS_SOURCES, AI_BUSINESS_KEYWORDS)
    print("  Fetching tech finance...")
    f_raw = fetch_section(FINANCE_SOURCES,     FINANCE_KEYWORDS)

    analytics   = top_n_deduped(a_raw, 3, min_score=1)
    ai_business = top_n_deduped(b_raw, 3, min_score=1)
    finance     = top_n_deduped(f_raw, 3, min_score=1)

    total    = len(analytics) + len(ai_business) + len(finance)
    date_str = datetime.now().strftime("%B %d, %Y")

    sections_data = [
        ("📊", "Data & Analytics",   analytics),
        ("🤖", "AI in Business",     ai_business),
        ("💰", "Tech Finance & IPOs", finance),
    ]

    html = build_html(sections_data, total, date_str)
    send_email(f"Daily Digest — {datetime.now().strftime('%b %d')}", html)
    print(f"Done. {total} links.")

if __name__ == "__main__":
    main()