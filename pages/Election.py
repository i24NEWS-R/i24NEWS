import streamlit as st
import geopandas as gpd
import pandas as pd
import plotly.express as px
import requests
import json
from shapely.geometry import Polygon

st.set_page_config(page_title="מפת בחירות היררכית בישראל", layout="wide")
st.title("מפת בחירות בישראל - תצוגה היררכית (Drill-Down)")

# ---------------------------------------------------------
# 1. ניהול מצב (Session State) לניווט היררכי
# ---------------------------------------------------------
if 'level' not in st.session_state:
    st.session_state.level = 'מחוזות'
if 'selected_district' not in st.session_state:
    st.session_state.selected_district = None
if 'selected_subdistrict' not in st.session_state:
    st.session_state.selected_subdistrict = None
if 'selected_city' not in st.session_state:
    st.session_state.selected_city = None

# מקרא צבעים למפלגות
PARTY_COLORS = {
    'הליכוד': '#2196F3',
    'יש עתיד': '#FF9800',
    'הציונות הדתית': '#00BCD4',
    'המחנה הממלכתי': '#9C27B0',
    'ש"ס': '#795548',
    'יהדות התורה': '#607D8B'
}

# ---------------------------------------------------------
# 2. טעינת גבולות מפה (כולל מנגנון יצירה עצמית אם אין אינטרנט)
# ---------------------------------------------------------
@st.cache_data
def load_fallback_geojson():
    url = "https://raw.githubusercontent.com/datasets/geo-boundaries/master/data/ISR.geojson"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        res = requests.get(url, headers=headers, timeout=4)
        if res.status_code == 200:
            geojson_data = res.json()
            gdf = gpd.GeoDataFrame.from_features(geojson_data["features"])
            gdf.crs = "EPSG:4326"
            
            # הגדרת ID מפורש לכל פוליגון ב-GeoJSON
            for idx, feature in enumerate(geojson_data['features']):
                feature['id'] = str(idx)
            return geojson_data, gdf
    except Exception:
        pass

    # במידה וההורדה נכשלה - יצירת 6 מחוזות גיאוגרפיים מובנים בקוד
    poly_north = Polygon([(35.0, 33.3), (35.6, 33.3), (35.6, 32.6), (35.0, 32.6)])
    poly_haifa = Polygon([(34.9, 32.6), (35.2, 32.6), (35.0, 32.3), (34.9, 32.4)])
    poly_center = Polygon([(34.7, 32.3), (35.0, 32.3), (35.0, 31.8), (34.7, 31.8)])
    poly_tlv = Polygon([(34.75, 32.12), (34.85, 32.12), (34.85, 32.02), (34.75, 32.02)])
    poly_jeru = Polygon([(35.0, 31.9), (35.3, 31.9), (35.3, 31.6), (35.0, 31.6)])
    poly_south = Polygon([(34.2, 31.6), (35.5, 31.6), (34.9, 29.5), (34.8, 29.5)])

    gdf = gpd.GeoDataFrame({
        'id': [str(i) for i in range(6)],
        'name': ["מחוז הצפון", "מחוז חיפה", "מחוז המרכז", "מחוז תל אביב", "מחוז ירושלים", "מחוז הדרום"],
        'geometry': [poly_north, poly_haifa, poly_center, poly_tlv, poly_jeru, poly_south]
    }, crs="EPSG:4326")
    
    geojson_data = json.loads(gdf.to_json())
    for idx, feature in enumerate(geojson_data['features']):
        feature['id'] = str(idx)
        
    return geojson_data, gdf

geojson_raw, gdf = load_fallback_geojson()

# ---------------------------------------------------------
# 3. סרגל הניווט (Sidebar)
# ---------------------------------------------------------
st.sidebar.header("ניווט היררכי")

if st.sidebar.button("↺ חזרה לרמת מחוזות"):
    st.session_state.level = 'מחוזות'
    st.session_state.selected_district = None
    st.session_state.selected_subdistrict = None
    st.session_state.selected_city = None
    st.rerun()

st.sidebar.markdown("---")

districts_list = ["מחוז הצפון", "מחוז חיפה", "מחוז המרכז", "מחוז תל אביב", "מחוז ירושלים", "מחוז הדרום"]

