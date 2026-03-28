import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
from datetime import date
from fetcher import fetch_headlines
from scorer import score_headlines
from database import save_scores, load_history, load_headlines

st.set_page_config(
    page_title="Finance Sentiment Dashboard",
    layout="wide",
    page_icon="📰"
)

# --- Groupings ---
CORE = ["equities", "credit", "commodities", "fx", "rates"]
SECTORS = ["tech", "energy", "financials", "healthcare"]
GEOS = ["us", "europe", "asia", "emerging"]
SPECIAL = ["private_credit"]

ALL_CLASSES = CORE + SECTORS + GEOS + SPECIAL

LABELS = {
    "equities": "Equities", "credit": "Credit",
    "commodities": "Commodities", "fx": "FX", "rates": "Rates",
    "tech": "Tech", "energy": "Energy",
    "financials": "Financials", "healthcare": "Healthcare",
    "us": "🇺🇸 US", "europe": "🇪🇺 Europe",
    "asia": "🌏 Asia", "emerging": "🌍 EM",
    "private_credit": "Private Credit / CLOs"
}

COLORS = {
    "equities": "#4C9BE8", "credit": "#F4A261",
    "commodities": "#2A9D8F", "fx": "#E76F51", "rates": "#A786C9",
    "tech": "#56CCF2", "energy": "#F2994A",
    "financials": "#6FCF97", "healthcare": "#EB5757",
    "us": "#2F80ED", "europe": "#9B51E0",
    "asia": "#F2C94C", "emerging": "#219653",
    "private_credit": "#BB6BD9"
}

# --- Header ---
st.title("📰 Finance AI Sentiment Dashboard")
st.caption(
    f"Last updated: {date.today()} | "
    "Module 01 of the Finance AI Stack"
)

# --- Refresh ---
if st.button("🔄 Refresh Today's Sentiment"):
    with st.spinner("Fetching headlines and scoring sentiment..."):
        all_headlines = fetch_headlines()
        scores = {}
        for ac, headlines in all_headlines.items():
            if headlines:
                score, summary, bullish, bearish = score_headlines(headlines)
            else:
                score, summary, bullish, bearish = 0.0, "No data", [], []
            scores[ac] = {
                "score": score,
                "summary": summary,
                "top_bullish": bullish,
                "top_bearish": bearish
            }
        save_scores(scores)
    st.success("Sentiment updated!")

df = load_history()
today = str(date.today())
today_df = df[df['date'] == today]

scores_dict = {}
if not today_df.empty:
    scores_dict = dict(zip(today_df['asset_class'], today_df['score']))

# ================================================================
# SECTION 1 — CORE ASSET CLASSES
# ================================================================
st.markdown("---")
st.subheader("🌐 Core Asset Classes")

if today_df.empty:
    st.info("No data yet — hit Refresh above.")
else:
    core_df = today_df[today_df['asset_class'].isin(CORE)]
    cols = st.columns(5)
    for i, ac in enumerate(CORE):
        row = core_df[core_df['asset_class'] == ac]
        if not row.empty:
            score = row['score'].values[0]
            summary = row['summary'].values[0]
            emoji = "🟢" if score > 0.1 else "🔴" if score < -0.1 else "🟡"
            cols[i].metric(
                label=f"{emoji} {LABELS[ac]}",
                value=f"{score:+.2f}",
                help=summary
            )

# ================================================================
# SECTION 2 — SECTOR EQUITIES
# ================================================================
st.markdown("---")
st.subheader("🏭 Sector Breakdown")

if not today_df.empty:
    sector_df = today_df[today_df['asset_class'].isin(SECTORS)]
    cols = st.columns(4)
    for i, ac in enumerate(SECTORS):
        row = sector_df[sector_df['asset_class'] == ac]
        if not row.empty:
            score = row['score'].values[0]
            summary = row['summary'].values[0]
            emoji = "🟢" if score > 0.1 else "🔴" if score < -0.1 else "🟡"
            cols[i].metric(
                label=f"{emoji} {LABELS[ac]}",
                value=f"{score:+.2f}",
                help=summary
            )

# ================================================================
# SECTION 3 — GEOGRAPHIES
# ================================================================
st.markdown("---")
st.subheader("🌍 Geographic Sentiment")

if not today_df.empty:
    geo_df = today_df[today_df['asset_class'].isin(GEOS)]
    cols = st.columns(4)
    for i, ac in enumerate(GEOS):
        row = geo_df[geo_df['asset_class'] == ac]
        if not row.empty:
            score = row['score'].values[0]
            summary = row['summary'].values[0]
            emoji = "🟢" if score > 0.1 else "🔴" if score < -0.1 else "🟡"
            cols[i].metric(
                label=f"{emoji} {LABELS[ac]}",
                value=f"{score:+.2f}",
                help=summary
            )

