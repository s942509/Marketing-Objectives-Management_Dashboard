import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="營銷目標管理 Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700&display=swap');

.stApp { background-color: #0d1117; color: #e0e0e0; font-family: 'Noto Sans TC', sans-serif; }
[data-testid="stSidebar"] { background-color: #161b27; border-right: 1px solid #252d3d; }
[data-testid="stSidebar"] * { color: #c9d1e0 !important; }
.section-title {
    font-size: 1.15rem; font-weight: 700; color: #e0e0e0;
    margin-bottom: 0.4rem; letter-spacing: 0.02em;
}
hr { border-color: #252d3d !important; }
[data-testid="stMetricValue"] { font-size: 1.8rem !important; font-weight: 700; }
[data-testid="stMetricDelta"] { font-size: 0.78rem; }
[data-testid="metric-container"] {
    background: linear-gradient(135deg, #161b27 0%, #1c2336 100%);
    border: 1px solid #252d3d;
    border-radius: 14px;
    padding: 16px 20px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
}
</style>
""", unsafe_allow_html=True)

# ── Google Sheet 設定 ─────────────────────────────────────────────────────────
SHEET_ID = "1cBjCD6ql1YliqH1QbbNb3bm41tn4c1D3LCyoZcsgQIM"
GIDS = {
    "產品資訊":           "2055196795",
    "客戶資訊":           "1292669580",
    "業務員年度銷售目標表": "1119049741",
    "業務員目標完成分析表": "1958610401",
    "銷售明細":           "820751903",
    "禮品領用表":         "76801093",
    "禮品庫存表":         "290066815",
    "客戶關係維護表":     "568240245",
}

def sheet_url(gid):
    return f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}"

@st.cache_data(ttl=600)
def load_all():
    return {name: pd.read_csv(sheet_url(gid)) for name, gid in GIDS.items()}

try:
    sheets     = load_all()
    df_target  = sheets["業務員年度銷售目標表"]
    df_achieve = sheets["業務員目標完成分析表"]
    df_sales   = sheets["銷售明細"]
    df_clients = sheets["客戶資訊"]
    df_gifts   = sheets["禮品庫存表"]
    df_crm     = sheets["客戶關係維護表"]
except Exception as e:
    st.error(f"❌ 無法連接 Google Sheet。\n\n錯誤：{e}")
    st.stop()

# ── 數值轉型 ──────────────────────────────────────────────────────────────────
def to_num(df, cols):
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

to_num(df_achieve, ["當季目標","實際完成","提出金額"])
to_num(df_target,  ["第一季度目標","第二季度目標","第三季度目標","第四季度目標","年度目標"])
to_num(df_sales,   ["銷售金額","數量","銷售單價"])
to_num(df_gifts,   ["數量","已領用數量","剩餘數量"])
to_num(df_crm,     ["費用"])

df_achieve["達成率"] = (
    df_achieve["實際完成"] / df_achieve["當季目標"].replace(0, pd.NA) * 100
).round(1).fillna(0)

total_target  = df_achieve["當季目標"].sum()
total_achieve = df_achieve["實際完成"].sum()
total_rate    = round(total_achieve / total_target * 100, 1) if total_target else 0
total_sales   = df_sales["銷售金額"].sum()

# ── 圖表樣式共用 ──────────────────────────────────────────────────────────────
# 色盤 — 柔和藍粉紫調，有層次
PALETTE = ["#5b8dee", "#a78bfa", "#f472b6", "#34d399", "#fbbf24", "#60a5fa", "#fb923c"]

def base_layout(height=320, legend=True):
    """Return a clean dark layout dict (no xaxis/yaxis — set per chart)."""
    d = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(13,17,23,0.6)",
        font=dict(color="#8899aa", size=11, family="Noto Sans TC"),
        margin=dict(l=12, r=12, t=36, b=12),
        height=height,
    )
    if legend:
        d["legend"] = dict(
            font=dict(color="#aabbcc", size=10),
            bgcolor="rgba(0,0,0,0)",
            orientation="h",
            yanchor="bottom", y=1.02,
            xanchor="center", x=0.5,
        )
    else:
        d["showlegend"] = False
    return d

def ax(showgrid=True, title=None, tickangle=0, **kw):
    d = dict(
        linecolor="#252d3d",
        gridcolor="#1a2133" if showgrid else "rgba(0,0,0,0)",
        showgrid=showgrid,
        tickangle=tickangle,
        zeroline=False,
    )
    if title:
        d["title"] = dict(text=title, font=dict(size=10, color="#667788"))
    d.update(kw)
    return d

# 弧度陰影感 — 所有 bar 用 rounded corners via marker line
BAR_STYLE = dict(marker_line_width=0, opacity=0.92)

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📋 主選單")
    st.markdown("---")
    page = st.radio("", [
        "🏠 首頁總覽",
        "📊 全覽 Dashboard",
        "🎯 目標達成分析",
        "💰 銷售明細",
        "👥 客戶分析",
        "🎁 禮品庫存",
    ], label_visibility="collapsed")
    st.markdown("---")
    if st.button("🔄 重新整理資料"):
        st.cache_data.clear()
        st.rerun()
    st.markdown(
        "<div style='font-size:0.72rem;color:#445;margin-top:10px;'>"
        "資料來源：Google Sheets<br>每 10 分鐘自動更新</div>",
        unsafe_allow_html=True,
    )

# ── 格式化金額 ────────────────────────────────────────────────────────────────
def fmt(n):
    return f"{n:,.0f}$"

# ─────────────────────────────────────────────────────────────────────────────
# 共用圖表函數
# ─────────────────────────────────────────────────────────────────────────────

def chart_area_target(height=300):
    names = df_achieve["姓名"].tolist()
    x = list(range(len(names)))
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x, y=df_achieve["當季目標"].tolist(), name="當季目標", mode="lines",
        line=dict(color="#5b8dee", width=2.5, shape="spline"),
        fill="tozeroy", fillcolor="rgba(91,141,238,0.18)",
    ))
    fig.add_trace(go.Scatter(
        x=x, y=df_achieve["實際完成"].tolist(), name="實際完成", mode="lines",
        line=dict(color="#f472b6", width=2.5, shape="spline"),
        fill="tozeroy", fillcolor="rgba(244,114,182,0.18)",
    ))
    layout = base_layout(height)
    layout.update(
        xaxis=ax(showgrid=False, tickvals=x, ticktext=names, tickangle=-40),
        yaxis=ax(showgrid=True),
    )
    fig.update_layout(**layout)
    return fig

def chart_deviation(height=310):
    df_s = df_achieve.sort_values("達成率", ascending=False)
    dev  = df_s["達成率"] - 80
    colors = ["#5b8dee" if v >= 0 else "#f472b6" for v in dev]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=list(range(len(df_s))), y=dev.tolist(),
        marker_color=colors, marker_line_width=0,
        text=[f"{r}%" for r in df_s["達成率"]],
        textposition="outside", textfont=dict(size=9, color="#8899aa"),
    ))
    layout = base_layout(height, legend=False)
    layout.update(
        xaxis=ax(showgrid=False, tickvals=list(range(len(df_s))),
                 ticktext=df_s["姓名"].tolist(), tickangle=-40),
        yaxis=ax(showgrid=True, title="偏差 % (基準80%)"),
    )
    fig.update_layout(**layout)
    return fig

def chart_top5(height=260):
    df_t = df_achieve.nlargest(5, "提出金額")[["姓名","提出金額","達成率"]]
    fig = px.bar(df_t, x="提出金額", y="姓名", orientation="h",
                 color="達成率", color_continuous_scale=["#f472b6","#5b8dee"],
                 text="提出金額")
    fig.update_traces(texttemplate="%{text:,.0f}$", textposition="outside",
                      marker_line_width=0, opacity=0.92)
    layout = base_layout(height, legend=False)
    layout["coloraxis_showscale"] = False
    layout.update(
        xaxis=ax(showgrid=True),
        yaxis=ax(showgrid=False),
    )
    fig.update_layout(**layout)
    return fig

def chart_product_pie(height=260):
    df_p = df_sales.groupby("產品名稱")["銷售金額"].sum().reset_index()
    fig = px.pie(df_p, names="產品名稱", values="銷售金額",
                 color_discrete_sequence=PALETTE, hole=0.45)
    fig.update_traces(
        textinfo="percent+label",
        textfont_size=10,
        marker=dict(line=dict(color="#0d1117", width=2)),
        pull=[0.03]*len(df_p),
    )
    layout = base_layout(height)
    fig.update_layout(**layout)
    return fig

def chart_quarterly(height=360):
    quarters = ["第一季度目標","第二季度目標","第三季度目標","第四季度目標"]
    colors_q = ["#5b8dee","#a78bfa","#f472b6","#fbbf24"]
    fig = go.Figure()
    for i, q in enumerate(quarters):
        fig.add_trace(go.Bar(name=q, x=df_target["姓名"], y=df_target[q],
                             marker_color=colors_q[i], marker_line_width=0, opacity=0.9))
    layout = base_layout(height)
    layout["barmode"] = "group"
    layout.update(
        xaxis=ax(showgrid=False, tickangle=-30),
        yaxis=ax(showgrid=True),
    )
    fig.update_layout(**layout)
    return fig

def chart_annual(height=370):
    df_s = df_target.sort_values("年度目標", ascending=True)
    fig = px.bar(df_s, x="年度目標", y="姓名", orientation="h",
                 color="年度目標", color_continuous_scale=["#1a2a4a","#5b8dee"],
                 text="年度目標")
    fig.update_traces(texttemplate="%{text:,.0f}$", textposition="outside",
                      marker_line_width=0, opacity=0.92)
    layout = base_layout(height, legend=False)
    layout["coloraxis_showscale"] = False
    layout.update(
        xaxis=ax(showgrid=True),
        yaxis=ax(showgrid=False),
    )
    fig.update_layout(**layout)
    return fig

def chart_sales_by_person(height=370):
    df_b = (df_sales.groupby("業務員")["銷售金額"].sum()
            .reset_index().sort_values("銷售金額", ascending=True))
    fig = px.bar(df_b, x="銷售金額", y="業務員", orientation="h",
                 color="銷售金額", color_continuous_scale=["#1a2a4a","#5b8dee"],
                 text="銷售金額")
    fig.update_traces(texttemplate="%{text:,.0f}$", textposition="outside",
                      marker_line_width=0, opacity=0.92)
    layout = base_layout(height, legend=False)
    layout["coloraxis_showscale"] = False
    layout.update(
        xaxis=ax(showgrid=True),
        yaxis=ax(showgrid=False),
    )
    fig.update_layout(**layout)
    return fig

def chart_product_qty(height=370):
    df_q = (df_sales.groupby("產品名稱")["數量"].sum()
            .reset_index().sort_values("數量", ascending=False))
    fig = px.bar(df_q, x="產品名稱", y="數量",
                 color="數量", color_continuous_scale=["#1a2a4a","#a78bfa"],
                 text="數量")
    fig.update_traces(textposition="outside", marker_line_width=0, opacity=0.92)
    layout = base_layout(height, legend=False)
    layout["coloraxis_showscale"] = False
    layout.update(
        xaxis=ax(showgrid=False, tickangle=-25),
        yaxis=ax(showgrid=True),
    )
    fig.update_layout(**layout)
    return fig

def chart_client_grade(height=300):
    df_g = df_clients["客戶等級"].value_counts().reset_index()
    df_g.columns = ["客戶等級","數量"]
    fig = px.pie(df_g, names="客戶等級", values="數量",
                 color_discrete_sequence=PALETTE, hole=0.42)
    fig.update_traces(
        textinfo="percent+label", textfont_size=10,
        marker=dict(line=dict(color="#0d1117", width=2)),
        pull=[0.03]*len(df_g),
    )
    layout = base_layout(height)
    fig.update_layout(**layout)
    return fig

def chart_client_source(height=300):
    df_s = df_clients["客戶來源"].value_counts().reset_index()
    df_s.columns = ["來源","數量"]
    fig = px.bar(df_s, x="來源", y="數量",
                 color="數量", color_continuous_scale=["#1a2a4a","#34d399"],
                 text="數量")
    fig.update_traces(textposition="outside", marker_line_width=0, opacity=0.92)
    layout = base_layout(height, legend=False)
    layout["coloraxis_showscale"] = False
    layout.update(
        xaxis=ax(showgrid=False),
        yaxis=ax(showgrid=True),
    )
    fig.update_layout(**layout)
    return fig

def chart_gift_stacked(height=340):
    """禮品庫存 — 100% stacked bar"""
    df_g = df_gifts.copy()
    total = df_g["數量"].replace(0, 1)
    df_g["已領用%"] = (df_g["已領用數量"] / total * 100).round(1)
    df_g["剩餘%"]   = (df_g["剩餘數量"]   / total * 100).round(1)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="已領用", x=df_g["禮品名稱"], y=df_g["已領用%"],
        marker_color="#f472b6", marker_line_width=0, opacity=0.9,
        text=[f"{v}%" for v in df_g["已領用%"]], textposition="inside",
        textfont=dict(color="white", size=11),
    ))
    fig.add_trace(go.Bar(
        name="剩餘", x=df_g["禮品名稱"], y=df_g["剩餘%"],
        marker_color="#5b8dee", marker_line_width=0, opacity=0.9,
        text=[f"{v}%" for v in df_g["剩餘%"]], textposition="inside",
        textfont=dict(color="white", size=11),
    ))
    layout = base_layout(height)
    layout["barmode"] = "stack"
    layout.update(
        xaxis=ax(showgrid=False),
        yaxis=ax(showgrid=True, title="佔比 %", range=[0, 105]),
    )
    fig.update_layout(**layout)
    return fig

def chart_crm(height=300):
    df_c = df_crm.groupby("維護內容")["費用"].sum().reset_index().sort_values("費用", ascending=False)
    fig = px.bar(df_c, x="維護內容", y="費用",
                 color="費用", color_continuous_scale=["#1a2a4a","#fbbf24"],
                 text="費用")
    fig.update_traces(texttemplate="%{text:,.0f}$", textposition="outside",
                      marker_line_width=0, opacity=0.92)
    layout = base_layout(height, legend=False)
    layout["coloraxis_showscale"] = False
    layout.update(
        xaxis=ax(showgrid=False),
        yaxis=ax(showgrid=True),
    )
    fig.update_layout(**layout)
    return fig

# ─────────────────────────────────────────────────────────────────────────────
# KPI 列
# ─────────────────────────────────────────────────────────────────────────────
def kpi_row():
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("當季總目標",   fmt(total_target))
    k2.metric("當季實際完成", fmt(total_achieve))
    k3.metric("整體達成率",   f"{total_rate}%",
              delta=f"{'↑' if total_rate >= 80 else '↓'} 目標 80%")
    k4.metric("銷售金額合計", fmt(total_sales))

# ─────────────────────────────────────────────────────────────────────────────
# PAGE : 首頁總覽
# ─────────────────────────────────────────────────────────────────────────────
if page == "🏠 首頁總覽":
    st.markdown("## 營銷目標管理 Dashboard")
    st.markdown("---")
    kpi_row()
    st.markdown("---")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='section-title'>目標 vs 實際完成</div>", unsafe_allow_html=True)
        st.plotly_chart(chart_area_target(), use_container_width=True)
    with c2:
        st.markdown("<div class='section-title'>達成率排名（基準 80%）</div>", unsafe_allow_html=True)
        st.plotly_chart(chart_deviation(), use_container_width=True)

    st.markdown("---")
    b1, b2 = st.columns(2)
    with b1:
        st.markdown("<div class='section-title'>提成金額 Top 5</div>", unsafe_allow_html=True)
        st.plotly_chart(chart_top5(), use_container_width=True)
    with b2:
        st.markdown("<div class='section-title'>產品銷售金額分佈</div>", unsafe_allow_html=True)
        st.plotly_chart(chart_product_pie(), use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE : 全覽 Dashboard
# ─────────────────────────────────────────────────────────────────────────────
elif page == "📊 全覽 Dashboard":
    st.markdown("## 📊 全覽 Dashboard")
    st.markdown("---")
    kpi_row()
    st.markdown("---")

    # Row 1
    r1a, r1b = st.columns(2)
    with r1a:
        st.markdown("<div class='section-title'>目標 vs 實際完成</div>", unsafe_allow_html=True)
        st.plotly_chart(chart_area_target(270), use_container_width=True)
    with r1b:
        st.markdown("<div class='section-title'>達成率排名</div>", unsafe_allow_html=True)
        st.plotly_chart(chart_deviation(270), use_container_width=True)

    # Row 2
    r2a, r2b, r2c = st.columns(3)
    with r2a:
        st.markdown("<div class='section-title'>提成 Top 5</div>", unsafe_allow_html=True)
        st.plotly_chart(chart_top5(240), use_container_width=True)
    with r2b:
        st.markdown("<div class='section-title'>產品銷售分佈</div>", unsafe_allow_html=True)
        st.plotly_chart(chart_product_pie(240), use_container_width=True)
    with r2c:
        st.markdown("<div class='section-title'>客戶等級分佈</div>", unsafe_allow_html=True)
        st.plotly_chart(chart_client_grade(240), use_container_width=True)

    # Row 3
    r3a, r3b = st.columns(2)
    with r3a:
        st.markdown("<div class='section-title'>業務員銷售金額</div>", unsafe_allow_html=True)
        st.plotly_chart(chart_sales_by_person(300), use_container_width=True)
    with r3b:
        st.markdown("<div class='section-title'>禮品庫存比例</div>", unsafe_allow_html=True)
        st.plotly_chart(chart_gift_stacked(300), use_container_width=True)

    # Row 4 — 銷售明細表（可滾輪縮放）
    st.markdown("---")
    st.markdown("<div class='section-title'>銷售明細（可縮放）</div>", unsafe_allow_html=True)
    cols = ["單號","銷售日期","業務員","公司名稱","產品名稱","數量","銷售單價","銷售金額"]
    avail = [c for c in cols if c in df_sales.columns]
    df_s_fmt = df_sales[avail].copy()
    for c in ["銷售金額","銷售單價"]:
        if c in df_s_fmt.columns:
            df_s_fmt[c] = df_s_fmt[c].apply(lambda x: f"{x:,.0f}$")
    st.dataframe(df_s_fmt, use_container_width=True, hide_index=True, height=280)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE : 目標達成分析
# ─────────────────────────────────────────────────────────────────────────────
elif page == "🎯 目標達成分析":
    st.markdown("## 🎯 業務員目標達成分析")
    st.markdown("---")

    df_show = df_achieve[["姓名","當季目標","實際完成","達成率","提出金額","排名"]].copy()
    df_show["當季目標"] = df_show["當季目標"].apply(fmt)
    df_show["實際完成"] = df_show["實際完成"].apply(fmt)
    df_show["提出金額"] = df_show["提出金額"].apply(fmt)
    df_show["達成率"]   = df_show["達成率"].apply(lambda x: f"{x}%")
    st.dataframe(df_show, use_container_width=True, hide_index=True, height=460)

    st.markdown("---")
    t1, t2 = st.columns(2)
    with t1:
        st.markdown("<div class='section-title'>各季度目標分佈</div>", unsafe_allow_html=True)
        st.plotly_chart(chart_quarterly(), use_container_width=True)
    with t2:
        st.markdown("<div class='section-title'>年度目標總覽</div>", unsafe_allow_html=True)
        st.plotly_chart(chart_annual(), use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE : 銷售明細
# ─────────────────────────────────────────────────────────────────────────────
elif page == "💰 銷售明細":
    st.markdown("## 💰 銷售明細")
    st.markdown("---")

    # 滾輪縮放區間 slider
    all_dates = df_sales["銷售日期"].astype(str).unique().tolist()
    cols = ["單號","銷售日期","業務員","公司名稱","產品名稱","數量","銷售單價","銷售金額"]
    avail = [c for c in cols if c in df_sales.columns]
    df_disp = df_sales[avail].copy()
    for c in ["銷售金額","銷售單價"]:
        if c in df_disp.columns:
            df_disp[c] = df_disp[c].apply(lambda x: f"{x:,.0f}$")

    total_rows = len(df_disp)
    row_range = st.slider("顯示資料筆數範圍（滾輪調整）", 1, total_rows,
                           (1, min(total_rows, 14)), key="sales_range")
    st.dataframe(df_disp.iloc[row_range[0]-1:row_range[1]],
                 use_container_width=True, hide_index=True, height=400)

    st.markdown("---")
    s1, s2 = st.columns(2)
    with s1:
        st.markdown("<div class='section-title'>業務員銷售金額</div>", unsafe_allow_html=True)
        st.plotly_chart(chart_sales_by_person(), use_container_width=True)
    with s2:
        st.markdown("<div class='section-title'>各產品銷售數量</div>", unsafe_allow_html=True)
        st.plotly_chart(chart_product_qty(), use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE : 客戶分析
# ─────────────────────────────────────────────────────────────────────────────
elif page == "👥 客戶分析":
    st.markdown("## 👥 客戶分析")
    st.markdown("---")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='section-title'>客戶等級分佈</div>", unsafe_allow_html=True)
        st.plotly_chart(chart_client_grade(), use_container_width=True)
    with c2:
        st.markdown("<div class='section-title'>客戶來源分佈</div>", unsafe_allow_html=True)
        st.plotly_chart(chart_client_source(), use_container_width=True)

    st.markdown("---")
    st.markdown("<div class='section-title'>客戶列表</div>", unsafe_allow_html=True)
    dcols = [c for c in ["客戶編碼","公司名稱","連絡人","客戶等級","客戶來源"] if c in df_clients.columns]
    st.dataframe(df_clients[dcols], use_container_width=True, hide_index=True, height=400)

    if "費用" in df_crm.columns and df_crm["費用"].sum() > 0:
        st.markdown("---")
        st.markdown("<div class='section-title'>客戶關係維護費用</div>", unsafe_allow_html=True)
        st.plotly_chart(chart_crm(), use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE : 禮品庫存
# ─────────────────────────────────────────────────────────────────────────────
elif page == "🎁 禮品庫存":
    st.markdown("## 🎁 禮品庫存管理")
    st.markdown("---")

    # KPI
    g1, g2, g3 = st.columns(3)
    g1.metric("禮品種類",   f"{len(df_gifts)} 種")
    g2.metric("已領用總數", f"{int(df_gifts['已領用數量'].sum())} 件")
    g3.metric("剩餘總數",   f"{int(df_gifts['剩餘數量'].sum())} 件")

    st.markdown("---")
    st.dataframe(df_gifts, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("<div class='section-title'>庫存使用比例（100% 堆疊）</div>", unsafe_allow_html=True)
    st.plotly_chart(chart_gift_stacked(380), use_container_width=True)
