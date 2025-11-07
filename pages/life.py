# pages/life.py
from dash import html, dcc, Input, Output, State, callback
import dash
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import numpy as np

dash.register_page(__name__, path="/life", name="Life (WHO)")
px.defaults.template = "plotly"  # figures lisibles sur fond blanc

# ──────────────────────────── Data ────────────────────────────
DATA = Path("data/clean/who_life_clean.csv")
DF = pd.read_csv(DATA) if DATA.exists() else pd.DataFrame()

REQ_TEXT = ["Country", "Status"]
REQ_NUM  = ["Year", "Life expectancy", "GDP", "Schooling",
            "Adult Mortality", "Population", "Income composition of resources"]

for c in REQ_TEXT:
    if c not in DF.columns:
        DF[c] = pd.Series(dtype="object")
for c in REQ_NUM:
    if c not in DF.columns:
        DF[c] = pd.Series(dtype="float64")

for c in REQ_NUM:
    DF[c] = pd.to_numeric(DF[c], errors="coerce")

if "Year" in DF.columns:
    DF["Year"] = DF["Year"].round().astype("Int64")

DF = DF.dropna(subset=["Country", "Year", "Life expectancy"]).copy()
DF["Year"] = DF["Year"].astype(int)

# ─────────── Normalisations & indices ───────────
def minmax_norm(s: pd.Series) -> pd.Series:
    s = pd.to_numeric(s, errors="coerce")
    if s.dropna().empty:
        return pd.Series(np.nan, index=s.index)
    vmin, vmax = s.min(), s.max()
    if pd.isna(vmin) or pd.isna(vmax) or vmin == vmax:
        return pd.Series(np.nan, index=s.index)
    return (s - vmin) / (vmax - vmin)

# Globale (utile ailleurs)
DF["life_norm"]   = minmax_norm(DF["Life expectancy"])
DF["school_norm"] = minmax_norm(DF["Schooling"])
inc = pd.to_numeric(DF["Income composition of resources"], errors="coerce")
if inc.dropna().between(0, 1).mean() > 0.95:
    DF["income_norm"] = inc
else:
    DF["income_norm"] = minmax_norm(DF["GDP"])
DF["HDI_simplified"] = DF[["life_norm", "school_norm", "income_norm"]].mean(axis=1)

# Annuel (normalisation par année)
def minmax_norm_yearwise(series):
    out = pd.Series(index=series.index, dtype="float64")
    for y, idx in DF.groupby("Year").groups.items():
        s = series.loc[idx]
        if s.dropna().empty or s.min() == s.max():
            out.loc[idx] = np.nan
        else:
            out.loc[idx] = (s - s.min()) / (s.max() - s.min())
    return out

DF["life_norm_y"]   = minmax_norm_yearwise(DF["Life expectancy"])
DF["school_norm_y"] = minmax_norm_yearwise(DF["Schooling"])

income_norm_y = pd.Series(index=DF.index, dtype="float64")
for y, idx in DF.groupby("Year").groups.items():
    inc_y = pd.to_numeric(DF.loc[idx, "Income composition of resources"], errors="coerce")
    if inc_y.dropna().between(0, 1).mean() > 0.95:
        income_norm_y.loc[idx] = inc_y
    else:
        gdp_y = pd.to_numeric(DF.loc[idx, "GDP"], errors="coerce")
        if gdp_y.dropna().empty or gdp_y.min() == gdp_y.max():
            income_norm_y.loc[idx] = np.nan
        else:
            income_norm_y.loc[idx] = (gdp_y - gdp_y.min()) / (gdp_y.max() - gdp_y.min())
DF["income_norm_y"] = income_norm_y

DF["HDI_year"] = DF[["life_norm_y", "school_norm_y", "income_norm_y"]].mean(axis=1)

# ─────────── UI lists ───────────
countries_all = sorted(DF["Country"].dropna().unique().tolist())
y_min, y_max = int(DF["Year"].min()), int(DF["Year"].max())
years_all = sorted(DF["Year"].dropna().astype(int).unique().tolist())

