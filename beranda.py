# File: page_beranda.py
import streamlit as st

def show_page():
    st.title("🍳 ResepPintar")
    st.markdown("Selamat datang di **ResepPintar**! Web ini dirancang untuk membantu Anda menemukan ide masakan berdasarkan bahan-bahan yang Anda miliki. Mari bergabung dalam petualangan memahami dan memanfaatkan bahan di dapur dengan cara yang inovatif dan berkelanjutan. 🧑‍🍳✨")

    st.header("Tahukah Kamu?")
    st.markdown("Aplikasi ini bertujuan membantu mengurangi limbah makanan (food waste) di Indonesia.")

    # Kotak Metrik
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="metric-box grey">
            <h3>Limbah Makanan</h3>
            <p>184 kg</p>
            <span>per kapita / tahun</span>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="metric-box yellow">
            <h3>Bahan Sering Terbuang</h3>
            <p>Sayuran</p>
            <span>& Makanan Sisa</span>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="metric-box blue">
            <h3>Potensi Penghematan</h3>
            <p>~Rp 5 Juta</p>
            <span>per keluarga / tahun</span>
        </div>
        """, unsafe_allow_html=True)
        
    col4, col5 = st.columns(2)
    with col4:
        st.markdown("""
        <div class="metric-box green">
            <h3>Resep Tersedia</h3>
            <p>500.000+</p>
            <span>dari seluruh dunia</span>
        </div>
        """, unsafe_allow_html=True)
    with col5:
        st.markdown("""
        <div class="metric-box red">
            <h3>Tantangan Memasak</h3>
            <p>65%</p>
            <span>orang bingung masak apa</span>
        </div>
        """, unsafe_allow_html=True)