# ================================================================
# SECTION 4 — PRIVATE CREDIT / CLOs
# ================================================================
st.markdown("---")
st.subheader("🏦 Private Credit & CLOs")

if not today_df.empty:
    pc_row = today_df[today_df['asset_class'] == 'private_credit']
    if not pc_row.empty:
        score = pc_row['score'].values[0]
        summary = pc_row['summary'].values[0]
        emoji = "🟢" if score > 0.1 else "🔴" if score < -0.1 else "🟡"
        col1, col2 = st.columns([1, 3])
        col1.metric(
            label=f"{emoji} Private Credit / CLOs",
            value=f"{score:+.2f}",
            help=summary
        )
        col2.info(f"**Sentiment:** {summary}")

# ================================================================
# SECTION 5 — DIVERGENCE DETECTOR
# ================================================================
st.markdown("---")
st.subheader("⚡ Divergence Detector")

if not today_df.empty:
    divergences = []
    checked = []

    for ac1 in CORE:
        for ac2 in CORE:
            if ac1 != ac2 and (ac2, ac1) not in checked:
                s1 = scores_dict.get(ac1, 0)
                s2 = scores_dict.get(ac2, 0)
                diff = abs(s1 - s2)
                if s1 * s2 < 0 and diff > 0.3:
                    divergences.append({
                        "pair": f"{LABELS[ac1]} vs {LABELS[ac2]}",
                        "score_a": s1,
                        "score_b": s2,
                        "gap": round(diff, 2),
                        "ac1": ac1,
                        "ac2": ac2
                    })
                checked.append((ac1, ac2))

    for sector in SECTORS:
        eq_score = scores_dict.get('equities', 0)
        sec_score = scores_dict.get(sector, 0)
        diff = abs(eq_score - sec_score)
        if eq_score * sec_score < 0 and diff > 0.3:
            divergences.append({
                "pair": f"Equities vs {LABELS[sector]}",
                "score_a": eq_score,
                "score_b": sec_score,
                "gap": round(diff, 2),
                "ac1": "equities",
                "ac2": sector
            })

    if divergences:
        st.warning(f"⚠️ {len(divergences)} divergence(s) detected today")
        for d in divergences:
            a_emoji = "🟢" if d['score_a'] > 0 else "🔴"
            b_emoji = "🟢" if d['score_b'] > 0 else "🔴"
            st.write(
                f"**{d['pair']}** — "
                f"{a_emoji} {d['score_a']:+.2f} vs "
                f"{b_emoji} {d['score_b']:+.2f} "
                f"| Gap: **{d['gap']}**"
            )
            ac1 = d.get('ac1', '')
            ac2 = d.get('ac2', '')
            if ('commodities' in [ac1, ac2] and 'rates' in [ac1, ac2]):
                st.caption(
                    "↳ Commodities bullish while rates bearish "
                    "— possible inflationary pressure building"
                )
            elif ('equities' in [ac1, ac2] and 'credit' in [ac1, ac2]):
                st.caption(
                    "↳ Equity optimism not confirmed by credit "
                    "— watch for equity pullback"
                )
            elif ('equities' in [ac1, ac2] and 'rates' in [ac1, ac2]):
                st.caption(
                    "↳ Rate pessimism not priced into equities yet "
                    "— potential repricing risk"
                )
    else:
        st.success(
            "✅ No major divergences detected — "
            "asset classes broadly aligned"
        )

# ================================================================
# SECTION 6 — TOP BULLISH & BEARISH HEADLINES
# ================================================================
st.markdown("---")
st.subheader("📰 Top Headlines Today")

if not today_df.empty:
    selected = st.selectbox(
        "Select asset class to view headlines:",
        options=ALL_CLASSES,
        format_func=lambda x: LABELS.get(x, x)
    )

    hl_df = load_headlines(selected)

    if not hl_df.empty:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 🟢 Top 5 Bullish Headlines")
            bullish = json.loads(hl_df['top_bullish'].values[0])
            for h in bullish:
                score = h['score']
                st.markdown(
                    f"**+{score:.2f}** — [{h['title']}]({h['url']})  \n"
                    f"<small>{h['source']}</small>",
                    unsafe_allow_html=True
                )
                st.markdown("---")

        with col2:
            st.markdown("#### 🔴 Top 5 Bearish Headlines")
            bearish = json.loads(hl_df['top_bearish'].values[0])
            for h in bearish:
                score = h['score']
                st.markdown(
                    f"**{score:.2f}** — [{h['title']}]({h['url']})  \n"
                    f"<small>{h['source']}</small>",
                    unsafe_allow_html=True
                )
                st.markdown("---")
    else:
        st.info("Refresh to load headlines for this asset class.")

