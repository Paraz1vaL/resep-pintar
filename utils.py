# File: utils.py
import streamlit as st
import requests
import deepl  # Import library
import time

# --- Konfigurasi API ---
SPOONACULAR_API_KEY = st.secrets.get("SPOONACULAR_API_KEY")
DEEPL_API_KEY = st.secrets.get("DEEPL_API_KEY") # Ambil key DeepL

SPOONACULAR_URL_SEARCH = "https://api.spoonacular.com/recipes/findByIngredients"
SPOONACULAR_URL_DETAIL_TEMPLATE = "https://api.spoonacular.com/recipes/{id}/information"

# --- Inisialisasi Penerjemah ---
# <-- PERUBAHAN BESAR DI BLOK INI -->
translator = None
if DEEPL_API_KEY:
    try:
        # Inisialisasi translator resmi DeepL
        # KITA TAMBAHKAN 'server_url' UNTUK API GRATIS
        translator = deepl.Translator(
            DEEPL_API_KEY,
            server_url="https://api-free.deepl.com" # <-- INI SOLUSINYA
        )
        
        # Kita tes otentikasi sekali saat startup
        usage = translator.get_usage()
        if usage.character.limit_exceeded:
            st.error("Otentikasi DeepL Berhasil, TAPI Kuota Anda sudah habis.")
        else:
            print("Otentikasi DeepL (Free API) Berhasil.")

    except deepl.exceptions.AuthorizationException as e:
        # Error ini berarti API KEY Anda 100% salah
        st.error(f"Gagal Otentikasi DeepL: API Key Anda salah. Cek .streamlit/secrets.toml. Detail: {e}")
        translator = None # Pastikan translator nonaktif
    except Exception as e:
        # Error lain (misal: tidak bisa konek)
        st.error(f"Gagal menginisialisasi DeepL Translator: {e}")
        translator = None
else:
    st.error("API Key DeepL tidak ditemukan. Harap tambahkan DEEPL_API_KEY ke .streamlit/secrets.toml")

# --- Fungsi CSS Kustom (Tidak berubah) ---
def load_custom_css():
    st.markdown("""
    <style>
    /* CSS untuk menyembunyikan spinner "Running..." */
    [data-testid="stSpinner"] {
        display: none;
    }

    /* CSS untuk kotak metrik kustom (kode Anda) */
    .metric-box {
        background-color: #333; border-radius: 10px; padding: 15px;
        margin-bottom: 10px; color: white;
    }
    .metric-box h3 { font-size: 16px; color: #CCC; margin-bottom: 5px; }
    .metric-box p { font-size: 24px; font-weight: bold; margin-bottom: 5px; }
    .metric-box span { font-size: 14px; color: #AAA; }
    .metric-box.blue { background-color: #004a9e; }
    .metric-box.yellow { background-color: #b38600; }
    .metric-box.green { background-color: #006400; }
    .metric-box.red { background-color: #8b0000; }
    .metric-box.grey { background-color: #4a4a4a; }
    </style>
    """, unsafe_allow_html=True)

# --- Fungsi Backend (Cache) ---

@st.cache_data(ttl=3600)
def terjemahkan_ke_inggris(teks_indonesia):
    """Menerjemahkan input pengguna dari ID ke EN menggunakan DeepL."""
    if not translator:
        print("Translator DeepL tidak siap, skip terjemahan.")
        return None # Gagal jika translator tidak siap
        
    print(f"CACHE MISS (DeepL): Menerjemahkan KE EN '{teks_indonesia}'")
    try:
        result = translator.translate_text(teks_indonesia, source_lang="ID", target_lang="EN-US")
        return result.text
    except Exception as e:
        st.error(f"Error saat menerjemahkan (DeepL ID-EN): {e}")
        return None

@st.cache_data(ttl=3600)
def search_recipes_api(ingredients_query):
    """Memanggil API Spoonacular findByIngredients (Tidak berubah)."""
    if not SPOONACULAR_API_KEY:
        st.error("API Key Spoonacular belum diatur.")
        return []
    
    print(f"CACHE MISS: Memanggil API pencarian untuk '{ingredients_query}'")
    params = {
        "ingredients": ingredients_query, "number": 5,
        "apiKey": SPOONACULAR_API_KEY, "ranking": 1
    }
    try:
        response = requests.get(SPOONACULAR_URL_SEARCH, params=params)
        response.raise_for_status()
        search_data = response.json()
        return [recipe.get('id') for recipe in search_data if recipe.get('id')]
    except requests.RequestException as e:
        st.error(f"Gagal koneksi API pencarian: {e}")
        return []

@st.cache_data(ttl=3600)
def get_recipe_detail_api(recipe_id):
    """Memanggil API Spoonacular dan menerjemahkan (DeepL)."""
    if not SPOONACULAR_API_KEY or not translator:
        print("Spoonacular Key atau Translator DeepL tidak siap, skip detail.")
        return None
        
    print(f"CACHE MISS (DeepL): Memanggil API detail untuk ID '{recipe_id}'")
    detail_url = SPOONACULAR_URL_DETAIL_TEMPLATE.format(id=recipe_id)
    params = { "apiKey": SPOONACULAR_API_KEY, "includeNutrition": False }
    
    try:
        # 1. Ambil data (Bahasa Inggris)
        response = requests.get(detail_url, params=params)
        response.raise_for_status()
        detail = response.json()
        
        nama_en = detail.get('title', 'Judul Tidak Ditemukan')
        url_en = detail.get('sourceUrl', f"https://spoonacular.com/recipes/{nama_en}-{recipe_id}")
        bahan_en_list = [item.get('original') for item in detail.get('extendedIngredients', []) if item.get('original')]
        langkah_en_list = []
        instructions = detail.get('analyzedInstructions', [])
        if instructions:
            steps_list = instructions[0].get('steps', [])
            langkah_en_list = [step_item.get('step') for step_item in steps_list if step_item.get('step')]
        else:
            langkah_en_list = ["Langkah detail tidak tersedia, silakan cek URL sumber."]

        # --- Solusi Cepat: Hanya terjemahkan Judul dan Bahan ---
        num_bahan = len(bahan_en_list)
        all_texts_to_translate = [nama_en] + bahan_en_list
        
        print(f"Menerjemahkan {len(all_texts_to_translate)} teks (Judul+Bahan) via DeepL...")
        
        results = translator.translate_text(
            all_texts_to_translate, 
            source_lang="EN", 
            target_lang="ID"
        )
        
        translated_texts = [r.text for r in results]
        print("Selesai menerjemahkan batch DeepL.")

        if not translated_texts: raise Exception("Terjemahan batch DeepL gagal.")

        # 4. Pisahkan kembali
        nama_id = translated_texts[0]
        bahan_id_list = translated_texts[1 : 1 + num_bahan]
        langkah_id_list = langkah_en_list # Kita tetap pakai langkah dalam Bahasa Inggris
        
        # 5. Kembalikan data
        return {"nama": nama_id, "url": url_en, "bahan": bahan_id_list, "langkah": langkah_id_list}
        
    except Exception as e:
        print(f"Error di get_recipe_detail_api (DeepL): {e}")
        return None