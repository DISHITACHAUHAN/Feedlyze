import html
from collections import Counter

import sqlite3
import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000/analyzer"
DB_FILE = "reviews.db"


# ---------------- Database helpers (unchanged) ----------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            review TEXT,
            label TEXT,
            score INTEGER,
            theme TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def save_results(results):
    conn = sqlite3.connect(DB_FILE)
    conn.executemany(
        "INSERT INTO reviews (review, label, score, theme) VALUES (?, ?, ?, ?)",
        [(r["review"], r["label"], r["score"], r["theme"]) for r in results],
    )
    conn.commit()
    conn.close()


def load_history():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.execute("SELECT review, label, score, theme FROM reviews ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return [
        {"review": r[0], "label": r[1], "score": r[2], "theme": r[3]}
        for r in rows
    ]


# ---------------- Page config ----------------
st.set_page_config(
    page_title="Feedlyze",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------- Theme / CSS ----------------
st.markdown(
    """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Sora:wght@500;600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --voxora-primary: #4A7FE8;
            --voxora-primary-dark: #2F5FC4;
            --voxora-primary-tint: #EAF2FF;
            --voxora-bg-top: #F2F7FF;
            --voxora-bg-bottom: #FFFFFF;
            --voxora-heading: #10294B;
            --voxora-text: #3C4E63;
            --voxora-text-soft: #6C7D91;
            --voxora-border: #DEEAFB;
            --voxora-shadow: 0 4px 18px rgba(16, 41, 75, 0.06);
            --voxora-shadow-hover: 0 8px 24px rgba(16, 41, 75, 0.11);
            --voxora-positive-bg: #E4F6EA;
            --voxora-positive-text: #1E8449;
            --voxora-negative-bg: #FCEAEA;
            --voxora-negative-text: #C0392B;
            --voxora-neutral-bg: #EAF1F9;
            --voxora-neutral-text: #4A6178;
            --voxora-error-bg: #F1F1F1;
            --voxora-error-text: #6B6B6B;
        }

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            color: var(--voxora-text);
        }

        .stApp {
            background: linear-gradient(180deg, var(--voxora-bg-top) 0%, var(--voxora-bg-bottom) 420px);
        }

        h1, h2, h3, h4 {
            font-family: 'Sora', sans-serif;
            color: var(--voxora-heading);
        }

        #MainMenu, footer, header {visibility: hidden;}

        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1080px;
        }

        /* ---- Hero ---- */
        .voxora-hero {
            background: linear-gradient(120deg, #EAF2FF 0%, #F8FBFF 100%);
            border: 1px solid var(--voxora-border);
            border-radius: 20px;
            padding: 3rem 2.6rem;
            margin-bottom: 1.8rem;
            box-shadow: var(--voxora-shadow);
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            gap: 1.1rem;
        }
        .voxora-hero-icon {
            width: 60px;
            height: 60px;
            flex-shrink: 0;
            border-radius: 16px;
            background: var(--voxora-primary);
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 6px 16px rgba(74, 127, 232, 0.35);
            margin-bottom: 0.3rem;
        }
        .voxora-hero-title {
            font-family: 'Sora', sans-serif;
            font-size: 3rem;
            font-weight: 700;
            color: var(--voxora-heading);
            margin: 0;
            line-height: 1.1;
            letter-spacing: -0.01em;
        }
        .voxora-hero-tagline {
            font-size: 1.15rem;
            font-weight: 600;
            color: var(--voxora-primary-dark);
            margin: 0;
            text-align: center;
        }
        .voxora-hero-desc {
            font-size: 0.95rem;
            color: var(--voxora-text-soft);
            margin: 0;
            max-width: 520px;
            text-align: center;
        }

        /* ---- Section headings ---- */
        .voxora-section-title {
            font-family: 'Sora', sans-serif;
            font-size: 1.25rem;
            font-weight: 600;
            color: var(--voxora-heading);
            margin: 1.6rem 0 0.8rem 0;
        }

        /* ---- Cards (native Streamlit bordered containers) ---- */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 16px !important;
            border: 1px solid var(--voxora-border) !important;
            box-shadow: var(--voxora-shadow);
            background: #FFFFFF;
            transition: box-shadow 0.15s ease;
        }
        div[data-testid="stVerticalBlockBorderWrapper"]:hover {
            box-shadow: var(--voxora-shadow-hover);
        }

        textarea {
            border-radius: 12px !important;
            border: 1px solid var(--voxora-border) !important;
        }

        .stButton > button {
            background: var(--voxora-primary);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 0.55rem 1.4rem;
            font-weight: 600;
            font-family: 'Inter', sans-serif;
            box-shadow: 0 4px 12px rgba(74, 127, 232, 0.28);
            transition: background 0.15s ease, transform 0.1s ease;
        }
        .stButton > button:hover {
            background: var(--voxora-primary-dark);
            color: white;
            transform: translateY(-1px);
        }

        /* ---- Metric cards ---- */
        .voxora-metric-card {
            background: #FFFFFF;
            border: 1px solid var(--voxora-border);
            border-radius: 14px;
            padding: 1.1rem 1.2rem;
            box-shadow: var(--voxora-shadow);
            height: 100%;
            transition: box-shadow 0.15s ease, transform 0.1s ease;
        }
        .voxora-metric-card:hover {
            box-shadow: var(--voxora-shadow-hover);
            transform: translateY(-2px);
        }
        .voxora-metric-icon {
            font-size: 1.15rem;
            margin-bottom: 0.35rem;
        }
        .voxora-metric-label {
            font-size: 0.8rem;
            color: var(--voxora-text-soft);
            font-weight: 500;
            margin-bottom: 0.3rem;
        }
        .voxora-metric-value {
            font-family: 'Sora', sans-serif;
            font-size: 1.6rem;
            font-weight: 700;
            color: var(--voxora-heading);
        }

        /* ---- Badges ---- */
        .voxora-badge {
            display: inline-block;
            padding: 0.22rem 0.7rem;
            border-radius: 999px;
            font-size: 0.8rem;
            font-weight: 600;
            white-space: nowrap;
        }
        .badge-positive { background: var(--voxora-positive-bg); color: var(--voxora-positive-text); }
        .badge-negative { background: var(--voxora-negative-bg); color: var(--voxora-negative-text); }
        .badge-neutral  { background: var(--voxora-neutral-bg);  color: var(--voxora-neutral-text); }
        .badge-error    { background: var(--voxora-error-bg);    color: var(--voxora-error-text); }

        /* ---- Results table ---- */
        .voxora-table-wrap {
            border: 1px solid var(--voxora-border);
            border-radius: 14px;
            overflow: hidden;
            box-shadow: var(--voxora-shadow);
            background: #FFFFFF;
        }
        table.voxora-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9rem;
        }
        table.voxora-table th {
            text-align: left;
            background: var(--voxora-primary-tint);
            color: var(--voxora-heading);
            font-weight: 600;
            padding: 0.7rem 1rem;
            border-bottom: 1px solid var(--voxora-border);
        }
        table.voxora-table th:nth-child(1) { width: 46%; }
        table.voxora-table th:nth-child(2) { width: 16%; }
        table.voxora-table th:nth-child(3) { width: 12%; }
        table.voxora-table th:nth-child(4) { width: 26%; }
        table.voxora-table td {
            padding: 0.65rem 1rem;
            border-bottom: 1px solid #F0F4FA;
            color: var(--voxora-text);
            vertical-align: top;
        }
        table.voxora-table tr:last-child td { border-bottom: none; }
        table.voxora-table tr:hover td { background: #F8FBFF; }

        /* ---- Insight card ---- */
        .voxora-insight {
            background: var(--voxora-primary-tint);
            border: 1px solid var(--voxora-border);
            border-radius: 16px;
            padding: 1.2rem 1.4rem;
            margin: 1rem 0 1.4rem 0;
        }
        .voxora-insight-title {
            font-family: 'Sora', sans-serif;
            font-weight: 600;
            color: var(--voxora-heading);
            margin-bottom: 0.3rem;
        }
        .voxora-insight-body {
            color: var(--voxora-text);
            font-size: 0.95rem;
            margin: 0;
        }

        /* ---- Empty state ---- */
        .voxora-empty {
            text-align: center;
            padding: 2.4rem 1.5rem;
            border: 1px dashed var(--voxora-border);
            border-radius: 16px;
            background: #FAFCFF;
            margin-top: 0.5rem;
        }
        .voxora-empty-title {
            font-family: 'Sora', sans-serif;
            font-weight: 600;
            font-size: 1.1rem;
            color: var(--voxora-heading);
            margin-bottom: 0.35rem;
        }
        .voxora-empty-desc {
            color: var(--voxora-text-soft);
            font-size: 0.92rem;
            margin: 0;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------- Helpers ----------------
def badge_html(label):
    label_norm = (label or "").lower()
    display = {
        "positive": "🟢 Positive",
        "negative": "🔴 Negative",
        "neutral": "🔵 Neutral",
        "error": "⚪ Error",
    }.get(label_norm, f"🔵 {label_norm.title()}" if label_norm else "—")
    css_class = {
        "positive": "badge-positive",
        "negative": "badge-negative",
        "neutral": "badge-neutral",
        "error": "badge-error",
    }.get(label_norm, "badge-neutral")
    return f'<span class="voxora-badge {css_class}">{html.escape(display)}</span>'


def render_results_table(rows):
    body_rows = []
    for r in rows:
        review_safe = html.escape(r["review"])
        theme_safe = html.escape(str(r["theme"]))
        body_rows.append(
            f"<tr><td>{review_safe}</td><td>{badge_html(r['label'])}</td>"
            f"<td>{r['score']}</td><td>{theme_safe}</td></tr>"
        )
    table_html = (
        '<div class="voxora-table-wrap"><table class="voxora-table">'
        "<thead><tr><th>Customer Review</th><th>Sentiment</th><th>Score</th><th>Theme</th></tr></thead>"
        f"<tbody>{''.join(body_rows)}</tbody></table></div>"
    )
    st.markdown(table_html, unsafe_allow_html=True)


def metric_card(col, icon, label, value):
    with col:
        st.markdown(
            f"""
            <div class="voxora-metric-card">
                <div class="voxora-metric-icon">{icon}</div>
                <div class="voxora-metric-label">{html.escape(label)}</div>
                <div class="voxora-metric-value">{html.escape(str(value))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ---------------- App ----------------
init_db()

st.markdown(
    """
    <div class="voxora-hero">
        <div class="voxora-hero-icon">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 15a3 3 0 0 0 3-3V6a3 3 0 0 0-6 0v6a3 3 0 0 0 3 3Z" stroke="white" stroke-width="1.8"/>
                <path d="M19 11v1a7 7 0 0 1-14 0v-1" stroke="white" stroke-width="1.8" stroke-linecap="round"/>
                <path d="M12 19v3" stroke="white" stroke-width="1.8" stroke-linecap="round"/>
            </svg>
        </div>
        <div>
            <p class="voxora-hero-title">Feedlyze</p>
            <p class="voxora-hero-tagline"> AI-Powered Customer Feedback Intelligence Platform<.</p>
            <p class="voxora-hero-desc">Analyze customer feedback with AI to discover sentiment, trends, and the topics that matter most.</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---- Analyze Feedback ----
st.markdown('<p class="voxora-section-title">Analyze Customer Feedback</p>', unsafe_allow_html=True)

with st.container(border=True):
    reviews_text = st.text_area(
        "Customer reviews",
        height=180,
        placeholder="Paste customer reviews here, one review per line...",
        label_visibility="collapsed",
    )
    st.caption("Enter one customer review per line.")
    analyze_clicked = st.button("Analyze Feedback", type="primary")

if analyze_clicked:
    reviews = [line.strip() for line in reviews_text.split("\n") if line.strip()]
    if not reviews:
        st.warning("Please paste at least one review.")
    else:
        results = []
        connection_error = False
        with st.spinner("Analyzing customer feedback..."):
            for review in reviews:
                try:
                    response = requests.post(API_URL, json={"text": review}, timeout=10)
                    response.raise_for_status()
                    data = response.json()
                    results.append({
                        "review": review,
                        "label": data["label"],
                        "score": data["score"],
                        "theme": data["theme"],
                    })
                except requests.exceptions.ConnectionError:
                    connection_error = True
                    break
                except Exception:
                    results.append({
                        "review": review,
                        "label": "error",
                        "score": 0,
                        "theme": "error",
                    })

        if connection_error:
            st.session_state.pop("results", None)
            st.session_state.connection_error = True
        else:
            st.session_state.results = results
            st.session_state.connection_error = False

if st.session_state.get("connection_error"):
    st.error("⚠️ Unable to connect to the analysis service. Please make sure the backend is running.")

if "results" in st.session_state:
    results = st.session_state.results

    scores = [r["score"] for r in results if r["label"] != "error"]
    positive = [r for r in results if r["label"] == "positive"]
    themes = [r["theme"] for r in results if r["theme"] != "error"]
    top_theme = Counter(themes).most_common(1)[0][0] if themes else None

    # ---- Analytics Dashboard ----
    st.markdown('<p class="voxora-section-title">Analytics Dashboard</p>', unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    metric_card(m1, "📝", "Total Reviews", len(results))
    metric_card(m2, "⭐", "Average Sentiment Score", round(sum(scores) / len(scores), 1) if scores else "—")
    metric_card(m3, "👍", "Positive Feedback", f"{round(len(positive) / len(results) * 100)}%" if results else "—")
    metric_card(m4, "🏷️", "Top Customer Theme", top_theme if top_theme else "—")

    # ---- Feedback Results ----
    st.markdown('<p class="voxora-section-title">Feedback Analysis</p>', unsafe_allow_html=True)
    render_results_table(results)

    # ---- AI Customer Insight ----
    if top_theme:
        st.markdown(
            f"""
            <div class="voxora-insight">
                <p class="voxora-insight-title">🔎 Key Customer Insight</p>
                <p class="voxora-insight-body">Customers are mainly discussing <strong>{html.escape(str(top_theme))}</strong>,
                indicating that this is currently the most important topic in customer feedback.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ---- Save Analysis ----
    if st.button("💾 Save Analysis"):
        save_results(results)
        st.success("✅ Analysis saved successfully!")

elif not st.session_state.get("connection_error"):
    # ---- Empty state ----
    st.markdown(
        """
        <div class="voxora-empty">
            <p class="voxora-empty-title">Ready to understand your customers?</p>
            <p class="voxora-empty-desc">Paste your customer reviews above and let Voxora uncover the insights.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---- Feedback History ----
with st.expander("📊 Feedback History"):
    history = load_history()
    if history:
        hist_scores = [r["score"] for r in history if r["label"] != "error"]
        hist_positive = [r for r in history if r["label"] == "positive"]

        h1, h2, h3 = st.columns(3)
        metric_card(h1, "📁", "Total Saved Reviews", len(history))
        metric_card(
            h2,
            "👍",
            "Historical Positive %",
            f"{round(len(hist_positive) / len(history) * 100)}%" if history else "—",
        )
        metric_card(
            h3,
            "⭐",
            "Historical Average Score",
            round(sum(hist_scores) / len(hist_scores), 1) if hist_scores else "—",
        )

        st.markdown("<br>", unsafe_allow_html=True)
        render_results_table(history)
    else:
        st.write("No saved reviews yet.")