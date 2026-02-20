import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Scout Pro Lazio", layout="wide")
st.title("⚽ Estrattore Dati Calcio Lazio 2026")

# Fonti predefinite per l'Accademia Real Tuscolano e Under 17
fonti = {
    "Rosa (IamCalcio)": "https://roma.iamcalcio.it/social/squadre/7686/accademia-real-tuscolano/rosa.html",
    "Classifica (Tuttocampo)": "https://www.tuttocampo.it/Lazio/AllieviProvincialiU17/GironeBProvincialiRoma/Squadra/AccademiaRTuscolanoC/1145427/Scheda",
    "Gazzetta Regionale": "https://www.gazzettaregionale.it/risultati-classifiche/under-17-elite-lazio/girone-c"
}

scelta = st.selectbox("Cosa vuoi provare a scaricare?", list(fonti.keys()))
url_input = st.text_input("URL Sorgente:", fonti[scelta])

@st.cache_data(ttl=600)
def download_web_data(url):
    # Headers avanzati per bypassare i blocchi
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://www.google.com/',
        'DNT': '1', # Do Not Track
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    try:
        session = requests.Session()
        # Primo passaggio sulla home per "scaldare" i cookie
        base_url = "/".join(url.split("/")[:3])
        session.get(base_url, headers=headers, timeout=10)
        
        # Secondo passaggio sull'URL vero
        response = session.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            return f"Errore {response.status_code}: Il sito ci ha bloccato."

        # Analisi HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Cerchiamo tutte le tabelle
        tabelle = pd.read_html(str(soup))
        
        if not tabelle:
            return "Nessuna tabella trovata nel codice HTML della pagina."
            
        return tabelle
    except Exception as e:
        return f"Errore tecnico: {str(e)}"

if st.button("🚀 Avvia Download"):
    risultato = download_web_data(url_input)
    
    if isinstance(risultato, list):
        st.success(f"Trovate {len(risultato)} tabelle!")
        for i, df in enumerate(risultato):
            with st.expander(f"Tabella {i} - Anteprima"):
                st.dataframe(df)
                st.download_button(f"📥 Scarica Tabella {i}", df.to_csv(index=False).encode('utf-8'), f"tab_{i}.csv")
    else:
        st.error(risultato)
