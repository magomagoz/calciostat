import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Scout U17 Roma", layout="wide")
st.title("⚽ Database Under 17 - Lazio")

# URL di esempio reale per il Girone A (testato e funzionante)
default_url = "https://www.gazzettaregionale.it/risultati-classifiche/under-17-elite/girone-a"

url = st.text_input("Inserisci l'URL della Gazzetta Regionale:", value=default_url)

if st.button("🔄 Aggiorna Dati Manualmente"):
    if not url or not url.startswith("http"):
        st.error("Per favore, inserisci un URL valido che inizi con http o https")
    else:
        st.cache_data.clear()
        st.info("Download in corso...")

@st.cache_data(ttl=3600)
def scarica_classifica(target_url):
    headers = {'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15'}
    try:
        response = requests.get(target_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Il sito usa tabelle classiche. Pandas è perfetto qui.
        tabelle = pd.read_html(response.text)
        
        # Di solito la classifica è la prima tabella (indice 0)
        # o quella con più righe
        if tabelle:
            df = max(tabelle, key=len) 
            return df
        return None
    except Exception as e:
        return f"Errore: {e}"

if url:
    risultato = scarica_classifica(url)
    
    if isinstance(risultato, pd.DataFrame):
        st.success("Dati caricati con successo!")
        # Pulizia base: rinominiamo le colonne se necessario
        st.dataframe(risultato, use_container_width=True)
        
        # Export per il tuo lavoro su iPad
        csv = risultato.to_csv(index=False).encode('utf-8')
        st.download_button("💾 Salva su iPad (CSV)", csv, "classifica_u17.csv", "text/csv")
    else:
        st.error(risultato)
