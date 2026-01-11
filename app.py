import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# --- 1. CONFIG DASHBOARD ---
st.set_page_config(page_title="Executive Financial Dashboard", layout="wide")

# --- 2. CSS UTAMA ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
    html, body, [class*="css"] { 
        font-family: 'Plus Jakarta Sans', sans-serif; 
        background-color: #F8FAFC; 
    }
    .main-title { 
        color: #475569; font-weight: 800; font-size: 2.5rem; 
        margin-bottom: 25px; text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNGSI ANIMASI DENGAN CSS TERINTEGRASI ---
def animated_metric(label, value, prefix="", suffix="", color="#B2CEE0", element_id=""):
    decimals = 2 if prefix == "$" else (1 if suffix == "%" else 0)
    
    html_code = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
        .metric-card {{
            background: white;
            padding: 22px;
            border-radius: 18px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.04);
            border-top: 5px solid {color};
            font-family: 'Plus Jakarta Sans', sans-serif;
        }}
        .metric-label {{ color: #64748b; font-size: 14px; font-weight: 600; }}
        .metric-value {{ color: #1e293b; font-size: 26px; font-weight: 800; margin-top: 5px; }}
    </style>
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{prefix}<span id="{element_id}">0</span>{suffix}</div>
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/countup.js/1.9.3/countUp.min.js"></script>
    <script>
        var numAnim = new CountUp('{element_id}', 0, {value}, {decimals}, 2);
        if (!numAnim.error) {{ numAnim.start(); }}
    </script>
    """
    return st.components.v1.html(html_code, height=140)

# --- 3. DATA LOADING ---
@st.cache_data
def load_data():
    file_path = "Financial Sample.xlsx"
    if not os.path.exists(file_path): return None
    df = pd.read_excel(file_path)
    df.columns = [c.strip().replace(' ', '_').lower() for c in df.columns]
    cols_fin = ['sales', 'profit', 'units_sold', 'gross_sales', 'cogs', 'discounts']
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

# --- 4. SIDEBAR ---
st.sidebar.markdown("### 🌸 Filter Dashboard")
selected_countries = st.sidebar.multiselect("Pilih Negara", df['country'].unique(), default=df['country'].unique())
df_filtered = df[df['country'].isin(selected_countries)].copy()

# --- 5. CLUSTERING (Tetap ada di latar belakang untuk detail data) ---
if len(df_filtered) > 1:
    X = df_filtered[['units_sold', 'profit']]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    df_filtered['segment_cluster'] = kmeans.fit_predict(X_scaled)
    df_filtered['segment_cluster'] = df_filtered['segment_cluster'].map({0: 'Low Performance', 1: 'High Performance', 2: 'Average'})

# --- 6. HEADER ---
st.markdown('<h1 class="main-title">🌸 Financial Intelligence Insights 🌸</h1>', unsafe_allow_html=True)

# --- 7. METRICS (ANIMATED) ---
total_sales = df_filtered['sales'].sum()
total_profit = df_filtered['profit'].sum()
units_sold = df_filtered['units_sold'].sum()
margin = (total_profit / total_sales * 100) if total_sales != 0 else 0

m1, m2, m3, m4 = st.columns(4)
with m1:
    animated_metric("💰 Total Sales", total_sales/1e6, prefix="$", suffix="M", color="#B2CEE0", element_id="m1")
with m2:
    animated_metric("📈 Total Profit", total_profit/1e6, prefix="$", suffix="M", color="#FFB7B2", element_id="m2")
with m3:
    animated_metric("📦 Units Sold", units_sold, prefix="", suffix="", color="#B2DFDB", element_id="m3")
with m4:
    animated_metric("📊 Gross Margin", margin, prefix="", suffix="%", color="#FDFD96", element_id="m4")

st.write("") 

# --- 8. ROW ATAS: MAP & MARKET SEGMENT BAR PLOT (Pembaruan di Sini) ---
col_left, col_right = st.columns([1.5, 1])
with col_left:
    st.subheader("🌍 Sebaran Penjualan Global")
    map_data = df_filtered.groupby('country')['sales'].sum().reset_index()
    fig_map = px.choropleth(map_data, locations="country", locationmode='country names', color="sales",
                            color_continuous_scale=["#E0F2F1", "#B2DFDB", "#80CBC4", "#4DB6AC", "#26A69A"])
    fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor='rgba(0,0,0,0)', geo=dict(showframe=False))
    st.plotly_chart(fig_map, use_container_width=True)

with col_right:
    st.subheader("📊 Unit Terjual per Kategori Segmen")
    # Agregasi total unit terjual per kategori 'segment'
    df_market_seg = df_filtered.groupby('segment')['units_sold'].sum().sort_values(ascending=True).reset_index()
    
    # Membuat Bar Plot Horizontal agar nama segmen panjang mudah dibaca
    fig_bar = px.bar(df_market_seg, x='units_sold', y='segment', orientation='h',
                     color='units_sold',
                     color_continuous_scale=["#B2CEE0", "#4DB6AC"],
                     text_auto='.2s')
    
    fig_bar.update_layout(
        plot_bgcolor='white', 
        margin=dict(t=10, b=0, l=0, r=0),
        xaxis_title="Total Unit Terjual",
        yaxis_title="",
        coloraxis_showscale=False
    )
    st.plotly_chart(fig_bar, use_container_width=True)

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


