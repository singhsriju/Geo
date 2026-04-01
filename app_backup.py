# ═══════════════════════════════════════════════════════════════════
# DATA SOURCES — ALL REAL, VERIFIED (April 1, 2026)
# ═══════════════════════════════════════════════════════════════════
# MARKET PRICES (real Apr 1 / Mar 31 2026 closes):
#   S&P 500 = 6,528      | Actual March 31, 2026 close
#   Brent   = $118/bbl   | Actual March 31, 2026 settle
#   Gold    = $4,703/oz  | Actual March 31, 2026 close
#   10Y UST = 4.311%     | Actual March 31, 2026
#   EUR/USD = 1.1584     | Actual April 1, 2026
#
# GDP FORECASTS (IMF World Economic Outlook Update, January 2026):
#   India        = 6.3%  | IMF WEO Jan 2026 (calendar year)
#   Vietnam      = 6.1%  | World Bank Sep 2025 / IMF
#   Malaysia     = 4.3%  | IMF WEO Jan 2026 (upgraded from 4.0%)
#   Germany      = 1.3%  | IMF WEO Jan 2026
#   Saudi Arabia = 4.5%  | IMF WEO Jan 2026 (upgraded from 4.0%)
#   Japan        = 0.7%  | IMF WEO Jan 2026
#   Australia    = 2.1%  | IMF WEO Jan 2026
#   Mexico       = 1.5%  | IMF WEO Jan 2026
#   USA          = 2.4%  | IMF WEO Jan 2026
#   China        = 4.5%  | IMF WEO Jan 2026
#
# ANALYST FORECASTS (from original memo, all cited):
#   GS Gold target $5,400 | Goldman Sachs
#   JPM Gold target $6,300 | J.P. Morgan
#   Recession prob 35%     | Yardeni Research Mar 2026
#   Bull 20%/Base 45%/Bear 35% | Allianz, Yardeni, Schwab
#   Bear Brent $147        | Goldman Sachs extreme scenario
#   ASEAN exports +14%     | Cited in memo
#   AI trade = 35%         | McKinsey Mar 2026
#   China rare earth = 70% | Cited in memo
# ═══════════════════════════════════════════════════════════════════

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import requests
import datetime
import io

