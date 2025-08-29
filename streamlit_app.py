#######################
# Import libraries
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

#######################
# Page configuration
st.set_page_config(
    page_title="KOSPI Asset Ranking Dashboard",
    page_icon="🏂",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("default")

#######################
# CSS styling
st.markdown("""
<style>

[data-testid="block-container"] {
    padding-left: 2rem;
    padding-right: 2rem;
    padding-top: 1rem;
    padding-bottom: 0rem;
    margin-bottom: -7rem;
}

[data-testid="stVerticalBlock"] {
    padding-left: 0rem;
    padding-right: 0rem;
}

[data-testid="stMetric"] {
    background-color: white;     /* 박스 배경 흰색 */
    color: black;                /* 숫자 및 텍스트 검정 */
    text-align: center;
    padding: 20px 0;
    min-height: 120px;           /* 박스 크기 확장 */
    margin-bottom: 15px;         /* 박스 사이 간격 */
    border-radius: 10px;
    border: 1px solid #ccc;      /* 테두리 회색 */
}

[data-testid="stMetricLabel"] {
  display: flex;
  justify-content: center;
  align-items: center;
  color: black;                  /* 라벨 글자 검정 */
  font-weight: bold;
}

[data-testid="stMetricDelta"] {
  color: black !important;       /* 변화 수치도 검정 */
}

[data-testid="stMetricDeltaIcon-Up"],
[data-testid="stMetricDeltaIcon-Down"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

</style>
""", unsafe_allow_html=True)

#######################
# Load data
df_reshaped = pd.read_excel('kospi_asset_rank_04-24.xlsx', engine="openpyxl") 

#######################
# Sidebar
with st.sidebar:
    st.title("⚙️ Dashboard Controls")

    # 연도 선택
    years = df_reshaped["년도"].dropna().unique()
    selected_year = st.selectbox("연도 선택", sorted(years, reverse=True))

    # 회사 선택
    companies = df_reshaped["회사명"].dropna().unique()
    selected_companies = st.multiselect("회사 선택", companies, default=companies[:5])

    # 재무지표 선택
    metrics = ["자산총계", "부채총계", "자본총계", "매출액", "영업이익", "당기순이익"]
    selected_metric = st.radio("재무지표 선택", metrics, index=0)

    # 컬러 테마 선택
    color_theme = st.selectbox("컬러 테마", ["Blues", "Greens", "Reds", "Viridis", "Plasma"])

#######################
# Dashboard Main Panel
col = st.columns((1.5, 4.5, 2), gap='medium')

with col[0]:
    st.subheader("📌 Key Metrics")

    # 연도별 데이터
    df_year = df_reshaped[df_reshaped["년도"] == selected_year]

    # Top 회사
    top_company = df_year.loc[df_year["자산총계"].idxmax()]
    st.metric(
        label=f"자산총계 1위 기업 ({selected_year})",
        value=f"{top_company['회사명']} : {top_company['자산총계']:,} 억원"
    )

    # 총 자산 규모
    total_assets = df_year["자산총계"].sum()
    st.metric("총 자산 규모", f"{total_assets:,} 억원")

    # 평균 영업이익률
    df_year = df_year.copy()
    df_year["영업이익률"] = df_year["영업이익"] / df_year["매출액"]
    avg_op_margin = df_year["영업이익률"].mean(skipna=True)
    st.metric("평균 영업이익률", f"{avg_op_margin:.2%}")

    # 흑자 기업 비율
    positive_ratio = (df_year["당기순이익"] > 0).mean()
    st.metric("흑자 기업 비율", f"{positive_ratio:.2%}")

with col[1]:
    st.subheader("📊 Main Visualizations")

    df_year = df_reshaped[df_reshaped["년도"] == selected_year]

    # 자산총계 Top 10
    top10_assets = df_year.nlargest(10, "자산총계")

    bar_chart = px.bar(
        top10_assets,
        x="회사명",
        y="자산총계",
        title=f"{selected_year}년 자산총계 Top 10",
        color="자산총계",
        color_continuous_scale=color_theme
    )
    st.plotly_chart(bar_chart, use_container_width=True)

    # 자산총계 vs 영업이익 산점도
    scatter = px.scatter(
        df_year,
        x="자산총계",
        y="영업이익",
        size="매출액",
        color="당기순이익",
        hover_name="회사명",
        title=f"{selected_year}년 자산총계 vs 영업이익",
        color_continuous_scale=color_theme
    )
    st.plotly_chart(scatter, use_container_width=True)

with col[2]:
    st.subheader("🏆 Rankings & Details")

    df_year = df_reshaped[df_reshaped["년도"] == selected_year]

    # Top 10 기업 랭킹 (순위 1부터 시작)
    top10_table = df_year.nlargest(10, "자산총계")[["회사명", "자산총계", "영업이익", "당기순이익"]].reset_index(drop=True)
    top10_table.index = top10_table.index + 1  # 순위 1부터
    top10_table.index.name = "순위"

    st.markdown(f"**{selected_year}년 자산총계 Top 10 기업**")
    st.dataframe(top10_table.style.format({
        "자산총계": "{:,}",
        "영업이익": "{:,}",
        "당기순이익": "{:,}"
    }))

    # 데이터 설명
    st.markdown("---")
    st.subheader("ℹ️ About Data")
    st.write("""
    - **자산총계**: 기업이 보유한 총자산  
    - **부채총계**: 기업이 부담하는 총부채  
    - **자본총계**: 자산 - 부채  
    - **매출액**: 일정 기간 동안 벌어들인 총 매출  
    - **영업이익**: 본업에서 발생한 이익  
    - **당기순이익**: 최종 손익 (세금 등 반영 후)  

    데이터 출처: 금융감독원/거래소 공시 자료 기반  
    """)
