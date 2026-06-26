import streamlit as st

def set_rtl():
    # שורה אחת שקוראת לקובץ החיצוני ומזריקה אותו כחוק עליון לאפליקציה
    st.markdown('<style>' + open('style.css', encoding='utf-8').read() + '</style>', unsafe_allow_html=True)