# ─────────── Chart options ───────────
CHART_OPTIONS = [
    {"label": "📈 Tendance (Life expectancy — sélection)", "value": "trend"},
    {"label": "💸 GDP vs Life (année — sélection)",        "value": "gdp_scatter"},
    {"label": "🎓 Schooling vs Life (année — sélection)",  "value": "school_scatter"},
    {"label": "⚰️ Adult Mortality vs Life (année — sélection)", "value": "mort_scatter"},
    {"label": "📊 Histogramme Life (sélection)",           "value": "life_hist"},
    {"label": "🧩 Corrélation (sélection)",                "value": "corr_sel"},
    # Globaux
    {"label": "🌍 PIB vs Vie (global)",                    "value": "gdp_life_all"},
    {"label": "📈 Vie moyenne (global)",                   "value": "avg_life_trend"},
    {"label": "📊 Distribution Vie (global)",              "value": "life_hist_global"},
    {"label": "🧩 Corrélation (global)",                   "value": "corr_global"},
    # HDI (on garde résumé + scatter)
    {"label": "📊 HDI – résumé (moyenne + IQR)",           "value": "hdi_summary"},
    {"label": "🧭 Vie vs HDI (année)",                     "value": "hdi_scatter"},
]

# ─────────── Helpers ───────────
def style_fig(fig):
    fig.update_layout(
        paper_bgcolor="#ffffff", plot_bgcolor="#ffffff", font_color="#111827",
        margin=dict(l=10, r=10, t=50, b=10),
        legend=dict(borderwidth=0, bgcolor="rgba(255,255,255,0)"),
        hoverlabel=dict(bgcolor="#ffffff", font_color="#111827"),
    )
    fig.update_xaxes(automargin=True)
    fig.update_yaxes(automargin=True)
    return fig

def relaxed_axis_limits(x, pad=0.10):
    s = pd.to_numeric(x, errors="coerce").dropna()
    if s.empty:
        return None
    vmin, vmax = float(s.min()), float(s.max())
    if vmin == vmax:
        vmin -= 1.0; vmax += 1.0
    d = vmax - vmin
    return [vmin - d * pad, vmax + d * pad]

def corr_heatmap(df: pd.DataFrame, cols, title: str):
    cols = [c for c in cols if c in df.columns]
    if not cols:
        return style_fig(px.imshow(np.array([[np.nan]]), title=title))
    num = df[cols].apply(pd.to_numeric, errors="coerce").dropna(how="all", axis=1)
    drop_const = [c for c in num.columns if num[c].nunique(dropna=True) <= 1]
    num = num.drop(columns=drop_const, errors="ignore")
    if num.shape[1] < 2:
        return style_fig(px.imshow(np.array([[1.0]]), x=num.columns, y=num.columns, title=title, text_auto=True))
    corr = num.corr(method="pearson")
    fig = px.imshow(corr, text_auto=True, color_continuous_scale="RdBu", zmin=-1, zmax=1,
                    title=title, aspect="auto")
    return style_fig(fig)

