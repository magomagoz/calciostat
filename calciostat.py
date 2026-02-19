import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="U17 Roma Scout", layout="wide")

st.title("⚽ Scouting Under 17 - Roma")

# Funzione di scraping (cacheata per non sovraccaricare il sito)
@st.cache_data(ttl=3600)
def fetch_data(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    
    # QUI inseriremo la logica specifica per i selettori CSS della Gazzetta
    # Per ora simuliamo un dataframe
    return pd.DataFrame({
        'Squadra': ['Trastevere', 'Vigor Perconti', 'Urbetevere'],
        'Punti': [42, 40, 38],
        'Forma': ['V-V-S', 'V-P-V', 'V-V-V']
    })

url_target = "https://www.gazzettaregionale.it/under-17-elite/girone-a"

if st.button('Aggiorna Dati'):
    data = fetch_data(url_target)
    st.table(data)

# Sidebar per filtri
st.sidebar.header("Filtri")
girone = st.sidebar.selectbox("Seleziona Girone", ["Elite A", "Elite B", "Regionali"])

