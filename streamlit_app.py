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
    selected_companies = st.multiselect("회사 선택", companies, default=[])

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

    if selected_companies:
        df_selected = df_year[df_year["회사명"].isin(selected_companies)]

        for _, row in df_selected.iterrows():
            # 회사별 주요 메트릭 카드
            st.metric(
                label=f"{row['회사명']} ({selected_year}) 총자산",
                value=f"{row['자산총계']:,} 억원"
            )

            # 영업이익률
            if pd.notna(row["매출액"]) and row["매출액"] != 0:
                op_margin = row["영업이익"] / row["매출액"]
                st.metric(
                    label=f"{row['회사명']} 평균 영업이익률",
                    value=f"{op_margin:.2%}"
                )

            # 흑자 여부
            profit_status = "흑자" if row["당기순이익"] > 0 else "적자"
            st.metric(
                label=f"{row['회사명']} 당기순이익",
                value=f"{row['당기순이익']:,} 억원",
                delta=profit_status
            )
            st.markdown("---")

    else:
        # 회사 선택 안 하면 기존 요약 지표 보여줌
        top_company = df_year.loc[df_year["자산총계"].idxmax()]
        st.metric(
            label=f"자산총계 1위 기업 ({selected_year})",
            value=f"{top_company['회사명']} : {top_company['자산총계']:,} 억원"
        )

        total_assets = df_year["자산총계"].sum()
        st.metric("총 자산 규모", f"{total_assets:,} 억원")

        df_year = df_year.copy()
        df_year["영업이익률"] = df_year["영업이익"] / df_year["매출액"]
        avg_op_margin = df_year["영업이익률"].mean(skipna=True)
        st.metric("평균 영업이익률", f"{avg_op_margin:.2%}")

        positive_ratio = (df_year["당기순이익"] > 0).mean()
        st.metric("흑자 기업 비율", f"{positive_ratio:.2%}")

with col[1]:
    st.subheader("📊 Main Visualizations")

    df_year = df_reshaped[df_reshaped["년도"] == selected_year].copy()

    # 선택한 재무지표를 숫자형으로 안전 변환(정렬/색상 계산 안정성)
    df_year[selected_metric] = pd.to_numeric(df_year[selected_metric], errors="coerce")

    # 선택 지표 Top 10
    top10_metric = df_year.nlargest(10, selected_metric)

    bar_chart = px.bar(
        top10_metric,
        x="회사명",
        y=selected_metric,
        title=f"{selected_year}년 {selected_metric} Top 10",
        color=selected_metric,
        color_continuous_scale=color_theme
    )
    st.plotly_chart(bar_chart, use_container_width=True)

    # 산점도는 기존 유지(자산총계 vs 영업이익)
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

    top10_table = df_year.nlargest(10, "자산총계")[["회사명", "자산총계", "영업이익", "당기순이익"]].reset_index(drop=True)
    top10_table.index = top10_table.index + 1
    top10_table.index.name = "순위"

    st.markdown(f"**{selected_year}년 자산총계 Top 10 기업**")
    st.dataframe(top10_table.style.format({
        "자산총계": "{:,}",
        "영업이익": "{:,}",
        "당기순이익": "{:,}"
    }))

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
