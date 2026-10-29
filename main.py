
import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(
    page_title="SchoolMove | 등하교 교통비 계산기",
    page_icon="🚌",
    layout="wide"
)

# 디자인
st.markdown("""
<style>
    .block-container {
        max-width: 1100px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    div[data-testid="stMetric"] {
        background: #f8fafc;
        padding: 16px;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
    }
</style>
""", unsafe_allow_html=True)

# 제목
st.title("🚌 SchoolMove")
st.write("등하교 교통비를 계산하고 교통수단별 비용을 비교해 보세요.")

# 입력 UI
st.subheader("통학비 미리 계산해 보기")

fare = st.number_input(
    "편도 1회 요금 (원)",
    min_value=0,
    value=1500,
    step=50
)

trips = st.selectbox(
    "하루 이용 횟수",
    options=[1, 2, 4],
    index=1,
    format_func=lambda x: {
        1: "편도 1회",
        2: "왕복 2회",
        4: "하루 4회"
    }[x]
)

days = st.number_input(
    "월간 등교 일수",
    min_value=1,
    max_value=31,
    value=20,
    step=1
)

budget = st.number_input(
    "월간 교통비 예산 (원)",
    min_value=0,
    value=70000,
    step=5000
)

# 계산 결과
daily_cost = fare * trips
monthly_cost = daily_cost * days
annual_cost = monthly_cost * 12
remaining = budget - monthly_cost

st.divider()
st.subheader("계산 결과")

col1, col2 = st.columns(2)

with col1:
    st.metric("하루 교통비", f"{daily_cost:,}원")
    st.metric("연간 예상 교통비", f"{annual_cost:,}원")

with col2:
    st.metric("월간 교통비", f"{monthly_cost:,}원")
    st.metric("예산 대비 잔액", f"{remaining:,}원")

if budget > 0:
    usage = monthly_cost / budget

    st.write(f"월간 예산 사용률: {usage * 100:.1f}%")
    st.progress(min(usage, 1.0))

    if remaining < 0:
        st.error(f"월간 예산을 {-remaining:,}원 초과했습니다.")
    else:
        st.success("설정한 월간 교통비 예산 이내입니다.")
else:
    st.info("예산을 0원보다 크게 설정하면 사용률을 확인할 수 있습니다.")

# 교통수단별 요금 입력
st.divider()
st.subheader("교통수단별 요금 비교")
st.caption("아래 요금은 예시입니다. 실제 결제 요금에 맞게 수정하세요.")

col1, col2 = st.columns(2)

with col1:
    bus_fare = st.number_input(
        "버스 편도 요금 (원)",
        min_value=0,
        value=1500,
        step=50
    )

    subway_fare = st.number_input(
        "지하철 편도 요금 (원)",
        min_value=0,
        value=1500,
        step=50
    )

with col2:
    transfer_fare = st.number_input(
        "버스 + 지하철 환승 요금 (원)",
        min_value=0,
        value=1600,
        step=50
    )

    other_fare = st.number_input(
        "기타 교통수단 편도 요금 (원)",
        min_value=0,
        value=2000,
        step=50
    )

fares = {
    "버스": bus_fare,
    "지하철": subway_fare,
    "버스 + 지하철 환승": transfer_fare,
    "기타 교통수단": other_fare
}

# 비교 데이터 생성
records = []

for name, price in fares.items():
    daily = price * trips
    monthly = daily * days
    annual = monthly * 12

    records.append({
        "교통수단": name,
        "편도 요금": price,
        "하루 교통비": daily,
        "월간 교통비": monthly,
        "연간 교통비": annual
    })

df = pd.DataFrame(records)

# 비용 비교 표
st.subheader("교통수단별 예상 비용")

display_df = df.copy()

for column in [
    "편도 요금",
    "하루 교통비",
    "월간 교통비",
    "연간 교통비"
]:
    display_df[column] = display_df[column].apply(
        lambda value: f"{value:,}원"
    )

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)

# 월간 비용 그래프
st.subheader("월간 교통비 비교 그래프")

fig = px.bar(
    df,
    x="교통수단",
    y="월간 교통비",
    color="교통수단",
    text="월간 교통비",
    title="교통수단별 월간 예상 교통비"
)

fig.update_traces(
    texttemplate="%{text:,}원",
    textposition="outside",
    cliponaxis=False
)

fig.update_layout(
    showlegend=False,
    xaxis_title="교통수단",
    yaxis_title="월간 교통비 (원)",
    yaxis_rangemode="tozero",
    margin=dict(t=60, b=20)
)

st.plotly_chart(fig, use_container_width=True)

# 등교 일수별 그래프
st.subheader("등교 일수에 따른 교통비 변화")

days_data = pd.DataFrame({
    "등교 일수": list(range(1, 32))
})

for name, price in fares.items():
    days_data[name] = (
        days_data["등교 일수"] * trips * price
    )

long_data = days_data.melt(
    id_vars="등교 일수",
    var_name="교통수단",
    value_name="월간 교통비"
)

fig2 = px.line(
    long_data,
    x="등교 일수",
    y="월간 교통비",
    color="교통수단",
    markers=True,
    title="등교 일수별 예상 교통비"
)

fig2.update_layout(
    xaxis_title="월간 등교 일수 (일)",
    yaxis_title="월간 교통비 (원)",
    yaxis_rangemode="tozero"
)

st.plotly_chart(fig2, use_container_width=True)

# 절약 분석
st.divider()
st.subheader("교통비 절약 분석")

selected_transport = st.selectbox(
    "현재 주로 이용하는 교통수단",
    list(fares.keys())
)

selected_fare = fares[selected_transport]

cheaper = {
    name: price
    for name, price in fares.items()
    if price < selected_fare
}

if cheaper:
    alternative = min(cheaper, key=cheaper.get)

    saving_monthly = (
        selected_fare - cheaper[alternative]
    ) * trips * days

    saving_annual = saving_monthly * 12

    st.write(f"현재 교통수단: **{selected_transport}**")
    st.write(f"저렴한 대안: **{alternative}**")

    col1, col2 = st.columns(2)

    col1.metric(
        "월간 예상 절약 금액",
        f"{saving_monthly:,}원"
    )

    col2.metric(
        "연간 예상 절약 금액",
        f"{saving_annual:,}원"
    )

else:
    st.info(
        "선택한 교통수단보다 저렴한 대안이 없습니다. "
        "요금을 수정하면 다시 비교할 수 있습니다."
    )

# CSV 다운로드
st.divider()
st.subheader("계산 결과 저장")

csv_data = df.to_csv(index=False).encode("utf-8-sig")

st.download_button(
    label="📥 교통비 결과 CSV 다운로드",
    data=csv_data,
    file_name="schoolmove_results.csv",
    mime="text/csv"
)

# 안내
st.caption(
    "본 프로그램은 입력한 요금을 바탕으로 예상 비용을 계산합니다. "
    "실제 지출은 학생 할인, 환승 할인, 정기권, 방학 및 결석 등에 따라 "
    "달라질 수 있습니다. 연간 비용은 월간 비용이 12개월 동안 "
    "동일하다고 가정한 값입니다."
)
