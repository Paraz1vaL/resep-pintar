# File: utils.py
import streamlit as st
import requests
import deepl  # <-- PERUBAHAN: Import library baru
import time # (Kita masih pakai time, tapi untuk hal lain)

# --- Konfigurasi API ---
# Ambil kedua API key dari secrets
SPOONACULAR_API_KEY = st.secrets.get("SPOONACULAR_API_KEY")
DEEPL_API_KEY = st.secrets.get("DEEPL_API_KEY") # <-- PERUBAHAN: Ambil key DeepL

# URL Spoonacular (tetap sama)
SPOONACULAR_URL_SEARCH = "https://api.spoonacular.com/recipes/findByIngredients"
SPOONACULAR_URL_DETAIL_TEMPLATE = "https://api.spoonacular.com/recipes/{id}/information"

# --- Inisialisasi Penerjemah ---
# <-- PERUBAHAN BESAR DI BLOK INI -->
translator = None
if DEEPL_API_KEY:
    try:
        # Inisialisasi translator resmi DeepL
        translator = deepl.Translator(DEEPL_API_KEY)
    except Exception as e:
        st.error(f"Gagal menginisialisasi DeepL Translator: {e}")
else:
    # Tampilkan error jika key tidak ada di secrets.toml
    st.error("API Key DeepL tidak ditemukan. Harap tambahkan DEEPL_API_KEY ke .streamlit/secrets.toml")

# --- Fungsi CSS Kustom (Tidak berubah) ---
def load_custom_css():
    st.markdown("""
    <style>
    [data-testid="stSpinner"] { display: none; }
    .metric-box { ... } /* (Saya singkat, tapi kode CSS Anda tetap ada di sini) */
    /* ... (sisa kode CSS Anda) ... */
    </style>
    """, unsafe_allow_html=True)

# --- Fungsi Backend (Cache) ---

@st.cache_data(ttl=3600)
def terjemahkan_ke_inggris(teks_indonesia):
    """Menerjemahkan input pengguna dari ID ke EN menggunakan DeepL."""
    if not translator:
        return None # Gagal jika translator tidak siap
        
    print(f"CACHE MISS (DeepL): Menerjemahkan KE EN '{teks_indonesia}'")
    try:
        # <-- PERUBAHAN: Cara memanggil DeepL -->
        # "EN-US" lebih spesifik daripada "EN"
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

        # --- PERUBAHAN KUNCI: METODE BATCH DEEPL ---
        # (Kita tetap pada solusi terakhir: hanya terjemahkan Judul dan Bahan)
        num_bahan = len(bahan_en_list)
        all_texts_to_translate = [nama_en] + bahan_en_list
        
        print(f"Menerjemahkan {len(all_texts_to_translate)} teks (Judul+Bahan) via DeepL...")
        
        # DeepL secara otomatis menangani list sebagai batch
        results = translator.translate_text(
            all_texts_to_translate, 
            source_lang="EN", 
            target_lang="ID"
        )
        
        # Ambil teks dari hasil (DeepL mengembalikan objek)
        translated_texts = [r.text for r in results]
        
        print("Selesai menerjemahkan batch DeepL.")

        if not translated_texts: raise Exception("Terjemahan batch DeepL gagal.")

        # 4. Pisahkan kembali
        nama_id = translated_texts[0]
        bahan_id_list = translated_texts[1 : 1 + num_bahan]
        # Kita tetap pakai langkah dalam Bahasa Inggris (solusi kecepatan)
        langkah_id_list = langkah_en_list
        
        # 5. Kembalikan data
        return {"nama": nama_id, "url": url_en, "bahan": bahan_id_list, "langkah": langkah_id_list}
        
    except Exception as e:
        print(f"Error di get_recipe_detail_api (DeepL): {e}")
        return None