# ─────────── Builders ───────────
def build_chart(kind, df_sel, year_single):
    # Globaux
    if kind == "gdp_life_all":
        dfa = DF.dropna(subset=["GDP", "Life expectancy"])
        fig = px.scatter(dfa, x="GDP", y="Life expectancy",
                         opacity=0.6, render_mode="webgl",
                         title="Relation entre le PIB et l'espérance de vie (global)")
        fig.update_xaxes(range=relaxed_axis_limits(dfa["GDP"]))
        fig.update_yaxes(range=relaxed_axis_limits(dfa["Life expectancy"]))
        return style_fig(fig)

    if kind == "avg_life_trend":
        ts = DF.groupby("Year", as_index=False)["Life expectancy"].mean()
        fig = px.line(ts, x="Year", y="Life expectancy", markers=True,
                      title="Évolution de l'espérance de vie moyenne dans le monde")
        return style_fig(fig)

    if kind == "life_hist_global":
        vals = DF["Life expectancy"].dropna()
        nbins = min(40, max(15, int(np.sqrt(len(vals))))) if len(vals) else 20
        fig = px.histogram(DF, x="Life expectancy", nbins=nbins,
                           title="Distribution de l'espérance de vie (global)", opacity=0.85)
        if len(vals):
            counts, bins = np.histogram(vals, bins=nbins, density=True)
            centers = (bins[:-1] + bins[1:]) / 2
            smooth = np.convolve(counts, np.ones(5)/5, mode="same")
            fig.add_trace(go.Scatter(x=centers, y=smooth, mode="lines",
                                     name="Densité (approx)", line=dict(width=2)))
        return style_fig(fig)

    if kind == "corr_global":
        cols = ["Life expectancy", "GDP", "Schooling", "Adult Mortality",
                "Population", "Income composition of resources", "HDI_simplified", "HDI_year"]
        return corr_heatmap(DF, cols, "Corrélation (global)")

    # Sélection vide
    if df_sel.empty:
        return style_fig(px.scatter(title="Aucune donnée pour ce filtre."))

    # Sélection
    if kind == "trend":
        fig = px.line(df_sel, x="Year", y="Life expectancy", color="Country",
                      markers=True, title="Évolution de l’espérance de vie (sélection)")
        return style_fig(fig)

    if kind == "gdp_scatter":
        dfa = df_sel[df_sel["Year"].astype(int) == int(year_single)]
        fig = px.scatter(dfa, x="GDP", y="Life expectancy",
                         color="Status" if "Status" in dfa.columns else None,
                         hover_name="Country", opacity=0.85, render_mode="webgl",
                         title=f"GDP ↔ Life expectancy — {int(year_single)} (sélection)")
        fig.update_xaxes(range=relaxed_axis_limits(dfa["GDP"]))
        fig.update_yaxes(range=relaxed_axis_limits(dfa["Life expectancy"]))
        return style_fig(fig)

    if kind == "school_scatter":
        dfa = df_sel[df_sel["Year"].astype(int) == int(year_single)]
        fig = px.scatter(dfa, x="Schooling", y="Life expectancy",
                         color="Status" if "Status" in dfa.columns else None,
                         hover_name="Country", opacity=0.85, render_mode="webgl",
                         title=f"Schooling ↔ Life expectancy — {int(year_single)} (sélection)")
        fig.update_xaxes(range=relaxed_axis_limits(dfa["Schooling"]))
        fig.update_yaxes(range=relaxed_axis_limits(dfa["Life expectancy"]))
        return style_fig(fig)

    if kind == "mort_scatter":
        dfa = df_sel[df_sel["Year"].astype(int) == int(year_single)]
        fig = px.scatter(dfa, x="Adult Mortality", y="Life expectancy",
                         color="Status" if "Status" in dfa.columns else None,
                         hover_name="Country", opacity=0.85, render_mode="webgl",
                         title=f"Adult Mortality ↔ Life expectancy — {int(year_single)} (sélection)")
        fig.update_xaxes(range=relaxed_axis_limits(dfa["Adult Mortality"]))
        fig.update_yaxes(range=relaxed_axis_limits(dfa["Life expectancy"]))
        return style_fig(fig)

    if kind == "life_hist":
        nbins = min(40, max(10, int(np.sqrt(len(df_sel))))) if len(df_sel) else 20
        fig = px.histogram(df_sel, x="Life expectancy", nbins=nbins,
                           title="Distribution de l'espérance de vie (sélection)")
        return style_fig(fig)

    if kind == "corr_sel":
        cols = ["Life expectancy", "GDP", "Schooling", "Adult Mortality",
                "Population", "Income composition of resources", "HDI_simplified", "HDI_year"]
        return corr_heatmap(df_sel, cols, "Corrélation (sélection)")

    # HDI — résumé (moyenne + IQR)
    if kind == "hdi_summary":
        dfa = df_sel.dropna(subset=["HDI_year"]).copy()
        if dfa.empty:
            return style_fig(px.line(title="HDI (annuel) indisponible pour cette sélection"))

        agg = (dfa.groupby("Year")["HDI_year"]
                 .agg(mean="mean",
                      p25=lambda s: np.nanpercentile(s, 25),
                      p75=lambda s: np.nanpercentile(s, 75))
                 .reset_index())

        fig = px.line(agg, x="Year", y="mean",
                      title="HDI (normalisation annuelle) — moyenne + IQR 25–75%")
        fig.add_trace(go.Scatter(
            x=agg["Year"], y=agg["p75"], mode="lines", name="P75", line=dict(width=0),
            hoverinfo="skip"
        ))
        fig.add_trace(go.Scatter(
            x=agg["Year"], y=agg["p25"], mode="lines", name="P25", line=dict(width=0),
            fill="tonexty", hoverinfo="skip"
        ))
        fig.update_yaxes(title="HDI (0–1)", range=[0, 1])
        return style_fig(fig)

    if kind == "hdi_scatter":
        dfa = df_sel[df_sel["Year"].astype(int) == int(year_single)].copy()
        dfa = dfa.dropna(subset=["HDI_year"])
        if dfa.empty:
            return style_fig(px.scatter(title=f"Pas d’IDH (annuel) pour {int(year_single)}"))
        fig = px.scatter(dfa, x="HDI_year", y="Life expectancy",
                         color="Status" if "Status" in dfa.columns else None,
                         hover_name="Country", opacity=0.85, render_mode="webgl",
                         title=f"Life expectancy ↔ HDI (normalisation annuelle) — {int(year_single)}")
        fig.update_xaxes(range=relaxed_axis_limits(dfa["HDI_year"]))
        fig.update_yaxes(range=relaxed_axis_limits(dfa["Life expectancy"]))
        return style_fig(fig)

    return style_fig(px.scatter(title="Type de graphe inconnu."))

