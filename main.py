import streamlit as st

st.title("港幣兌換澳元")
st.number_input("港幣", value=200000, step=1, key="hkd")
l, r = st.columns(2)
l.number_input("賣出價1", value=4.9695, key="selling_price1")
r.number_input("賣出價2", value=4.9798, key="selling_price2")
aud1 = round(st.session_state.hkd/st.session_state.selling_price1, 4)
aud2 = round(st.session_state.hkd/st.session_state.selling_price2, 4)
l.write(f"兌換澳幣1: {aud1}")
r.write(f"兌換澳幣2: {aud2}")

st.number_input("定期日數", value=7, step=1, key="days")
l, r = st.columns(2)
l.number_input("利率1", value=0.15, step=0.01, key="interest_rate1")
r.number_input("利率2", value=12.8, step=0.01, key="interest_rate2")
interest1 = round(aud1*(st.session_state.interest_rate1/100)*(st.session_state.days/365), 4)
interest2 = round(aud2*(st.session_state.interest_rate2/100)*(st.session_state.days/365), 4)
l.write(f"獲得利息1: {interest1}")
r.write(f"獲得利息2: {interest2}")
l.write(f"總數1: {round(aud1+interest1, 4)}")
r.write(f"總數2: {round(aud2+interest2, 4)}")