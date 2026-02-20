import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Scout U17 Roma", layout="wide")
st.title("⚽ Database Under 17 - Lazio (API Mode)")

# L'URL che hai trovato tu è la chiave del tesoro!
default_api_url = "https://v2.apiweb.gazzettaregionale.it/classifiche"

url = st.text_input("Sorgente Dati API:", value=default_api_url).strip()

@st.cache_data(ttl=600)
def scarica_dati_api(api_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15',
        'Accept': 'application/json' # Chiediamo esplicitamente dati JSON
    }
    
    try:
        response = requests.get(api_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Trasformiamo il JSON in un dizionario Python
        data = response.json()
        
        # I dati delle API solitamente sono annidati. 
        # Proviamo a estrarre la lista principale (potrebbe servire un aggiustamento 
        # in base alla struttura esatta che vedi nei log)
        if 'data' in data:
            df = pd.DataFrame(data['data'])
        elif isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            df = pd.DataFrame(data)
            
        return df
        
    except Exception as e:
        return f"💥 Errore API: {str(e)}"

if st.button("🔄 Forza Aggiornamento API"):
    st.cache_data.clear()
    st.rerun()

if url:
    with st.spinner("Interrogando il server della Gazzetta..."):
        risultato = scarica_dati_api(url)
    
    if isinstance(risultato, pd.DataFrame):
        st.success("Dati estratti direttamente dal database!")
        
        # Mostra le prime righe per capire quali colonne ci servono
        st.dataframe(risultato, use_container_width=True)
        
        csv = risultato.to_csv(index=False).encode('utf-8')
        st.download_button("💾 Scarica JSON/CSV su iPad", csv, "api_data.csv", "text/csv")
    else:
        st.error(risultato)
