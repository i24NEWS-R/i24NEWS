import os
import pandas as pd
import plotly.express as px
import streamlit as st

# הגדרת העמוד
st.set_page_config(page_title="דשבורד תוכניות", layout="wide")

# עיצוב CSS: יישור RTL ומרכוז תוכן העמוד
st.markdown(
    """
    <style>
    /* יישור לימין של כל העמוד והרכיבים */
    html, body, [data-testid="stAppViewContainer"] {
        direction: rtl;
        text-align: right;
    }
    
    /* מרכוז התיבה המרכזית */
    .main .block-container {
        max-width: 1100px;
        padding-top: 2rem;
        padding-bottom: 2rem;
        margin: 0 auto;
    }
    
    /* יישור כותרות ומדדים לימין */
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
        text-align: right !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# נתיב לקובץ ה-CSV בתוך תיקיית pages
DATA_PATH = os.path.join(os.path.dirname(__file__), "Shows.csv")

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    
    # המרת תאריכים סלחנית לפורמט יום/חודש/שנה
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['Date'])
    
    # חישוב נתח שוק
    df['Share'] = (df['i24'] / df['Reference'].replace(0, pd.NA)) * 100
    df['Share'] = df['Share'].fillna(0)
    
    return df

df = load_data()

min_date = df['Date'].min().date()
max_date = df['Date'].max().date()
default_start = pd.to_datetime("2026-01-01").date()
init_start = default_start if default_start >= min_date else min_date

# ניהול מצב תאריכים (Session State) עבור הכפתורים
if "date_range" not in st.session_state:
    st.session_state.date_range = (init_start, max_date)

st.title("דשבורד תוכניות")

# ===== תפריט עליון שקוף וצר =====
with st.container():
    col1, col2, col3, col4 = st.columns([2.5, 1.5, 2.5, 1.5])

    # 1. בחירת תוכנית
    with col1:
        all_titles = sorted(df['Title'].dropna().unique().tolist())
        default_title = "המהדורה המרכזית איי 24"
        title_index = all_titles.index(default_title) if default_title in all_titles else 0

        selected_title = st.selectbox(
            "בחירת תוכנית:",
            options=all_titles,
            index=title_index
        )

    # 2. בחירת מדד
    with col2:
        metric_option = st.selectbox(
            "בחירת מדד:",
            options=["רייטינג", "נתח שוק"],
            index=0
        )

    # 3. בחירת תאריכים + כפתורי איפוס וחודש אחרון
    with col3:
        st.write("בחירת תאריכים:")
        
        # כפתורי קשר מהיר
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            if st.button("כל התאריכים", use_container_width=True):
                st.session_state.date_range = (min_date, max_date)
                st.rerun()
        with btn_col2:
            if st.button("חודש אחרון", use_container_width=True):
                one_month_ago = max_date - pd.Timedelta(days=30)
                st.session_state.date_range = (max(min_date, one_month_ago), max_date)
                st.rerun()

        date_range = st.date_input(
            label="תאריכים",
            value=st.session_state.date_range,
            min_value=min_date,
            max_value=max_date,
            label_visibility="collapsed"
        )

        if isinstance(date_range, tuple) and len(date_range) == 2:
            start_date, end_date = date_range
            st.session_state.date_range = date_range
        elif isinstance(date_range, tuple) and len(date_range) == 1:
            start_date = end_date = date_range[0]
        else:
            start_date = end_date = date_range

    # 4. אופן הצגת הנתונים
    with col4:
        freq_option = st.selectbox(
            "אופן הצגת הנתונים:",
            options=["יומית", "שבועית", "חודשית"],
            index=0
        )

st.divider()

# ===== עיבוד הנתונים =====
col_to_plot = 'i24' if metric_option == "רייטינג" else 'Share'

filtered_df = df[
    (df['Title'] == selected_title) &
    (df['Date'] >= pd.to_datetime(start_date)) &
    (df['Date'] <= pd.to_datetime(end_date))
].sort_values('Date')

# סך כל התצפיות המקוריות בטווח התאריכים הנבחר
total_observations = len(filtered_df)

# אגרגציה לפי התדירות הנבחרת
if freq_option == "שבועית":
    plot_df = filtered_df.resample('W-MON', on='Date')[col_to_plot].mean().reset_index()
elif freq_option == "חודשית":
    plot_df = filtered_df.resample('MS', on='Date')[col_to_plot].mean().reset_index()
else:  # יומית
    plot_df = filtered_df[['Date', col_to_plot]].copy()

# עיגול הערכים לעשירית אחת בלבד
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
        markers=True
    )
    
    # הסרת כותרות הציריים + עיצוב פורמט עשרוני בודד בציר Y ובמרחף
    fig.update_traces(
        line_color='#1f77b4',
        line_width=2.5,
        hovertemplate="תאריך: %{x|%Y-%m-%d}<br>ערך: %{y:.1f}<extra></extra>"
    )
    fig.update_layout(
        hovermode="x unified",
        xaxis_title="",  # ללא כותרת למטה
        yaxis_title="",  # ללא כותרת בצד
        yaxis=dict(tickformat=".1f"),
        font=dict(size=14),
        height=450
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # כרטיסי סיכום מעוגלים לעשירית אחת
    c1, c2, c3 = st.columns(3)
    avg_val = filtered_df[col_to_plot].mean() if not filtered_df.empty else 0
    max_val = filtered_df[col_to_plot].max() if not filtered_df.empty else 0
    
    c1.metric("ממוצע בתקופה", f"{avg_val:.1f}")
    c2.metric("שיא בתקופה", f"{max_val:.1f}")
    c3.metric("מספר תצפיות", total_observations)
