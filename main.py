import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="SchoolMove | 등하교 교통비 계산기",
    page_icon="🚌",
    layout="wide",
)

# ---------- Style ----------
st.markdown("""
<style>
    .stApp { background: #f5f7fb; }
    .block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1200px; }
    .hero {
        padding: 1.7rem 1.8rem;
        border-radius: 22px;
        background: linear-gradient(120deg, #14213d 0%, #264b70 100%);
        color: white;
        margin-bottom: 1.2rem;
    }
    .hero h1 { color: white; margin-bottom: .35rem; }
    .hero p { color: #e2eaf5; margin-bottom: 0; font-size: 1.02rem; }
    div[data-testid="stMetric"] {
        background: white; padding: 1rem 1.1rem; border-radius: 16px;
        border: 1px solid #e5eaf2;
    }
    .small-note { color: #64748b; font-size: .88rem; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <h1>🚌 SchoolMove</h1>
  <p>나의 등하교 교통비를 계산하고, 교통수단별 비용을 비교해 보세요.</p>
</div>
""", unsafe_allow_html=True)

# ---------- Sidebar inputs ----------
st.sidebar.header("⚙️ 통학 조건 설정")
st.sidebar.caption("요금은 예시값입니다. 실제 요금에 맞게 수정하세요.")

school_days = st.sidebar.number_input(
    "한 달 등교 일수", min_value=1, max_value=31, value=20, step=1
)
daily_trips = st.sidebar.selectbox(
    "하루 이용 횟수", options=[1, 2, 3, 4], index=1,
    format_func=lambda x: f"{x}회"
)
monthly_budget = st.sidebar.number_input(
    "월간 교통비 예산 (원)", min_value=0, max_value=2_000_000,
    value=70000, step=5000
)
st.sidebar.markdown("---")
st.sidebar.caption("계산 가정: 1년은 12개월이며, 매달 등교 일수와 요금이 같다고 가정합니다.")

st.subheader("1. 교통수단별 요금 입력")
st.write("편도 1회 요금을 입력하세요. 환승 할인이나 학생 할인은 실제 결제 금액을 반영해 직접 조정할 수 있어요.")

default_fares = {
    "버스": 1500,
    "지하철": 1500,
    "버스 + 지하철 환승": 1600,
    "기타 교통수단": 2000,
}

cols = st.columns(4)
fares = {}
for col, (name, default) in zip(cols, default_fares.items()):
    with col:
        fares[name] = st.number_input(
            f"{name} 편도 요금 (원)",
            min_value=0, max_value=100000, value=default, step=50,
            key=f"fare_{name}"
        )

# ---------- Calculations ----------
def won(value):
    return f"{round(value):,}원"

records = []
for name, fare in fares.items():
    daily_cost = fare * daily_trips
    monthly_cost = daily_cost * school_days
    annual_cost = monthly_cost * 12
    records.append({
        "교통수단": name,
        "편도 요금": fare,
        "하루 교통비": daily_cost,
        "월간 교통비": monthly_cost,
        "연간 교통비": annual_cost,
    })

df = pd.DataFrame(records)
