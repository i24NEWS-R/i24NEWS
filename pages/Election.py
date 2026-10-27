import geopandas as gpd
import pandas as pd
import folium

# 1. טעינת גבולות הנפות/המחוזות (קובץ GeoJSON ללא חורים)
# ניתן להשתמש בקובץ GeoJSON מקומי או בקישור ישיר לקובץ מ-GitHub/data.gov.il
geojson_url = "https://raw.githubusercontent.com/datasets/geo-boundaries/master/data/ISR.geojson" # דוגמה לקישור גבולות
gdf = gpd.read_file(geojson_url)

# 2. טעינת נתוני הבחירות (דוגמה למבנה נתונים שמכינים מראש)
# הנתונים כוללים: מזהה/שם האזור, המפלגה המנצחת, והצבע המשויך לה
election_data = pd.DataFrame({
    'region_name': ['Jerusalem', 'Tel Aviv', 'Northern', 'Haifa', 'Central', 'Southern'],
    'winning_party': ['יהדות התורה', 'יש עתיד', 'הליכוד', 'יש עתיד', 'הליכוד', 'הליכוד'],
    'color': ['#795548', '#FF9800', '#2196F3', '#FF9800', '#2196F3', '#2196F3'] # קודי צבע למפלגות
})

# 3. מיזוג הנתונים הגיאוגרפיים עם נתוני הבחירות
merged_gdf = gdf.merge(election_data, left_on='name', right_on='region_name', how='left')

# 4. יצירת מפת בסיס חינמית (OpenStreetMap)
m = folium.Map(location=[31.5, 34.75], zoom_start=8, tiles='OpenStreetMap')

# 5. הוספת השכבה הגיאוגרפית הצבועה על המפה
folium.GeoJson(
    merged_gdf,
    style_function=lambda feature: {
        'fillColor': feature['properties']['color'] if feature['properties']['color'] else '#cccccc',
        'color': 'black',       # צבע גבול האזור
        'weight': 1,           # עובי הגבול
        'fillOpacity': 0.6     # שקיפות הצבע
    },
    tooltip=folium.GeoJsonTooltip(
        fields=['region_name', 'winning_party'],
        aliases=['אזור:', 'מפלגה מובילה:'],
        localize=True
    )
).add_to(m)

# 6. שמירת המפה כקובץ HTML אינטראקטיבי
m.save("israel_election_map.html")
print("המפה נוצרה בהצלחה ושמורה כ-israel_election_map.html!")
