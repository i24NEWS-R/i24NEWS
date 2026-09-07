import os
import pandas as pd
import plotly.express as px
import streamlit as st

# הגדרת העמוד
st.set_page_config(page_title="דשבורד תוכניות", layout="wide")

# CSS: יישור RTL, מרכוז והצמדת אלמנטים לגובה אחיד
st.markdown(
    """
    <style>
    html, body, [data-testid="stAppViewContainer"], .main {
        direction: rtl !important;
        text-align: right !important;
    }

    .main .block-container {
        max-width: 1100px;
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        margin: 0 auto;
    }

    h1, h2, h3, h4, label, p, div {
        text-align: right !important;
    }

    div[data-baseweb="select"] > div, input {
        text-align: right !important;
        direction: rtl !important;
    }

    [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
        text-align: right !important;
        justify-content: flex-start !important;
    }

    /* יישור גובה הכפתורים בדיוק לקו הכותרת "בחירת תאריכים:" */
    div[data-testid="column"] button {
        margin-top: 28px !important;
        padding: 2px 4px !important;
        font-size: 12px !important;
        height: 38px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

DATA_PATH = os.path.join(os.path.dirname(__file__), "Shows.csv")

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['Date'])
    
    df['Share'] = (df['i24'] / df['Reference'].replace(0, pd.NA)) * 100
    df['Share'] = df['Share'].fillna(0)
    
    return df

df = load_data()

min_date = df['Date'].min().date()
max_date = df['Date'].max().date()
default_start = pd.to_datetime("2026-01-01").date()
init_start = default_start if default_start >= min_date else min_date

if "date_range" not in st.session_state:
    st.session_state.date_range = (init_start, max_date)

st.title("דשבורד תוכניות")

# ===== שורה אחת הדוקה וצרה לכל האלמנטים והכפתורים =====
with st.container():
    # חלוקת פרופורציות שדה קצרות להכנסת כל הרכיבים בשורה אחת
    col_show, col_metric, col_date, col_btn1, col_btn2, col_freq = st.columns([1.8, 1.2, 1.8, 0.6, 0.8, 1.2])

    # 1. בחירת תוכנית (מקוכצת)
    with col_show:
        all_titles = sorted(df['Title'].dropna().unique().tolist())
        default_title = "המהדורה המרכזית איי 24"
        title_index = all_titles.index(default_title) if default_title in all_titles else 0

        selected_title = st.selectbox(
            "בחירת תוכנית:",
            options=all_titles,
            index=title_index
        )

    # 2. בחירת מדד (מקוכצת)
    with col_metric:
        metric_option = st.selectbox(
            "בחירת מדד:",
            options=["רייטינג", "נתח שוק"],
            index=0
        )

    # 3. בחירת תאריכים
    with col_date:
        date_range = st.date_input(
            label="בחירת תאריכים:",
            value=st.session_state.date_range,
            min_value=min_date,
            max_value=max_date
        )

        if isinstance(date_range, tuple) and len(date_range) == 2:
            start_date, end_date = date_range
            st.session_state.date_range = date_range
        elif isinstance(date_range, tuple) and len(date_range) == 1:
            start_date = end_date = date_range[0]
        else:
            start_date = end_date = date_range

    # 4. כפתור "הכל" (צמוד לתאריכים)
    with col_btn1:
        if st.button("הכל", use_container_width=True):
            st.session_state.date_range = (min_date, max_date)
            st.rerun()

    # 5. כפתור "חודש אחרון" (צמוד לתאריכים)
    with col_btn2:
        if st.button("חודש אחרון", use_container_width=True):
            one_month_ago = max_date - pd.Timedelta(days=30)
            st.session_state.date_range = (max(min_date, one_month_ago), max_date)
            st.rerun()

    # 6. אופן הצגת הנתונים (מקוכצת)
    with col_freq:
        freq_option = st.selectbox(
            "אופן הצגת הנתונים:",
            options=["יומית", "שבועית", "חודשית"],
            index=0
        )

st.divider()

# ===== עיבוד והכנת הנתונים =====
col_to_plot = 'i24' if metric_option == "רייטינג" else 'Share'

filtered_df = df[
    (df['Title'] == selected_title) &
    (df['Date'] >= pd.to_datetime(start_date)) &
    (df['Date'] <= pd.to_datetime(end_date))
].sort_values('Date')

total_observations = len(filtered_df)

if freq_option == "שבועית":
    plot_df = filtered_df.resample('W-MON', on='Date')[col_to_plot].mean().reset_index()
elif freq_option == "חודשית":
    plot_df = filtered_df.resample('MS', on='Date')[col_to_plot].mean().reset_index()
else:
    plot_df = filtered_df[['Date', col_to_plot]].copy()

plot_df[col_to_plot] = plot_df[col_to_plot].round(1)

# ===== תרשים מרכזי =====
if plot_df.empty:
    st.warning("לא נמצאו נתונים עבור הסינון הנבחר.")
else:
    fig = px.line(
        plot_df,
        x='Date',
        y=col_to_plot,
        title=f"{selected_title} — {metric_option} ({freq_option})",
        markers=True,
        line_shape="spline"
    )
    
    fig.update_traces(
        line_color='#1f77b4',
        line_width=2.5,
        hovertemplate="תאריך: %{x|%Y-%m-%d}<br>ערך: %{y:.1f}<extra></extra>"
    )
    fig.update_layout(
        hovermode="x unified",
        xaxis_title="",
        yaxis_title="",
        yaxis=dict(tickformat=".1f"),
        font=dict(size=14),
        height=450,
        title_x=1.0
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # כרטיסי סיכום
    c1, c2, c3 = st.columns(3)
    avg_val = filtered_df[col_to_plot].mean() if not filtered_df.empty else 0
    max_val = filtered_df[col_to_plot].max() if not filtered_df.empty else 0
    
    c1.metric("ממוצע בתקופה", f"{avg_val:.1f}")
    c2.metric("שיא בתקופה", f"{max_val:.1f}")
    c3.metric("מספר תצפיות", total_observations)