if st.session_state.level == 'מחוזות':
    selected_dist = st.sidebar.selectbox("1. בחר מחוז (Drill-Down):", ["-- בחר מחוז --"] + districts_list)
    if selected_dist != "-- בחר מחוז --":
        st.session_state.selected_district = selected_dist
        st.session_state.level = 'נפות'
        st.rerun()

elif st.session_state.level == 'נפות':
    st.sidebar.write(f"**מחוז:** {st.session_state.selected_district}")
    subdistricts = [f"{st.session_state.selected_district} - נפה מזרחית", f"{st.session_state.selected_district} - נפה מערבית"]
    selected_sub = st.sidebar.selectbox("2. בחר נפה:", ["-- בחר נפה --"] + subdistricts)
    if selected_sub != "-- בחר נפה --":
        st.session_state.selected_subdistrict = selected_sub
        st.session_state.level = 'ערים'
        st.rerun()

elif st.session_state.level == 'ערים':
    st.sidebar.write(f"**מחוז:** {st.session_state.selected_district}")
    st.sidebar.write(f"**נפה:** {st.session_state.selected_subdistrict}")
    cities = ["עיר א'", "עיר ב'", "יישוב ג'"]
    selected_c = st.sidebar.selectbox("3. בחר עיר:", ["-- בחר עיר --"] + cities)
    if selected_c != "-- בחר עיר --":
        st.session_state.selected_city = selected_c
        st.session_state.level = 'שכונות'
        st.rerun()

elif st.session_state.level == 'שכונות':
    st.sidebar.write(f"**מחוז:** {st.session_state.selected_district}")
    st.sidebar.write(f"**נפה:** {st.session_state.selected_subdistrict}")
    st.sidebar.write(f"**עיר:** {st.session_state.selected_city}")

# ---------------------------------------------------------
# 4. התאמת הנתונים והצגת המפה
# ---------------------------------------------------------
st.subheader(f"רמה נוכחית: {st.session_state.level}")

num_features = len(geojson_raw['features'])

if st.session_state.level == 'מחוזות':
    df_display = pd.DataFrame({
        'id': [str(i) for i in range(num_features)],
        'name': (districts_list * 5)[:num_features],
        'מפלגה מובילה': (['הליכוד', 'יש עתיד', 'הליכוד', 'יש עתיד', 'יהדות התורה', 'הליכוד'] * 5)[:num_features],
        'אחוז תמיכה': (['34%', '28%', '31%', '35%', '42%', '39%'] * 5)[:num_features]
    })
    zoom_level = 7
    center_coords = {"lat": 31.5, "lon": 34.75}
else:
    df_display = pd.DataFrame({
        'id': [str(i) for i in range(num_features)],
        'name': [f"{st.session_state.level} - אזור {i+1}" for i in range(num_features)],
        'מפלגה מובילה': (['יש עתיד', 'הליכוד', 'הציונות הדתית', 'המחנה הממלכתי', 'ש"ס', 'הליכוד'] * 5)[:num_features],
        'אחוז תמיכה': (['40%', '35%', '28%', '22%', '31%', '45%'] * 5)[:num_features]
    })
    zoom_level = 8.5 if st.session_state.level == 'נפות' else 11
    center_coords = {"lat": 32.0, "lon": 34.8}

# יצירת המפה באמצעות Plotly (עם חיבור תקין של ID כמחרוזת)
try:
    fig = px.choropleth_map(
        df_display,
        geojson=geojson_raw,
        locations='id',
        color='מפלגה מובילה',
        hover_name='name',
        hover_data=['אחוז תמיכה'],
        color_discrete_map=PARTY_COLORS,
        map_style="carto-positron",
        center=center_coords,
        zoom=zoom_level,
        opacity=0.7
    )
except AttributeError:
    fig = px.choropleth_mapbox(
        df_display,
        geojson=geojson_raw,
        locations='id',
        color='מפלגה מובילה',
        hover_name='name',
        hover_data=['אחוז תמיכה'],
        color_discrete_map=PARTY_COLORS,
        mapbox_style="carto-positron",
        center=center_coords,
        zoom=zoom_level,
        opacity=0.7
    )

fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, height=650)
st.plotly_chart(fig, use_container_width=True)
