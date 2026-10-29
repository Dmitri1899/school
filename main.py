
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="SchoolMove | 등하교 교통비 계산기",
    page_icon="🚌",
    layout="wide"
)

st.title("🚌 SchoolMove")
st.subheader("스마트 등하교 교통비 계산기")
st.write("등하교 교통비를 계산하고 교통수단별 비용을 비교해 보세요.")

st.sidebar.header("⚙️ 통학 조건 설정")

days = st.sidebar.number_input(
    "한 달 등교 일수",
    min_value=1,
    max_value=31,
    value=20
)

trips = st.sidebar.selectbox(
    "하루 이용 횟수",
    [1, 2, 3, 4],
    index=1
)

budget = st.sidebar.number_input(
    "월간 교통비 예산 (원)",
    min_value=0,
    value=70000,
    step=5000
)

st.info("아래 요금은 예시입니다. 실제 결제 요금에 맞게 수정하세요.")

st.header("1. 교통수단별 요금 입력")

col1, col2, col3, col4 = st.columns(4)

with col1:
    bus = st.number_input(
        "버스 편도 요금 (원)",
        min_value=0,
        value=1500,
        step=50
    )

with col2:
    subway = st.number_input(
        "지하철 편도 요금 (원)",
        min_value=0,
        value=1500,
        step=50
    )

with col3:
    transfer = st.number_input(
        "환승 시 편도 요금 (원)",
        min_value=0,
        value=1600,
        step=50
    )

with col4:
    other = st.number_input(
        "기타 교통수단 편도 요금 (원)",
        min_value=0,
        value=2000,
        step=50
    )

fares = {
    "버스": bus,
    "지하철": subway,
    "버스 + 지하철 환승": transfer,
    "기타 교통수단": other
}

st.divider()
st.header("2. 나의 예상 교통비")

selected = st.selectbox(
    "주로 이용하는 교통수단",
    list(fares.keys())
)

fare = fares[selected]

daily_cost = fare * trips
monthly_cost = daily_cost * days
annual_cost = monthly_cost * 12
remaining = budget - monthly_cost

m1, m2, m3, m4 = st.columns(4)

m1.metric("하루 교통비", f"{daily_cost:,}원")
m2.metric("월간 교통비", f"{monthly_cost:,}원")
m3.metric("연간 교통비", f"{annual_cost:,}원")
m4.metric("예산 잔액", f"{remaining:,}원")

if budget > 0:
    usage = monthly_cost / budget
    st.write(f"월간 예산 사용률: {usage * 100:.1f}%")
    st.progress(min(usage, 1.0))

    if monthly_cost > budget:
        st.error(
            f"예산을 {monthly_cost - budget:,}원 초과했습니다."
        )
    else:
        st.success(
            f"예산 이내입니다. "
            f"남은 금액은 {remaining:,}원입니다."
        )
else:
    st.warning("예산을 0원보다 크게 설정하면 사용률을 확인할 수 있습니다.")

st.divider()
st.header("3. 교통수단별 비용 비교")

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

display_df = df.copy()

for column in [
    "편도 요금",
    "하루 교통비",
    "월간 교통비",
    "연간 교통비"
]:
    display_df[column] = display_df[column].map(
        lambda x: f"{x:,}원"
    )

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)

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
    textposition="outside"
)

fig.update_layout(
    showlegend=False,
    yaxis_title="월간 교통비 (원)",
    xaxis_title="교통수단",
    yaxis_rangemode="tozero"
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("등교 일수에 따른 비용 변화")

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
    title="등교 일수에 따른 월간 교통비 변화"
)

fig2.update_layout(
    xaxis_title="월간 등교 일수",
    yaxis_title="월간 교통비 (원)",
    yaxis_rangemode="tozero"
)

st.plotly_chart(fig2, use_container_width=True)

st.divider()
st.header("4. 교통비 절약 분석")

cheaper = {
    name: price
    for name, price in fares.items()
    if price < fare
}

if cheaper:
    alternative = min(cheaper, key=cheaper.get)
    saving = (fare - cheaper[alternative]) * trips * days

    st.write(f"현재 선택: **{selected}**")
    st.write(f"저렴한 대안: **{alternative}**")
    st.metric("월간 예상 절약 금액", f"{saving:,}원")
    st.metric("연간 예상 절약 금액", f"{saving * 12:,}원")
else:
    st.info(
        "현재 선택한 교통수단보다 저렴한 대안이 없습니다. "
        "요금을 변경하면 다시 비교할 수 있습니다."
    )

st.divider()
st.header("5. 계산 결과 다운로드")

csv = df.to_csv(index=False).encode("utf-8-sig")

st.download_button(
    label="📥 교통비 결과 CSV 다운로드",
    data=csv,
    file_name="schoolmove_results.csv",
    mime="text/csv"
)

st.caption(
    "본 프로그램은 입력한 요금을 바탕으로 예상 비용을 계산합니다. "
    "실제 교통비는 학생 할인, 환승 할인, 정기권 및 이용 조건에 따라 달라질 수 있습니다."
)
