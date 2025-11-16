# File: page_cari_resep.py
import streamlit as st
from utils import (
    terjemahkan_ke_inggris, 
    search_recipes_api, 
    get_recipe_detail_api
)

def show_page():
    st.title("Pencarian Resep")
    st.markdown("Masukkan bahan-bahan yang Anda miliki (pisahkan dengan koma), dan kami akan carikan resep yang cocok!")
    
    search_query = st.text_input(
        "Masukkan bahan-bahan Anda:",
        placeholder="Contoh: daging sapi, bawang putih, kecap",
        label_visibility="collapsed"
    )

    if st.button("Cari Resep Sekarang"):
        if not search_query:
            st.warning("Mohon masukkan nama bahan terlebih dahulu.")
        else:
            # Progress UI
            progress = st.progress(0)
            status_text = st.empty()

            # Step 1: Terjemahkan
            status_text.text("Menerjemahkan bahan...")
            progress.progress(10)

            translated_query = terjemahkan_ke_inggris(search_query)
            if translated_query is None:
                st.error("Proses terjemahan gagal. Coba lagi.")
                st.stop()

            # Step 2: Cari resep
            status_text.text("Mencari resep berdasarkan bahan...")
            progress.progress(35)

            recipe_ids = search_recipes_api(translated_query)
            if not recipe_ids:
                st.info(f"Tidak ada hasil untuk '{search_query}'. Coba bahan lain.")
                st.stop()

            # Step 3: Ambil detail resep
            status_text.text("Mengambil detail resep...")
            all_recipes_data = []
            total_ids = len(recipe_ids)

            for index, recipe_id in enumerate(recipe_ids):
                detail_data = get_recipe_detail_api(recipe_id)
                if detail_data:
                    all_recipes_data.append(detail_data)

                # update progress per item
                current_progress = 35 + int((index + 1) / total_ids * 55)
                progress.progress(current_progress)

            if not all_recipes_data:
                st.error("Gagal mengambil detail resep.")
                st.stop()

            # Step 4: Tampilkan hasil
            status_text.text("Menyelesaikan proses...")
            progress.progress(100)

            st.success(f"Ditemukan {len(all_recipes_data)} resep teratas!")
            status_text.empty()  # Hapus status teks

            for resep in all_recipes_data:
                with st.expander(f"**{resep['nama']}**"):
                    st.subheader("Bahan-bahan:")
                    for bahan in resep['bahan']:
                        st.markdown(f"- {bahan}")

                    st.subheader("Langkah-langkah:")
                    for i, langkah in enumerate(resep['langkah'], 1):
                        st.markdown(f"{i}. {langkah}")

                    st.markdown(f"\n[Lihat resep asli]({resep['url']})", unsafe_allow_html=True)
