import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# --- 1. CONFIG DASHBOARD ---
st.set_page_config(page_title="Executive Financial Dashboard", layout="wide")

# --- 2. PREMIUM PASTEL CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
    html, body, [class*="css"] { 
        font-family: 'Plus Jakarta Sans', sans-serif; 
        background-color: #F8FAFC; 
    }
    
    /* Custom Metric Card Style */
    .metric-card {
        background: white;
        padding: 22px;
        border-radius: 18px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.04);
        border-top: 5px solid #B2CEE0;
    }
    .metric-label { color: #64748b; font-size: 14px; font-weight: 600; }
    .metric-value { color: #1e293b; font-size: 26px; font-weight: 800; margin-top: 5px; }
    
    .main-title { 
        color: #475569; 
        font-weight: 800; 
        font-size: 2.5rem; 
        margin-bottom: 25px; 
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATA LOADING & ROBUST CLEANING ---
@st.cache_data
def load_data():
    file_path = "Financial Sample.xlsx"
    if not os.path.exists(file_path): return None
    
    df = pd.read_excel(file_path)
    df.columns = [c.strip().replace(' ', '_').lower() for c in df.columns]
    
    # FIX: Pembersihan mendalam agar profit negatif (akuntansi) tidak hilang
    cols_fin = ['sales', 'profit', 'units_sold', 'gross_sales', 'cogs', 'discounts']
    for col in cols_fin:
        if df[col].dtype == 'object':
            df[col] = df[col].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False).str.strip()
            # Deteksi format (100) sebagai -100
            df[col] = df[col].apply(lambda x: f"-{x[1:-1]}" if x.startswith('(') and x.endswith(')') else x)
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    df['date'] = pd.to_datetime(df['date'])
    return df

df = load_data()

if df is None:
    st.error("File 'Financial Sample.xlsx' tidak ditemukan!")
    st.stop()

# --- 4. SIDEBAR ---
st.sidebar.markdown("### 🌸 Filter Dashboard")
selected_countries = st.sidebar.multiselect("Pilih Negara", df['country'].unique(), default=df['country'].unique())
df_filtered = df[df['country'].isin(selected_countries)].copy()

# --- 5. CLUSTERING (MACHINE LEARNING) ---
if len(df_filtered) > 1:
    X = df_filtered[['units_sold', 'profit']]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    df_filtered['segment_cluster'] = kmeans.fit_predict(X_scaled)
    df_filtered['segment_cluster'] = df_filtered['segment_cluster'].map({0: 'Low Performance', 1: 'High Performance', 2: 'Average'})

# --- 6. HEADER ---
st.markdown('<h1 class="main-title">🌸 Financial Intelligence Insights</h1>', unsafe_allow_html=True)

# --- 7. METRICS (UPGRADED DESIGN) ---
total_sales = df_filtered['sales'].sum()
total_profit = df_filtered['profit'].sum()
units_sold = df_filtered['units_sold'].sum()
margin = (total_profit / total_sales * 100) if total_sales != 0 else 0

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(f'<div class="metric-card"><div class="metric-label">💰 Total Sales</div><div class="metric-value">${total_sales/1e6:.2f}M</div></div>', unsafe_allow_html=True)
with m2:
    st.markdown(f'<div class="metric-card" style="border-top-color: #FFB7B2;"><div class="metric-label">📈 Total Profit</div><div class="metric-value">${total_profit/1e6:.2f}M</div></div>', unsafe_allow_html=True)
with m3:
    st.markdown(f'<div class="metric-card" style="border-top-color: #B2DFDB;"><div class="metric-label">📦 Units Sold</div><div class="metric-value">{units_sold:,.0f}</div></div>', unsafe_allow_html=True)
with m4:
    st.markdown(f'<div class="metric-card" style="border-top-color: #FDFD96;"><div class="metric-label">📊 Gross Margin</div><div class="metric-value">{margin:.1f}%</div></div>', unsafe_allow_html=True)

st.write("") 

# --- 8. ROW ATAS: MAP & CLUSTER ---
col_left, col_right = st.columns([1.5, 1])

with col_left:
    st.subheader("🌍 Sebaran Penjualan Global")
    map_data = df_filtered.groupby('country')['sales'].sum().reset_index()
    fig_map = px.choropleth(
        map_data, locations="country", locationmode='country names', color="sales",
        color_continuous_scale=["#E0F2F1", "#B2DFDB", "#80CBC4", "#4DB6AC", "#26A69A"]
    )
    fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor='rgba(0,0,0,0)', geo=dict(showframe=False))
    st.plotly_chart(fig_map, use_container_width=True)

with col_right:
    st.subheader("🎯 Klaster Profitabilitas")
    fig_clust = px.scatter(df_filtered, x='units_sold', y='profit', color='segment_cluster',
                           color_discrete_sequence=["#FFB7B2", "#B2CEE0", "#FDFD96"])
    fig_clust.update_layout(plot_bgcolor='white', margin=dict(t=10, b=0, l=0, r=0))
    st.plotly_chart(fig_clust, use_container_width=True)

# --- 9. ROW BAWAH: TREND & PIE CHART PROFIT ---
c1, c2 = st.columns(2)

with c1:
    st.subheader("📈 Tren Profit Bulanan")
    df_trend = df_filtered.groupby('date')['profit'].sum().reset_index()
    fig_trend = px.area(df_trend, x='date', y='profit', color_discrete_sequence=['#B2CEE0'])
    fig_trend.update_layout(plot_bgcolor='rgba(0,0,0,0)', xaxis_title="", yaxis_title="Profit ($)")
    st.plotly_chart(fig_trend, use_container_width=True)

with c2:
    st.subheader("🥧 Kontribusi Profit per Produk")
    df_pie = df_filtered.groupby('product')['profit'].sum().reset_index()
    # Pie Chart (Donut Style)
    fig_pie = px.pie(df_pie, values='profit', names='product',
                     color_discrete_sequence=px.colors.qualitative.Pastel,
                     hole=0.4)
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    fig_pie.update_layout(margin=dict(t=0, b=0, l=0, r=0))
    st.plotly_chart(fig_pie, use_container_width=True)

# --- 10. DETAIL TABLE ---
with st.expander("🔍 Lihat Detail Data Transaksi"):
    st.dataframe(df_filtered.style.background_gradient(cmap='Pastel1', subset=['profit']), use_container_width=True)
