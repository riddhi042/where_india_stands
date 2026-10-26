"""Where India Stands - a World Bank data explorer for research-internship portfolios.

Run:  streamlit run app.py
Data: real World Bank WDI indicators, bundled in data/panel.csv (rebuild with build_data.py).
"""
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import statsmodels.api as sm
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

st.set_page_config(page_title="Where India Stands", page_icon="📊", layout="wide")

GDP = "GDP per capita (PPP, current intl $)"
LIFE = "Life expectancy (years)"
SCHOOL = "Secondary school enrolment (% gross)"
UNEMP = "Unemployment (% of labour force)"
INFL = "Inflation, consumer prices (% annual)"
MOBILE = "Mobile subscriptions (per 100 people)"
ELEC = "Access to electricity (% of population)"
INFMORT = "Infant mortality (per 1,000 live births)"
METRICS = [GDP, LIFE, SCHOOL, UNEMP, INFL, MOBILE, ELEC, INFMORT]


@st.cache_data
def load_panel():
    return pd.read_csv("data/panel.csv")


def snapshot(panel, since=2015):
    """Most recent non-null value per country per indicator, since `since`."""
    recent = panel[panel["year"] >= since].sort_values("year")
    snap = recent.groupby("iso3")[METRICS].last()
    meta = panel.drop_duplicates("iso3").set_index("iso3")[["country", "region"]]
    return snap.join(meta).reset_index()


# ---------------------------------------------------------------------- app
FLAG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="54" height="36" viewBox="0 0 54 36" '
    'style="vertical-align:middle;margin-right:14px;border-radius:4px;box-shadow:0 0 0 1px #8884">'
    '<rect width="54" height="12" fill="#FF9933"/><rect y="12" width="54" height="12" fill="#FFFFFF"/>'
    '<rect y="24" width="54" height="12" fill="#138808"/>'
    '<circle cx="27" cy="18" r="5" fill="none" stroke="#000080" stroke-width="1"/>'
    '<circle cx="27" cy="18" r="1" fill="#000080"/></svg>'
)
st.markdown(f"<h1 style='margin:0;padding-bottom:0.3rem'>{FLAG}Where India Stands</h1>", unsafe_allow_html=True)
st.caption(
    "Where does India stand against the world on income, health, education and digital access - "
    "and what actually tracks with prosperity? Source: World Bank World Development Indicators (WDI)."
)

try:
    panel = load_panel()
except Exception as e:  # network problem etc.
    st.error(f"Could not load data: {e}")
    st.stop()

snap = snapshot(panel)
IND = "IND"
metrics = METRICS

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📈 India vs peers", "🔎 Explorer", "🧮 What predicts income?", "🧩 Country clusters", "🔮 India trend"]
)

# ---- Tab 1: trends
with tab1:
    c1, c2 = st.columns([1, 2])
    metric = c1.selectbox("Indicator", metrics, key="m1")
    has_data = panel.dropna(subset=[metric]).drop_duplicates("iso3")
    iso2name = dict(zip(has_data["iso3"], has_data["country"]))
    options = sorted(n for i, n in iso2name.items() if i != "IND")
    defaults = [iso2name[i] for i in ["CHN", "BGD", "IDN", "VNM", "BRA", "PAK"] if i in iso2name]
    peers = c1.multiselect(f"Compare with ({len(options)} countries have data)", options, default=defaults,
                           key=f"peers_{metric}")
    names = ["India"] + peers
    d = panel[panel["country"].isin(names)].dropna(subset=[metric])
    fig = px.line(d, x="year", y=metric, color="country", markers=True)
    c2.plotly_chart(fig, width="stretch")

    st.subheader("Where India ranks today")
    rows = []
    for m in metrics:
        s = snap[["iso3", m]].dropna()
        if IND in set(s["iso3"]):
            val = s.loc[s["iso3"] == IND, m].iloc[0]
            pct = (s[m] < val).mean() * 100
            rows.append({"Indicator": m, "India": round(val, 2), "Higher than % of countries": round(pct, 1), "Countries": len(s)})
    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
    st.caption("For unemployment and inflation, a lower value is generally better.")

# ---- Tab 2: explorer
with tab2:
    c1, c2, c3 = st.columns(3)
    x = c1.selectbox("X axis", metrics, index=2, key="x")
    y = c2.selectbox("Y axis", metrics, index=1, key="y")
    logx = c3.checkbox("Log X axis", value=(x == GDP))
    d = snap.dropna(subset=[x, y]).copy()
    d["is_india"] = np.where(d["iso3"] == IND, "India", "Other")
    fig = px.scatter(
        d, x=x, y=y, color="region", hover_name="country", log_x=logx,
        trendline="ols", trendline_scope="overall", opacity=0.75,
    )
    ind = d[d["iso3"] == IND]
    if len(ind):
        fig.add_trace(go.Scatter(x=ind[x], y=ind[y], mode="markers+text", text=["India"], textposition="top center",
                                 marker=dict(size=16, color="red", symbol="star"), name="India"))
    st.plotly_chart(fig, width="stretch")
    if len(d) > 10:
        corr = d[x].corr(d[y])
        st.info(f"Correlation across {len(d)} countries: **{corr:.2f}**. Correlation is not causation - "
                "richer countries differ from poorer ones in many ways at once.")

