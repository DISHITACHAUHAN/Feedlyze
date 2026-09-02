# 🎙️ Feedlyze

> **AI-Powered Customer Feedback Intelligence Platform**

Feedlyze transforms customer feedback into actionable business insights. Every day, businesses receive thousands of customer reviews and comments. While this data is incredibly valuable, manually analyzing it makes it difficult to identify recurring problems, understand customer sentiment, and determine the next steps. 

Feedlyze solves this using AI-powered feedback analysis to detect sentiments, uncover recurring themes, and present actionable insights through an intuitive dashboard.

---

## 🚀 Key Idea
**Customer Voice → AI Analysis → Insights → Action → Business Growth**

Feedlyze goes beyond simply classifying reviews as positive or negative. It helps businesses understand:
*   😊 **What** customers like
*   😞 **Why** customers are dissatisfied
*   🔎 **What** problems occur repeatedly
*   🏷️ **Which** topics customers discuss most
*   📊 **Overall** customer sentiment
*   💡 **What** areas to prioritize for improvement

---

## 🎯 Problem vs. Proposed Solution

### The Problem
Traditional review systems focus only on ratings or basic sentiment. Analyzing massive amounts of feedback manually is time-consuming, inconsistent, hard to scale, and difficult to translate into business decisions. *The real challenge: What are customers saying, why are they saying it, and what should the business do next?*

### The Solution
Feedlyze uses an AI-powered analysis pipeline to transform raw reviews into structured insights. 
*   **Processes:** Accepts multiple reviews and sends them to a backend analyzer.
*   **Analyzes:** Detects sentiment, generates a score, and identifies the main theme.
*   **Aggregates:** Highlights important issues and provides actionable business recommendations.
*   **Stores:** Saves analyzed feedback into a database for future reference.

---

## ✨ Features

*   📝 **Customer Feedback Analysis:** Process multiple reviews simultaneously.
*   😊 **Sentiment Analysis:** Classifies feedback into 🟢 Positive, 🔴 Negative, 🔵 Neutral, or ⚪ Error.
*   ⭐ **Sentiment Score:** Quantifies the overall customer response.
*   🏷️ **Theme Detection:** Identifies primary topics (e.g., *Product Quality, Delivery, Customer Support, Pricing*).
*   📊 **Analytics Dashboard:** Displays total reviews, sentiment averages, and top themes.
*   🤖 **AI Recommendations:** Converts feedback patterns into prioritized improvement strategies.
*   💾 **Feedback History:** Saves data to a local SQLite database for future review.
*   🎨 **Modern SaaS UI:** Clean, responsive Streamlit interface with insight cards and sentiment badges.

---

## 🏗️ System Architecture

```text
                    ┌──────────────────────┐
                    │  Customer Reviews    │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  Feedlyze Frontend   │
                    │     (Streamlit)      │
                    └──────────┬───────────┘
                               │ HTTP POST
                               ▼
                    ┌──────────────────────┐
                    │   FastAPI Backend    │
                    │      /analyzer       │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │     AI Analysis      │
                    │  • Sentiment         │
                    │  • Score             │
                    │  • Theme             │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  Structured Results  │
                    └──────────┬───────────┘
                               │
                ┌──────────────┴──────────────┐
                ▼                             ▼
       ┌─────────────────┐          ┌─────────────────┐
       │   Analytics     │          │ SQLite Database │
       │   Dashboard     │          │   (Feedback)    │
       └─────────────────┘          └─────────────────┘
                │
                ▼
       ┌─────────────────┐
       │  AI Insights &  │
       │ Recommendations │
       └─────────────────┘
