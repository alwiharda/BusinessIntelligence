import streamlit as st
import pandas as pd
import plotly.express as px
import os
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# --- 1. CONFIG DASHBOARD ---
st.set_page_config(page_title="Executive Financial Dashboard", layout="wide")

# --- 2. CUSTOM CSS (PASTEL THEME) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #F8FAFC; }
    
    /* Metric Card Styling */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
        border-left: 6px solid #B2CEE0;
    }
    .main-title { color: #475569; font-weight: 800; font-size: 2.2rem; margin-bottom: 25px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATA LOADING & ROBUST CLEANING ---
@st.cache_data
def load_data():
    file_path = "Financial Sample.xlsx"
    if not os.path.exists(file_path): return None
    
    df = pd.read_excel(file_path)
    df.columns = [c.strip().replace(' ', '_').lower() for c in df.columns]
    
    # Cleaning: Menangani simbol $, koma, dan format akuntansi (100) -> -100
    cols_fin = ['sales', 'profit', 'units_sold', 'gross_sales', 'cogs', 'discounts']
    for col in cols_fin:
        if df[col].dtype == 'object':
            # Hilangkan spasi dan simbol
            df[col] = df[col].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False).str.strip()
            # Deteksi angka dalam kurung sebagai negatif
            df[col] = df[col].apply(lambda x: f"-{x[1:-1]}" if x.startswith('(') and x.endswith(')') else x)
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    df['date'] = pd.to_datetime(df['date'])
    return df

df = load_data()

if df is None:
    st.error("File 'Financial Sample.xlsx' tidak ditemukan di direktori GitHub Anda!")
    st.stop()

# --- 4. SIDEBAR FILTERS ---
st.sidebar.markdown("### 🌸 Control Panel")
countries = st.sidebar.multiselect("Pilih Negara", df['country'].unique(), default=df['country'].unique())
segments = st.sidebar.multiselect("Pilih Segmen", df['segment'].unique(), default=df['segment'].unique())

df_filtered = df[(df['country'].isin(countries)) & (df['segment'].isin(segments))].copy()

# --- 5. CLUSTERING LOGIC ---
if not df_filtered.empty:
    X_clust = df_filtered[['units_sold', 'profit']]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_clust)
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    df_filtered['cluster_label'] = kmeans.fit_predict(X_scaled)
    df_filtered['cluster_label'] = df_filtered['cluster_label'].map({0: 'Low Performance', 1: 'High Performance', 2: 'Average'})

# --- 6. HEADER ---
st.markdown('<h1 class="main-title">🌸 Financial Performance Analysis</h1>', unsafe_allow_html=True)

# --- 7. KPI METRICS ---
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
col_m1.metric("Total Sales", f"${df_filtered['sales'].sum()/1e6:.2f}M")
col_m2.metric("Total Profit", f"${df_filtered['profit'].sum()/1e6:.2f}M")
col_m3.metric("Units Sold", f"{df_filtered['units_sold'].sum():,.0f}")
col_m4.metric("Avg Margin", f"{(df_filtered['profit'].sum()/df_filtered['sales'].sum()*100):.1f}%" if df_filtered['sales'].sum() != 0 else "0%")

st.markdown("---")

# --- 8. VISUALISASI ROW 1 (PIE CHART & MAP) ---
c1, c2 = st.columns([1, 1.2])

with c1:
    st.subheader("🍕 Profit Contribution by Product")
    # Profit Pie Chart
    
    fig_pie = px.pie(df_filtered, values='profit', names='product',
                     color_discrete_sequence=px.colors.qualitative.Pastel,
                     hole=0.5) # Membuat Donut Chart agar lebih modern
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    fig_pie.update_layout(showlegend=False, margin=dict(t=30, b=10, l=10, r=10))
    st.plotly_chart(fig_pie, use_container_width=True)

with c2:
    st.subheader("🌍 Global Sales Distribution")
    map_data = df_filtered.groupby('country')['sales'].sum().reset_index()
    fig_map = px.choropleth(map_data, locations="country", locationmode='country names',
                            color="sales", color_continuous_scale="Mint")
    fig_map.update_layout(margin=dict(t=10, b=10, l=10, r=10))
    st.plotly_chart(fig_map, use_container_width=True)

# --- 9. VISUALISASI ROW 2 (TREND & CLUSTER) ---
c3, c4 = st.columns([1.2, 1])

with c3:
    st.subheader("📈 Monthly Profit Trend")
    df_monthly = df_filtered.groupby(pd.Grouper(key='date', freq='M'))['profit'].sum().reset_index()
    fig_trend = px.area(df_monthly, x='date', y='profit', color_discrete_sequence=['#B2CEE0'])
    fig_trend.update_layout(xaxis_title="", yaxis_title="Profit ($)", plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_trend, use_container_width=True)

with c4:
    st.subheader("🎯 Clustering Analysis")
    fig_scatter = px.scatter(df_filtered, x='units_sold', y='profit', color='cluster_label',
                             color_discrete_sequence=["#FFB7B2", "#B2E2F2", "#FDFD96"],
                             hover_data=['product', 'country'])
    fig_scatter.update_layout(plot_bgcolor='white')
    st.plotly_chart(fig_scatter, use_container_width=True)

# --- 10. RAW DATA TABLE ---
with st.expander("🔍 View Raw Data Details"):
    st.dataframe(df_filtered.sort_values('date', ascending=False), use_container_width=True)

st.caption("Dashboard v1.3 | Powered by Streamlit & Machine Learning")
