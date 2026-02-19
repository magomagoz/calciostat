import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Scout U17 Roma", page_icon="⚽")

st.title("⚽ Database Under 17 - Lazio")

# --- NUOVA LOGICA DI SCRAPING ---
@st.cache_data(ttl=3600)
def get_data_gazzetta(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1'
    }
    try:
        response = requests.get(url, headers=headers)
        
        # Se il sito restituisce 404, avvisiamo l'utente in modo chiaro
        if response.status_code == 404:
            st.warning("⚠️ URL non trovato (404). Verifica che il link sia corretto direttamente sul sito della Gazzetta.")
            return None
            
        response.raise_for_status()
        
        # Molte pagine della Gazzetta non usano tabelle HTML standard <table> 
        # ma strutture <div>. Se pd.read_html fallisce, usiamo BeautifulSoup.
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Proviamo a cercare tabelle
        tabelle = pd.read_html(response.text)
        if tabelle:
            return tabelle[0]
        else:
            st.info("Nessuna tabella standard trovata. Il sito potrebbe usare un formato diverso.")
            return None

    except Exception as e:
        st.error(f"Errore tecnico: {e}")
        return None

# --- UI ---
# Suggerimento: prova a copiare l'URL esatto navigando sul sito dalla barra del browser
url_input = st.text_input("Incolla l'URL della classifica dal sito Gazzetta Regionale:", 
                         placeholder="https://www.gazzettaregionale.it/...")

if st.button("🔄 Aggiorna Dati"):
    st.cache_data.clear()

if url_input:
    df = get_data_gazzetta(url_input)
    if df is not None:
        st.dataframe(df, use_container_width=True)
