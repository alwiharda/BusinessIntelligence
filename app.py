import streamlit as st
import pandas as pd
import plotly.express as px
import os
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Financial & Clustering Dashboard", page_icon="📊", layout="wide")

# --- 2. CUSTOM CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #FBFBFE; }
    div[data-testid="stMetric"] {
        background-color: #FFFFFF; padding: 20px; border-radius: 20px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.02); border-left: 6px solid #FFB7B2;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATA LOADING & ETL ---
@st.cache_data
def load_data():
    file_path = "Financial Sample.xlsx"
    if not os.path.exists(file_path): return None
    df = pd.read_excel(file_path)
    df.columns = [c.strip().replace(' ', '_').lower() for c in df.columns]
    df['date'] = pd.to_datetime(df['date'])
    cols_fin = ['sales', 'profit', 'units_sold', 'gross_sales']
    for col in cols_fin:
        if df[col].dtype == 'object':
            df[col] = df[col].astype(str).str.replace(r'[\$,]', '', regex=True)
            df[col] = df[col].str.replace(r'\(', '-', regex=True).str.replace(r'\)', '', regex=True).astype(float)
    return df

df = load_data()

if df is None:
    st.error("⚠️ File 'Financial Sample.xlsx' tidak ditemukan!")
    st.stop()

# --- 4. SIDEBAR FILTER ---
st.sidebar.header("🎨 Filter Analisis")
country = st.sidebar.multiselect("Pilih Negara", df['country'].unique(), default=df['country'].unique())
df_filtered = df[df['country'].isin(country)].copy() # Gunakan .copy() untuk menghindari SettingWithCopyWarning

# --- 5. DATA MINING: K-MEANS CLUSTERING ---
if not df_filtered.empty:
    X_clust = df_filtered[['units_sold', 'profit']]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_clust)

    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    df_filtered['cluster'] = kmeans.fit_predict(X_scaled)
    df_filtered['cluster'] = df_filtered['cluster'].astype(str)

# --- 6. HEADER ---
st.title("🌸 Financial Intelligence & Clustering")

# --- 7. ROW 1: KPI ---
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Sales", f"${df_filtered['sales'].sum()/1e6:.2f}M")
m2.metric("Total Profit", f"${df_filtered['profit'].sum()/1e6:.2f}M")
m3.metric("Units Sold", f"{df_filtered['units_sold'].sum():,.0f}")
m4.metric("Avg Margin", f"{(df_filtered['profit'].sum()/df_filtered['sales'].sum()*100):.1f}%" if df_filtered['sales'].sum() != 0 else "0%")

st.write("---")

# --- 8. ROW 2: CLUSTERING ANALYSIS ---
col_clust_text, col_clust_chart = st.columns([1, 2])

with col_clust_text:
    st.subheader("🎯 Analisis Segmentasi")
    st.write("Rata-rata performa per kelompok transaksi:")
    
    # Ringkasan Klaster
    summary_df = df_filtered.groupby('cluster')[['units_sold', 'profit']].mean()
    # Menampilkan tabel (tanpa gradien jika Anda ingin menghindari resiko matplotlib lagi, 
    # tapi karena sudah ditambah di requirements, ini akan aman)
    st.dataframe(summary_df.style.background_gradient(cmap='PuBu'), use_container_width=True)

with col_clust_chart:
    
    fig_clust = px.scatter(df_filtered, x='units_sold', y='profit', color='cluster',
                           hover_data=['product', 'country', 'segment'],
                           title="Segmentasi Transaksi: Units Sold vs Profit",
                           color_discrete_sequence=px.colors.qualitative.Pastel)
    fig_clust.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_clust, use_container_width=True)

# --- 9. ROW 3: TREND & MAP ---
c1, c2 = st.columns(2)

with c1:
    st.subheader("📈 Tren Penjualan")
    df_trend = df_filtered.groupby('date')['sales'].sum().reset_index()
    fig_line = px.line(df_trend, x='date', y='sales', color_discrete_sequence=['#B2CEE0'])
    st.plotly_chart(fig_line, use_container_width=True)

with c2:
    st.subheader("🌍 Sebaran Penjualan Global")
    map_data = df_filtered.groupby('country')['sales'].sum().reset_index()
    fig_map = px.choropleth(map_data, locations="country", locationmode='country names', 
                            color="sales", color_continuous_scale="Purples")
    st.plotly_chart(fig_map, use_container_width=True)

# --- 10. ROW 4: DATA TABLE ---
with st.expander("🔍 Lihat Detail Data Mentah"):
    st.write(df_filtered)
