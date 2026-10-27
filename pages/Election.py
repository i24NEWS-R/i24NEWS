import streamlit as st
import geopandas as gpd
import pandas as pd
import plotly.express as px
import requests
import json

st.set_page_config(page_title="מפת בחירות בישראל", layout="wide")
st.title("מפת בחירות בישראל - תצוגה רציפה ללא חורים")

# 1. משיכת קובץ ה-GeoJSON אונליין עם User-Agent למניעת חסימות HTTP
@st.cache_data
def load_geojson():
    url = "https://raw.githubusercontent.com/wmgeolab/geoBoundaries/main/releaseData/gbOpen/ISR/ADM1/geoBoundaries-ISR-ADM1_gbOpen.geojson"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        geojson_data = response.json()
        gdf = gpd.GeoDataFrame.from_features(geojson_data["features"])
        # הגדרת מערכת קואורדינטות תקנית
        gdf.crs = "EPSG:4326"
        return geojson_data, gdf
    else:
        st.error(f"שגיאה בהורדת מפת הבסיס: HTTP {response.status_code}")
        return None, None

geojson_raw, gdf = load_geojson()

if gdf is not None:
    # 2. יצירת נתוני הצבעה לדוגמה לפי שמות המחוזות/האזורים בקובץ
    # השמות בקובץ מגיעים באנגלית (shapeName), ולכן נצפה את הנתונים בהתאם:
    regions = gdf['shapeName'].tolist()
    
    # שיוך מפלגה מנצחת וצבע לכל אזור
    party_mapping = {
        regions[0]: {'party': 'הליכוד', 'color': '#2196F3'},
        regions[1]: {'party': 'יש עתיד', 'color': '#FF9800'},
        regions[2]: {'party': 'הציונות הדתית', 'color': '#00BCD4'},
        regions[3]: {'party': 'המחנה הממלכתי', 'color': '#9C27B0'},
        regions[4]: {'party': 'ש"ס', 'color': '#795548'},
    } if len(regions) >= 5 else {}

    # בניית DataFrame של תוצאות הבחירות
    df_results = pd.DataFrame([
        {
            'shapeName': region,
            'מפלגה מובילה': party_mapping.get(region, {}).get('party', 'הליכוד'),
            'color': party_mapping.get(region, {}).get('color', '#2196F3')
        }
        for region in regions
    ])

    # מיזוג הנתונים לתוך ה-GeoDataFrame
    gdf = gdf.merge(df_results, on='shapeName')

    # 3. יצירת המפה באמצעות Plotly Express
    fig = px.choropleth_mapbox(
        gdf,
        geojson=geojson_raw,
        locations=gdf.index,
        color='מפלגה מובילה',
        hover_name='shapeName',
        hover_data={'מפלגה מובילה': True},
        mapbox_style="carto-positron",  # מפת בסיס חינמית ונקייה
        center={"lat": 31.5, "lon": 34.75},
        zoom=7,
        opacity=0.6
    )

    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        height=650
    )

    # הצגת המפה ב-Streamlit
    st.plotly_chart(fig, use_container_width=True)
