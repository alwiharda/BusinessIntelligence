import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# --- 1. CONFIG DASHBOARD ---
st.set_page_config(page_title="Executive Financial Dashboard", layout="wide")

# --- 2. CSS & ANIMATION SCRIPT ---
st.markdown("""
    <script src="https://cdnjs.cloudflare.com/ajax/libs/countup.js/1.9.3/countUp.min.js"></script>
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] { 
        font-family: 'Plus Jakarta Sans', sans-serif; 
        background-color: #F8FAFC; 
    }

    /* Modern Metric Card Design */
    .metric-card {
        background: white;
        padding: 24px;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        border-top: 6px solid #B2CEE0;
        transition: transform 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
    }
    .metric-label { 
        color: #64748b; 
        font-size: 15px; 
        font-weight: 600; 
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .metric-value { 
        color: #1e293b; 
        font-size: 28px; 
        font-weight: 800; 
        margin-top: 8px; 
    }
    
    .main-title { 
        color: #475569; 
        font-weight: 800; 
        font-size: 2.8rem; 
        margin-bottom: 30px; 
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# Fungsi Helper untuk Metrik Beranimasi
def animated_metric(label, value, icon, prefix="", suffix="", color="#B2CEE0", element_id=""):
    decimals = 1 if suffix == "%" else (2 if "M" in suffix else 0)
    
    html_code = f"""
    <div class="metric-card" style="border-top-color: {color};">
        <div class="metric-label"><span>{icon}</span> {label}</div>
        <div class="metric-value">{prefix}<span id="{element_id}">0</span>{suffix}</div>
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/countup.js/1.9.3/countUp.min.js"></script>
    <script>
        var numAnim = new CountUp('{element_id}', 0, {value}, {decimals}, 2.5);
        if (!numAnim.error) {{
            numAnim.start();
        }}
    </script>
    """
    st.components.v1.html(html_code, height=150)

# --- 3. DATA LOADING ---
@st.cache_data
def load_data():
    file_path = "Financial Sample.xlsx"
    if not os.path.exists(file_path): return None
    df = pd.read_excel(file_path)
    df.columns = [c.strip().replace(' ', '_').lower() for c in df.columns]
    
    cols_fin = ['sales', 'profit', 'units_sold', 'gross_sales']
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

# --- 5. CLUSTERING ---
if len(df_filtered) > 1:
    X = df_filtered[['units_sold', 'profit']]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    df_filtered['segment_cluster'] = kmeans.fit_predict(X_scaled)
    df_filtered['segment_cluster'] = df_filtered['segment_cluster'].map({0: 'Low Performance', 1: 'High Performance', 2: 'Average'})

# --- 6. HEADER ---
st.markdown('<h1 class="main-title">🌸 Financial Intelligence Insights</h1>', unsafe_allow_html=True)

# --- 7. ANIMATED METRICS ---
total_sales = df_filtered['sales'].sum()
total_profit = df_filtered['profit'].sum()
units_sold = df_filtered['units_sold'].sum()
margin = (total_profit / total_sales * 100) if total_sales != 0 else 0

m1, m2, m3, m4 = st.columns(4)
with m1:
    animated_metric("Total Sales", total_sales/1e6, "💰", prefix="$", suffix="M", color="#B2CEE0", element_id="sales_id")
with m2:
    animated_metric("Total Profit", total_profit/1e6, "📈", prefix="$", suffix="M", color="#FFB7B2", element_id="profit_id")
with m3:
    animated_metric("Units Sold", units_sold, "📦", color="#B2DFDB", element_id="units_id")
with m4:
    animated_metric("Gross Margin", margin, "📊", suffix="%", color="#FDFD96", element_id="margin_id")

st.write("") 

# --- 8. ROW ATAS: MAP & CLUSTER ---
col_left, col_right = st.columns([1.5, 1])
with col_left:
    st.subheader("🌍 Sebaran Penjualan Global")
    map_data = df_filtered.groupby('country')['sales'].sum().reset_index()
    fig_map = px.choropleth(map_data, locations="country", locationmode='country names', color="sales",
                            color_continuous_scale=["#E0F2F1", "#B2DFDB", "#80CBC4", "#4DB6AC", "#26A69A"])
    fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor='rgba(0,0,0,0)', geo=dict(showframe=False))
    st.plotly_chart(fig_map, use_container_width=True)

with col_right:
    st.subheader("🎯 Klaster Profitabilitas")
    fig_clust = px.scatter(df_filtered, x='units_sold', y='profit', color='segment_cluster',
                           color_discrete_sequence=["#FFB7B2", "#B2CEE0", "#FDFD96"])
    fig_clust.update_layout(plot_bgcolor='white', margin=dict(t=10, b=0, l=0, r=0))
    st.plotly_chart(fig_clust, use_container_width=True)

# --- 9. ROW BAWAH: TREND & PIE CHART ---
c1, c2 = st.columns(2)
with c1:
    st.subheader("📈 Tren Profit Bulanan")
    df_trend = df_filtered.groupby('date')['profit'].sum().reset_index()
    fig_trend = px.line(df_trend, x='date', y='profit', line_shape='spline')
    fig_trend.update_traces(line_color='#B2CEE0', line_width=4)
    fig_trend.update_layout(plot_bgcolor='rgba(0,0,0,0)', xaxis_title="", yaxis_title="Profit ($)", 
                            yaxis=dict(showgrid=True, gridcolor='#F1F5F9'))
    st.plotly_chart(fig_trend, use_container_width=True)

with c2:
    st.subheader("🥧 Kontribusi Profit per Produk")
    df_pie = df_filtered.groupby('product')['profit'].sum().reset_index()
    fig_pie = px.pie(df_pie, values='profit', names='product', hole=0.4,
                     color_discrete_sequence=px.colors.qualitative.Pastel)
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_pie, use_container_width=True)

# --- 10. DETAIL TABLE ---
with st.expander("🔍 Lihat Detail Data Transaksi"):
    st.dataframe(df_filtered.sort_values(by='date', ascending=False), use_container_width=True)
