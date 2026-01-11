import streamlit as st
import pandas as pd
import plotly.express as px
import os
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# --- 1. CONFIG DASHBOARD ---
st.set_page_config(page_title="Executive Financial Dashboard", layout="wide")

# --- 2. CSS & ANIMATION SCRIPT (Kunci Utama Perubahan) ---
st.markdown("""
    <script src="https://cdnjs.cloudflare.com/ajax/libs/countup.js/1.9.3/countUp.min.js"></script>
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] { 
        font-family: 'Plus Jakarta Sans', sans-serif; 
        background-color: #F8FAFC; 
    }

    /* Modern Card dengan Shadow dan Hover */
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        border-top: 6px solid #B2CEE0;
        margin-bottom: 10px;
    }
    .metric-label { 
        color: #64748b; font-size: 15px; font-weight: 600; 
        display: flex; align-items: center; gap: 8px;
    }
    .metric-value { 
        color: #1e293b; font-size: 30px; font-weight: 800; margin-top: 8px; 
    }
    
    .main-title { 
        color: #475569; font-weight: 800; font-size: 2.8rem; 
        margin-bottom: 30px; text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# Fungsi Helper untuk Metrik Beranimasi
def animated_metric(label, value, icon, prefix="", suffix="", color="#B2CEE0", element_id=""):
    # Logika desimal
    decimals = 1 if suffix == "%" else (2 if "M" in suffix else 0)
    
    html_code = f"""
    <div class="metric-card" style="border-top-color: {color};">
        <div class="metric-label"><span>{icon}</span> {label}</div>
        <div class="metric-value">{prefix}<span id="{element_id}">0</span>{suffix}</div>
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/countup.js/1.9.3/countUp.min.js"></script>
    <script>
        (function() {{
            var numAnim = new CountUp('{element_id}', 0, {value}, {decimals}, 2.5);
            if (!numAnim.error) {{
                numAnim.start();
            }}
        }})();
    </script>
    """
    st.components.v1.html(html_code, height=140)

# --- 3. DATA LOADING ---
@st.cache_data
def load_data():
    file_path = "Financial Sample.xlsx"
    if not os.path.exists(file_path): return None
    df = pd.read_excel(file_path)
    df.columns = [c.strip().replace(' ', '_').lower() for c in df.columns]
    
    # Cleaning supaya profit tidak hilang
    for col in ['sales', 'profit', 'units_sold']:
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

# --- 4. FILTER SIDEBAR ---
st.sidebar.markdown("### 🌸 Filter Dashboard")
selected_countries = st.sidebar.multiselect("Negara", df['country'].unique(), default=df['country'].unique())
df_filtered = df[df['country'].isin(selected_countries)].copy()

# --- 5. HEADER ---
st.markdown('<h1 class="main-title">🌸 Financial Intelligence Insights</h1>', unsafe_allow_html=True)

# --- 6. ANIMATED METRICS (BAGIAN YANG BERUBAH DRASTIS) ---
total_sales = df_filtered['sales'].sum()
total_profit = df_filtered['profit'].sum()
units_sold = df_filtered['units_sold'].sum()
margin = (total_profit / total_sales * 100) if total_sales != 0 else 0

m1, m2, m3, m4 = st.columns(4)
with m1:
    animated_metric("Total Sales", total_sales/1e6, "💰", prefix="$", suffix="M", color="#B2CEE0", element_id="id1")
with m2:
    animated_metric("Total Profit", total_profit/1e6, "📈", prefix="$", suffix="M", color="#FFB7B2", element_id="id2")
with m3:
    animated_metric("Units Sold", units_sold, "📦", color="#B2DFDB", element_id="id3")
with m4:
    animated_metric("Gross Margin", margin, "📊", suffix="%", color="#FDFD96", element_id="id4")

# --- 7. ROW ATAS: MAP & CLUSTER ---
c_map, c_clust = st.columns([1.5, 1])
with c_map:
    st.subheader("🌍 Sebaran Penjualan Global")
    map_data = df_filtered.groupby('country')['sales'].sum().reset_index()
    fig_map = px.choropleth(map_data, locations="country", locationmode='country names', color="sales",
                            color_continuous_scale="Mint")
    fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor='rgba(0,0,0,0)', geo=dict(showframe=False))
    st.plotly_chart(fig_map, use_container_width=True)

with c_clust:
    st.subheader("🥧 Kontribusi Profit")
    df_pie = df_filtered.groupby('product')['profit'].sum().reset_index()
    fig_pie = px.pie(df_pie, values='profit', names='product', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
    fig_pie.update_layout(margin=dict(t=0, b=0, l=0, r=0))
    st.plotly_chart(fig_pie, use_container_width=True)

# --- 8. ROW BAWAH: TREND ---
st.subheader("📈 Tren Profit Bulanan")
df_trend = df_filtered.groupby('date')['profit'].sum().reset_index()
fig_trend = px.line(df_trend, x='date', y='profit', line_shape='spline')
fig_trend.update_traces(line_color='#B2CEE0', line_width=4)
fig_trend.update_layout(plot_bgcolor='rgba(0,0,0,0)', xaxis_title="", yaxis_title="Profit ($)")
st.plotly_chart(fig_trend, use_container_width=True)