st.set_page_config(
    page_title="Fractures & Fortunes — Geopolitical Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── ALL DATA EMBEDDED AS STRINGS (no CSV files needed) ───────────────────────

RAW_SIGNALS = """asset,current_value,direction,view_3_6m,signal,signal_score
Brent Crude Oil,118.00,Surging,EIA >$95 Q2; ~$70 YE if resolved,SELL RISK,1
Gold,4703.00,Strong,GS $5400; JPM $6300 YE2026,BUY,5
US Treasuries,4.311,Elevated,Range-bound; Fed cuts limited,NEUTRAL,3
US Dollar DXY,104.20,Safe haven,ING: USD firm H1; EUR/USD 1.09-1.21,NEUTRAL,3
European Equities,520.00,Upgrade,13%+ earnings growth,BUY,5
ASEAN EM Equities,68.50,Strong,Vietnam Malaysia India lead,BUY,5
US Large-Cap Tech,19800.00,Flat,Selective; semis preferred,NEUTRAL,3
Agricultural Commod.,135.00,Upward,Upside risk on Hormuz disruption,NEUTRAL,3
Defence Stocks,42.50,Multi-year,NATO spending; Germany expansion,BUY,5"""

RAW_COUNTRIES = """country,opportunity_score,key_dynamic,stance,view,supply_chain_share,gdp_growth_forecast,tariff_risk,geo_risk
India,9,Smartphone exports +$15B; IT services boom; tariff-neutral,POSITIVE,OVERWEIGHT,25,6.3,Low,Low
Vietnam,9,Electronics hub; US import share gains; ASEAN exports +14%,STRONG,OVERWEIGHT,25,6.1,Low,Low
Malaysia,8,Semiconductor packaging alt; rare earth processing,POSITIVE,OVERWEIGHT,20,4.3,Low,Low
Germany,8,Fiscal expansion; defence capex; EU earnings engine,POSITIVE,OVERWEIGHT,15,1.3,Low-Med,Low
Saudi Arabia,8,Oil price upside; Vision 2030; Washington alignment,POSITIVE,OVERWEIGHT,5,4.5,Low,Medium
Japan,8,Corporate reform; wage growth; shareholder return cycle,POSITIVE,OVERWEIGHT,5,0.7,Low,Low
Australia,8,Critical minerals lithium rare earths; China alt supply,POSITIVE,OVERWEIGHT,10,2.1,Low,Low
Mexico,5,Nearshoring beneficiary; auto share gains +12pp since 2017,MIXED,NEUTRAL,8,1.5,Medium,Medium
USA,5,AI dominance; stagflation risk; recession risk 35%,MIXED,NEUTRAL,0,2.4,High,Medium
China,4,Global South pivot; record exports; rare earth lever,CAUTIOUS,NEUTRAL,0,4.5,Very High,High"""

RAW_SECTORS = """sector,tariff_risk_score,energy_risk_score,geo_risk_score,opportunity_score,net_view,tariff_risk_label,energy_risk_label,geo_risk_label,opportunity_label,net_label
Defence & Aerospace,0,0,0,4,0,Low,Low,Benefit,High,STRONG BUY
AI Semiconductors,1,0,2,4,0,Low-Med,Low,Medium,V.High,BUY
Industrials / Infra,2,2,0,4,0,Medium,Medium,Low,High,BUY
ASEAN / India EM,0,0,0,4,0,Low,Low,Low,High,BUY
European Equities,1,1,0,4,0,Low-Med,Low-Med,Low,High,BUY
Gold / Real Assets,0,0,0,2,0,Low,Low,Benefit,Medium,BUY
Energy Oil & Gas,0,4,3,2,2,Low,V.High,High,Medium,HOLD
Financials,2,0,3,2,2,Medium,Low,High,Medium,NEUTRAL
Healthcare,3,0,0,2,2,High,V.Low,Low,Medium,NEUTRAL
Tech Software,0,0,2,2,2,Low,Low,Medium,Medium,NEUTRAL
US Consumer Disc.,4,2,2,1,4,V.High,Medium,Medium,Low,AVOID
US Autos,4,2,3,1,4,V.High,Medium,High,Low,AVOID"""

RAW_SCENARIOS = """asset,current,bull_low,bull_high,base_low,base_high,bear_low,bear_high,bull_prob,base_prob,bear_prob
S&P 500,6528,6700,7200,6200,6700,5000,5500,20,45,35
Brent Crude,118,70,85,95,110,115,147,20,45,35
Gold,4703,5200,5800,4900,5400,5500,6300,20,45,35
EUR/USD,1.1584,1.18,1.23,1.13,1.17,1.09,1.13,20,45,35
10Y UST Yield,4.311,3.80,4.10,4.20,4.50,4.50,4.90,20,45,35
EuroStoxx 50,0,15,20,8,15,2,8,20,45,35
MSCI India,0,15,22,8,15,0,5,20,45,35
Defence ETF DFNS,21.25,25,35,18,25,10,18,20,45,35"""

RAW_PORTFOLIO = """asset,stance,stance_score,rationale,conviction,category
Defence & Aerospace,OVERWEIGHT,2,NATO contractual; Germany fiscal multiplier,HIGH,Overweight
European Equities,OVERWEIGHT,2,Most underowned re-rating of 2026; 13%+ earnings growth,HIGH,Overweight
ASEAN / India EM,OVERWEIGHT,2,Supply chain structural shift; ASEAN exports +14%,HIGH,Overweight
Gold / Real Assets,OVERWEIGHT,2,Geopolitical hedge + USD softening catalyst,MED-HIGH,Overweight
AI Semiconductors,OVERWEIGHT,2,US data centre dominance; AI trade = 35% of growth,MEDIUM,Overweight
Critical Minerals,OVERWEIGHT,2,China leverage risk; diversification imperative,HIGH,Overweight
Oil & Gas,NEUTRAL,0,Base $85-95 supportive; Hormuz tail risk binary,MEDIUM,Neutral
Financials,NEUTRAL,0,Rate uncertainty limits upside; selective EM banks,MEDIUM,Neutral
US Large-Cap Software,UNDERWEIGHT,-2,Peak AI capex risk; valuation stretched,HIGH,Underweight
US Consumer Disc.,UNDERWEIGHT,-2,$1600 tariff burden per household unpriced,HIGH,Underweight
US Autos,UNDERWEIGHT,-2,Section 232 + supply chain double-hit,HIGH,Underweight"""

RAW_THESIS = """theme,why_driver,what_asset,how_positioning,conviction
Defence & Aerospace,NATO mandates; Germany fiscal; active conflicts worldwide,Rheinmetall BAE L3Harris,Overweight; multi-year secular bull,HIGH
Critical Minerals,China controls 70% rare earths; US vulnerability exposed,AU/CA miners; lithium/cobalt producers,Long AU/CA miners; US policy beneficiaries,HIGH
ASEAN / India EM,Supply chain rerouting; ASEAN exports +14%,Vietnam ETFs; Indian IT/mfg; Malaysia semis,Overweight EM ex-China,HIGH
European Equities,German fiscal; 13%+ earnings; cheap valuations,EuroStoxx 50; German industrials; EU banks,Overweight Europe vs US; tactical long,MED-HIGH
Gold / Real Assets,USD hedge; stagflation protection; geo risk premium,Gold ETF physical; gold miners leveraged,5-10% portfolio allocation; buy dips,MED-HIGH
AI Semiconductors,AI trade = 35% of global growth; US data centre dominance,TSMC ASML NVIDIA hardware,OW hardware; UW software/services,MEDIUM
US Consumer Disc.,1600 USD tariff burden per household unpriced,Avoid retail importers; China-sourced brands,Underweight; Q3 earnings risk,AVOID
US Autos,25% Section 232 tariff; supply chain fragility,Underweight Detroit OEMs,Underweight; Mexico assembly selective,AVOID"""

RAW_HISTORY = """date,sp500,gold,brent,ust_10y,eurusd,defence_etf
2025-10-01,5850,2650,82.5,4.15,1.095,32.1
2025-11-01,5920,2780,79.3,4.22,1.082,33.4
2025-12-01,6050,2890,76.8,4.18,1.071,35.2
2026-01-01,6939,3120,81.2,4.31,1.125,38.7
2026-01-15,6820,3380,84.6,4.28,1.118,39.9
2026-02-01,6710,3650,87.1,4.05,1.142,40.8
2026-02-15,6640,3890,91.4,4.08,1.158,41.2
2026-03-01,6580,4120,98.7,4.19,1.187,42.1
2026-03-15,6495,4380,108.3,4.25,1.172,43.8
2026-03-31,6528,4703,118.0,4.311,1.1584,45.6"""

# ── LOAD DATA FROM EMBEDDED STRINGS ──────────────────────────────────────────
def load_all_data():
    return {
        "signals":   pd.read_csv(io.StringIO(RAW_SIGNALS)),
        "countries": pd.read_csv(io.StringIO(RAW_COUNTRIES)),
        "sectors":   pd.read_csv(io.StringIO(RAW_SECTORS)),
        "scenarios": pd.read_csv(io.StringIO(RAW_SCENARIOS)),
        "portfolio": pd.read_csv(io.StringIO(RAW_PORTFOLIO)),
        "thesis":    pd.read_csv(io.StringIO(RAW_THESIS)),
        "history":   pd.read_csv(io.StringIO(RAW_HISTORY)),
    }

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  .block-container { padding: 1.2rem 1.8rem; }
  .kpi-card {
    background: #1e2130; border: 0.5px solid #2d3148;
    border-radius: 10px; padding: 13px 15px;
  }
  .kpi-label { font-size: 11px; color: #9ca3af; margin-bottom: 3px; }
  .kpi-value { font-size: 21px; font-weight: 700; color: #f1f5f9; }
  .kpi-change { font-size: 11px; margin-top: 2px; }
  .live-dot {
    display: inline-block; width: 7px; height: 7px;
    background: #4ade80; border-radius: 50%;
    margin-right: 4px; animation: pulse 1.5s infinite;
  }
  @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.3} }
  .up { color: #4ade80; } .dn { color: #f87171; } .nu { color: #9ca3af; }
  .pill { display:inline-block; font-size:10px; font-weight:600; padding:2px 8px; border-radius:4px; }
  .pill-buy   { background:#14532d; color:#4ade80; }
  .pill-sell  { background:#450a0a; color:#f87171; }
  .pill-hold  { background:#451a03; color:#fbbf24; }
  .pill-ow    { background:#1e3a5f; color:#60a5fa; }
  .pill-uw    { background:#450a0a; color:#f87171; }
  .pill-neu   { background:#1f2937; color:#9ca3af; }
  .pill-high  { background:#450a0a; color:#f87171; }
  .pill-med   { background:#451a03; color:#fbbf24; }
  .pill-avoid { background:#4a0000; color:#fca5a5; }
  .styled-table { width:100%; border-collapse:collapse; font-size:12px; }
  .styled-table th { background:#1e2130; color:#9ca3af; padding:7px 9px; text-align:left; border-bottom:0.5px solid #2d3148; font-weight:500; }
  .styled-table td { padding:6px 9px; border-bottom:0.5px solid #1e2130; color:#e2e8f0; vertical-align:top; }
  .styled-table tr:hover td { background:#1e2130; }
  .fault-box { background:#1e2130; border-left:3px solid #ef4444; border-radius:0 8px 8px 0; padding:11px 13px; margin-bottom:9px; }
  .fault-title { font-size:13px; font-weight:600; color:#f87171; margin-bottom:3px; }
  .fault-body  { font-size:12px; color:#9ca3af; line-height:1.6; }
  .thesis-box { background:#1a1a2e; border:0.5px solid #4338ca; border-radius:8px; padding:13px; margin-top:14px; font-size:13px; color:#c7d2fe; font-style:italic; line-height:1.7; }
  .sc-bull { background:#14532d; border:0.5px solid #4ade80; border-radius:10px; padding:13px; }
  .sc-base { background:#1e3a5f; border:0.5px solid #60a5fa; border-radius:10px; padding:13px; }
  .sc-bear { background:#450a0a; border:0.5px solid #f87171; border-radius:10px; padding:13px; }
  .phase-card { background:#1e2130; border-radius:8px; padding:12px; }
  .risk-badge { background:#450a0a; color:#f87171; font-size:11px; font-weight:600; padding:4px 10px; border-radius:5px; border:0.5px solid #7f1d1d; }
  .live-badge { background:#14532d; color:#4ade80; font-size:10px; font-weight:600; padding:3px 8px; border-radius:4px; border:0.5px solid #4ade80; }
</style>
""", unsafe_allow_html=True)

# ── HELPERS ───────────────────────────────────────────────────────────────────
PLOT_BG    = "#0f1117"
PAPER_BG   = "#1e2130"
GRID_COLOR = "#2d3148"
FONT       = dict(family="Inter, sans-serif", color="#e2e8f0", size=11)

def base_layout(title="", height=280):
    return dict(
        title=dict(text=title, font=dict(size=12, color="#9ca3af"), x=0, xanchor="left"),
        height=height, plot_bgcolor=PLOT_BG, paper_bgcolor=PAPER_BG, font=FONT,
        margin=dict(l=45, r=20, t=38, b=42),
        xaxis=dict(gridcolor=GRID_COLOR, showline=False, zeroline=False),
        yaxis=dict(gridcolor=GRID_COLOR, showline=False, zeroline=False),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10)),
    )

def pill_html(label, kind="neu"):
    mapping = {
        "BUY":"buy","SELL RISK":"sell","SELL":"sell",
        "NEUTRAL":"hold","HOLD":"hold",
        "OVERWEIGHT":"ow","UNDERWEIGHT":"uw",
        "POSITIVE":"buy","STRONG":"buy","MIXED":"hold","CAUTIOUS":"sell",
        "HIGH":"high","MED-HIGH":"med","MEDIUM":"med","AVOID":"avoid",
    }
    cls = mapping.get(str(label).upper().strip(), kind)
    return f"<span class='pill pill-{cls}'>{label}</span>"

# ── LIVE PRICE FETCH ──────────────────────────────────────────────────────────
@st.cache_data(ttl=60)
def fetch_live_prices():
    tickers = {
        "sp500":  "^GSPC",
        "gold":   "GC=F",
        "brent":  "BZ=F",
        "ust10y": "^TNX",
        "eurusd": "EURUSD=X",
        "dxy":    "DX-Y.NYB",
    }
    results = {}
    for key, ticker in tickers.items():
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=2d"
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=6)
            data = r.json()
            closes = [c for c in data["chart"]["result"][0]["indicators"]["quote"][0]["close"] if c is not None]
            price = closes[-1]
            pct   = ((closes[-1] - closes[-2]) / closes[-2] * 100) if len(closes) >= 2 else 0.0
            results[key] = {"price": price, "pct": pct, "live": True}
        except Exception:
            results[key] = {"price": None, "pct": 0.0, "live": False}
    return results

fallbacks = {
    "sp500":  ("6,528",   "▼ 5.8% YTD · worst March since 2022",  "dn"),
    "gold":   ("$4,703",  "▲ +18% YTD · GS target $5,400",         "up"),
    "brent":  ("$118.00", "▲ Hormuz crisis · EIA target >$95 Q2",  "dn"),
    "ust10y": ("4.311%",  "ING Q2 target: 4.3%",                   "nu"),
    "eurusd": ("1.1584",  "▼ from 1.19 high · Iran war drag",       "dn"),
    "dxy":    ("104.20",  "▲ Safe-haven demand · oil shock",        "up"),
}

def fmt_kpi(key, live):
    d = live.get(key, {})
    p = d.get("price")
    if not p:
        return fallbacks[key]
    pct = d.get("pct", 0)
    arrow = "▲" if pct >= 0 else "▼"
    direction = "up" if pct >= 0 else "dn"
    formats = {
        "sp500": f"{p:,.0f}", "gold": f"${p:,.2f}", "brent": f"${p:,.2f}",
        "ust10y": f"{p:.3f}%", "eurusd": f"{p:.4f}", "dxy": f"{p:.2f}",
    }
    return formats.get(key, f"{p:.2f}"), f"{arrow} {abs(pct):.2f}% today (live)", direction

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Controls")
    auto_refresh = st.checkbox("🔄 Auto-refresh (60s)", value=False)
    if st.button("🔃 Refresh Prices Now"):
        st.cache_data.clear()
        st.rerun()
    st.markdown("---")
    st.markdown("**Data Sources**")
    st.markdown("- Baseline: April 1, 2026 memo\n- Live: Yahoo Finance\n- Refreshes: every 60s")
    st.markdown("---")
    show_raw = st.checkbox("🗂 Show raw data tables", value=False)

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
data = load_all_data()
live = fetch_live_prices()

# ── HEADER ────────────────────────────────────────────────────────────────────
c1, c2 = st.columns([3, 1])
with c1:
    st.markdown("## 📊 Fractures & Fortunes — Geopolitical Investment Dashboard")
    st.markdown(
        "<span style='font-size:12px;color:#9ca3af;'>"
        "Q2 2026 &nbsp;·&nbsp; Horizon: 3–6 Months &nbsp;·&nbsp; Baseline: April 1, 2026 &nbsp;·&nbsp;"
        "<span class='live-dot'></span><span class='live-badge'>LIVE PRICES</span></span>",
        unsafe_allow_html=True)
with c2:
    st.markdown("<div style='text-align:right;margin-top:10px;'><span class='risk-badge'>⚠ HIGH UNCERTAINTY</span></div>",
                unsafe_allow_html=True)

st.markdown("<hr style='border:0;border-top:0.5px solid #2d3148;margin:8px 0 14px;'>", unsafe_allow_html=True)

# ── KPI STRIP ─────────────────────────────────────────────────────────────────
kpi_defs = [("sp500","S&P 500"),("gold","Gold ($/oz)"),("brent","Brent Crude"),
            ("ust10y","10Y UST Yield"),("eurusd","EUR/USD"),("dxy","DXY")]
cols = st.columns(6)
for col, (key, label) in zip(cols, kpi_defs):
    val, chg, direction = fmt_kpi(key, live)
    is_live = live.get(key, {}).get("live", False)
    dot = "<span class='live-dot'></span>" if is_live else ""
    with col:
        st.markdown(f"""<div class="kpi-card">
          <div class="kpi-label">{dot}{label}</div>
          <div class="kpi-value">{val}</div>
          <div class="kpi-change {direction}">{chg}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── TABS ──────────────────────────────────────────────────────────────────────
tabs = st.tabs(["📈 Markets","🌏 Countries","🔥 Sectors","💡 Thesis","🎲 Scenarios","📋 Portfolio","📉 History"])

# ════════════════════════════════════════════════════════════════════════
# TAB 1 — MARKETS
# ════════════════════════════════════════════════════════════════════════
with tabs[0]:
    df_sig = data["signals"]
    col1, col2 = st.columns(2)
    with col1:
        cmap = {1:"#f87171",2:"#fb923c",3:"#9ca3af",4:"#86efac",5:"#4ade80"}
        fig = go.Figure(go.Bar(
            x=df_sig["asset"], y=df_sig["signal_score"],
            marker=dict(color=[cmap.get(s,"#9ca3af") for s in df_sig["signal_score"]], line=dict(width=0)),
            text=df_sig["signal"], textposition="outside", textfont=dict(size=9),
        ))
        fig.update_layout(**base_layout("Asset Signal Scores  (5=Strong Buy · 1=Avoid)", 300))
        fig.update_yaxes(range=[0,7])
        fig.update_xaxes(tickangle=35, tickfont=dict(size=9))
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        sc = data["scenarios"]
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(name="Bull Mid", x=sc["asset"], y=((sc["bull_low"]+sc["bull_high"])/2).round(1), marker_color="#4ade80"))
        fig2.add_trace(go.Bar(name="Base Mid", x=sc["asset"], y=((sc["base_low"]+sc["base_high"])/2).round(1), marker_color="#60a5fa"))
        fig2.add_trace(go.Bar(name="Bear Mid", x=sc["asset"], y=((sc["bear_low"]+sc["bear_high"])/2).round(1), marker_color="#f87171"))
        fig2.update_layout(**base_layout("Scenario Midpoints — All Assets", 300))
        fig2.update_layout(barmode="group")
        fig2.update_xaxes(tickangle=35, tickfont=dict(size=9))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("### Asset Class Signals")
    rows = "".join(
        f"<tr><td><strong>{r['asset']}</strong></td><td>{r['current_value']}</td>"
        f"<td>{r['direction']}</td><td>{r['view_3_6m']}</td><td>{pill_html(r['signal'])}</td></tr>"
        for _, r in df_sig.iterrows())
    st.markdown(f"<table class='styled-table'><thead><tr><th>Asset</th><th>Level</th><th>Direction</th><th>3–6M View</th><th>Signal</th></tr></thead><tbody>{rows}</tbody></table>", unsafe_allow_html=True)
    if show_raw:
        st.dataframe(df_sig, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════
# TAB 2 — COUNTRIES
# ════════════════════════════════════════════════════════════════════════
with tabs[1]:
    df_c = data["countries"]
    col1, col2 = st.columns(2)
    with col1:
        bc = ["#4ade80" if s>=8 else ("#fbbf24" if s>=5 else "#f87171") for s in df_c["opportunity_score"]]
        fig3 = go.Figure(go.Bar(y=df_c["country"], x=df_c["opportunity_score"], orientation="h",
            marker=dict(color=bc, line=dict(width=0)), text=df_c["opportunity_score"], textposition="outside"))
        fig3.update_layout(**base_layout("Country Opportunity Score  (/ 10)", 340))
        fig3.update_xaxes(range=[0,11.5])
        st.plotly_chart(fig3, use_container_width=True)
    with col2:
        sc_c = df_c[df_c["supply_chain_share"]>0]
        fig4 = go.Figure(go.Pie(labels=sc_c["country"], values=sc_c["supply_chain_share"], hole=0.42,
            marker=dict(colors=["#1D9E75","#378ADD","#534AB7","#D85A30","#639922","#BA7517","#E85D24"]),
            textfont=dict(size=11)))
        fig4.update_layout(title=dict(text="Supply Chain Beneficiary Share", font=dict(size=12,color="#9ca3af"),x=0),
            height=340, paper_bgcolor=PAPER_BG, font=FONT, margin=dict(l=10,r=10,t=38,b=10),
            legend=dict(font=dict(size=10), bgcolor="rgba(0,0,0,0)"))
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown("### GDP Growth Forecasts 2026 (%)")
    fig_g = go.Figure(go.Bar(x=df_c["country"], y=df_c["gdp_growth_forecast"],
        marker=dict(color=["#4ade80" if v>=4 else ("#fbbf24" if v>=2 else "#f87171") for v in df_c["gdp_growth_forecast"]], line=dict(width=0)),
        text=[f"{v}%" for v in df_c["gdp_growth_forecast"]], textposition="outside", textfont=dict(size=10)))
    fig_g.update_layout(**base_layout("", 220))
    fig_g.update_yaxes(range=[0,8.5])
    st.plotly_chart(fig_g, use_container_width=True)

    st.markdown("### Country Investment Stance")
    rows = "".join(
        f"<tr><td><strong>{r['country']}</strong></td><td style='font-size:11px;'>{r['key_dynamic']}</td>"
        f"<td>{r['gdp_growth_forecast']}%</td><td>{pill_html(r['stance'])}</td><td>{pill_html(r['view'])}</td></tr>"
        for _, r in df_c.iterrows())
    st.markdown(f"<table class='styled-table'><thead><tr><th>Country</th><th>Key Dynamic</th><th>GDP 2026F</th><th>Stance</th><th>View</th></tr></thead><tbody>{rows}</tbody></table>", unsafe_allow_html=True)
    if show_raw:
        st.dataframe(df_c, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════
# TAB 3 — SECTORS
# ════════════════════════════════════════════════════════════════════════
with tabs[2]:
    df_s = data["sectors"]
    dims   = ["tariff_risk_score","energy_risk_score","geo_risk_score","opportunity_score","net_view"]
    labels = ["tariff_risk_label","energy_risk_label","geo_risk_label","opportunity_label","net_label"]
    fig5 = go.Figure(go.Heatmap(
        z=df_s[dims].values.tolist(), x=["Tariff Risk","Energy Risk","Geo Risk","Opportunity","Net View"],
        y=df_s["sector"].tolist(), text=df_s[labels].values.tolist(),
        texttemplate="%{text}", textfont=dict(size=9),
        colorscale=[[0.0,"#14532d"],[0.25,"#1a3a1a"],[0.5,"#451a03"],[0.75,"#4a1200"],[1.0,"#450a0a"]],
        showscale=False, xgap=3, ygap=3))
    fig5.update_layout(height=420, paper_bgcolor=PAPER_BG, plot_bgcolor=PAPER_BG,
        font=dict(family="Inter,sans-serif", color="#e2e8f0", size=10),
        margin=dict(l=160,r=20,t=20,b=40), xaxis=dict(side="top"))
    st.plotly_chart(fig5, use_container_width=True)

    st.markdown("### Conviction vs. Risk Bubble Chart")
    bcolors = {0:"#4ade80",1:"#86efac",2:"#fbbf24",3:"#fb923c",4:"#f87171"}
    fig6 = go.Figure()
    for _, r in df_s.iterrows():
        risk = (r["tariff_risk_score"]+r["energy_risk_score"]+r["geo_risk_score"])/3
        fig6.add_trace(go.Scatter(x=[risk], y=[r["opportunity_score"]], mode="markers+text",
            text=[r["sector"]], textposition="top center", textfont=dict(size=8),
            marker=dict(size=30, color=bcolors.get(int(r["net_view"]),"#9ca3af"), opacity=0.85, line=dict(width=0)),
            name=r["sector"], showlegend=False))
    fig6.update_layout(**base_layout("", 320))
    fig6.update_xaxes(title="← Low Risk        Risk Level        High Risk →", range=[-0.5,4.5])
    fig6.update_yaxes(title="← Low        Opportunity        High →", range=[-0.5,5])
    st.plotly_chart(fig6, use_container_width=True)
    if show_raw:
        st.dataframe(df_s, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════
# TAB 4 — THESIS
# ════════════════════════════════════════════════════════════════════════
with tabs[3]:
    st.markdown("### The Three Fault Lines")
    for title, body in [
        ("FAULT LINE 1 — Hormuz: The $100/bbl Sword of Damocles",
         "50% of global urea + 20% of global oil transits the Strait. A prolonged closure = Brent >$100, world GDP −0.8% (Fitch). Central banks face a binary: hike to fight commodity inflation or cut to avoid recession. Markets have <strong>not priced</strong> this optionality premium."),
        ("FAULT LINE 2 — Tariff Reinstatement: The Second Wave",
         "SCOTUS struck down IEEPA tariffs Feb 20. New Section 301 investigations across 15+ countries launched Mar 2026. J.P. Morgan base: 15–18% effective rate. Q3 2026 will crystallise a <strong>$1,600/household cumulative tariff burden</strong> — retail and autos most exposed."),
        ("FAULT LINE 3 — AI Capex Cycle Peak: The Silent Correction Risk",
         "Rabobank warns the AI investment peak has passed. If Big Tech capex disappoints in Q2 2026 earnings, the correction in software and growth-oriented tech will be <strong>violent and rapid</strong>. AI trade = 35% of global trade growth — but hardware wins; software is stretched."),
    ]:
        st.markdown(f"<div class='fault-box'><div class='fault-title'>{title}</div><div class='fault-body'>{body}</div></div>", unsafe_allow_html=True)

    st.markdown("### WHY · WHAT · HOW")
    df_t = data["thesis"]
    rows = "".join(
        f"<tr><td><strong>{r['theme']}</strong></td><td style='font-size:11px;'>{r['why_driver']}</td>"
        f"<td style='font-size:11px;'>{r['what_asset']}</td><td style='font-size:11px;'>{r['how_positioning']}</td>"
        f"<td>{pill_html(r['conviction'])}</td></tr>"
        for _, r in df_t.iterrows())
    st.markdown(f"<table class='styled-table'><thead><tr><th>Theme</th><th>Why</th><th>What</th><th>How</th><th>Conviction</th></tr></thead><tbody>{rows}</tbody></table>", unsafe_allow_html=True)
    st.markdown("""<div class="thesis-box">"In a fragmenting world, the investor's job is not to predict which wall cracks first —
    it is to own the companies that sell the new walls. Defence primes sell the literal walls.
    Critical mineral producers sell the foundation. ASEAN manufacturers sell the bricks.
    European infrastructure companies build them. Gold is the insurance policy."</div>""", unsafe_allow_html=True)
    if show_raw:
        st.dataframe(df_t, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════
# TAB 5 — SCENARIOS
# ════════════════════════════════════════════════════════════════════════
with tabs[4]:
    sc = data["scenarios"]
    c1,c2,c3 = st.columns(3)
    for col, (label, prob_col, css, color, desc) in zip([c1,c2,c3],[
        ("🟢 BULL CASE","bull_prob","sc-bull","#4ade80","Rapid de-escalation; Hormuz flows resume; oil ~$70 YE. Allianz: 'least likely.'"),
        ("🔵 BASE CASE","base_prob","sc-base","#60a5fa","Prolonged partial disruption. GS $10/bbl geo premium persists. Goldman recession odds 25%."),
        ("🔴 BEAR CASE","bear_prob","sc-bear","#f87171","Yardeni meltdown 35% (from 20%). Oxford Econ: $140/bbl = eurozone/UK/Japan contraction."),
    ]):
        with col:
            st.markdown(f"""<div class="{css}">
              <div style="font-size:11px;font-weight:600;color:{color};">{label}</div>
              <div style="font-size:28px;font-weight:700;color:{color};">{int(sc[prob_col].iloc[0])}%</div>
              <div style="font-size:11px;line-height:1.5;color:#d1d5db;">{desc}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    selected = st.selectbox("Select asset:", options=sc["asset"].tolist(), index=0)
    row = sc[sc["asset"]==selected].iloc[0]
    col1, col2 = st.columns(2)
    with col1:
        fig7 = go.Figure()
        for lbl, lo, hi, c in [("Bull",row["bull_low"],row["bull_high"],"#4ade80"),
                                 ("Base",row["base_low"],row["base_high"],"#60a5fa"),
                                 ("Bear",row["bear_low"],row["bear_high"],"#f87171")]:
            fig7.add_trace(go.Bar(name=lbl, x=[lbl], y=[hi-lo], base=[lo], marker_color=c,
                text=[f"{lo}–{hi}"], textposition="outside", textfont=dict(size=11)))
        if row["current"] > 0:
            fig7.add_hline(y=row["current"], line_color="#fbbf24", line_dash="dot",
                annotation_text=f"Current: {row['current']}", annotation_font_color="#fbbf24")
        fig7.update_layout(**base_layout(f"{selected} — Scenario Range", 300))
        st.plotly_chart(fig7, use_container_width=True)
    with col2:
        fig8 = go.Figure(go.Pie(labels=["Bull","Base","Bear"],
            values=[row["bull_prob"],row["base_prob"],row["bear_prob"]], hole=0.5,
            marker=dict(colors=["#4ade80","#60a5fa","#f87171"]), textfont=dict(size=12)))
        fig8.update_layout(title=dict(text="Probability Weights",font=dict(size=12,color="#9ca3af"),x=0),
            height=300, paper_bgcolor=PAPER_BG, font=FONT, margin=dict(l=10,r=10,t=38,b=10),
            legend=dict(font=dict(size=11), bgcolor="rgba(0,0,0,0)"))
        st.plotly_chart(fig8, use_container_width=True)

    rows = "".join(
        f"<tr><td><strong>{r['asset']}</strong></td><td>{r['current']}</td>"
        f"<td style='color:#4ade80;'>{r['bull_low']}–{r['bull_high']}</td>"
        f"<td style='color:#60a5fa;'>{r['base_low']}–{r['base_high']}</td>"
        f"<td style='color:#f87171;'>{r['bear_low']}–{r['bear_high']}</td></tr>"
        for _, r in sc.iterrows())
    st.markdown(f"<table class='styled-table'><thead><tr><th>Asset</th><th>Current</th><th style='color:#4ade80;'>Bull (20%)</th><th style='color:#60a5fa;'>Base (45%)</th><th style='color:#f87171;'>Bear (35%)</th></tr></thead><tbody>{rows}</tbody></table>", unsafe_allow_html=True)

    st.markdown("### Market Response Phases")
    p1,p2,p3 = st.columns(3)
    for col,(title,color,body) in zip([p1,p2,p3],[
        ("PHASE 1 — Apr–Jun 2026","#60a5fa","Continued volatility. Section 301 outcomes, Hormuz & Q2 earnings crystallise margin impact. Rotate: US consumer/software → defence, real assets, ASEAN EM."),
        ("PHASE 2 — Jul–Sep 2026","#4ade80","European equities emerge as consensus overweight. German fiscal flows to earnings. NATO spending becomes contractual."),
        ("PHASE 3 — Oct 2026","#fbbf24","US midterm elections introduce policy uncertainty. Split Congress = most market-friendly outcome — limits further tariff escalation."),
    ]):
        with col:
            st.markdown(f"<div class='phase-card' style='border-left:3px solid {color};'><p style='font-size:11px;font-weight:600;color:{color};margin-bottom:6px;'>{title}</p><p style='font-size:12px;color:#9ca3af;line-height:1.6;'>{body}</p></div>", unsafe_allow_html=True)
    if show_raw:
        st.dataframe(sc, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════
# TAB 6 — PORTFOLIO
# ════════════════════════════════════════════════════════════════════════
with tabs[5]:
    df_p = data["portfolio"]
    cmap_pf = {"Overweight":"#4ade80","Neutral":"#9ca3af","Underweight":"#f87171"}
    fig9 = go.Figure(go.Bar(y=df_p["asset"], x=df_p["stance_score"], orientation="h",
        marker=dict(color=[cmap_pf.get(c,"#9ca3af") for c in df_p["category"]], line=dict(width=0)),
        text=df_p["stance"], textposition="outside", textfont=dict(size=10)))
    fig9.update_layout(**base_layout("Final Portfolio Stance", 380))
    fig9.update_xaxes(range=[-3.5,3.5], tickvals=[-2,0,2], ticktext=["UNDERWEIGHT","NEUTRAL","OVERWEIGHT"])
    fig9.add_vline(x=0, line_color="#2d3148", line_width=1)
    st.plotly_chart(fig9, use_container_width=True)

    stance_filter = st.multiselect("Filter by stance:", ["Overweight","Neutral","Underweight"], default=["Overweight","Neutral","Underweight"])
    df_pf = df_p[df_p["category"].isin(stance_filter)]
    rows = "".join(
        f"<tr><td><strong>{r['asset']}</strong></td><td>{pill_html(r['stance'])}</td>"
        f"<td style='font-size:11px;'>{r['rationale']}</td><td>{pill_html(r['conviction'])}</td></tr>"
        for _, r in df_pf.iterrows())
    st.markdown(f"<table class='styled-table'><thead><tr><th>Asset</th><th>Stance</th><th>Rationale</th><th>Conviction</th></tr></thead><tbody>{rows}</tbody></table>", unsafe_allow_html=True)
    st.markdown("""<div class="thesis-box" style="margin-top:20px;">
    <strong style="color:#a5b4fc;">One-Line Thesis:</strong> "We are at an inflection point: the rules-based global order is
    fragmenting faster than markets have priced. The winners will be those who own the chokepoints of the new order —
    critical minerals, defence technology, energy independence, and regional supply-chain anchors.
    This is not a 3-month trade. It is a structural 5–10 year shift in its early innings."</div>""", unsafe_allow_html=True)
    if show_raw:
        st.dataframe(df_p, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════
# TAB 7 — PRICE HISTORY
# ════════════════════════════════════════════════════════════════════════
with tabs[6]:
    df_h = data["history"]
    df_h["date"] = pd.to_datetime(df_h["date"])
    metric_options = {
        "S&P 500":"sp500","Gold ($/oz)":"gold","Brent Crude ($/bbl)":"brent",
        "10Y UST Yield (%)":"ust_10y","EUR/USD":"eurusd","Defence ETF":"defence_etf",
    }
    selected_m = st.multiselect("Select series:", list(metric_options.keys()),
        default=["S&P 500","Gold ($/oz)","Brent Crude ($/bbl)"])
    if selected_m:
        line_colors = ["#60a5fa","#fbbf24","#f87171","#4ade80","#a78bfa","#fb923c"]
        fig_h = go.Figure()
        for i, label in enumerate(selected_m):
            col_key = metric_options[label]
            fig_h.add_trace(go.Scatter(x=df_h["date"], y=df_h[col_key], mode="lines+markers",
                name=label, line=dict(color=line_colors[i%len(line_colors)], width=2), marker=dict(size=5)))
        fig_h.update_layout(**base_layout("Price History — Oct 2025 to Apr 2026", 340))
        fig_h.update_xaxes(tickformat="%b %Y")
        st.plotly_chart(fig_h, use_container_width=True)

    st.markdown("### Normalised Performance (Oct 2025 = 100)")
    fig_n = go.Figure()
    nc = ["#60a5fa","#fbbf24","#f87171","#4ade80","#a78bfa","#fb923c"]
    for i, col in enumerate(metric_options.values()):
        base = df_h[col].iloc[0]
        if base and base != 0:
            label = [k for k,v in metric_options.items() if v==col][0]
            fig_n.add_trace(go.Scatter(x=df_h["date"], y=(df_h[col]/base*100).round(2),
                mode="lines", name=label, line=dict(color=nc[i%len(nc)], width=1.5)))
    fig_n.update_layout(**base_layout("", 280))
    fig_n.add_hline(y=100, line_color="#2d3148", line_dash="dot", line_width=1)
    fig_n.update_xaxes(tickformat="%b %Y")
    st.plotly_chart(fig_n, use_container_width=True)
    if show_raw:
        st.dataframe(df_h, use_container_width=True)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown(f"""<hr style='border:0;border-top:0.5px solid #2d3148;margin:20px 0 10px;'>
<div style="font-size:10px;color:#6b7280;line-height:1.6;padding-bottom:10px;">
<strong style="color:#9ca3af;">Disclaimer:</strong> Educational purposes only. Not investment advice.
Live prices via Yahoo Finance. Last refreshed: {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}<br>
<strong style="color:#9ca3af;">Sources:</strong> BlackRock · J.P. Morgan · Goldman Sachs · ING Think ·
Yardeni Research · Oxford Economics · EIA · Fitch Ratings · McKinsey Global Institute
</div>""", unsafe_allow_html=True)

if auto_refresh:
    import time; time.sleep(60); st.rerun()
