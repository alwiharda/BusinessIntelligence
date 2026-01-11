import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Customer Churn Dashboard", layout="wide")

# Custom CSS untuk tampilan Pastel & UI Modern
st.markdown("""
    <style>
    .stApp { background-color: #FDFCF0; }
    [data-testid="stMetric"] {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.02);
    }
    h1, h2, h3 { color: #6D8299; font-family: 'Segoe UI', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# Palet Warna Pastel
PASTEL_PALETTE = ['#AEC6CF', '#FFB7B2', '#B2E2F2', '#FFDAC1', '#E2F0CB', '#B5EAD7']

# --- 2. ETL & DATA CLEANING ---
@st.cache_data
def load_and_clean_data():
    file_path = 'WA_Fn-UseC_-Telco-Customer-Churn.csv'
    try:
        df = pd.read_csv(file_path)
        # Cleaning: Konversi TotalCharges ke numerik
        df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
        df.dropna(subset=['TotalCharges'], inplace=True)
        # Standardize string
        df['PaymentMethod'] = df['PaymentMethod'].str.replace(' (automatic)', '', regex=False)
        return df
    except FileNotFoundError:
        return None

df = load_and_clean_data()

if df is not None:
    # --- 3. SIDEBAR FILTER ---
    st.sidebar.header("⚙️ Filter Dashboard")
    contract_filter = st.sidebar.multiselect(
        "Pilih Tipe Kontrak:",
        options=df['Contract'].unique(),
        default=df['Contract'].unique()
    )
    
    # Filter Data
    filtered_df = df[df['Contract'].isin(contract_filter)]

    # --- 4. HEADER & KPI METRICS ---
    st.title("📊 Customer Churn Business Intelligence")
    st.markdown("Dashboard interaktif untuk menganalisis risiko churn dan segmentasi pelanggan.")

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Total Pelanggan", len(filtered_df))
    with m2:
        churn_rate = (filtered_df['Churn'] == 'Yes').mean() * 100
        st.metric("Churn Rate", f"{churn_rate:.1f}%")
    with m3:
        st.metric("Rata-rata Tenure", f"{filtered_df['tenure'].mean():.1f} Bln")
    with m4:
        st.metric("Total Revenue", f"${filtered_df['TotalCharges'].sum()/1e3:.1f}K")

    st.divider()

    # --- 5. VISUALISASI UTAMA & TAMBAHAN ---
    row1_col1, row1_col2 = st.columns(2)

    with row1_col1:
        st.subheader("📶 Churn Berdasarkan Layanan Internet")
        # Menghitung jumlah churn per layanan internet
        service_churn = filtered_df.groupby(['InternetService', 'Churn']).size().reset_index(name='Jumlah')
        fig_service = px.bar(service_churn, x="InternetService", y="Jumlah", color="Churn",
                             barmode="group",
                             color_discrete_sequence=[PASTEL_PALETTE[2], PASTEL_PALETTE[1]])
        fig_service.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_service, use_container_width=True)

    with row1_col2:
        st.subheader("📝 Churn per Tipe Kontrak")
        fig_bar = px.histogram(filtered_df, x="Contract", color="Churn",
                               barmode="group",
                               color_discrete_sequence=[PASTEL_PALETTE[0], PASTEL_PALETTE[1]])
        st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()

    # --- 6. DATA MINING (CLUSTERING) ---
    st.subheader("🎯 Segmentasi Pelanggan (K-Means Clustering)")
    col_clust1, col_clust2 = st.columns([2, 1])

    with col_clust1:
        # Menjalankan K-Means
        X = filtered_df[['tenure', 'MonthlyCharges']]
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        kmeans = KMeans(n_clusters=3, random_state=42)
        filtered_df['Cluster'] = kmeans.fit_predict(X_scaled)
        
        fig_cluster = px.scatter(filtered_df, x="tenure", y="MonthlyCharges", 
                                 color=filtered_df['Cluster'].astype(str), 
                                 symbol="Churn",
                                 title="Visualisasi Klaster: Tenure vs Monthly Charges",
                                 color_discrete_sequence=PASTEL_PALETTE)
        st.plotly_chart(fig_cluster, use_container_width=True)

    with col_clust2:
        st.info("""
        **Analisis Klaster:**
        - **Cluster 0 (Biru):** Pelanggan Baru/Biaya Rendah.
        - **Cluster 1 (Pink):** Pelanggan High-Charges.
        - **Cluster 2 (Cyan):** Pelanggan Setia (High Tenure).
        """)

    # --- 7. TABEL DATA ---
    with st.expander("🔍 Lihat Detail Data Mentah"):
        st.dataframe(filtered_df.head(100), use_container_width=True)

else:
    st.error("File 'WA_Fn-UseC_-Telco-Customer-Churn.csv' tidak ditemukan.")
