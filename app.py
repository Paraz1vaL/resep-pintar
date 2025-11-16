# File: app.py
import streamlit as st
from utils import load_custom_css
# Impor fungsi "show_page" dari setiap file halaman
import beranda
import resep
import tentang

# --- Konfigurasi Halaman Utama ---
# Ini harus menjadi perintah Streamlit PERTAMA
st.set_page_config(
    page_title="ResepPintar", 
    page_icon="🍳",
    layout="centered" # Mengatur layout ke tengah
)

# Muat CSS kustom (dari utils.py)
# Ini akan menyembunyikan spinner cache & menata kotak metrik
load_custom_css()

# --- Buat Menu Tab (Menu di Tengah) ---
tab_beranda, tab_cari, tab_tentang = st.tabs([
    "🏠 Beranda", 
    "🔍 Cari Resep", 
    "ℹ️ Tentang"
])

# --- Konten untuk setiap tab ---

with tab_beranda:
    # Panggil fungsi show_page dari file page_beranda.py
    beranda.show_page()

with tab_cari:
    # Panggil fungsi show_page dari file page_cari_resep.py
    resep.show_page()

with tab_tentang:
    # Panggil fungsi show_page dari file page_tentang.py
    tentang.show_page()