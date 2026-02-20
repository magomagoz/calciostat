import streamlit as st
import pandas as pd
import requests

st.title("⚽ Scout Real Tuscolano - Tuttocampo")

# URL della scheda squadra su Tuttocampo
url_tuscolano = "https://www.tuttocampo.it/Lazio/AllieviProvincialiU17/GironeBProvincialiRoma/Squadra/AccademiaRTuscolanoC/1145427/Scheda"

@st.cache_data(ttl=3600)
def get_tuttocampo_data(url):
    # Headers molto importanti per non essere bloccati da Tuttocampo
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
        'Accept-Language': 'it-IT,it;q=0.9',
        'Referer': 'https://www.tuttocampo.it/'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Cerchiamo le tabelle (Classifica, Risultati, Rosa)
        tabelle = pd.read_html(response.text)
        return tabelle
    except Exception as e:
        return f"Errore: {e}"

if st.button("🔄 Scarica Dati Accademia Real Tuscolano"):
    risultati = get_tuttocampo_data(url_tuscolano)
    
    if isinstance(risultati, list):
        st.success("Dati scaricati!")
        
        # Su Tuttocampo ci sono molte tabelle nella scheda squadra:
        # Tabelle tipiche: 0=Rosa, 1=Classifica, 2=Ultimi Risultati
        for i, tab in enumerate(risultati):
            st.write(f"Tabella {i}")
            st.dataframe(tab, use_container_width=True)
            
            # Bottone per scaricare la singola tabella
            csv = tab.to_csv(index=False).encode('utf-8')
            st.download_button(f"📥 Scarica Tabella {i}", csv, f"tuscolano_tab_{i}.csv", "text/csv")
    else:
        st.error(risultati)
