import streamlit as st
from components.navigation import nav_bar
from functions.ui.auth_page import init_auth_state
st.set_page_config(
    page_title="Currency Exchange",
    page_icon=":money_with_wings:",
    layout="wide",
    initial_sidebar_state="collapsed",
)
init_auth_state()
nav_bar()

st.title("港幣兌換澳元")
st.number_input("港幣", value=200000, step=1, key="hkd")
l, r = st.columns(2)
l.number_input("賣出價1", value=float(f"{4.9695:.4f}"), step=0.0001, format="%.4f", key="selling_price1")
r.number_input("賣出價2", value=float(f"{4.9798:.4f}"), step=0.0001, format="%.4f", key="selling_price2")
aud1 = round(st.session_state.hkd/st.session_state.selling_price1, 4)
aud2 = round(st.session_state.hkd/st.session_state.selling_price2, 4)
l.write(f"兌換澳幣1 (AUD): {aud1}")
r.write(f"兌換澳幣2 (AUD): {aud2}")

st.number_input("定期日數", value=7, step=1, key="aud_days")
l, r = st.columns(2)
l.number_input("利率1 (%)", value=0.15, step=0.01, key="aud_interest_rate1")
r.number_input("利率2 (%)", value=12.8, step=0.01, key="aud_interest_rate2")
interest1 = round(aud1*(st.session_state.aud_interest_rate1/100)*(st.session_state.aud_days/365), 4)
interest2 = round(aud2*(st.session_state.aud_interest_rate2/100)*(st.session_state.aud_days/365), 4)
l.write(f"獲得利息1 (AUD): {interest1}")
r.write(f"獲得利息2 (AUD): {interest2}")
total1 = round(aud1 + interest1, 4)
total2 = round(aud2 + interest2, 4)
if total1 > total2:
    l.markdown(f"總數1 (AUD): <span style='color: red; font-size: 20px;'>{total1}</span>", unsafe_allow_html=True)
    r.markdown(f"總數2 (AUD): {total2}")
else:
    l.markdown(f"總數1 (AUD): {total1}")
    r.markdown(f"總數2 (AUD): <span style='color: red; font-size: 20px;'>{total2}</span>", unsafe_allow_html=True)

st.divider()

st.title("澳元兌換港幣")
st.number_input("澳幣", value=1000, step=1, key="aud")
l, r = st.columns(2)
l.number_input("買入價1", value=float(f"{5.0005:.4f}"), step=0.0001, format="%.4f", key="buying_price1")
r.number_input("買入價2", value=float(f"{5.0108:.4f}"), step=0.0001, format="%.4f", key="buying_price2")
hkd1 = round(st.session_state.aud*st.session_state.buying_price1, 4)
hkd2 = round(st.session_state.aud*st.session_state.buying_price2, 4)
l.write(f"兌換港幣1 (HKD): {hkd1}")
r.write(f"兌換港幣2 (HKD): {hkd2}")

st.number_input("定期日數", value=7, step=1, key="hkd_days")
l, r = st.columns(2)
l.number_input("利率1 (%)", value=0.15, step=0.01, key="hkd_interest_rate1")
r.number_input("利率2 (%)", value=12.8, step=0.01, key="hkd_interest_rate2")
interest1 = round(hkd1*(st.session_state.hkd_interest_rate1/100)*(st.session_state.hkd_days/365), 4)
interest2 = round(hkd2*(st.session_state.hkd_interest_rate2/100)*(st.session_state.hkd_days/365), 4)
l.write(f"獲得利息1 (HKD): {interest1}")
r.write(f"獲得利息2 (HKD): {interest2}")
total1 = round(hkd1 + interest1, 4)
total2 = round(hkd2 + interest2, 4)
if total1 > total2:
    l.markdown(f"總數1 (HKD): <span style='color: red; font-size: 20px;'>{total1}</span>", unsafe_allow_html=True)
    r.markdown(f"總數2 (HKD): {total2}")
else:
    l.markdown(f"總數1 (HKD): {total1}")
    r.markdown(f"總數2 (HKD): <span style='color: red; font-size: 20px;'>{total2}</span>", unsafe_allow_html=True)