import streamlit as st

def set_rtl():
    st.markdown("""
        <style>
            /* רקע כללי בהיר ומרגיע */
            .stApp { background-color: #f8fafc; }
            
            /* עיצוב כרטיס יוקרתי */
            .custom-card {
                background: white;
                padding: 25px;
                border-radius: 15px;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
                margin-bottom: 20px;
                border: 1px solid #f1f5f9;
            }

            /* RTL ויישור גורף */
            .stApp, .stApp * { 
                direction: rtl !important; 
                text-align: right !important; 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }

            /* הסתרת כפתורי שליטה של גרפים לניקיון ויזואלי */
            .modebar { display: none !important; }
        </style>
    """, unsafe_allow_html=True)

set_rtl()

st.title("📺 פורטל הנתונים והמחקר - i24NEWS")
st.caption("ברוכים הבאים. בחרו פרויקט מתפריט הצד כדי להתחיל.")
