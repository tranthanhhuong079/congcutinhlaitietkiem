import pandas as pd
import streamlit as st

st.set_page_config(page_title="Công cụ Tính Lãi Gửi Tiết Kiệm", page_icon="🏦")

st.title("🏦 Công Cụ Tính Lãi Gửi Tiết Kiệm")
st.markdown(
    "Ứng dụng tính lãi suất tiết kiệm theo **Lãi Đơn** và **Lãi Kép** "
    "với các hình thức nhận lãi khác nhau."
)
st.divider()

PAYOUT_OPTIONS = {
    "Lãnh lãi theo tháng": 1,
    "Lãnh lãi theo quý": 3,
    "Lãnh lãi cuối kỳ": None,  # = toàn bộ kỳ hạn
    "Lãnh lãi đầu kỳ": None,   # = toàn bộ kỳ hạn, nhận ngay khi gửi
}


def fmt(x: float) -> str:
    return f"{x:,.0f} VND"


col1, col2 = st.columns(2)
with col1:
    principal = st.number_input(
        "1. Số tiền gửi (VND):", min_value=0, value=100_000_000, step=1_000_000
    )
    term = st.number_input("2. Kỳ hạn gửi (tháng):", min_value=1, value=12, step=1)
with col2:
    rate = st.number_input(
        "3. Lãi suất (%/năm):", min_value=0.0, value=6.5, step=0.1, format="%.2f"
    )
    mode = st.selectbox("4. Hình thức nhận lãi:", list(PAYOUT_OPTIONS.keys()))

method = st.radio(
    "5. Phương thức tính lãi:",
    ["Lãi Đơn", "Lãi Kép"],
    horizontal=True,
    help=(
        "Lãi đơn: lãi chỉ tính trên số tiền gốc ban đầu.\n\n"
        "Lãi kép: lãi mỗi kỳ được cộng vào gốc để sinh lãi ở kỳ sau "
        "(theo tháng/quý; với 'lãnh lãi cuối kỳ' lãi được nhập gốc hằng tháng)."
    ),
)

if mode == "Lãnh lãi đầu kỳ" and method == "Lãi Kép":
    st.warning("Lãnh lãi đầu kỳ không có lãi kép, hệ thống tính theo lãi đơn.")
    method = "Lãi Đơn"

# ---------- Tính toán ----------
r = rate / 100
step = PAYOUT_OPTIONS[mode] or term          # số tháng mỗi kỳ trả lãi
if method == "Lãi Kép" and mode == "Lãnh lãi cuối kỳ":
    step = 1                                  # nhập gốc hằng tháng

rows = []
balance = principal
elapsed = 0
total_interest = 0.0
while elapsed < term:
    months = min(step, term - elapsed)
    base = balance if method == "Lãi Kép" else principal
    interest = base * r * months / 12
    total_interest += interest
    elapsed += months
    if method == "Lãi Kép":
        balance += interest
    rows.append(
        {
            "Tháng thứ": elapsed,
            "Tiền lãi kỳ này": round(interest),
            "Tổng lãi tích lũy": round(total_interest),
            "Gốc + lãi tích lũy": round(principal + total_interest),
        }
    )

periodic = rows[0]["Tiền lãi kỳ này"] if rows else 0
total = principal + total_interest

# ---------- Kết quả ----------
st.divider()
st.subheader("📊 Kết Quả Dự Tính")

label = {
    "Lãnh lãi theo tháng": "Tiền lãi định kỳ (tháng):",
    "Lãnh lãi theo quý": "Tiền lãi định kỳ (quý):",
    "Lãnh lãi cuối kỳ": "Tiền lãi nhận cuối kỳ:",
    "Lãnh lãi đầu kỳ": "Tiền lãi nhận đầu kỳ:",
}[mode]

c1, c2, c3 = st.columns(3)
c1.metric(label, fmt(periodic))
c2.metric("Tổng tiền lãi thu về:", fmt(total_interest))
c3.metric("Tổng gốc + lãi nhận được:", fmt(total))

with st.expander("Xem chi tiết từng kỳ"):
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.line_chart(df.set_index("Tháng thứ")[["Gốc + lãi tích lũy"]])
