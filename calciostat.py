import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

# Configurazione Pagina
st.set_page_config(page_title="Scout U17 Roma", page_icon="⚽")

st.title("⚽ Database Under 17 - Lazio")
st.markdown("Dati estratti da *Gazzetta Regionale*")

# --- FUNZIONE CORE DI SCRAPING ---
@st.cache_data(ttl=3600) # La cache scade dopo un'ora o al refresh manuale
def get_data_gazzetta(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status() # Controlla se il sito risponde (200 OK)
        
        # Uso pandas per leggere le tabelle HTML direttamente
        # Di solito le classifiche sono in tag <table>
        tabelle = pd.read_html(response.text)
        
        # Restituiamo la tabella principale (spesso la prima o la seconda)
        df = tabelle[0] 
        return df
    except Exception as e:
        st.error(f"Errore durante il caricamento: {e}")
        return None

# --- INTERFACCIA UTENTE ---

url_input = st.text_input("Inserisci l'URL della categoria (es. Under 17 Elite Girone A):", 
                         "https://www.gazzettaregionale.it/risultati-classifiche/under-17-elite/girone-a")

col1, col2 = st.columns([1, 4])

with col1:
    # Il pulsante che svuota la cache e forza il ricaricamento
    if st.button("🔄 Aggiorna Dati"):
        st.cache_data.clear()
        st.success("Cache pulita! Caricamento in corso...")

# Esecuzione dello scraping
df_risultati = get_data_gazzetta(url_input)

if df_risultati is not None:
    st.subheader("Classifica / Risultati Correnti")
    
    # Mostra i dati in una tabella interattiva di Streamlit
    st.dataframe(df_risultati, use_container_width=True)
    
    # Download dei dati in CSV (comodissimo da iPad per Excel/Numbers)
    csv = df_risultati.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Scarica CSV per Excel", csv, "dati_u17.csv", "text/csv")
