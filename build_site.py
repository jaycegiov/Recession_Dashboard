import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# 1. DATA LOADING
SCRIPT_DIR = Path(__file__).parent.absolute()
df = pd.read_csv(SCRIPT_DIR / 'recession_data.csv', index_col=0)
df.index = pd.to_datetime(df.index)

latest_date = df.index[-1]
curr_y2 = df.iloc[-1]['10Y_2Y_Spread']
curr_y3 = df.iloc[-1]['10Y_3M_Spread']
curr_s = df.iloc[-1]['Sahm_Rule']

# 2. RISK LOGIC
score = 0
if curr_y2 < 0.7: score += 20 
if curr_s >= 0.3: score += 30
if curr_s >= 0.5: score += 50

color = "#f39c12" if score >= 30 else "#2ecc71"
if score >= 70: color = "#e74c3c"
status = "HIGH RISK" if score >= 70 else ("CAUTION" if score >= 30 else "STABLE")

# 3. INTERACTIVE CHART
fig = go.Figure()

# Clean Inversion Line (No comment text as requested)
fig.add_hline(y=0, line_dash="dash", line_color="#7f8c8d", line_width=1)

# Recession Shading
if 'USREC' in df.columns:
    start_date = None
    for i in range(len(df)):
        if df['USREC'].iloc[i] == 1 and start_date is None:
            start_date = df.index[i]
        elif df['USREC'].iloc[i] == 0 and start_date is not None:
            fig.add_vrect(x0=start_date, x1=df.index[i], fillcolor="grey", opacity=0.2, line_width=0)
            start_date = None

fig.add_trace(go.Scatter(x=df.index, y=df['10Y_2Y_Spread'], name="10Y-2Y Spread", line=dict(color='#2980b9', width=2.5)))
fig.add_trace(go.Scatter(x=df.index, y=df['10Y_3M_Spread'], name="10Y-3M Spread", line=dict(color='#16a085', width=2.5)))
fig.add_trace(go.Scatter(x=df.index, y=df['Sahm_Rule'], name="Sahm Rule", line=dict(color='#c0392b', width=3, dash='dot')))

fig.update_layout(
    updatemenus=[dict(type="buttons", direction="right", active=0, x=0.5, y=1.15, xanchor="center",
        buttons=list([
            dict(label="Show All", method="update", args=[{"visible": [True, True, True]}]),
            dict(label="10Y-2Y", method="update", args=[{"visible": [True, False, False]}]),
            dict(label="10Y-3M", method="update", args=[{"visible": [False, True, False]}]),
            dict(label="Sahm Rule", method="update", args=[{"visible": [False, False, True]}]),
        ]))],
    template='plotly_white', height=550, margin=dict(l=20, r=20, t=100, b=20),
    legend=dict(orientation="h", y=1.05, x=0.5, xanchor="center")
)

