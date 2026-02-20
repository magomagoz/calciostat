import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

st.set_page_config(page_title="Scout U17 Roma", layout="wide")
st.title("⚽ Database Under 17 - Lazio 2026")

# L'unica certezza è la Home dei risultati
URL_START = "https://www.gazzettaregionale.it/risultati-classifiche"

@st.cache_data(ttl=600)
def find_and_scrape(base_url, target_keywords):
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15',
        'Referer': 'https://www.gazzettaregionale.it/'
    }
    
    try:
        # 1. Carichiamo la pagina principale per trovare l'URL vero
        response = requests.get(base_url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Cerchiamo tutti i link che contengono le nostre parole chiave
        links = soup.find_all('a', href=True)
        found_url = None
        
        for link in links:
            href = link['href']
            # Cerchiamo un link che contenga "under-17" e "girone-c"
            if all(k in href.lower() for k in target_keywords):
                found_url = href if href.startswith('http') else f"https://www.gazzettaregionale.it{href}"
                break
        
        if not found_url:
            return "❌ Non riesco a trovare il link automatico. Il sito potrebbe essere protetto o cambiato."

        st.info(f"🔗 Link trovato: {found_url}")
        
        # 2. Proviamo a leggere la tabella dal link trovato
        res_final = requests.get(found_url, headers=headers)
        tabelle = pd.read_html(res_final.text)
        
        if tabelle:
            return max(tabelle, key=len)
        return "⚠️ Pagina trovata ma nessuna tabella dati rilevata."

    except Exception as e:
        return f"💥 Errore: {str(e)}"

# --- UI ---
keywords = st.text_input("Parole chiave ricerca (es: under 17 elite girone c)", "under-17-elite girone-c")

if st.button("🔍 Avvia Ricerca e Scarica"):
    st.cache_data.clear()
    word_list = keywords.lower().split()
    risultato = find_and_scrape(URL_START, word_list)
    
    if isinstance(risultato, pd.DataFrame):
        st.success("Dati estratti!")
        st.dataframe(risultato, use_container_width=True)
        st.download_button("📥 Scarica CSV", risultato.to_csv(index=False).encode('utf-8'), "scout.csv")
    else:
        st.error(risultato)
