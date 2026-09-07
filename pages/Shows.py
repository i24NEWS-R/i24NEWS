import os
import pandas as pd
import plotly.express as px
import streamlit as st

# הגדרת העמוד
st.set_page_config(page_title="דשבורד תוכניות", layout="wide")

# עיצוב CSS ליישור תפריט הצד לימין (RTL)
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        direction: rtl;
        text-align: right;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# נתיב לקובץ ה-CSV בתיקיית pages
DATA_PATH = os.path.join(os.path.dirname(__file__), "Shows.csv")

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    
    # המרת תאריכים סלחנית
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['Date'])
    
    # חישוב נתח שוק
    df['Share'] = (df['i24'] / df['Reference'].replace(0, pd.NA)) * 100
    df['Share'] = df['Share'].fillna(0)
    
    return df

df = load_data()

# ===== תפריט צדדי (Right Sidebar) =====
st.sidebar.header("תפריט סינון")

# 1. בחירת תוכנית (בולטים)
st.sidebar.subheader("בחירת תוכנית")
all_titles = sorted(df['Title'].dropna().unique().tolist())
default_title = "המהדורה המרכזית איי 24"
title_index = all_titles.index(default_title) if default_title in all_titles else 0

selected_title = st.sidebar.radio(
    label="בחר תוכנית:",
    options=all_titles,
    index=title_index,
    label_visibility="collapsed"
)

st.sidebar.divider()

# 2. בחירת מדד (בולטים)
st.sidebar.subheader("בחירת מדד")
metric_option = st.sidebar.radio(
    label="בחר מדד להצגה:",
    options=["רייטינג", "נתח שוק"],
    index=0,
    label_visibility="collapsed"
)

st.sidebar.divider()

# 3. בחירת תאריכים (בשורה אחת)
st.sidebar.subheader("בחירת תאריכים")
min_date = df['Date'].min().date()
max_date = df['Date'].max().date()
default_start = pd.to_datetime("2026-01-01").date()

start_val = default_start if default_start >= min_date else min_date

# בחירת טווח תאריכים בשורה אחת (Range Input)
date_range = st.sidebar.date_input(
    label="טווח תאריכים:",
    value=(start_val, max_date),
    min_value=min_date,
    max_value=max_date,
    label_visibility="collapsed"
)

# טיפול במקרה של בחירת תאריך יחיד תוך כדי הקלדה
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = end_date = date_range[0] if isinstance(date_range, tuple) else date_range

st.sidebar.divider()

# 4. אופן הצגת הנתונים (בולטים)
st.sidebar.subheader("אופן הצגת הנתונים")
freq_option = st.sidebar.radio(
    label="אופן הצגת הנתונים:",
    options=["יומית", "שבועית", "חודשית"],
    index=0,
    label_visibility="collapsed"
)

# ===== עיבוד הנתונים =====
col_to_plot = 'i24' if metric_option == "רייטינג" else 'Share'
y_label = "רייטינג (%)" if metric_option == "רייטינג" else "נתח שוק (%)"

filtered_df = df[
    (df['Title'] == selected_title) &
    (df['Date'] >= pd.to_datetime(start_date)) &
    (df['Date'] <= pd.to_datetime(end_date))
].sort_values('Date')

# אגרגציה לפי תדירות
if freq_option == "שבועית":
    plot_df = filtered_df.resample('W-MON', on='Date')[col_to_plot].mean().reset_index()
elif freq_option == "חודשית":
    plot_df = filtered_df.resample('MS', on='Date')[col_to_plot].mean().reset_index()
else:  # יומית
    plot_df = filtered_df[['Date', col_to_plot]].copy()

# ===== תרשים מרכזי =====
st.title(f"תרשים מגמה - {selected_title}")

if plot_df.empty:
    st.warning("לא נמצאו נתונים עבור הסינון הנבחר.")
else:
    fig = px.line(
        plot_df,
        x='Date',
        y=col_to_plot,
        title=f"{metric_option} - תצוגה {freq_option}",
        labels={'Date': 'תאריך', col_to_plot: y_label},
        markers=True
    )
    
    fig.update_traces(line_color='#1f77b4', line_width=2.5)
    fig.update_layout(
        hovermode="x unified",
        xaxis_title="תאריך",
        yaxis_title=y_label,
        font=dict(size=14)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # מדדי סיכום מתחת לגרף
    c1, c2, c3 = st.columns(3)
    c1.metric("ממוצע בתקופה", f"{plot_df[col_to_plot].mean():.2f}%")
    c2.metric("שיא בתקופה", f"{plot_df[col_to_plot].max():.2f}%")
    c3.metric("מספר תצפיות", len(plot_df))