# ================================================================
# SECTION 7 — 7-DAY TREND CHART
# ================================================================
st.markdown("---")
st.subheader("📈 7-Day Sentiment Trend")

if not df.empty:
    view = st.radio(
        "View:",
        ["Core", "Sectors", "Geographies", "All"],
        horizontal=True
    )

    if view == "Core":
        chart_df = df[df['asset_class'].isin(CORE)]
    elif view == "Sectors":
        chart_df = df[df['asset_class'].isin(SECTORS)]
    elif view == "Geographies":
        chart_df = df[df['asset_class'].isin(GEOS)]
    else:
        chart_df = df

    fig = px.line(
        chart_df,
        x='date',
        y='score',
        color='asset_class',
        markers=True,
        color_discrete_map=COLORS,
        labels={
            'score': 'Sentiment Score',
            'asset_class': 'Asset Class'
        }
    )
    fig.add_hline(
        y=0,
        line_dash="dash",
        line_color="white",
        opacity=0.3,
        annotation_text="Neutral"
    )
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        yaxis_title="Score (-1 bearish → +1 bullish)",
        xaxis_title="",
        legend_title="Asset Class"
    )
    st.plotly_chart(fig, use_container_width=True)

# ================================================================
# SECTION 8 — REGIME SIGNAL
# ================================================================
st.markdown("---")
st.subheader("📡 Regime Signal")

if not today_df.empty:
    core_today = today_df[today_df['asset_class'].isin(CORE)]
    avg = core_today['score'].mean()
    commodity_score = scores_dict.get('commodities', 0)
    credit_score = scores_dict.get('credit', 0)
    rates_score = scores_dict.get('rates', 0)

    col1, col2 = st.columns([1, 2])

    with col1:
        if avg > 0.15:
            st.success("🟢 RISK ON")
        elif avg < -0.15:
            st.error("🔴 RISK OFF")
        else:
            st.warning("🟡 MIXED")

    with col2:
        if avg > 0.15:
            st.write(
                "Broad positive sentiment across asset classes. "
                "Growth assets favoured. Risk appetite intact."
            )
        elif avg < -0.15:
            st.write(
                "Broad negative sentiment. Defensives, gold, and "
                "cash historically outperform in this regime."
            )
        elif commodity_score > 0.2 and rates_score < -0.1:
            st.write(
                "Commodity strength + rate pessimism = "
                "potential stagflation signal. "
                "Watch energy and real assets."
            )
        elif credit_score < -0.2 and avg > 0:
            st.write(
                "Equities positive but credit cracking — "
                "this divergence historically precedes "
                "equity weakness. Worth monitoring closely."
            )
        else:
            st.write(
                "Mixed signals across asset classes. "
                "No dominant regime. Stay diversified "
                "and watch for a catalyst."
            )

# ================================================================
# SECTION 9 — SECTOR VS BROAD EQUITY COMPARISON
# ================================================================
st.markdown("---")
st.subheader("🏭 Sector vs Broad Equity Comparison")