# ─────────── Layout ───────────
def layout():
    default_countries = countries_all[:3] if len(countries_all) >= 3 else countries_all
    if "France" in countries_all and "France" not in default_countries:
        default_countries = (default_countries + ["France"])[:3]

    graph_cfg = {"displayModeBar": False, "displaylogo": False, "responsive": True}

    return html.Div([
        html.H2("🌍 WHO — Life Expectancy (Single Page)"),

        # Filtres globaux
        html.Div(className="card", children=[
            html.Div(style={"display": "grid",
                            "gridTemplateColumns": "2fr 2fr 1fr",
                            "gap": "12px"}, children=[
                dcc.Dropdown(countries_all, default_countries, id="life-countries", multi=True,
                             placeholder="Choisir des pays…"),
                dcc.RangeSlider(y_min, y_max, value=[y_min, y_max], id="life-years",
                                marks={y_min: str(y_min), y_max: str(y_max)}, step=1, allowCross=False),
                dcc.Dropdown(years_all, value=years_all[-1] if years_all else None,
                             id="life-single-year", placeholder="Année (pour certains graphes)"),
            ])
        ]),

        # KPIs (requis par le callback)
        html.Div(className="card", style={"display": "grid",
                                          "gridTemplateColumns": "repeat(3, 1fr)",
                                          "gap": "16px"}, children=[
            html.Div([html.H4("Moy. espérance de vie"), html.H1(id="life-kpi-mean", style={"margin": 0})]),
            html.Div([html.H4("Plage d'années"), html.H1(id="life-kpi-years", style={"margin": 0})]),
            html.Div([html.H4("Nb pays sélectionnés"), html.H1(id="life-kpi-countries", style={"margin": 0})]),
        ]),

        # Grille 2×2 — défauts demandés
        html.Div(style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "16px"}, children=[
            html.Div(className="card", children=[
                dcc.Dropdown(CHART_OPTIONS, value="hdi_summary", id="life-chart-a", clearable=False),
                dcc.Graph(id="life-fig-a", className="graph", style={"height": "360px"}, config=graph_cfg)
            ]),
            html.Div(className="card", children=[
                dcc.Dropdown(CHART_OPTIONS, value="avg_life_trend", id="life-chart-b", clearable=False),
                dcc.Graph(id="life-fig-b", className="graph", style={"height": "360px"}, config=graph_cfg)
            ]),
            html.Div(className="card", children=[
                dcc.Dropdown(CHART_OPTIONS, value="trend", id="life-chart-c", clearable=False),
                dcc.Graph(id="life-fig-c", className="graph", style={"height": "360px"}, config=graph_cfg)
            ]),
            html.Div(className="card", children=[
                dcc.Dropdown(CHART_OPTIONS, value="corr_global", id="life-chart-d", clearable=False),
                dcc.Graph(id="life-fig-d", className="graph", style={"height": "360px"}, config=graph_cfg)
            ]),
        ]),

        # Export
        html.Div(className="footer-actions", children=[
            html.Button("Exporter la sélection (CSV)", id="life-export-btn", className="btn"),
            dcc.Download(id="life-export-dl"),
            html.Div(id="life-note", style={"fontSize": "12px", "color": "#9ca3af"})
        ])
    ])

