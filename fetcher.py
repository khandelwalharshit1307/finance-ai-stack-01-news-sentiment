from newsapi import NewsApiClient
from dotenv import load_dotenv
import os

load_dotenv()
api = NewsApiClient(api_key=os.getenv("NEWSAPI_KEY"))

QUERIES = {
    # Core Asset Classes
    "equities":    "stock market equities S&P earnings",
    "credit":      "credit spreads bonds high yield leveraged loans",
    "commodities": "oil gold commodities energy prices",
    "fx":          "dollar euro currency FX forex",
    "rates":       "Federal Reserve interest rates ECB central bank",

    # Sector Equities
    "tech":        "technology stocks semiconductors AI earnings Microsoft Apple",
    "energy":      "energy stocks oil gas ExxonMobil Shell BP",
    "financials":  "banks financial stocks JPMorgan Goldman Sachs earnings",
    "healthcare":  "healthcare stocks pharma biotech FDA earnings",

    # Geographies
    "us":          "US economy Federal Reserve Wall Street recession",
    "europe":      "European economy ECB eurozone Germany France",
    "asia":        "China Japan Asia economy PBOC Bank of Japan",
    "emerging":    "emerging markets Brazil India Indonesia currency",

    # Private Credit / CLOs
    "private_credit": "private credit direct lending CLO leveraged buyout covenant",
}

def fetch_headlines():
    results = {}
    for asset_class, query in QUERIES.items():
        try:
            articles = api.get_everything(
                q=query,
                language='en',
                sort_by='publishedAt',
                page_size=20
            )
            headlines = [
                {
                    "text": a['title'] + ". " + (a['description'] or ''),
                    "title": a['title'],
                    "url": a.get('url', ''),
                    "source": a.get('source', {}).get('name', '')
                }
                for a in articles['articles']
            ]
            results[asset_class] = headlines
        except Exception as e:
            print(f"Error fetching {asset_class}: {e}")
            results[asset_class] = []
    return results