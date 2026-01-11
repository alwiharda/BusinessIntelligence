import streamlit as st
import pandas as pd
import plotly.express as px
import os
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# --- 1. CONFIG DASHBOARD ---
st.set_page_config(page_title="Executive Financial Dashboard", layout="wide")

# --- 2. JAVASCRIPT & CSS UNTUK ANIMASI ANGKA ---
# Fungsi ini akan membuat angka "berjalan" dari 0 ke target
st.markdown("""
    <script src="https://cdnjs.cloudflare.com/ajax/libs/countup.js/1.9.3/countUp.min.js"></script>
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
    html, body, [class*="css"] { 
        font-family: 'Plus Jakarta Sans', sans-serif; 
        background-color: #F8FAFC; 
    }
    
    .metric-card {
        background: white;
        padding: 22px;
        border-radius: 18px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.04);
        border-top: 5px solid #B2CEE0;
        text-align: left;
    }
    .metric-label { color: #64748b; font-size: 14px; font-weight: 600; }
    .metric-value { color: #1e293b; font-size: 26px; font-weight: 800; margin-top: 5px; }
    
    .main-title { 
        color: #475569; font-weight: 800; font-size: 2.5rem; 
        margin-bottom: 25px; text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# Fungsi Helper untuk Render Kartu dengan Animasi
def animated_metric(label, value, prefix="", suffix="", color="#B2CEE0", element_id=""):
    html_code = f"""
    <div class="metric-card" style="border-top-color: {color};">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{prefix}<span id="{element_id}">0</span>{suffix}</div>
    </div>
    <script>
        var numAnim = new CountUp('{element_id}', 0, {value}, {2 if '.' in str(value) else 0}, 2.5);
        if (!numAnim.error) {{
            numAnim.start();
        }} else {{
            console.error(numAnim.error);
        }}
    </script>
    """
    return st.components.v1.html(html_code, height=130)

# --- 3. DATA LOADING ---
@st.cache_data
def load_data():
    file_path = "Financial Sample.xlsx"
    if not os.path.exists(file_path): return None
    df = pd.read_excel(file_path)
    df.columns = [c.strip().replace(' ', '_').lower() for c in df.columns]
    
    cols_fin = ['sales', 'profit', 'units_sold']
    for col in cols_fin:
        if df[col].dtype == 'object':
            df[col] = df[col].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False).str.strip()
            df[col] = df[col].apply(lambda x: f"-{x[1:-1]}" if x.startswith('(') and x.endswith(')') else x)
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    df['date'] = pd.to_datetime(df['date'])
    return df

df = load_data()

if df is None:
    st.error("File 'Financial Sample.xlsx' tidak ditemukan!")
    st.stop()

# --- 4. FILTER ---
st.sidebar.markdown("### 🌸 Filter Dashboard")
selected_countries = st.sidebar.multiselect("Pilih Negara", df['country'].unique(), default=df['country'].unique())
df_filtered = df[df['country'].isin(selected_countries)].copy()

# --- 5. HEADER ---
st.markdown('<h1 class="main-title">🌸 Financial Intelligence Insights</h1>', unsafe_allow_html=True)

# --- 6. ANIMATED METRICS ---
total_sales = df_filtered['sales'].sum() / 1e6
total_profit = df_filtered['profit'].sum() / 1e6
units_sold = df_filtered['units_sold'].sum()
margin = (df_filtered['profit'].sum() / df_filtered['sales'].sum() * 100) if df_filtered['sales'].sum() != 0 else 0

m1, m2, m3, m4 = st.columns(4)
with m1:
    animated_metric("💰 Total Sales", total_sales, prefix="$", suffix="M", color="#B2CEE0", element_id="sales_count")
with m2:
    animated_metric("📈 Total Profit", total_profit, prefix="$", suffix="M", color="#FFB7B2", element_id="profit_count")
with m3:
    animated_metric("📦 Units Sold", units_sold, prefix="", suffix="", color="#B2DFDB", element_id="units_count")
with m4:
    animated_metric("📊 Gross Margin", margin, prefix="", suffix="%", color="#FDFD96", element_id="margin_count")

# --- 7. VISUALISASI ---
col_left, col_right = st.columns([1.5, 1])

with col_left:
    st.subheader("🌍 Sebaran Penjualan Global")
    map_data = df_filtered.groupby('country')['sales'].sum().reset_index()
    fig_map = px.choropleth(map_data, locations="country", locationmode='country names', color="sales",
                            color_continuous_scale=["#E0F2F1", "#B2DFDB", "#80CBC4", "#4DB6AC", "#26A69A"])
    fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor='rgba(0,0,0,0)', geo=dict(showframe=False))
    st.plotly_chart(fig_map, use_container_width=True)

with col_right:
    st.subheader("🥧 Kontribusi Profit")
    df_pie = df_filtered.groupby('product')['profit'].sum().reset_index()
    fig_pie = px.pie(df_pie, values='profit', names='product', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig_pie, use_container_width=True)

# Tren Profit Melengkung Halus
st.subheader("📈 Tren Profit Bulanan")
df_trend = df_filtered.groupby('date')['profit'].sum().reset_index()
fig_trend = px.line(df_trend, x='date', y='profit', line_shape='spline')
fig_trend.update_traces(line_color='#B2CEE0', line_width=4)
fig_trend.update_layout(plot_bgcolor='rgba(0,0,0,0)', xaxis_title="", yaxis_title="Profit ($)")
st.plotly_chart(fig_trend, use_container_width=True)