# ─────────── Callback principal ───────────
@callback(
    Output("life-kpi-mean", "children"),
    Output("life-kpi-years", "children"),
    Output("life-kpi-countries", "children"),
    Output("life-fig-a", "figure"),
    Output("life-fig-b", "figure"),
    Output("life-fig-c", "figure"),
    Output("life-fig-d", "figure"),
    Output("life-note", "children"),
    Input("life-countries", "value"),
    Input("life-years", "value"),
    Input("life-single-year", "value"),
    Input("life-chart-a", "value"),
    Input("life-chart-b", "value"),
    Input("life-chart-c", "value"),
    Input("life-chart-d", "value"),
)
def update_dashboard(countries, year_range, year_single, ca, cb, cc, cd):
    if DF.empty:
        empty = style_fig(px.scatter(title="⚠️ Données introuvables (who_life_clean.csv)"))
        return "—", "—", "—", empty, empty, empty, empty, "Fichier introuvable."

    if not countries:
        countries = countries_all[:3] if len(countries_all) >= 3 else countries_all
    if not year_range:
        year_range = [y_min, y_max]
    if not year_single:
        year_single = y_max

    dff = DF[(DF["Country"].isin(countries)) &
             (DF["Year"] >= int(year_range[0])) &
             (DF["Year"] <= int(year_range[1]))].copy()

    if dff.empty:
        k1, k2, k3 = "—", f"{int(year_range[0])}–{int(year_range[1])}", len(countries)
    else:
        k1 = f"{dff['Life expectancy'].mean():.1f} ans"
        k2 = f"{int(dff['Year'].min())}–{int(dff['Year'].max())}"
        k3 = len(set(dff["Country"]))

    fig_a = build_chart(ca, dff, year_single)
    fig_b = build_chart(cb, dff, year_single)
    fig_c = build_chart(cc, dff, year_single)
    fig_d = build_chart(cd, dff, year_single)

    note = f"Sélection : {k3} pays, années {k2}. " \
           f"Les graphes 'globaux' ignorent les filtres. " \
           f"HDI_year = normalisation annuelle (min–max par année). " \
           f"Corrélation = Pearson."

    return k1, k2, k3, fig_a, fig_b, fig_c, fig_d, note

# ─────────── Export CSV ───────────
@callback(
    Output("life-export-dl", "data"),
    Input("life-export-btn", "n_clicks"),
    State("life-countries", "value"),
    State("life-years", "value"),
    prevent_initial_call=True
)
def export_selection(n, countries, year_range):
    if DF.empty or not n:
        return dash.no_update
    if not countries:
        countries = countries_all
    if not year_range:
        year_range = [y_min, y_max]
    dff = DF[(DF["Country"].isin(countries)) &
             (DF["Year"] >= int(year_range[0])) &
             (DF["Year"] <= int(year_range[1]))]
    return dcc.send_data_frame(dff.to_csv, "life_selection.csv", index=False)
