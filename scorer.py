from transformers import pipeline

scorer = pipeline(
    "sentiment-analysis",
    model="ProsusAI/finbert"
)

def score_headlines(headlines):
    if not headlines:
        return 0.0, "No headlines available", [], []

    texts = [h['text'] for h in headlines]
    results = scorer(texts, truncation=True, max_length=512)

    scored = []
    for headline, result in zip(headlines, results):
        if result['label'] == 'positive':
            s = result['score']
        elif result['label'] == 'negative':
            s = -result['score']
        else:
            s = 0
        scored.append({
            "title":  headline['title'],
            "url":    headline['url'],
            "source": headline['source'],
            "score":  round(s, 4)
        })

    scores_only = [h['score'] for h in scored]
    avg_score = sum(scores_only) / len(scores_only)

    # Sort for top bullish and bearish
    sorted_scored = sorted(scored, key=lambda x: x['score'], reverse=True)
    top_bullish = sorted_scored[:5]
    top_bearish = sorted_scored[-5:][::-1]

    if avg_score > 0.3:
        summary = "Strongly bullish sentiment dominating headlines"
    elif avg_score > 0.1:
        summary = "Mildly positive tone across recent news"
    elif avg_score < -0.3:
        summary = "Strongly bearish sentiment in recent coverage"
    elif avg_score < -0.1:
        summary = "Cautious or negative tone emerging"
    else:
        summary = "Mixed signals — no clear directional bias"

    return round(avg_score, 4), summary, top_bullish, top_bearish