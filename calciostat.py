import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Scout U17 Roma", layout="wide")
st.title("⚽ Database Under 17 - Lazio 2024/25")

# 1. Setup degli URL (Aggiornati dinamicamente per la stagione corrente)
# Nota: La Gazzetta usa spesso sottodomini o path stagionali
URL_BASE = "https://www.gazzettaregionale.it/risultati-classifiche"

st.sidebar.header("Configurazione")
categoria = st.sidebar.selectbox("Categoria", ["under-17-elite-lazio", "under-17-regionali-lazio"])
girone = st.sidebar.selectbox("Girone", ["girone-a", "girone-b", "girone-c"])

# Costruzione dinamica dell'URL
url_finale = f"{URL_BASE}/{categoria}/{girone}"

@st.cache_data(ttl=3600)
def fetch_data_robust(target_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
        'Referer': 'https://www.gazzettaregionale.it/'
    }
    
    try:
        # Tentativo 1: URL Diretto
        res = requests.get(target_url, headers=headers, timeout=15)
        
        # Se 404, proviamo l'URL senza l'anno (alcuni gironi sono strutturati diversamente)
        if res.status_code == 404:
            alt_url = target_url.replace("/2024-2025", "")
            res = requests.get(alt_url, headers=headers, timeout=15)

        res.raise_for_status()
        
        # Analizziamo l'HTML con BeautifulSoup per trovare la tabella "vera"
        soup = BeautifulSoup(res.text, 'html.parser')
        tabelle_html = soup.find_all('table')
        
        if not tabelle_html:
            return "Nessuna tabella trovata. Il sito potrebbe usare un caricamento asincrono."

        # Convertiamo la tabella più probabile in DataFrame
        # Cerchiamo quella che contiene la parola "Squadra" o "Punti"
        for t in tabelle_html:
            df = pd.read_html(str(t))[0]
            if len(df.columns) > 2: # Una classifica ha almeno 3 colonne
                return df
                
        return "Tabella trovata ma non valida per la classifica."

    except Exception as e:
        return f"Errore di connessione: {str(e)}"

# --- INTERFACCIA ---
st.info(f"🔍 Ricerca in corso su: {url_finale}")

if st.button("🚀 Scarica Dati Ora"):
    st.cache_data.clear()
    risultato = fetch_data_robust(url_finale)
    
    if isinstance(risultato, pd.DataFrame):
        st.session_state['classifica'] = risultato
        st.success("Dati estratti con successo!")
    else:
        st.error(risultato)
        st.warning("Consiglio: Apri il sito Gazzetta su Safari, naviga nel girone e controlla se l'URL è diverso da quello mostrato sopra.")

if 'classifica' in st.session_state:
    df = st.session_state['classifica']
    st.dataframe(df, use_container_width=True)
    
    # Pulizia al volo dei nomi squadre (Rimuove spazi extra e caratteri sporchi)
    if 'Squadra' in df.columns:
        df['Squadra'] = df['Squadra'].str.strip()
    
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Esporta per Scouting (CSV)", csv, "u17_data.csv", "text/csv")
