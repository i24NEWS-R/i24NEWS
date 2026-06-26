import streamlit as st

def set_rtl():
    st.markdown("""
        <style>
            /* רקע אפור-עמוק מודרני לכל האפליקציה */
            .stApp { 
                background-color: #f1f5f9 !important; 
            }
            
            /* עיצוב כרטיסים לבנים בולטים עם צל עשיר ופדינג נדיב */
            div[data-testid="stVerticalBlockBorder"] {
                background-color: #ffffff !important;
                padding: 35px 40px !important;
                border-radius: 16px !important;
                box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -4px rgba(0, 0, 0, 0.05) !important;
                border: none !important;
                margin-bottom: 25px !important;
            }

            /* יישור גורף לימין וכיוון RTL קשיח */
            .stApp, .stApp * { 
                direction: rtl !important; 
                text-align: right !important; 
                font-family: 'Segoe UI', system-ui, sans-serif !important;
            }
            
            /* הכרחת התיבות הנפתחות (Dropdowns) והטקסט בתוכן להתיישר לימין */
            div[data-baseweb="select"] * {
                text-align: right !important;
                direction: rtl !important;
            }
            div[data-testid="stSelectbox"] div {
                direction: rtl !important;
                text-align: right !important;
            }
            
            /* יישור כפתורי הרדיו של השאלות בצד ימין בצורה נקייה */
            div[data-testid="stRadio"] label {
                justify-content: flex-start !important;
                text-align: right !important;
                direction: rtl !important;
            }
        </style>
    """, unsafe_allow_html=True)

st.set_page_config(layout="wide", page_title="פורטל i24NEWS")
set_rtl()
