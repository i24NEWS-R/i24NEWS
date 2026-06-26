import streamlit as st

def set_rtl():
    st.markdown("""
        <style>
            /* רקע אפור-בטון בהיר ועמוק יותר ליצירת ניגודיות */
            .stApp { 
                background-color: #f1f5f9 !important; 
            }
            
            /* כרטיסים לבנים מובלטים עם צל עשיר ו-Padding נדיב */
            div[data-testid="stVerticalBlockBorder"] {
                background-color: #ffffff !important;
                padding: 35px 40px !important; /* פדינג רחב ומרווח מאוד */
                border-radius: 20px !important;
                box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.05) !important;
                border: none !important;
                margin-bottom: 30px !important;
            }

            /* RTL ויישור גורף */
            .stApp, .stApp * { 
                direction: rtl !important; 
                text-align: right !important; 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
            }
            
            /* תיקון קריטי: יישור הטקסט בתוך התיבות הנפתחות (Dropdowns) לימין */
            div[data-baseweb="select"] * {
                text-align: right !important;
                direction: rtl !important;
            }
            
            /* עיצוב כותרות נקי ויוקרתי */
            h1, h2, h3 {
                color: #0f172a !important;
                font-weight: 700 !important;
                letter-spacing: -0.5px;
            }
        </style>
    """, unsafe_allow_html=True)

st.set_page_config(layout="wide", page_title="פורטל i24NEWS")
set_rtl()