if not today_df.empty:
    sector_compare = []
    broad_equity = scores_dict.get('equities', 0)

    for ac in SECTORS:
        sec_score = scores_dict.get(ac, None)
        if sec_score is not None:
            sector_compare.append({
                "Sector": LABELS[ac],
                "Score": sec_score,
                "vs Broad Equity": round(sec_score - broad_equity, 3),
                "Type": "Sector"
            })

    sector_compare.append({
        "Sector": "📊 Broad Equity",
        "Score": broad_equity,
        "vs Broad Equity": 0,
        "Type": "Benchmark"
    })

    compare_df = pd.DataFrame(sector_compare)
    compare_df = compare_df.sort_values("Score", ascending=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### Sentiment Scores")
        fig_bar = px.bar(
            compare_df,
            x="Score",
            y="Sector",
            orientation='h',
            color="Score",
            color_continuous_scale=[
                "#E76F51", "#F4A261",
                "#E9C46A", "#2A9D8F", "#4C9BE8"
            ],
            range_color=[-1, 1],
            text="Score"
        )
        fig_bar.update_traces(
            texttemplate='%{text:+.2f}',
            textposition='outside'
        )
        fig_bar.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            coloraxis_showscale=False,
            xaxis=dict(range=[-1, 1], title=""),
            yaxis_title="",
            margin=dict(l=10, r=10, t=10, b=10)
        )
        fig_bar.add_vline(
            x=0,
            line_dash="dash",
            line_color="white",
            opacity=0.4
        )
        fig_bar.add_vline(
            x=broad_equity,
            line_dash="dot",
            line_color="#4C9BE8",
            opacity=0.8,
            annotation_text="Broad Equity",
            annotation_position="top"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        st.markdown("##### Relative to Broad Equity")
        rel_df = compare_df[compare_df['Type'] == 'Sector'].copy()
        rel_df = rel_df.sort_values("vs Broad Equity", ascending=True)

        fig_rel = px.bar(
            rel_df,
            x="vs Broad Equity",
            y="Sector",
            orientation='h',
            color="vs Broad Equity",
            color_continuous_scale=[
                "#E76F51", "#E9C46A", "#2A9D8F"
            ],
            range_color=[-0.5, 0.5],
            text="vs Broad Equity"
        )
        fig_rel.update_traces(
            texttemplate='%{text:+.3f}',
            textposition='outside'
        )
        fig_rel.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            coloraxis_showscale=False,
            xaxis=dict(title="Difference from Broad Equity"),
            yaxis_title="",
            margin=dict(l=10, r=10, t=10, b=10)
        )
        fig_rel.add_vline(
            x=0,
            line_dash="dash",
            line_color="white",
            opacity=0.4,
            annotation_text="In line with market",
            annotation_position="top"
        )
        st.plotly_chart(fig_rel, use_container_width=True)

    if not rel_df.empty:
        top_sector = rel_df.iloc[-1]
        bot_sector = rel_df.iloc[0]
        st.info(
            f"**Leading:** {top_sector['Sector']} is "
            f"{abs(top_sector['vs Broad Equity']):.2f} points "
            f"{'above' if top_sector['vs Broad Equity'] > 0 else 'below'} "
            f"broad equity sentiment.   "
            f"**Lagging:** {bot_sector['Sector']} is "
            f"{abs(bot_sector['vs Broad Equity']):.2f} points "
            f"{'below' if bot_sector['vs Broad Equity'] < 0 else 'above'} "
            f"broad equity sentiment."
        )

# ================================================================
# SECTION 10 — CROSS-ASSET CORRELATION MATRIX
# ================================================================
st.markdown("---")
st.subheader("🔗 Cross-Asset Sentiment Correlation")

if not df.empty and len(df['date'].unique()) >= 3:
    pivot = df.pivot_table(
        index='date',
        columns='asset_class',
        values='score'
    )
    pivot = pivot.dropna(axis=1, thresh=3)

    if pivot.shape[1] >= 2:
        corr = pivot.corr()
        corr.index = [LABELS.get(c, c) for c in corr.index]
        corr.columns = [LABELS.get(c, c) for c in corr.columns]

        fig_corr = go.Figure(data=go.Heatmap(
            z=corr.values,
            x=corr.columns.tolist(),
            y=corr.index.tolist(),
            colorscale=[
                [0.0, "#E76F51"],
                [0.5, "#1a1a2e"],
                [1.0, "#4C9BE8"]
            ],
            zmin=-1,
            zmax=1,
            text=corr.round(2).values,
            texttemplate="%{text}",
            textfont={"size": 11},
            hoverongaps=False
        ))
        fig_corr.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=10, r=10, t=10, b=10),
            height=500,
            xaxis=dict(tickangle=-45)
        )
        st.plotly_chart(fig_corr, use_container_width=True)

        st.markdown("##### 🔍 What This Shows")
        col1, col2 = st.columns(2)

        corr_pairs = []
        cols_list = corr.columns.tolist()
        for i in range(len(cols_list)):
            for j in range(i+1, len(cols_list)):
                val = corr.iloc[i, j]
                corr_pairs.append({
                    "Pair": f"{cols_list[i]} & {cols_list[j]}",
                    "Correlation": round(val, 2)
                })

        pairs_df = pd.DataFrame(corr_pairs).sort_values(
            "Correlation", ascending=False
        )

        with col1:
            st.markdown("**Highest (moving together)**")
            st.dataframe(
                pairs_df.head(5),
                hide_index=True,
                use_container_width=True
            )

        with col2:
            st.markdown("**Lowest (diverging)**")
            st.dataframe(
                pairs_df.tail(5).sort_values("Correlation"),
                hide_index=True,
                use_container_width=True
            )

        st.caption(
            "1.0 = always move together | "
            "-1.0 = always opposite | "
            "0 = no relationship | "
            "Based on all available historical data."
        )
