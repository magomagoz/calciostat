import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Scout U17 Roma", layout="wide")
st.title("⚽ Database Under 17 - Lazio 2024/25")

# Configurazione dei link corretti per la stagione attuale
GIRONI = {
    "Elite - Girone A": "https://www.gazzettaregionale.it/risultati-classifiche/2024-2025/under-17-elite-lazio/girone-a",
    "Elite - Girone B": "https://www.gazzettaregionale.it/risultati-classifiche/2024-2025/under-17-elite-lazio/girone-b",
    "Elite - Girone C": "https://www.gazzettaregionale.it/risultati-classifiche/2024-2025/under-17-elite-lazio/girone-c"
}

scelta = st.selectbox("Seleziona il Campionato:", list(GIRONI.keys()))
url_target = GIRONI[scelta]

@st.cache_data(ttl=3600)
def fetch_campionato(url):
    # Headers necessari per "ingannare" il server e farsi riconoscere come iPad
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Referer': 'https://www.gazzettaregionale.it/'
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Estrazione tabelle tramite Pandas
        tabelle = pd.read_html(response.text)
        if not tabelle:
            return None
            
        # La classifica è solitamente la tabella con più righe
        df = max(tabelle, key=len)
        return df
    except Exception as e:
        return f"Errore: {str(e)}"

if st.button("🔄 Scarica Classifica"):
    st.cache_data.clear()
    with st.spinner("Recupero dati in corso..."):
        risultato = fetch_campionato(url_target)
        
        if isinstance(risultato, pd.DataFrame):
            st.session_state['classifica'] = risultato
            st.success("Dati caricati correttamente!")
        else:
            st.error(risultato)

# Visualizzazione dei risultati
if 'classifica' in st.session_state:
    df = st.session_state['classifica']
    st.subheader(f"Classifica {scelta}")
    st.dataframe(df, use_container_width=True)
    
    # Pulsante di download per Excel
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Scarica per Excel", csv, f"{scelta}.csv", "text/csv")
