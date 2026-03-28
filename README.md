# 📰 Finance AI Sentiment Dashboard
### Module 01 of Finance × AI

A real-time financial news sentiment dashboard that reads 100+ 
headlines across 13 asset classes daily and quantifies market mood 
— automatically, in 30 seconds.

## What It Covers
🌐 Core: Equities, Credit, Commodities, FX, Rates
🏭 Sectors: Tech, Energy, Financials, Healthcare
🌍 Regions: US, Europe, Asia, Emerging Markets
🏦 Private Credit & CLOs

## Features
- FinBERT sentiment scoring (financial NLP model)
- Divergence detector
- Top 5 bullish and bearish headlines per asset class
- 7-day sentiment trend
- Sector vs broad equity comparison
- Geography vs global average comparison
- Regime signal: Risk On / Risk Off / Mixed

## How It Works
1. Fetches headlines via NewsAPI
2. Scores with FinBERT (-1 bearish → +1 bullish)
3. Stores daily in SQLite
4. Visualises in Streamlit

## Tech Stack
Python | FinBERT | NewsAPI | Streamlit | Plotly | SQLite

## Run Locally
pip install -r requirements.txt
streamlit run dashboard.py

## Live Demo
[Streamlit link]

## Part of Finance × AI
Module 01 of a weekly open-source series applying AI 
to real finance workflows.

## About
Harshit Khandelwal — MiM at ESSEC Business School, 
Leveraged Loans Analyst at BNP Paribas AM
[LinkedIn](your linkedin url)
