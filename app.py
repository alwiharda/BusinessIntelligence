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
    
    /* Card Style */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.03);
        border-bottom: 5px solid #E2E8F0;
    }
    
    .main-title { 
        color: #475569; 
        font-weight: 800; 
        font-size: 2.5rem; 
        margin-bottom: 20px; 
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATA LOADING & FIXING PROFIT ---
@st.cache_data
def load_data():
    file_path = "Financial Sample.xlsx"
    if not os.path.exists(file_path): return None
    
    df = pd.read_excel(file_path)
    df.columns = [c.strip().replace(' ', '_').lower() for c in df.columns]
    
    # FIX: Membersihkan data finansial secara mendalam
    cols_fin = ['sales', 'profit', 'units_sold', 'gross_sales', 'cogs', 'discounts']
    for col in cols_fin:
        if df[col].dtype == 'object':
            df[col] = df[col].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False).str.strip()
            # Menangani format (1,000.00) sebagai negatif
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
    df_filtered['segment_cluster'] = df_filtered['segment_cluster'].map({0: 'Low Vol', 1: 'High Prof', 2: 'Mid Vol'})

# --- 6. HEADER ---
st.markdown('<h1 class="main-title">Financial Executive Insights</h1>', unsafe_allow_html=True)

# --- 7. METRICS (PASTEL ACCENT) ---
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Sales", f"${df_filtered['sales'].sum()/1e6:.2f}M")
m2.metric("Total Profit", f"${df_filtered['profit'].sum()/1e6:.2f}M")
m3.metric("Units Sold", f"{df_filtered['units_sold'].sum():,.0f}")
m4.metric("Gross Margin", f"{(df_filtered['profit'].sum()/df_filtered['sales'].sum()*100):.1f}%" if df_filtered['sales'].sum() != 0 else "0%")

st.markdown("---")

# --- 8. VISUALISASI ATAS (MAP & CLUSTER) ---
col_left, col_right = st.columns([1.5, 1])

with col_left:
    st.subheader("🌍 Sebaran Penjualan Global")
    map_data = df_filtered.groupby('country')['sales'].sum().reset_index()
    # Gradien Pastel Mint
    fig_map = px.choropleth(map_data, locations="country", locationmode='country names', 
                            color="sales", color_continuous_scale=["#E0F2F1", "#B2DFDB", "#4DB6AC"])
    fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_map, use_container_width=True)

with col_right:
    st.subheader("🎯 Klaster Profitabilitas")
    fig_clust = px.scatter(df_filtered, x='units_sold', y='profit', color='segment_cluster',
                           color_discrete_sequence=["#FFB7B2", "#B2CEE0", "#FDFD96"], 
                           title="Segmentasi Transaksi")
    fig_clust.update_layout(plot_bgcolor='white')
    st.plotly_chart(fig_clust, use_container_width=True)

# --- 9. TREN & PIE CHART PROFIT (BAGIAN YANG DIUBAH) ---
c1, c2 = st.columns(2)
with c1:
    st.subheader("📈 Tren Profit Bulanan")
    df_trend = df_filtered.groupby('date')['profit'].sum().reset_index()
    fig_trend = px.line(df_trend, x='date', y='profit', line_shape='spline')
    fig_trend.update_traces(line_color='#B2CEE0', line_width=4)
    fig_trend.update_layout(plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_trend, use_container_width=True)

with c2:
    st.subheader("🥧 Kontribusi Profit per Produk")
    # Mengelompokkan profit berdasarkan produk
    df_profit_prod = df_filtered.groupby('product')['profit'].sum().reset_index()
    
    # Membuat Pie Chart (Donut Style)
    
    fig_pie = px.pie(df_profit_prod, values='profit', names='product',
                     color_discrete_sequence=px.colors.qualitative.Pastel,
                     hole=0.4) # Membuat lubang di tengah agar jadi Donut Chart
    
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    fig_pie.update_layout(showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.2))
    st.plotly_chart(fig_pie, use_container_width=True)

# --- 10. DETAIL TABLE ---
with st.expander("🔍 Lihat Detail Data Transaksi"):
    st.dataframe(df_filtered.style.background_gradient(cmap='Pastel1', subset=['profit']), use_container_width=True)