else:
    st.info(
        "Correlation matrix appears after 3+ days of data. "
        "Run the dashboard daily to build history."
    )

# ================================================================
# SECTION 9B — GEOGRAPHY VS GLOBAL AVERAGE COMPARISON
# ================================================================
st.markdown("---")
st.subheader("🌍 Geography vs Global Sentiment Comparison")

if not today_df.empty:
    geo_compare = []
    global_avg = today_df['score'].mean()

    for ac in GEOS:
        geo_score = scores_dict.get(ac, None)
        if geo_score is not None:
            geo_compare.append({
                "Region": LABELS[ac],
                "Score": geo_score,
                "vs Global Avg": round(geo_score - global_avg, 3),
                "Type": "Region"
            })

    geo_compare.append({
        "Region": "🌐 Global Average",
        "Score": global_avg,
        "vs Global Avg": 0,
        "Type": "Benchmark"
    })

    geo_df_chart = pd.DataFrame(geo_compare)
    geo_df_chart = geo_df_chart.sort_values("Score", ascending=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### Sentiment Scores by Region")
        fig_geo = px.bar(
            geo_df_chart,
            x="Score",
            y="Region",
            orientation='h',
            color="Score",
            color_continuous_scale=[
                "#E76F51", "#F4A261",
                "#E9C46A", "#2A9D8F", "#4C9BE8"
            ],
            range_color=[-1, 1],
            text="Score"
        )
        fig_geo.update_traces(
            texttemplate='%{text:+.2f}',
            textposition='outside'
        )
        fig_geo.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            coloraxis_showscale=False,
            xaxis=dict(range=[-1, 1], title=""),
            yaxis_title="",
            margin=dict(l=10, r=10, t=10, b=10)
        )
        fig_geo.add_vline(
            x=0,
            line_dash="dash",
            line_color="white",
            opacity=0.4
        )
        fig_geo.add_vline(
            x=global_avg,
            line_dash="dot",
            line_color="#4C9BE8",
            opacity=0.8,
            annotation_text="Global Avg",
            annotation_position="top"
        )
        st.plotly_chart(fig_geo, use_container_width=True)

    with col2:
        st.markdown("##### Relative to Global Average")
        rel_geo_df = geo_df_chart[
            geo_df_chart['Type'] == 'Region'
        ].copy()
        rel_geo_df = rel_geo_df.sort_values(
            "vs Global Avg", ascending=True
        )

        fig_geo_rel = px.bar(
            rel_geo_df,
            x="vs Global Avg",
            y="Region",
            orientation='h',
            color="vs Global Avg",
            color_continuous_scale=[
                "#E76F51", "#E9C46A", "#2A9D8F"
            ],
            range_color=[-0.5, 0.5],
            text="vs Global Avg"
        )
        fig_geo_rel.update_traces(
            texttemplate='%{text:+.3f}',
            textposition='outside'
        )
        fig_geo_rel.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            coloraxis_showscale=False,
            xaxis=dict(title="Difference from Global Average"),
            yaxis_title="",
            margin=dict(l=10, r=10, t=10, b=10)
        )
        fig_geo_rel.add_vline(
            x=0,
            line_dash="dash",
            line_color="white",
            opacity=0.4,
            annotation_text="In line with global",
            annotation_position="top"
        )
        st.plotly_chart(fig_geo_rel, use_container_width=True)

    if not rel_geo_df.empty:
        top_geo = rel_geo_df.iloc[-1]
        bot_geo = rel_geo_df.iloc[0]
        st.info(
            f"**Most Optimistic:** {top_geo['Region']} is "
            f"{abs(top_geo['vs Global Avg']):.2f} points "
            f"{'above' if top_geo['vs Global Avg'] > 0 else 'below'} "
            f"global average sentiment.   "
            f"**Most Pessimistic:** {bot_geo['Region']} is "
            f"{abs(bot_geo['vs Global Avg']):.2f} points "
            f"{'below' if bot_geo['vs Global Avg'] < 0 else 'above'} "
            f"global average sentiment."
        )
# ================================================================
# FOOTER
# ================================================================
st.markdown("---")
st.caption(
    "Finance AI Stack | Module 01 | "
    "Built with FinBERT + NewsAPI + Streamlit | "
    "https://github.com/khandelwalharshit1307/finance-ai-stack-01-news-sentiment"
)