# ---- Tab 3: regression
with tab3:
    st.markdown("**Cross-country OLS:** log(GDP per capita) regressed on health, education, mobile-access and electricity indicators.")
    feats = st.multiselect("Predictors", [m for m in metrics if m != GDP],
                           default=[INFMORT, SCHOOL,
                                    MOBILE, ELEC])
    d = snap.dropna(subset=[GDP] + feats)
    if feats and len(d) > len(feats) + 10:
        X = sm.add_constant(d[feats])
        y_ = np.log(d[GDP])
        model = sm.OLS(y_, X).fit(cov_type="HC3")
        res = pd.DataFrame({
            "coef": model.params, "std err": model.bse, "p-value": model.pvalues,
            "ci_low": model.conf_int()[0], "ci_high": model.conf_int()[1],
        }).round(4)
        a, b, c = st.columns(3)
        a.metric("R²", f"{model.rsquared:.2f}")
        b.metric("Countries", int(model.nobs))
        c.metric("Robust SEs", "HC3")
        st.dataframe(res, width="stretch")
        st.caption("Reading it: a coefficient of 0.02 means +1 unit of that predictor goes with ~2% higher GDP per capita, "
                   "holding the others fixed. This describes association, not cause.")
        if IND in set(d["iso3"]):
            row = d[d["iso3"] == IND]
            pred = np.exp(model.predict(sm.add_constant(row[feats], has_constant="add"))).iloc[0]
            actual = row[GDP].iloc[0]
            st.success(f"India's actual GDP per capita: **${actual:,.0f}** vs model-predicted **${pred:,.0f}** "
                       f"({'below' if actual < pred else 'above'} what its health/education/connectivity profile would suggest).")
        d = d.assign(fitted=model.fittedvalues, resid=model.resid)
        fig = px.scatter(d, x="fitted", y="resid", hover_name="country", color="region",
                         title="Residuals (outliers = countries the model explains poorly)")
        fig.add_hline(y=0)
        st.plotly_chart(fig, width="stretch")
    else:
        st.warning("Pick at least one predictor with enough data.")

# ---- Tab 4: clustering
with tab4:
    k = st.slider("Number of clusters", 3, 7, 4)
    feats = [m for m in metrics if m not in (INFL,)]
    d = snap.dropna(subset=feats).copy()
    Z = d[feats].copy()
    Z[GDP] = np.log(Z[GDP])
    Z = StandardScaler().fit_transform(Z)
    d["cluster"] = KMeans(n_clusters=k, n_init=10, random_state=42).fit_predict(Z).astype(str)
    fig = px.scatter(d, x=GDP, y=LIFE, color="cluster", hover_name="country", log_x=True)
    st.plotly_chart(fig, width="stretch")
    if IND in set(d["iso3"]):
        cl = d.loc[d["iso3"] == IND, "cluster"].iloc[0]
        mates = d[(d["cluster"] == cl) & (d["iso3"] != IND)].sort_values(GDP)["country"].tolist()
        st.success(f"India is in cluster **{cl}** with {len(mates)} similar countries: " + ", ".join(mates[:25]) + ("..." if len(mates) > 25 else ""))
    st.dataframe(d.groupby("cluster")[feats].mean().round(1), width="stretch")

# ---- Tab 5: trend / forecast
with tab5:
    m = st.selectbox("Indicator", metrics, key="m5")
    window = st.slider("Fit trend on last N years", 5, 20, 12)
    horizon = st.slider("Project to year", 2026, 2035, 2030)
    s = panel[(panel["iso3"] == IND)][["year", m]].dropna().tail(window)
    if len(s) >= 5:
        X = sm.add_constant(s["year"])
        fit = sm.OLS(s[m], X).fit()
        fut = pd.DataFrame({"year": range(int(s["year"].min()), horizon + 1)})
        pr = fit.get_prediction(sm.add_constant(fut["year"])).summary_frame(alpha=0.05)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=s["year"], y=s[m], mode="lines+markers", name="Actual"))
        fig.add_trace(go.Scatter(x=fut["year"], y=pr["mean"], name="Linear trend", line=dict(dash="dash")))
        fig.add_trace(go.Scatter(x=list(fut["year"]) + list(fut["year"])[::-1],
                                 y=list(pr["obs_ci_upper"]) + list(pr["obs_ci_lower"])[::-1],
                                 fill="toself", line=dict(width=0), opacity=0.2, name="95% interval"))
        st.plotly_chart(fig, width="stretch")
        st.caption(f"Slope: {fit.params['year']:.3f} per year. This is a naive extrapolation, not a forecast model - "
                   "treat it as a baseline to beat.")
    else:
        st.warning("Not enough India data for this indicator.")

with st.expander("Data & limitations"):
    st.markdown(
        "- Latest non-missing value since 2015 per country, so years differ slightly across countries.\n"
        "- Cross-country regressions show association, not causation.\n"
        "- Indicator definitions: https://data.worldbank.org/indicator\n"
        "- Regions are UN sub-regions; GDP is PPP in *current* international $, so compare countries within a year rather than across decades."
    )
