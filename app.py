import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Customer Churn Dashboard", layout="wide")

# Custom CSS & JS untuk Animasi Angka Berjalan dan UI Menarik
st.markdown("""
    <style>
    .stApp { background-color: #FDFCF0; }
    
    .main-title {
        text-align: center;
        color: #6D8299;
        font-family: 'Segoe UI', sans-serif;
        font-size: 3rem;
        font-weight: bold;
        padding: 20px 0;
    }
    
    .metric-label {
        color: #8E9794;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    h2, h3 { color: #6D8299; font-family: 'Segoe UI', sans-serif; margin-bottom: 20px;}
    div[data-testid="stMetric"] { display: none; } 
    
    /* Styling khusus untuk expander agar lebih menarik */
    .streamlit-expanderHeader {
        background-color: rgba(255, 255, 255, 0.5);
        border-radius: 10px;
        color: #6D8299 !important;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# Fungsi Helper untuk Animasi Counter (JavaScript)
def animated_metric(label, value, prefix="", suffix="", precision=0):
    div_id = label.replace(" ", "").lower()
    component_html = f"""
    <div style="text-align:center; font-family:'Segoe UI', sans-serif; background:rgba(255,255,255,0.8); padding:25px; border-radius:20px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: 1px solid rgba(255,255,255,0.3);">
        <div style="color:#8E9794; font-size:0.9rem; text-transform:uppercase; letter-spacing:1px; margin-bottom:5px;">{label}</div>
        <div id="{div_id}" style="font-size:2.2rem; font-weight:bold; color:#6D8299;">0</div>
    </div>
    <script>
    (function() {{
        var start = 0;
        var end = {value};
        var duration = 1500;
        var current = start;
        var increment = end > start ? (end / (duration / 16)) : 0;
        var obj = document.getElementById('{div_id}');
        var timer = setInterval(function() {{
            current += increment;
            if ((increment > 0 && current >= end) || (increment <= 0 && current <= end)) {{
                clearInterval(timer);
                current = end;
            }}
            var formatted = current.toLocaleString('en-US', {{minimumFractionDigits: {precision}, maximumFractionDigits: {precision}}});
            obj.innerHTML = "{prefix}" + formatted + "{suffix}";
        }}, 16);
    }})();
    </script>
    """
    st.components.v1.html(component_html, height=150)

# Palet Warna Pastel
PASTEL_PALETTE = ['#AEC6CF', '#FFB7B2', '#B2E2F2', '#FFDAC1', '#E2F0CB', '#B5EAD7']

# --- 2. LOAD DATA ---
@st.cache_data
def load_data():
    file_path = 'WA_Fn-UseC_-Telco-Customer-Churn.csv'
    try:
        df = pd.read_csv(file_path)
        df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
        df.dropna(subset=['TotalCharges'], inplace=True)
        df['PaymentMethod'] = df['PaymentMethod'].str.replace(' (automatic)', '', regex=False)
        return df
    except:
        return None

df = load_data()

if df is not None:
    # --- 3. SIDEBAR ---
    st.sidebar.header("⚙️ Filter")
    contract_filter = st.sidebar.multiselect("Tipe Kontrak:", df['Contract'].unique(), default=df['Contract'].unique())
    filtered_df = df[df['Contract'].isin(contract_filter)]

    # --- 4. HEADER & ANIMATED METRICS ---
    st.markdown('<div class="main-title">📊 Customer Churn Business Intelligence 📊</div>', unsafe_allow_html=True)
    
    total_cust = float(len(filtered_df))
    churn_rate = float((filtered_df['Churn'] == 'Yes').mean() * 100)
    avg_tenure = float(filtered_df['tenure'].mean())
    total_rev = float(filtered_df['TotalCharges'].sum() / 1e3)

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1: animated_metric("Total Pelanggan", total_cust)
    with col_m2: animated_metric("Churn Rate", churn_rate, suffix="%", precision=1)
    with col_m3: animated_metric("Rata-rata Tenure", avg_tenure, suffix=" Bln", precision=1)
    with col_m4: animated_metric("Total Revenue", total_rev, prefix="$", suffix="K", precision=1)

    st.divider()

    # --- 5. VISUALISASI BARIS ATAS (Internet & Contract) ---
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        st.subheader("📶 Layanan Internet")
        fig1 = px.histogram(filtered_df, x="InternetService", color="Churn", barmode="group",
                            color_discrete_sequence=[PASTEL_PALETTE[2], PASTEL_PALETTE[1]])
        fig1.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=350)
        st.plotly_chart(fig1, use_container_width=True)

    with col_v2:
        st.subheader("📝 Tipe Kontrak")
        fig2 = px.histogram(filtered_df, x="Contract", color="Churn", barmode="group",
                            color_discrete_sequence=[PASTEL_PALETTE[0], PASTEL_PALETTE[1]])
        fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=350)
        st.plotly_chart(fig2, use_container_width=True)

    # --- 6. VISUALISASI BARIS TENGAH (Pie Chart & Segmentasi Sampingan) ---
    col_v3, col_v4 = st.columns([1, 1]) 
    
    with col_v3:
        st.subheader("💳 Metode Pembayaran")
        fig3 = px.pie(filtered_df, names='PaymentMethod', hole=0.5, color_discrete_sequence=PASTEL_PALETTE)
        fig3.update_layout(paper_bgcolor='rgba(0,0,0,0)', height=400, showlegend=True)
        fig3.update_traces(textinfo='percent')
        st.plotly_chart(fig3, use_container_width=True)

    with col_v4:
        st.subheader("🎯 Segmentasi Pelanggan")
        X = filtered_df[['tenure', 'MonthlyCharges']]
        X_scaled = StandardScaler().fit_transform(X)
        filtered_df['Cluster'] = KMeans(n_clusters=3, random_state=42).fit_predict(X_scaled)
        
        fig4 = px.scatter(filtered_df, x="tenure", y="MonthlyCharges", color=filtered_df['Cluster'].astype(str),
                          symbol="Churn", color_discrete_sequence=PASTEL_PALETTE)
        fig4.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=400)
        st.plotly_chart(fig4, use_container_width=True)

    st.divider()

    # --- 7. TABEL DATA (BISA DISEMBUNYIKAN) ---
    with st.expander("🔍 Klik untuk Melihat Detail Database Pelanggan"):
        st.markdown("### Detail Data (100 Baris Pertama)")
        st.dataframe(
            filtered_df.head(100),
            use_container_width=True,
            column_config={
                "Churn": st.column_config.TextColumn("Status Churn"),
                "MonthlyCharges": st.column_config.NumberColumn("Biaya Bulanan", format="$%.2f"),
                "TotalCharges": st.column_config.ProgressColumn(
                    "Akumulasi Pendapatan", 
                    format="$%.2f", 
                    min_value=0, 
                    max_value=float(filtered_df['TotalCharges'].max())
                ),
                "tenure": st.column_config.NumberColumn("Tenure (Bulan)", format="%d 📅"),
                "Cluster": st.column_config.TextColumn("Grup Segmen"),
            },
            hide_index=True
        )

else:
    st.error("File tidak ditemukan.")

