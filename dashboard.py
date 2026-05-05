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

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700&display=swap');

.stApp { background-color: #0e1117; color: #e0e0e0; font-family: 'Noto Sans TC', sans-serif; }
[data-testid="stSidebar"] { background-color: #161b27; border-right: 1px solid #2a3040; }
[data-testid="stSidebar"] * { color: #c9d1e0 !important; }
.section-title { font-size: 1.4rem; font-weight: 700; color: #e0e0e0; margin-bottom: 0.5rem; }
hr { border-color: #2a3040 !important; }
[data-testid="stMetricDelta"] { font-size: 0.8rem; }
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

def sheet_url(gid: str) -> str:
    return f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}"

# ── 載入資料（每 10 分鐘自動更新）────────────────────────────────────────────
@st.cache_data(ttl=600)
def load_sheet(name: str) -> pd.DataFrame:
    return pd.read_csv(sheet_url(GIDS[name]))

@st.cache_data(ttl=600)
def load_all():
    return {name: load_sheet(name) for name in GIDS}

# ── 讀取所有分頁 ──────────────────────────────────────────────────────────────
try:
    sheets     = load_all()
    df_target  = sheets["業務員年度銷售目標表"]
    df_achieve = sheets["業務員目標完成分析表"]
    df_sales   = sheets["銷售明細"]
    df_clients = sheets["客戶資訊"]
    df_gifts   = sheets["禮品庫存表"]
    df_crm     = sheets["客戶關係維護表"]
except Exception as e:
    st.error(f"❌ 無法連接 Google Sheet，請確認試算表已設為「知道連結的任何人可以檢視」。\n\n錯誤：{e}")
    st.stop()

# ── 數值欄位強制轉型 ──────────────────────────────────────────────────────────
for col in ["當季目標", "實際完成", "提出金額"]:
    if col in df_achieve.columns:
        df_achieve[col] = pd.to_numeric(df_achieve[col], errors="coerce").fillna(0)

for col in ["第一季度目標","第二季度目標","第三季度目標","第四季度目標","年度目標"]:
    if col in df_target.columns:
        df_target[col] = pd.to_numeric(df_target[col], errors="coerce").fillna(0)

df_sales["銷售金額"] = pd.to_numeric(df_sales.get("銷售金額", 0), errors="coerce").fillna(0)
df_sales["數量"]     = pd.to_numeric(df_sales.get("數量", 0),     errors="coerce").fillna(0)

# ── 衍生指標 ──────────────────────────────────────────────────────────────────
df_achieve["達成率"] = (
    df_achieve["實際完成"] / df_achieve["當季目標"].replace(0, pd.NA) * 100
).round(1).fillna(0)
total_target  = df_achieve["當季目標"].sum()
total_achieve = df_achieve["實際完成"].sum()
total_rate    = round(total_achieve / total_target * 100, 1) if total_target else 0
total_sales   = df_sales["銷售金額"].sum()

# ── Plotly 共用 layout ────────────────────────────────────────────────────────
DARK = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#8899aa", size=11),
    margin=dict(l=10, r=10, t=30, b=30),
    xaxis=dict(linecolor="#2a3040", gridcolor="#1e2535"),
    yaxis=dict(linecolor="#2a3040", gridcolor="#1e2535"),
)
LEGEND = dict(font=dict(color="#aabbcc"), bgcolor="rgba(0,0,0,0)")

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📋 主選單")
    st.markdown("---")
    page = st.radio(
        label="",
        options=["🏠 首頁總覽", "🎯 目標達成分析", "💰 銷售明細", "👥 客戶分析", "🎁 禮品庫存"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    if st.button("🔄 重新整理資料"):
        st.cache_data.clear()
        st.rerun()
    st.markdown(
        "<div style='font-size:0.75rem;color:#556;margin-top:12px;'>"
        "資料來源：Google Sheets<br>每 10 分鐘自動更新</div>",
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────────────────────────────────────
# PAGE 1 : 首頁總覽
# ─────────────────────────────────────────────────────────────────────────────
if page == "🏠 首頁總覽":
    st.markdown("## 營銷目標管理 Dashboard")
    st.markdown("---")

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("當季總目標",   f"¥{total_target:,.0f}")
    k2.metric("當季實際完成", f"¥{total_achieve:,.0f}")
    k3.metric("整體達成率",   f"{total_rate}%",
              delta=f"{'↑' if total_rate >= 80 else '↓'} 目標 80%")
    k4.metric("銷售金額合計", f"¥{total_sales:,.0f}")

    st.markdown("---")
    col_left, col_right = st.columns(2)

    # Chart 1 — 目標 vs 實際完成（面積圖）
    with col_left:
        st.markdown("<div class='section-title'>目標 vs 實際完成</div>", unsafe_allow_html=True)
        names = df_achieve["姓名"].tolist()
        x = list(range(len(names)))
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=x, y=df_achieve["當季目標"].tolist(),
            name="當季目標", mode="lines",
            line=dict(color="#4895ef", width=2),
            fill="tozeroy", fillcolor="rgba(72,149,239,0.25)",
        ))
        fig1.add_trace(go.Scatter(
            x=x, y=df_achieve["實際完成"].tolist(),
            name="實際完成", mode="lines",
            line=dict(color="#f07167", width=2),
            fill="tozeroy", fillcolor="rgba(240,113,103,0.25)",
        ))
        fig1.update_layout(
            **DARK, height=290,
            legend=dict(**LEGEND, orientation="h", yanchor="bottom", y=1.02,
                        xanchor="center", x=0.5),
            xaxis=dict(showgrid=False, tickvals=x, ticktext=names, tickangle=-45,
                       linecolor="#2a3040"),
        )
        st.plotly_chart(fig1, use_container_width=True)

    # Chart 2 — 達成率偏差柱狀圖（正負雙色）
    with col_right:
        st.markdown("<div class='section-title'>達成率排名（基準 80%）</div>", unsafe_allow_html=True)
        df_sorted  = df_achieve.sort_values("達成率", ascending=False)
        deviation  = df_sorted["達成率"] - 80
        bar_colors = ["#4895ef" if v >= 0 else "#f07167" for v in deviation]
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=list(range(len(df_sorted))),
            y=deviation.tolist(),
            marker_color=bar_colors,
            text=[f"{r}%" for r in df_sorted["達成率"]],
            textposition="outside",
            textfont=dict(size=9, color="#8899aa"),
        ))
        fig2.update_layout(
            **DARK, height=310, showlegend=False,
            xaxis=dict(showgrid=False, tickvals=list(range(len(df_sorted))),
                       ticktext=df_sorted["姓名"].tolist(), tickangle=-45,
                       linecolor="#2a3040"),
            yaxis=dict(gridcolor="#1e2535", linecolor="#2a3040",
                       title="偏差 % (基準 80%)"),
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    b1, b2 = st.columns(2)

    with b1:
        st.markdown("<div class='section-title'>提成金額 Top 5</div>", unsafe_allow_html=True)
        df_top5 = df_achieve.nlargest(5, "提出金額")[["姓名", "提出金額", "達成率"]]
        fig3 = px.bar(df_top5, x="提出金額", y="姓名", orientation="h",
                      color="達成率", color_continuous_scale=["#f07167", "#4cc9f0"],
                      labels={"提出金額": "提成金額 (¥)", "達成率": "達成率 %"})
        fig3.update_layout(**DARK, height=260, coloraxis_showscale=False)
        st.plotly_chart(fig3, use_container_width=True)

    with b2:
        st.markdown("<div class='section-title'>產品銷售金額分佈</div>", unsafe_allow_html=True)
        df_prod = df_sales.groupby("產品名稱")["銷售金額"].sum().reset_index()
        fig4 = px.pie(df_prod, names="產品名稱", values="銷售金額",
                      color_discrete_sequence=px.colors.sequential.Blues_r, hole=0.45)
        fig4.update_layout(**DARK, height=260, showlegend=True, legend=LEGEND)
        st.plotly_chart(fig4, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE 2 : 目標達成分析
# ─────────────────────────────────────────────────────────────────────────────
elif page == "🎯 目標達成分析":
    st.markdown("## 🎯 業務員目標達成分析")
    st.markdown("---")

    df_show = df_achieve[["姓名", "當季目標", "實際完成", "達成率", "提出金額", "排名"]].copy()
    df_show["當季目標"] = df_show["當季目標"].apply(lambda x: f"¥{x:,.0f}")
    df_show["實際完成"] = df_show["實際完成"].apply(lambda x: f"¥{x:,.0f}")
    df_show["提出金額"] = df_show["提出金額"].apply(lambda x: f"¥{x:,.0f}")
    df_show["達成率"]   = df_show["達成率"].apply(lambda x: f"{x}%")
    st.dataframe(df_show, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("<div class='section-title'>各業務員年度季度目標分佈</div>", unsafe_allow_html=True)
    quarters = ["第一季度目標", "第二季度目標", "第三季度目標", "第四季度目標"]
    colors_q = ["#4895ef", "#4cc9f0", "#f07167", "#ffd166"]
    fig_q = go.Figure()
    for i, q in enumerate(quarters):
        fig_q.add_trace(go.Bar(name=q, x=df_target["姓名"], y=df_target[q],
                               marker_color=colors_q[i]))
    fig_q.update_layout(**DARK, barmode="group", height=370, legend=LEGEND)
    st.plotly_chart(fig_q, use_container_width=True)

    st.markdown("---")
    st.markdown("<div class='section-title'>年度目標總覽</div>", unsafe_allow_html=True)
    fig_annual = px.bar(
        df_target.sort_values("年度目標", ascending=True),
        x="年度目標", y="姓名", orientation="h",
        color="年度目標", color_continuous_scale=["#1a2a4a", "#4895ef"],
        text="年度目標",
    )
    fig_annual.update_traces(texttemplate="¥%{text:,.0f}", textposition="outside")
    fig_annual.update_layout(**DARK, height=380, coloraxis_showscale=False)
    st.plotly_chart(fig_annual, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE 3 : 銷售明細
# ─────────────────────────────────────────────────────────────────────────────
elif page == "💰 銷售明細":
    st.markdown("## 💰 銷售明細")
    st.markdown("---")

    cols = ["單號", "銷售日期", "業務員", "公司名稱", "產品名稱", "數量", "銷售單價", "銷售金額"]
    available = [c for c in cols if c in df_sales.columns]
    st.dataframe(df_sales[available], use_container_width=True, hide_index=True)

    st.markdown("---")
    s1, s2 = st.columns(2)

    with s1:
        st.markdown("<div class='section-title'>業務員銷售金額</div>", unsafe_allow_html=True)
        df_by_sales = (df_sales.groupby("業務員")["銷售金額"].sum()
                       .reset_index().sort_values("銷售金額", ascending=True))
        fig_s = px.bar(df_by_sales, x="銷售金額", y="業務員", orientation="h",
                       color_discrete_sequence=["#4895ef"], text="銷售金額")
        fig_s.update_traces(texttemplate="¥%{text:,.0f}", textposition="outside")
        fig_s.update_layout(**DARK, height=380)
        st.plotly_chart(fig_s, use_container_width=True)

    with s2:
        st.markdown("<div class='section-title'>各產品銷售數量</div>", unsafe_allow_html=True)
        df_qty = (df_sales.groupby("產品名稱")["數量"].sum()
                  .reset_index().sort_values("數量", ascending=False))
        fig_qty = px.bar(df_qty, x="產品名稱", y="數量",
                         color_discrete_sequence=["#4cc9f0"])
        fig_qty.update_layout(**DARK, height=380,
                              xaxis=dict(tickangle=-30, linecolor="#2a3040", showgrid=False))
        st.plotly_chart(fig_qty, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE 4 : 客戶分析
# ─────────────────────────────────────────────────────────────────────────────
elif page == "👥 客戶分析":
    st.markdown("## 👥 客戶分析")
    st.markdown("---")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("<div class='section-title'>客戶等級分佈</div>", unsafe_allow_html=True)
        df_grade = df_clients["客戶等級"].value_counts().reset_index()
        df_grade.columns = ["客戶等級", "數量"]
        fig_g = px.pie(df_grade, names="客戶等級", values="數量", hole=0.42,
                       color_discrete_sequence=["#4895ef","#4cc9f0","#f07167","#ffd166","#a8dadc"])
        fig_g.update_layout(**DARK, height=300, legend=LEGEND)
        st.plotly_chart(fig_g, use_container_width=True)

    with c2:
        st.markdown("<div class='section-title'>客戶來源分佈</div>", unsafe_allow_html=True)
        df_src = df_clients["客戶來源"].value_counts().reset_index()
        df_src.columns = ["來源", "數量"]
        fig_src = px.bar(df_src, x="來源", y="數量",
                         color_discrete_sequence=["#4cc9f0"], text="數量")
        fig_src.update_traces(textposition="outside")
        fig_src.update_layout(**DARK, height=300,
                              xaxis=dict(showgrid=False, linecolor="#2a3040"))
        st.plotly_chart(fig_src, use_container_width=True)

    st.markdown("---")
    st.markdown("<div class='section-title'>客戶列表</div>", unsafe_allow_html=True)
    display_cols = [c for c in ["客戶編碼","公司名稱","連絡人","客戶等級","客戶來源"]
                    if c in df_clients.columns]
    st.dataframe(df_clients[display_cols], use_container_width=True, hide_index=True)

    if "費用" in df_crm.columns:
        st.markdown("---")
        st.markdown("<div class='section-title'>客戶關係維護費用（依維護類型）</div>",
                    unsafe_allow_html=True)
        df_crm["費用"] = pd.to_numeric(df_crm["費用"], errors="coerce").fillna(0)
        df_crm_g = (df_crm.groupby("維護內容")["費用"].sum()
                    .reset_index().sort_values("費用", ascending=False))
        fig_crm = px.bar(df_crm_g, x="維護內容", y="費用",
                         color_discrete_sequence=["#f07167"], text="費用")
        fig_crm.update_traces(texttemplate="¥%{text:,.0f}", textposition="outside")
        fig_crm.update_layout(**DARK, height=300,
                              xaxis=dict(showgrid=False, linecolor="#2a3040"))
        st.plotly_chart(fig_crm, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE 5 : 禮品庫存
# ─────────────────────────────────────────────────────────────────────────────
elif page == "🎁 禮品庫存":
    st.markdown("## 🎁 禮品庫存管理")
    st.markdown("---")

    for col in ["數量", "已領用數量", "剩餘數量"]:
        if col in df_gifts.columns:
            df_gifts[col] = pd.to_numeric(df_gifts[col], errors="coerce").fillna(0)

    st.dataframe(df_gifts, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("<div class='section-title'>庫存 vs 已領用 vs 剩餘</div>", unsafe_allow_html=True)
    fig_gift = go.Figure()
    fig_gift.add_trace(go.Bar(name="總數量",  x=df_gifts["禮品名稱"], y=df_gifts["數量"],
                              marker_color="#4895ef"))
    fig_gift.add_trace(go.Bar(name="已領用", x=df_gifts["禮品名稱"], y=df_gifts["已領用數量"],
                              marker_color="#f07167"))
    fig_gift.add_trace(go.Bar(name="剩餘",   x=df_gifts["禮品名稱"], y=df_gifts["剩餘數量"],
                              marker_color="#4cc9f0"))
    fig_gift.update_layout(**DARK, barmode="group", height=350, legend=LEGEND)
    st.plotly_chart(fig_gift, use_container_width=True)

    st.markdown("---")
    st.markdown("<div class='section-title'>剩餘庫存比例</div>", unsafe_allow_html=True)
    df_gifts["剩餘率"] = (df_gifts["剩餘數量"] / df_gifts["數量"] * 100).round(1)
    fig_pct = px.bar(df_gifts, x="禮品名稱", y="剩餘率",
                     color="剩餘率",
                     color_continuous_scale=["#f07167", "#ffd166", "#4cc9f0"],
                     text="剩餘率", range_color=[0, 100])
    fig_pct.update_traces(texttemplate="%{text}%", textposition="outside")
    fig_pct.update_layout(**DARK, height=300, coloraxis_showscale=False,
                          xaxis=dict(showgrid=False, linecolor="#2a3040"),
                          yaxis=dict(range=[0, 120], title="剩餘率 %"))
    st.plotly_chart(fig_pct, use_container_width=True)
