# File: utils.py
import streamlit as st
import requests
from deep_translator import GoogleTranslator

# --- Konfigurasi API Spoonacular ---
API_KEY = st.secrets.get("SPOONACULAR_API_KEY", "KUNCI_BELUM_DIATUR")
SPOONACULAR_URL_SEARCH = "https://api.spoonacular.com/recipes/findByIngredients"
SPOONACULAR_URL_DETAIL_TEMPLATE = "https://api.spoonacular.com/recipes/{id}/information"

# --- Inisialisasi Penerjemah ---
# Kita buat di sini agar hanya diinisialisasi sekali
translator_to_en = GoogleTranslator(source='id', target='en')
translator_to_id = GoogleTranslator(source='en', target='id')

# --- Fungsi CSS Kustom ---
def load_custom_css():
    """Memuat CSS untuk kotak metrik & menyembunyikan spinner cache."""
    st.markdown("""
    <style>
    /* CSS untuk menyembunyikan spinner "Running..." */
    [data-testid="stSpinner"] {
        display: none;
    }

    /* CSS untuk kotak metrik kustom */
    .metric-box {
        background-color: #333; /* Warna dasar kotak */
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        color: white;
    }
    .metric-box h3 {
        font-size: 16px;
        color: #CCC; /* Warna label (abu-abu muda) */
        margin-bottom: 5px;
    }
    .metric-box p {
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .metric-box span {
        font-size: 14px;
        color: #AAA;
    }

    /* Warna-warna spesifik */
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
    """Menerjemahkan input pengguna dari ID ke EN."""
    print(f"CACHE MISS: Menerjemahkan KE EN '{teks_indonesia}'")
    try:
        return translator_to_en.translate(teks_indonesia)
    except Exception as e:
        st.error(f"Error saat menerjemahkan (ID-EN): {e}")
        return None

@st.cache_data(ttl=3600)
def search_recipes_api(ingredients_query):
    """Memanggil API Spoonacular findByIngredients."""
    if API_KEY == "KUNCI_BELUM_DIATUR":
        st.error("API Key Spoonacular belum diatur di .streamlit/secrets.toml")
        return []
    print(f"CACHE MISS: Memanggil API pencarian untuk '{ingredients_query}'")
    params = {
        "ingredients": ingredients_query, "number": 5,
        "apiKey": API_KEY, "ranking": 1
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
    """Memanggil API Spoonacular dan menerjemahkan hasil (Metode Batch)."""
    if API_KEY == "KUNCI_BELUM_DIATUR": return None
    print(f"CACHE MISS: Memanggil API detail untuk ID '{recipe_id}'")
    detail_url = SPOONACULAR_URL_DETAIL_TEMPLATE.format(id=recipe_id)
    params = { "apiKey": API_KEY, "includeNutrition": False }
    try:
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
        
        num_bahan = len(bahan_en_list)
        all_texts_to_translate = [nama_en] + bahan_en_list + langkah_en_list
        
        print(f"Menerjemahkan {len(all_texts_to_translate)} teks secara batch...")
        translated_texts = translator_to_id.translate_batch(all_texts_to_translate)
        print("Selesai menerjemahkan batch.")

        if not translated_texts: raise Exception("Terjemahan batch gagal.")
        
        nama_id = translated_texts[0]
        bahan_id_list = translated_texts[1 : 1 + num_bahan]
        langkah_id_list = translated_texts[1 + num_bahan :]
        
        return {"nama": nama_id, "url": url_en, "bahan": bahan_id_list, "langkah": langkah_id_list}
    except Exception as e:
        print(f"Error di get_recipe_detail_api: {e}")
        return None