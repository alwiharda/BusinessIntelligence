import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Customer Churn Dashboard", layout="wide")

# Custom CSS agar semua elemen menyatu dengan background dan judul di tengah
st.markdown("""
    <style>
    /* Latar belakang utama */
    .stApp { background-color: #FDFCF0; }
    
    /* Judul Utama di Tengah */
    .main-title {
        text-align: center;
        color: #6D8299;
        font-family: 'Segoe UI', sans-serif;
        font-size: 3rem;
        font-weight: bold;
        padding: 20px 0;
    }
    
    /* Kartu metrik tanpa border putih yang kaku */
    [data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.5);
        padding: 20px;
        border-radius: 15px;
    }
    
    h2, h3 { color: #6D8299; font-family: 'Segoe UI', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

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

    # --- 4. HEADER (JUDUL DI TENGAH) ---
    st.markdown('<div class="main-title">📊 Customer Churn Business Intelligence</div>', unsafe_allow_html=True)
    
    m1, m2, m3, m4 = st.columns(4)
    with m1: st.metric("Total Pelanggan", len(filtered_df))
    with m2: st.metric("Churn Rate", f"{(filtered_df['Churn'] == 'Yes').mean()*100:.1f}%")
    with m3: st.metric("Rata-rata Tenure", f"{filtered_df['tenure'].mean():.1f} Bln")
    with m4: st.metric("Total Revenue", f"${filtered_df['TotalCharges'].sum()/1e3:.1f}K")

    st.divider()

    # --- 5. VISUALISASI BARIS ATAS (Layanan & Kontrak) ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📶 Layanan Internet")
        fig1 = px.histogram(filtered_df, x="InternetService", color="Churn", barmode="group",
                            color_discrete_sequence=[PASTEL_PALETTE[2], PASTEL_PALETTE[1]])
        fig1.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=350)
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.subheader("📝 Tipe Kontrak")
        fig2 = px.histogram(filtered_df, x="Contract", color="Churn", barmode="group",
                            color_discrete_sequence=[PASTEL_PALETTE[0], PASTEL_PALETTE[1]])
        fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=350)
        st.plotly_chart(fig2, use_container_width=True)

    # --- 6. VISUALISASI PIE CHART (Kecil & Tengah) ---
    st.write("") 
    _, col_pie, _ = st.columns([1, 2, 1]) 
    with col_pie:
        st.subheader("💳 Metode Pembayaran")
        fig3 = px.pie(filtered_df, names='PaymentMethod', hole=0.5, color_discrete_sequence=PASTEL_PALETTE)
        fig3.update_layout(paper_bgcolor='rgba(0,0,0,0)', height=350, showlegend=True)
        fig3.update_traces(textinfo='percent')
        st.plotly_chart(fig3, use_container_width=True)

    st.divider()

    # --- 7. CLUSTERING ---
    st.subheader("🎯 Segmentasi Pelanggan")
    X = filtered_df[['tenure', 'MonthlyCharges']]
    X_scaled = StandardScaler().fit_transform(X)
    filtered_df['Cluster'] = KMeans(n_clusters=3, random_state=42).fit_predict(X_scaled)
    
    fig4 = px.scatter(filtered_df, x="tenure", y="MonthlyCharges", color=filtered_df['Cluster'].astype(str),
                      symbol="Churn", color_discrete_sequence=PASTEL_PALETTE)
    fig4.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=450)
    st.plotly_chart(fig4, use_container_width=True)

else:
    st.error("File tidak ditemukan.")
