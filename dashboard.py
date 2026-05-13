import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(
    page_title="營銷目標管理 Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700&display=swap');

:root {
    --app-font: clamp(12px, 0.82vw, 16px);
    --title-font: clamp(24px, 1.7vw, 34px);
    --section-font: clamp(15px, 1vw, 20px);
    --metric-font: clamp(24px, 1.6vw, 34px);
}

.stApp {
    background-color: #0d1117;
    color: #e0e0e0;
    font-family: 'Noto Sans TC', sans-serif;
}

.block-container {
    max-width: 1680px;
    padding-top: 2.2rem;
    padding-left: clamp(1rem, 2.5vw, 3rem);
    padding-right: clamp(1rem, 2.5vw, 3rem);
}

[data-testid="stSidebar"] {
    background-color: #161b27;
    border-right: 1px solid #252d3d;
}

[data-testid="stSidebar"] * {
    color: #c9d1e0 !important;
}

.main-title {
    font-size: var(--title-font);
    font-weight: 700;
    color: #f3f6fb;
    letter-spacing: 0;
    margin: 0 0 0.6rem 0;
}

.page-subtitle {
    color: #8899aa;
    font-size: var(--app-font);
    margin-bottom: 1.2rem;
}

.section-title {
    font-size: var(--section-font);
    font-weight: 700;
    color: #e0e0e0;
    margin: 0.25rem 0 0.5rem 0;
    letter-spacing: 0;
}

hr {
    border-color: #252d3d !important;
    margin: 1.25rem 0 !important;
}

[data-testid="metric-container"] {
    background: linear-gradient(135deg, #161b27 0%, #1c2336 100%);
    border: 1px solid #252d3d;
    border-radius: 8px;
    padding: clamp(12px, 1vw, 18px) clamp(14px, 1.2vw, 22px);
    box-shadow: 0 4px 18px rgba(0,0,0,0.32);
}

[data-testid="stMetricValue"] {
    font-size: var(--metric-font) !important;
    font-weight: 700;
}

[data-testid="stMetricLabel"] {
    font-size: clamp(12px, 0.78vw, 15px) !important;
}

[data-testid="stMetricDelta"] {
    font-size: clamp(11px, 0.72vw, 14px) !important;
}

.chart-wrap {
    border-top: 1px solid #252d3d;
    padding-top: 1rem;
}

[data-testid="stPlotlyChart"] {
    width: 100% !important;
    min-width: 0 !important;
}

[data-testid="stDataFrame"] {
    width: 100% !important;
}

@media (max-width: 900px) {
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }
}
</style>
""", unsafe_allow_html=True)


def inject_plotly_resizer():
    components.html("""
<script>
(function () {
    const doc = window.parent.document;

    function clamp(v, min, max) {
        return Math.max(min, Math.min(max, v));
    }

    function countBars(trace) {
        if (!trace) return 1;
        if (Array.isArray(trace.y)) return Math.max(trace.y.length, 1);
        if (Array.isArray(trace.x)) return Math.max(trace.x.length, 1);
        return 1;
    }

    function sizesFor(gd) {
        const box = gd.getBoundingClientRect();
        const w = box.width || 700;
        const h = box.height || 320;

        const base = clamp(Math.min(w / 58, h / 22), 11, 38);

        let maxBars = 1;
        if (gd.data) {
            gd.data.forEach(function (trace) {
                if (trace.type === "bar") {
                    maxBars = Math.max(maxBars, countBars(trace));
                }
            });
        }

        const rowHeight = h / maxBars;

        /*
          關鍵：
          - 小圖 bar 很密時，文字大小受 rowHeight 限制
          - fullscreen 時 rowHeight 變大，文字自然放大
        */
        const barText = clamp(
            Math.min(base * 1.35, rowHeight * 0.42),
            10,
            42
        );

        const insideBarText = clamp(
            Math.min(base * 1.15, rowHeight * 0.36),
            9,
            34
        );

        const pieText = clamp(base * 1.35, 14, 46);

        return {
            font: Math.round(base),
            tick: Math.round(base * 0.9),
            axisTitle: Math.round(base * 0.9),
            legend: Math.round(base * 0.95),
            barText: Math.round(barText),
            insideBarText: Math.round(insideBarText),
            pieText: Math.round(pieText),
            marginL: Math.round(clamp(w * 0.09, 66, 170)),
            marginR: Math.round(clamp(w * 0.08, 74, 190)),
            marginT: Math.round(clamp(h * 0.15, 48, 120)),
            marginB: Math.round(clamp(h * 0.15, 48, 120))
        };
    }

    function relayout(gd) {
        if (!gd || gd.dataset.resizing === "1") return;

        const Plotly = window.parent.Plotly || window.Plotly;
        if (!Plotly || !Plotly.relayout || !Plotly.restyle) return;

        const s = sizesFor(gd);
        gd.dataset.resizing = "1";

        const update = {
            "font.size": s.font,
            "legend.font.size": s.legend,
            "xaxis.tickfont.size": s.tick,
            "xaxis.title.font.size": s.axisTitle,
            "yaxis.tickfont.size": s.tick,
            "yaxis.title.font.size": s.axisTitle,
            "margin.l": s.marginL,
            "margin.r": s.marginR,
            "margin.t": s.marginT,
            "margin.b": s.marginB
        };

        const textSizes = [];
        const outsideTextSizes = [];
        const insideTextSizes = [];
        const textPositions = [];
        const automargins = [];

        if (gd.data) {
            gd.data.forEach(function (trace) {
                if (trace.type === "pie") {
                    textSizes.push(s.pieText);
                    outsideTextSizes.push(s.pieText);
                    insideTextSizes.push(Math.round(s.pieText * 0.85));
                    textPositions.push("outside");
                    automargins.push(true);
                } else if (trace.type === "bar") {
                    const position = trace.textposition || "outside";
                    const isInside = position === "inside";

                    textSizes.push(isInside ? s.insideBarText : s.barText);
                    outsideTextSizes.push(s.barText);
                    insideTextSizes.push(s.insideBarText);
                    textPositions.push(position);
                    automargins.push(null);
                } else {
                    textSizes.push(s.font);
                    outsideTextSizes.push(s.font);
                    insideTextSizes.push(s.font);
                    textPositions.push(trace.textposition || null);
                    automargins.push(null);
                }
            });

            Plotly.restyle(gd, {
                "textfont.size": textSizes,
                "outsidetextfont.size": outsideTextSizes,
                "insidetextfont.size": insideTextSizes,
                "textposition": textPositions,
                "automargin": automargins
            });
        }

        Plotly.relayout(gd, update).finally(function () {
            gd.dataset.resizing = "0";
        });
    }

    function wire() {
        const plots = doc.querySelectorAll(".js-plotly-plot");
        plots.forEach(function (gd) {
            if (gd.dataset.autoFont === "1") {
                relayout(gd);
                return;
            }

            gd.dataset.autoFont = "1";
            const observer = new ResizeObserver(function () {
                window.requestAnimationFrame(function () {
                    relayout(gd);
                });
            });

            observer.observe(gd);
            relayout(gd);
        });
    }

    wire();
    setInterval(wire, 1200);
    window.parent.addEventListener("resize", wire);

    doc.addEventListener("fullscreenchange", function () {
        setTimeout(wire, 250);
        setTimeout(wire, 800);
        setTimeout(wire, 1500);
    });
})();
</script>
""", height=0)



inject_plotly_resizer()

COLOR_DARK_BLUE = "#0068C9"
COLOR_BLUE = "#83C9FF"
COLOR_PINK = "#FFABAB"
COLOR_DEEP_PINK = "#FFF4E5"
PALETTE = [COLOR_DARK_BLUE, COLOR_BLUE, COLOR_PINK, COLOR_DEEP_PINK]

PLOT_CONFIG = {
    "responsive": True,
    "displaylogo": False,
    "modeBarButtonsToRemove": ["lasso2d", "select2d"],
}

SHEET_ID = "1cBjCD6ql1YliqH1QbbNb3bm41tn4c1D3LCyoZcsgQIM"
GIDS = {
    "產品資訊": "2055196795",
    "客戶資訊": "1292669580",
    "業務員年度銷售目標表": "1119049741",
    "業務員目標完成分析表": "1958610401",
    "銷售明細": "820751903",
    "禮品領用表": "76801093",
    "禮品庫存表": "290066815",
    "客戶關係維護表": "568240245",
}


def sheet_url(gid):
    return f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}"


@st.cache_data(ttl=600)
def load_all():
    return {name: pd.read_csv(sheet_url(gid)) for name, gid in GIDS.items()}


try:
    sheets = load_all()
    df_target = sheets["業務員年度銷售目標表"]
    df_achieve = sheets["業務員目標完成分析表"]
    df_sales = sheets["銷售明細"]
    df_clients = sheets["客戶資訊"]
    df_gifts = sheets["禮品庫存表"]
    df_crm = sheets["客戶關係維護表"]
except Exception as e:
    st.error(f"❌ 無法連接 Google Sheet。\n\n錯誤：{e}")
    st.stop()


def to_num(df, cols):
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)


to_num(df_achieve, ["當季目標", "實際完成", "提出金額"])
to_num(df_target, ["第一季度目標", "第二季度目標", "第三季度目標", "第四季度目標", "年度目標"])
to_num(df_sales, ["銷售金額", "數量", "銷售單價"])
to_num(df_gifts, ["數量", "已領用數量", "剩餘數量"])
to_num(df_crm, ["費用"])

df_achieve["達成率"] = (
    df_achieve["實際完成"] / df_achieve["當季目標"].replace(0, pd.NA) * 100
).round(1).fillna(0)

total_target = df_achieve["當季目標"].sum()
total_achieve = df_achieve["實際完成"].sum()
total_rate = round(total_achieve / total_target * 100, 1) if total_target else 0
total_sales = df_sales["銷售金額"].sum()

ANOMALY_NAMES = ["關羽"]

df_sales_by_emp = (
    df_sales.groupby("工號", dropna=False)["銷售金額"]
    .sum()
    .reset_index()
    .rename(columns={"銷售金額": "銷售明細金額"})
)

target_cols = [
    "工號", "第一季度目標", "第二季度目標", "第三季度目標", "第四季度目標", "年度目標"
]

df_goal = df_achieve.merge(
    df_target[target_cols],
    on="工號",
    how="left",
).merge(
    df_sales_by_emp,
    on="工號",
    how="left",
)

df_goal["銷售明細金額"] = df_goal["銷售明細金額"].fillna(0)
df_goal["目標缺口"] = df_goal["當季目標"] - df_goal["實際完成"]
df_goal["異常"] = df_goal["姓名"].isin(ANOMALY_NAMES)
df_goal["異常註記"] = df_goal.apply(
    lambda r: f"分析表實際 {r['實際完成']:,.0f}$ / 銷售明細 {r['銷售明細金額']:,.0f}$"
    if r["異常"] else "",
    axis=1,
)

total_gap = total_target - total_achieve
avg_rate = round(df_goal["達成率"].mean(), 1) if len(df_goal) else 0
top_goal_person = df_goal.sort_values("達成率", ascending=False).iloc[0]["姓名"] if len(df_goal) else "-"


def fmt(n):
    return f"{n:,.0f}$"


def base_layout(height=320, legend=True):
    layout = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(13,17,23,0.6)",
        autosize=True,
        height=height,
        font=dict(color="#a8b4c2", size=15, family="Noto Sans TC"),
        margin=dict(l=76, r=86, t=58, b=62),
        hoverlabel=dict(
            bgcolor="#161b27",
            bordercolor="#252d3d",
            font=dict(color="#f3f6fb", family="Noto Sans TC"),
        ),
        uniformtext=dict(mode="show", minsize=13),
    )

    if legend:
        layout["legend"] = dict(
            font=dict(color="#b8c4d2", size=15),
            bgcolor="rgba(0,0,0,0)",
            orientation="h",
            yanchor="bottom",
            y=1.03,
            xanchor="center",
            x=0.5,
        )
    else:
        layout["showlegend"] = False

    return layout


def ax(showgrid=True, title=None, tickangle=0, **kw):
    axis = dict(
        linecolor="#252d3d",
        gridcolor="#1a2133" if showgrid else "rgba(0,0,0,0)",
        showgrid=showgrid,
        tickangle=tickangle,
        zeroline=False,
        tickfont=dict(size=14, color="#c1cad6"),
    )

    if title:
        axis["title"] = dict(
            text=title,
            font=dict(size=14, color="#8290a3"),
        )

    axis.update(kw)
    return axis


def chart_area_target(height=260):
    names = df_achieve["姓名"].tolist()
    x = list(range(len(names)))

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x,
        y=df_achieve["當季目標"].tolist(),
        name="當季目標",
        mode="lines",
        line=dict(color=COLOR_DARK_BLUE, width=2.5),
        fill="tozeroy",
        fillcolor="rgba(0,104,201,0.25)",
    ))
    fig.add_trace(go.Scatter(
        x=x,
        y=df_achieve["實際完成"].tolist(),
        name="實際完成",
        mode="lines",
        line=dict(color=COLOR_PINK, width=2.5),
        fill="tozeroy",
        fillcolor="rgba(255,171,171,0.25)",
    ))

    layout = base_layout(height)
    layout.update(
        xaxis=ax(False, tickvals=x, ticktext=names, tickangle=-35),
        yaxis=ax(True),
    )
    fig.update_layout(**layout)
    return fig


def chart_deviation(height=260):
    df_s = df_achieve.sort_values("達成率", ascending=True)
    dev = (df_s["達成率"] - 80).tolist()
    colors = [COLOR_DARK_BLUE if v >= 0 else COLOR_DEEP_PINK for v in dev]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=list(range(len(df_s))),
        x=dev,
        orientation="h",
        marker=dict(color=colors, line_width=0, opacity=0.88, cornerradius=8),
        text=[f"{r}%" for r in df_s["達成率"]],
        textposition="outside",
        textfont=dict(size=12, color="#bcd1ea"),
        cliponaxis=False,
    ))

    layout = base_layout(height, legend=False)
    layout.update(
        yaxis=ax(False, tickvals=list(range(len(df_s))), ticktext=df_s["姓名"].tolist()),
        xaxis=ax(True, title="偏差 %（基準 80%）"),
    )
    fig.update_layout(**layout)
    return fig


def chart_top5(height=260):
    df_t = df_achieve.nlargest(5, "提出金額")[["姓名", "提出金額", "達成率"]]

    fig = px.bar(
        df_t,
        x="提出金額",
        y="姓名",
        orientation="h",
        color="達成率",
        color_continuous_scale=[COLOR_DEEP_PINK, COLOR_BLUE, COLOR_DARK_BLUE],
        text="提出金額",
    )

    fig.update_traces(
        texttemplate="%{text:,.0f}$",
        textposition="outside",
        textfont=dict(size=12, color="#bcd1ea"),
        marker=dict(line_width=0, opacity=0.9, cornerradius=8),
        cliponaxis=False,
    )

    layout = base_layout(height, legend=False)
    layout["coloraxis_showscale"] = False
    layout.update(
        xaxis=ax(True, title="提出金額"),
        yaxis=ax(False, title="姓名"),
        margin=dict(l=78, r=110, t=38, b=58),
    )
    fig.update_layout(**layout)
    return fig


def pie_chart(labels, values, height=300, hole=0.45):
    colors = (PALETTE * 10)[:len(labels)]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=hole,
        marker=dict(colors=colors, line=dict(color="#0d1117", width=2)),
        textinfo="label+percent",
        textposition="outside",
        textfont=dict(size=12, color="#f3f6fb", family="Noto Sans TC"),
        outsidetextfont=dict(size=18, color="#f3f6fb", family="Noto Sans TC"),
        insidetextfont=dict(size=16, color="#f3f6fb", family="Noto Sans TC"),
        automargin=True,
        pull=[0.035] * len(labels),
        opacity=0.9,
        hovertemplate="<b>%{label}</b><br>數值: %{value:,.0f}<br>比例: %{percent}<extra></extra>",
    )])

    layout = base_layout(height, legend=False)
    layout.update(
        margin=dict(l=80, r=150, t=50, b=50),
        showlegend=False,
    )
    fig.update_layout(**layout)
    return fig


def chart_product_pie(height=260, hole=0.45):
    df_p = df_sales.groupby("產品名稱")["銷售金額"].sum().reset_index()
    return pie_chart(df_p["產品名稱"], df_p["銷售金額"], height=height, hole=hole)


def chart_quarterly(height=400):
    quarters = ["第一季度目標", "第二季度目標", "第三季度目標", "第四季度目標"]

    fig = go.Figure()
    for q, color in zip(quarters, PALETTE):
        fig.add_trace(go.Bar(
            name=q,
            y=df_target["姓名"],
            x=df_target[q],
            orientation="h",
            marker=dict(color=color, line_width=0, opacity=0.88, cornerradius=7),
        ))

    layout = base_layout(height)
    layout["barmode"] = "group"
    layout.update(yaxis=ax(False), xaxis=ax(True))
    fig.update_layout(**layout)
    return fig

def chart_goal_bullet(height=520):
    df_s = df_goal.sort_values("達成率", ascending=True).copy()
    colors = [
        "#ff4d4f" if is_bad else (COLOR_DARK_BLUE if rate >= 80 else COLOR_BLUE)
        for is_bad, rate in zip(df_s["異常"], df_s["達成率"])
    ]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        name="當季目標",
        y=df_s["姓名"],
        x=df_s["當季目標"],
        orientation="h",
        marker=dict(color="rgba(120,132,150,0.26)", line_width=0, cornerradius=8),
        hovertemplate="<b>%{y}</b><br>當季目標: %{x:,.0f}$<extra></extra>",
    ))

    fig.add_trace(go.Bar(
        name="實際完成",
        y=df_s["姓名"],
        x=df_s["實際完成"],
        orientation="h",
        marker=dict(color=colors, line_width=0, opacity=0.92, cornerradius=8),
        text=[f"{v:.1f}%" for v in df_s["達成率"]],
        textposition="outside",
        textfont=dict(size=12, color="#d7e8ff"),
        cliponaxis=False,
        customdata=df_s[["當季目標", "達成率", "目標缺口", "銷售明細金額", "異常註記"]],
        hovertemplate=(
            "<b>%{y}</b><br>"
            "實際完成: %{x:,.0f}$<br>"
            "當季目標: %{customdata[0]:,.0f}$<br>"
            "達成率: %{customdata[1]:.1f}%<br>"
            "目標缺口: %{customdata[2]:,.0f}$<br>"
            "銷售明細金額: %{customdata[3]:,.0f}$<br>"
            "%{customdata[4]}"
            "<extra></extra>"
        ),
    ))

    layout = base_layout(height)
    layout["barmode"] = "overlay"
    layout.update(
        xaxis=ax(True, title="金額"),
        yaxis=ax(False),
        legend=dict(
            font=dict(color="#b8c4d2", size=15),
            bgcolor="rgba(0,0,0,0)",
            orientation="h",
            yanchor="bottom",
            y=1.03,
            xanchor="center",
            x=0.5,
        ),
        margin=dict(l=86, r=130, t=58, b=62),
    )

    fig.update_layout(**layout)
    return fig


def chart_quarter_heatmap(height=420):
    quarters = ["第一季度目標", "第二季度目標", "第三季度目標", "第四季度目標"]
    df_h = df_target.set_index("姓名")[quarters]

    fig = go.Figure(data=go.Heatmap(
        z=df_h.values,
        x=["Q1", "Q2", "Q3", "Q4"],
        y=df_h.index,
        colorscale=[
            [0, "#161b27"],
            [0.45, COLOR_BLUE],
            [1, COLOR_DARK_BLUE],
        ],
        text=[[f"{v/1000:.0f}k" for v in row] for row in df_h.values],
        texttemplate="%{text}",
        textfont=dict(color="#f3f6fb", size=12),
        hovertemplate="<b>%{y}</b><br>%{x}: %{z:,.0f}$<extra></extra>",
        showscale=False,
    ))

    layout = base_layout(height, legend=False)
    layout.update(
        xaxis=ax(False, title="季度"),
        yaxis=ax(False),
        margin=dict(l=86, r=40, t=44, b=54),
    )
    fig.update_layout(**layout)
    return fig


def chart_goal_scatter(height=420):
    df_s = df_goal.copy()
    sizes = df_s["銷售明細金額"].clip(lower=1)
    marker_colors = ["#ff4d4f" if v else COLOR_BLUE for v in df_s["異常"]]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_s["達成率"],
        y=df_s["年度目標"],
        mode="markers+text",
        text=df_s["姓名"],
        textposition="top center",
        marker=dict(
            size=(sizes / sizes.max() * 34 + 10) if sizes.max() else 16,
            color=marker_colors,
            line=dict(color="#0d1117", width=1.5),
            opacity=0.9,
        ),
        customdata=df_s[["當季目標", "實際完成", "銷售明細金額", "異常註記"]],
        hovertemplate=(
            "<b>%{text}</b><br>"
            "達成率: %{x:.1f}%<br>"
            "年度目標: %{y:,.0f}$<br>"
            "當季目標: %{customdata[0]:,.0f}$<br>"
            "實際完成: %{customdata[1]:,.0f}$<br>"
            "銷售明細金額: %{customdata[2]:,.0f}$<br>"
            "%{customdata[3]}"
            "<extra></extra>"
        ),
    ))

    fig.add_vline(
        x=80,
        line_width=1.4,
        line_dash="dash",
        line_color="#8899aa",
        annotation_text="80% 基準",
        annotation_font_color="#8899aa",
    )

    layout = base_layout(height, legend=False)
    layout.update(
        xaxis=ax(True, title="達成率 %", ticksuffix="%"),
        yaxis=ax(True, title="年度目標"),
        margin=dict(l=86, r=64, t=48, b=62),
    )
    fig.update_layout(**layout)
    return fig


def chart_product_treemap(height=360):
    df_p = (
        df_sales.groupby("產品名稱", dropna=False)["銷售金額"]
        .sum()
        .reset_index()
        .sort_values("銷售金額", ascending=False)
    )

    fig = px.treemap(
        df_p,
        path=["產品名稱"],
        values="銷售金額",
        color="銷售金額",
        color_continuous_scale=[COLOR_BLUE, COLOR_DARK_BLUE],
    )

    fig.update_traces(
        texttemplate="<b>%{label}</b><br>%{value:,.0f}$",
        textfont=dict(size=16, color="#f3f6fb"),
        marker=dict(line=dict(color="#0d1117", width=2)),
        hovertemplate="<b>%{label}</b><br>銷售金額: %{value:,.0f}$<extra></extra>",
    )

    layout = base_layout(height, legend=False)
    layout["coloraxis_showscale"] = False
    layout.update(margin=dict(l=8, r=8, t=28, b=8))
    fig.update_layout(**layout)
    return fig


def chart_crm_source_level(height=360):
    if not {"客戶等級", "客戶來源", "費用"}.issubset(df_crm.columns):
        return chart_crm(height)

    df_c = (
        df_crm.groupby(["客戶來源", "客戶等級"], dropna=False)["費用"]
        .sum()
        .reset_index()
    )

    fig = px.bar(
        df_c,
        x="費用",
        y="客戶來源",
        color="客戶等級",
        orientation="h",
        color_discrete_sequence=PALETTE,
        text="費用",
    )

    fig.update_traces(
        texttemplate="%{text:,.0f}$",
        textposition="inside",
        textfont=dict(size=12, color="#f3f6fb"),
        marker=dict(line_width=0, opacity=0.9, cornerradius=6),
        cliponaxis=False,
    )

    layout = base_layout(height)
    layout["barmode"] = "stack"
    layout.update(
        xaxis=ax(True, title="維護費用"),
        yaxis=ax(False, title="客戶來源"),
        margin=dict(l=86, r=48, t=58, b=58),
    )
    fig.update_layout(**layout)
    return fig


def chart_annual(height=370):
    df_s = df_target.sort_values("年度目標", ascending=True)

    fig = px.bar(
        df_s,
        x="年度目標",
        y="姓名",
        orientation="h",
        color="年度目標",
        color_continuous_scale=[COLOR_DARK_BLUE, COLOR_BLUE],
        text="年度目標",
    )
    fig.update_traces(
        texttemplate="%{text:,.0f}$",
        textposition="outside",
        textfont=dict(size=12, color="#bcd1ea"),
        marker=dict(line_width=0, opacity=0.88, cornerradius=8),
        cliponaxis=False,
    )

    layout = base_layout(height, legend=False)
    layout["coloraxis_showscale"] = False
    layout.update(xaxis=ax(True), yaxis=ax(False))
    fig.update_layout(**layout)
    return fig


def chart_sales_by_person(height=370):
    df_b = df_sales.groupby("業務員")["銷售金額"].sum().reset_index().sort_values("銷售金額")

    fig = px.bar(
        df_b,
        x="銷售金額",
        y="業務員",
        orientation="h",
        color="銷售金額",
        color_continuous_scale=[COLOR_DARK_BLUE, COLOR_BLUE],
        text="銷售金額",
    )
    fig.update_traces(
        texttemplate="%{text:,.0f}$",
        textposition="outside",
        textfont=dict(size=12, color="#bcd1ea"),
        marker=dict(line_width=0, opacity=0.88, cornerradius=8),
        cliponaxis=False,
    )

    layout = base_layout(height, legend=False)
    layout["coloraxis_showscale"] = False
    layout.update(xaxis=ax(True), yaxis=ax(False))
    fig.update_layout(**layout)
    return fig


def chart_product_qty(height=370):
    df_q = df_sales.groupby("產品名稱")["數量"].sum().reset_index().sort_values("數量")

    fig = px.bar(
        df_q,
        x="數量",
        y="產品名稱",
        orientation="h",
        color="數量",
        color_continuous_scale=[COLOR_DARK_BLUE, COLOR_BLUE],
        text="數量",
    )
    fig.update_traces(
        textposition="outside",
        textfont=dict(size=12, color="#bcd1ea"),
        marker=dict(line_width=0, opacity=0.88, cornerradius=8),
        cliponaxis=False,
    )

    layout = base_layout(height, legend=False)
    layout["coloraxis_showscale"] = False
    layout.update(xaxis=ax(True), yaxis=ax(False))
    fig.update_layout(**layout)
    return fig


def chart_client_grade(height=300):
    df_g = df_clients["客戶等級"].value_counts().reset_index()
    df_g.columns = ["客戶等級", "數量"]
    return pie_chart(df_g["客戶等級"], df_g["數量"], height=height, hole=0.42)


def chart_client_source(height=300):
    df_s = df_clients["客戶來源"].value_counts().reset_index()
    df_s.columns = ["來源", "數量"]
    df_s = df_s.sort_values("數量")

    fig = px.bar(
        df_s,
        x="數量",
        y="來源",
        orientation="h",
        color="數量",
        color_continuous_scale=[COLOR_DARK_BLUE, COLOR_BLUE],
        text="數量",
    )
    fig.update_traces(
        textposition="outside",
        textfont=dict(size=12, color="#bcd1ea"),
        marker=dict(line_width=0, opacity=0.88, cornerradius=8),
        cliponaxis=False,
    )

    layout = base_layout(height, legend=False)
    layout["coloraxis_showscale"] = False
    layout.update(xaxis=ax(True), yaxis=ax(False))
    fig.update_layout(**layout)
    return fig


def chart_gift_stacked(height=340):
    df_g = df_gifts.copy()
    total = df_g["數量"].replace(0, 1)
    df_g["已領用%"] = (df_g["已領用數量"] / total * 100).round(1)
    df_g["剩餘%"] = (df_g["剩餘數量"] / total * 100).round(1)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="已領用",
        y=df_g["禮品名稱"],
        x=df_g["已領用%"],
        orientation="h",
        marker=dict(color=COLOR_DEEP_PINK, line_width=0, opacity=0.88, cornerradius=6),
        text=[f"{v}%" for v in df_g["已領用%"]],
        textposition="inside",
        textfont=dict(color="#111827", size=18),
        cliponaxis=False,
    ))
    fig.add_trace(go.Bar(
        name="剩餘",
        y=df_g["禮品名稱"],
        x=df_g["剩餘%"],
        orientation="h",
        marker=dict(color=COLOR_DARK_BLUE, line_width=0, opacity=0.88, cornerradius=6),
        text=[f"{v}%" for v in df_g["剩餘%"]],
        textposition="inside",
        textfont=dict(color="white", size=18),
        cliponaxis=False,
    ))

    layout = base_layout(height)
    layout["barmode"] = "stack"
    layout.update(yaxis=ax(False), xaxis=ax(True, title="佔比 %", range=[0, 105]))
    fig.update_layout(**layout)
    return fig


def chart_crm(height=300):
    df_c = df_crm.groupby("維護內容")["費用"].sum().reset_index().sort_values("費用")

    fig = px.bar(
        df_c,
        x="費用",
        y="維護內容",
        orientation="h",
        color="費用",
        color_continuous_scale=[COLOR_DARK_BLUE, COLOR_DEEP_PINK],
        text="費用",
    )
    fig.update_traces(
        texttemplate="%{text:,.0f}$",
        textposition="outside",
        textfont=dict(size=12, color="#bcd1ea"),
        marker=dict(line_width=0, opacity=0.88, cornerradius=8),
        cliponaxis=False,
    )

    layout = base_layout(height, legend=False)
    layout["coloraxis_showscale"] = False
    layout.update(xaxis=ax(True), yaxis=ax(False))
    fig.update_layout(**layout)
    return fig


def show_chart(fig):
    st.plotly_chart(fig, use_container_width=True, config=PLOT_CONFIG)


def kpi_row():
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("當季總目標", fmt(total_target))
    k2.metric("當季實際完成", fmt(total_achieve))
    k3.metric("整體達成率", f"{total_rate}%", delta=f"{'↑' if total_rate >= 80 else '↓'} 目標 80%")
    k4.metric("銷售金額合計", fmt(total_sales))


with st.sidebar:
    st.markdown("### 📋 主選單")
    st.markdown("---")

    page = st.radio(
        "",
        [
            "🏠 首頁總覽",
            "📊 全覽 Dashboard",
            "🎯 目標達成分析",
            "💰 銷售明細",
            "👥 客戶分析",
            "🎁 禮品庫存",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")

    if st.button("🔄 重新整理資料"):
        st.cache_data.clear()
        st.rerun()

    st.markdown(
        "<div style='font-size:0.72rem;color:#8b98aa;margin-top:10px;'>"
        "資料來源：Google Sheets<br>每 10 分鐘自動更新</div>",
        unsafe_allow_html=True,
    )


if page == "🏠 首頁總覽":
    st.markdown("<div class='main-title'>營銷目標管理 Dashboard</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>當季目標、實際完成、達成率與產品銷售概況</div>", unsafe_allow_html=True)

    kpi_row()
    st.markdown("---")

    c1, c2 = st.columns([1.08, 0.92])
    with c1:
        st.markdown("<div class='chart-wrap'><div class='section-title'>目標 vs 實際完成</div></div>", unsafe_allow_html=True)
        show_chart(chart_area_target(300))
    with c2:
        st.markdown("<div class='chart-wrap'><div class='section-title'>達成率排名（基準 80%）</div></div>", unsafe_allow_html=True)
        show_chart(chart_deviation(300))

    b1, b2 = st.columns([1.08, 0.92])
    with b1:
        st.markdown("<div class='chart-wrap'><div class='section-title'>提成金額 Top 5</div></div>", unsafe_allow_html=True)
        show_chart(chart_top5(320))
    with b2:
        st.markdown("<div class='chart-wrap'><div class='section-title'>產品銷售金額分佈</div></div>", unsafe_allow_html=True)
        show_chart(chart_product_pie(320))


elif page == "📊 全覽 Dashboard":
    st.markdown("<div class='main-title'>全覽 Dashboard</div>", unsafe_allow_html=True)
    kpi_row()
    st.markdown("---")

    r1a, r1b = st.columns(2)
    with r1a:
        st.markdown("<div class='section-title'>目標 vs 實際完成</div>", unsafe_allow_html=True)
        show_chart(chart_area_target(300))
    with r1b:
        st.markdown("<div class='section-title'>達成率排名</div>", unsafe_allow_html=True)
        show_chart(chart_deviation(300))

    r2a, r2b, r2c = st.columns(3)
    with r2a:
        st.markdown("<div class='section-title'>提成 Top 5</div>", unsafe_allow_html=True)
        show_chart(chart_top5(280))
    with r2b:
        st.markdown("<div class='section-title'>產品銷售分佈</div>", unsafe_allow_html=True)
        show_chart(chart_product_pie(280))
    with r2c:
        st.markdown("<div class='section-title'>客戶等級分佈</div>", unsafe_allow_html=True)
        show_chart(chart_client_grade(280))

    r3a, r3b = st.columns(2)
    with r3a:
        st.markdown("<div class='section-title'>業務員銷售金額</div>", unsafe_allow_html=True)
        show_chart(chart_sales_by_person(330))
    with r3b:
        st.markdown("<div class='section-title'>禮品庫存比例</div>", unsafe_allow_html=True)
        show_chart(chart_gift_stacked(330))

    st.markdown("---")
    st.markdown("<div class='section-title'>銷售明細</div>", unsafe_allow_html=True)

    cols = ["單號", "銷售日期", "業務員", "公司名稱", "產品名稱", "數量", "銷售單價", "銷售金額"]
    avail = [c for c in cols if c in df_sales.columns]
    df_s_fmt = df_sales[avail].copy()

    for c in ["銷售金額", "銷售單價"]:
        if c in df_s_fmt.columns:
            df_s_fmt[c] = df_s_fmt[c].apply(lambda x: f"{x:,.0f}$")

    st.dataframe(df_s_fmt, use_container_width=True, hide_index=True, height=280)


elif page == "🎯 目標達成分析":
    st.markdown("<div class='main-title'>業務員目標達成分析</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='page-subtitle'>整合當季目標、實際完成、年度目標、銷售明細與客戶維護投入</div>",
        unsafe_allow_html=True,
    )

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("當季總目標", fmt(total_target))
    k2.metric("當季實際完成", fmt(total_achieve))
    k3.metric("整體達成率", f"{total_rate}%", delta=f"目標 80%")
    k4.metric("目標缺口", fmt(total_gap))
    k5.metric("最佳達成人員", top_goal_person)

    if df_goal["異常"].any():
        anomaly_text = "；".join(
            df_goal.loc[df_goal["異常"], ["姓名", "異常註記"]]
            .apply(lambda r: f"{r['姓名']}：{r['異常註記']}", axis=1)
            .tolist()
        )
        st.markdown(
            f"""
            <div style="
                margin-top:0.8rem;
                padding:0.75rem 1rem;
                border:1px solid rgba(255,77,79,0.55);
                background:rgba(255,77,79,0.12);
                color:#ffd1d1;
                border-radius:8px;
                font-size:clamp(12px,0.82vw,15px);
            ">
                資料異常提示：{anomaly_text}。圖中以紅色標示。
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    r1a, r1b = st.columns([1.18, 0.82])
    with r1a:
        st.markdown("<div class='section-title'>業務員目標達成 Bullet Chart</div>", unsafe_allow_html=True)
        show_chart(chart_goal_bullet(540))

    with r1b:
        st.markdown("<div class='section-title'>年度目標 vs 達成率</div>", unsafe_allow_html=True)
        show_chart(chart_goal_scatter(540))

    r2a, r2b = st.columns([1.05, 0.95])
    with r2a:
        st.markdown("<div class='section-title'>季度目標壓力熱力圖</div>", unsafe_allow_html=True)
        show_chart(chart_quarter_heatmap(420))

    with r2b:
        st.markdown("<div class='section-title'>產品銷售貢獻</div>", unsafe_allow_html=True)
        show_chart(chart_product_treemap(420))

    r3a, r3b = st.columns([1.05, 0.95])
    with r3a:
        st.markdown("<div class='section-title'>客戶來源 × 等級 × 維護費用</div>", unsafe_allow_html=True)
        show_chart(chart_crm_source_level(360))

    with r3b:
        st.markdown("<div class='section-title'>目標達成資料表</div>", unsafe_allow_html=True)

        df_show = df_goal[[
            "姓名", "當季目標", "實際完成", "銷售明細金額", "達成率",
            "目標缺口", "提出金額", "排名", "異常註記", "異常"
        ]].copy()

        for c in ["當季目標", "實際完成", "銷售明細金額", "目標缺口", "提出金額"]:
            df_show[c] = df_show[c].apply(fmt)

        df_show["達成率"] = df_show["達成率"].apply(lambda x: f"{x}%")
        df_show = df_show.drop(columns=["異常"])

        def highlight_anomaly(row):
            is_bad = row["異常註記"] != ""
            return [
                "background-color: rgba(255,77,79,0.18); color: #ffd1d1;"
                if is_bad else ""
                for _ in row
            ]

        st.dataframe(
            df_show.style.apply(highlight_anomaly, axis=1),
            use_container_width=True,
            hide_index=True,
            height=360,
        )



elif page == "💰 銷售明細":
    st.markdown("<div class='main-title'>銷售明細</div>", unsafe_allow_html=True)

    cols = ["單號", "銷售日期", "業務員", "公司名稱", "產品名稱", "數量", "銷售單價", "銷售金額"]
    avail = [c for c in cols if c in df_sales.columns]
    df_disp = df_sales[avail].copy()

    for c in ["銷售金額", "銷售單價"]:
        if c in df_disp.columns:
            df_disp[c] = df_disp[c].apply(lambda x: f"{x:,.0f}$")

    total_rows = len(df_disp)
    row_range = st.slider(
        "顯示資料筆數範圍",
        1,
        total_rows,
        (1, min(total_rows, 14)),
        key="sales_range",
    )

    st.dataframe(
        df_disp.iloc[row_range[0] - 1:row_range[1]],
        use_container_width=True,
        hide_index=True,
        height=400,
    )

    st.markdown("---")

    s1, s2 = st.columns(2)
    with s1:
        st.markdown("<div class='section-title'>業務員銷售金額</div>", unsafe_allow_html=True)
        show_chart(chart_sales_by_person())
    with s2:
        st.markdown("<div class='section-title'>各產品銷售數量</div>", unsafe_allow_html=True)
        show_chart(chart_product_qty())


elif page == "👥 客戶分析":
    st.markdown("<div class='main-title'>客戶分析</div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='section-title'>客戶等級分佈</div>", unsafe_allow_html=True)
        show_chart(chart_client_grade())
    with c2:
        st.markdown("<div class='section-title'>客戶來源分佈</div>", unsafe_allow_html=True)
        show_chart(chart_client_source())

    st.markdown("---")
    st.markdown("<div class='section-title'>客戶列表</div>", unsafe_allow_html=True)

    dcols = [c for c in ["客戶編碼", "公司名稱", "連絡人", "客戶等級", "客戶來源"] if c in df_clients.columns]
    st.dataframe(df_clients[dcols], use_container_width=True, hide_index=True, height=400)

    if "費用" in df_crm.columns and df_crm["費用"].sum() > 0:
        st.markdown("---")
        st.markdown("<div class='section-title'>客戶關係維護費用</div>", unsafe_allow_html=True)
        show_chart(chart_crm())


elif page == "🎁 禮品庫存":
    st.markdown("<div class='main-title'>禮品庫存管理</div>", unsafe_allow_html=True)

    g1, g2, g3 = st.columns(3)
    g1.metric("禮品種類", f"{len(df_gifts)} 種")
    g2.metric("已領用總數", f"{int(df_gifts['已領用數量'].sum())} 件")
    g3.metric("剩餘總數", f"{int(df_gifts['剩餘數量'].sum())} 件")

    st.markdown("---")
    st.dataframe(df_gifts, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("<div class='section-title'>庫存使用比例（100% 堆疊）</div>", unsafe_allow_html=True)
    show_chart(chart_gift_stacked(420))