# 4. HTML TEMPLATE
html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Recession Watch Dashboard</title>
    <style>
        body {{ 
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; 
            background-color: #f4f7f6; 
            background-image: radial-gradient(#d1d1d1 1px, transparent 1px); 
            background-size: 40px 40px;
            color: #333; margin: 0; padding: 0; 
        }}
        .top-hero {{ background: #ffffff; padding: 30px; border-bottom: 1px solid #ddd; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }}
        .content-container {{ max-width: 1000px; margin: 40px auto; padding: 0 20px; }}
        .info-window {{
            background: #2c3e50; color: #ecf0f1; padding: 40px; border-radius: 20px; 
            box-shadow: 0 15px 35px rgba(0,0,0,0.2); margin-bottom: 40px;
        }}
        .status-badge {{ display: inline-block; padding: 5px 15px; border-radius: 4px; background: {color}; color: white; font-weight: bold; }}
        .score-display {{ font-size: 64px; font-weight: 900; margin: 10px 0; }}
        h2 {{ border-bottom: 2px solid {color}; padding-bottom: 10px; margin-top: 40px; color: #fff; font-size: 1.8em; }}
        .explanation-text {{ line-height: 1.6; margin-bottom: 1.5em; color: #bdc3c7; font-size: 1.05em; text-align: justify; }}
        strong {{ color: white; }}
        
        /* Range Table Styling */
        .range-table {{ width: 100%; margin-top: 15px; border-collapse: collapse; font-size: 0.9em; background: rgba(0,0,0,0.2); border-radius: 8px; overflow: hidden; }}
        .range-table td {{ padding: 10px; border-bottom: 1px solid rgba(255,255,255,0.05); }}
        .range-tag {{ font-weight: bold; padding: 2px 8px; border-radius: 4px; font-size: 0.8em; }}
        .tag-healthy {{ background: #2ecc71; color: white; }}
        .tag-caution {{ background: #f39c12; color: white; }}
        .tag-danger {{ background: #e74c3c; color: white; }}
        
        .source-link {{ color: {color}; font-size: 0.85em; text-decoration: none; display: block; margin-top: 15px; font-weight: bold; }}
    </style>
</head>
<body>

    <div class="top-hero">
        <div style="max-width: 1100px; margin: auto;">
            <div class="status-badge">{status}</div>
            <div class="score-display">{score}% <small style="font-size: 18px; color: #7f8c8d;">Risk Probability</small></div>
            {fig.to_html(full_html=False, include_plotlyjs='cdn')}
        </div>
    </div>

    <div class="content-container">
        <div class="info-window">
            
            <h2>Yield Curve Analysis</h2>
            
            <p class="explanation-text">
                <strong>1. The 10-Year vs. 2-Year Treasury Spread (10Y-2Y):</strong><br>
                Historically regarded as the "Gold Standard" of recession forecasting, the 10Y-2Y spread represents the difference in yield between long-term and short-term US Treasury bonds. Currently at <strong>{curr_y2:.2f}%</strong>.
                <table class="range-table">
                    <tr><td>> 0.50%</td><td><span class="range-tag tag-healthy">HEALTHY</span> Standard expansionary environment.</td></tr>
                    <tr><td>0.00% to 0.50%</td><td><span class="range-tag tag-caution">CAUTION</span> Flattening curve; signaling late-cycle growth.</td></tr>
                    <tr><td>< 0.00%</td><td><span class="range-tag tag-danger">RECESSION SIGNAL</span> Inverted curve; credit crunch probable.</td></tr>
                </table>
                <a href="https://www.stlouisfed.org/on-the-economy/2023/october/understanding-the-yield-curve-inversion" class="source-link">Source: St. Louis FED</a>
            </p>

            <p class="explanation-text">
                <strong>2. The 10-Year vs. 3-Month Treasury Spread (10Y-3M):</strong><br>
                The Federal Reserve's preferred metric. It reflects the cost of immediate liquidity relative to long-term growth. Currently at <strong>{curr_y3:.2f}%</strong>.
                <table class="range-table">
                    <tr><td>> 1.00%</td><td><span class="range-tag tag-healthy">HEALTHY</span> Strong liquidity and growth expectations.</td></tr>
                    <tr><td>0.00% to 1.00%</td><td><span class="range-tag tag-caution">CAUTION</span> Policy tightening beginning to restrict growth.</td></tr>
                    <tr><td>< 0.00%</td><td><span class="range-tag tag-danger">RECESSION SIGNAL</span> Restrictive policy likely leading to a hard landing.</td></tr>
                </table>
                <a href="https://www.newyorkfed.org/research/capital_markets/yc_index.html" class="source-link">Source: New York FED</a>
            </p>

            <h2>Labor & Sentiment Indicators</h2>

            <p class="explanation-text">
                <strong>3. The Sahm Rule Recession Indicator:</strong><br>
                This indicator identifies the "real economy" momentum. It triggers when unemployment rises 0.5% above its 12-month low. Currently at <strong>{curr_s:.2f}%</strong>.
                <table class="range-table">
                    <tr><td>< 0.35%</td><td><span class="range-tag tag-healthy">HEALTHY</span> Strong labor market stability.</td></tr>
                    <tr><td>0.35% to 0.49%</td><td><span class="range-tag tag-caution">CAUTION</span> Early warning; labor market starting to crack.</td></tr>
                    <tr><td>> 0.50%</td><td><span class="range-tag tag-danger">RECESSION SIGNAL</span> Negative feedback loop underway.</td></tr>
                </table>
                <a href="https://fred.stlouisfed.org/series/SAHMREALTIME" class="source-link">Source: FRED Economic Data</a>
            </p>

            <p class="explanation-text">
                <strong>4. Cass Freight Index (Shipments):</strong><br>
                Measures the physical movement of goods. Useful as a "truth serum" for the industrial cycle vs the financial economy.
                <table class="range-table">
                    <tr><td>> 2.0% YoY</td><td><span class="range-tag tag-healthy">HEALTHY</span> Robust physical demand and logistics.</td></tr>
                    <tr><td>-2.0% to 2.0% YoY</td><td><span class="range-tag tag-caution">CAUTION</span> Stagnating demand; Industrial slowdown.</td></tr>
                    <tr><td>< -2.0% YoY</td><td><span class="range-tag tag-danger">RECESSION SIGNAL</span> Contraction in physical goods movement.</td></tr>
                </table>
                <a href="https://www.cassinfo.com/freight-audit-payment/cass-transportation-indexes" class="source-link">Source: Cass Information Systems</a>
            </p>

            <p class="explanation-text">
                <strong>5. The "R-Word" Index:</strong><br>
                Tracks "Reflexivity"—where the fear of a recession leads to pre-emptive saving and a self-fulfilling prophecy.
                <table class="range-table">
                    <tr><td>Low Mentions</td><td><span class="range-tag tag-healthy">HEALTHY</span> High consumer and business confidence.</td></tr>
                    <tr><td>Rising Mentions</td><td><span class="range-tag tag-caution">CAUTION</span> Behavioral shift toward defensive spending.</td></tr>
                    <tr><td>Spiking Mentions</td><td><span class="range-tag tag-danger">RECESSION SIGNAL</span> Fear-driven demand collapse is imminent.</td></tr>
                </table>
                <a href="https://www.economist.com/graphic-detail/2022/07/07/our-r-word-index-suggests-that-america-may-be-heading-for-recession" class="source-link">Source: The Economist</a>
            </p>

        </div>
        <div style="height: 50px;"></div>
    </div>

</body>
</html>
"""

with open(SCRIPT_DIR / "final_site.html", "w") as f:
    f.write(html_template)

print("Dashboard Updated with Range Tables and Clean Zero Line!")