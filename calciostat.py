import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Scout U17 Roma", layout="wide")
st.title("⚽ Database Under 17 - Lazio")

# URL suggerito per la stagione attuale
url_suggerito = "https://www.gazzettaregionale.it/risultati-classifiche/2024-2025/under-17-elite-lazio/girone-a"

url = st.text_input("Incolla qui l'URL della Gazzetta Regionale:", value=url_suggerito).strip()

@st.cache_data(ttl=600)
def scarica_dati(target_url):
    if not target_url.startswith("http"):
        return "Errore: Inserisci un URL che inizi con https://"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15'
    }
    
    try:
        response = requests.get(target_url, headers=headers, timeout=15)
        if response.status_code == 404:
            return "❌ Errore 404: Questa pagina non esiste sul sito della Gazzetta. Verifica l'URL."
        
        response.raise_for_status()
        
        # Estrazione tabelle
        tabelle = pd.read_html(response.text)
        if not tabelle:
            return "⚠️ Nessuna tabella trovata nella pagina."
            
        # Prendiamo la tabella più grande (solitamente la classifica)
        df = max(tabelle, key=len)
        return df
        
    except Exception as e:
        return f"💥 Errore tecnico: {str(e)}"

if st.button("🔄 Aggiorna Dati"):
    st.cache_data.clear()
    st.rerun()

if url:
    risultato = scarica_dati(url)
    
    if isinstance(risultato, pd.DataFrame):
        st.success("Dati caricati!")
        # Mostriamo la tabella pulita
        st.dataframe(risultato, use_container_width=True)
        
        # Bottone per scaricare il file su iPad
        csv = risultato.to_csv(index=False).encode('utf-8')
        st.download_button("💾 Salva in Excel/CSV", csv, "classifica.csv", "text/csv")
    else:
        st.error(risultato)

st.info("💡 Consiglio: Vai sul sito Gazzetta Regionale dal browser, naviga fino alla classifica del Girone C e copia l'URL che vedi in alto. Poi incollalo qui.")
