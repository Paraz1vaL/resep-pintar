# File: page_tentang.py
import streamlit as st

def show_page():
    st.title("Tentang ResepPintar")
    st.markdown("""
    **ResepPintar** adalah katalog resep berbasis web yang dirancang untuk membantu pengguna menemukan ide masakan berdasarkan bahan-bahan yang mereka miliki.
    
    Aplikasi ini dibuat untuk mengatasi kebingungan memasak harian dan membantu mengurangi limbah makanan (food waste).
    
    ### Teknologi yang Digunakan
    * **Framework:** Streamlit
    * **API Resep:** Spoonacular
    * **Penerjemah:** DeepL
    """)
    st.markdown("---")
   