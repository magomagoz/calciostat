import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Scout U17 Roma", layout="wide")

st.title("⚽ Database Under 17 - Lazio 2024/25")

# Menu a tendina per evitare errori di battitura degli URL
gironi = {
    "Girone A": "https://www.gazzettaregionale.it/risultati-classifiche/2024-2025/under-17-elite-lazio/girone-a",
    "Girone B": "https://www.gazzettaregionale.it/risultati-classifiche/2024-2025/under-17-elite-lazio/girone-b",
    "Girone C": "https://www.gazzettaregionale.it/risultati-classifiche/2024-2025/under-17-elite-lazio/girone-c"
}

scelta = st.selectbox("Seleziona il Girone da caricare:", list(gironi.keys()))
url_selezionato = gironi[scelta]

@st.cache_data(ttl=600)
def carica_dati(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15'
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return f"Errore {response.status_code}: Controlla se l'URL è ancora attivo."
        
        # Cerchiamo le tabelle nella pagina
        tabelle = pd.read_html(response.text)
        if not tabelle:
            return "Nessuna tabella trovata. Il sito potrebbe aver cambiato formato."
        
        # La classifica di solito è la tabella più grande
        df = max(tabelle, key=len)
        return df
    except Exception as e:
        return f"Errore tecnico: {str(e)}"

if st.button("🔄 Carica / Aggiorna Classifica"):
    st.cache_data.clear()
    risultato = carica_dati(url_selezionato)
    
    if isinstance(risultato, pd.DataFrame):
        st.session_state['data'] = risultato
        st.success(f"Dati del {scelta} caricati correttamente!")
    else:
        st.error(risultato)

# Visualizzazione dei dati se presenti
if 'data' in st.session_state:
    df = st.session_state['data']
    
    # Mostra la tabella
    st.subheader(f"Classifica Attuale - {scelta}")
    st.dataframe(df, use_container_width=True)
    
    # Export per il tuo lavoro di scouting
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("💾 Esporta Classifica (CSV)", csv, f"classifica_{scelta}.csv", "text/csv")
