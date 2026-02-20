import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

st.title("🕵️ Debugger Gazzetta U17")

url = st.text_input("Inserisci l'URL esatto:")

if st.button("Analizza Pagina"):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    }
    
    with st.spinner("Sto cercando di leggere il sito..."):
        res = requests.get(url, headers=headers)
        
        if res.status_code != 200:
            st.error(f"Il sito ha risposto con errore {res.status_code}")
        else:
            st.success("Connessione riuscita!")
            
            # TEST 1: Vediamo se ci sono tabelle standard
            tabelle = pd.read_html(res.text)
            if len(tabelle) > 0:
                st.write(f"Trovate {len(tabelle)} tabelle!")
                st.dataframe(tabelle[0])
            else:
                st.warning("Nessuna tabella <table> trovata nel codice HTML.")
                
                # TEST 2: Stampiamo un pezzetto di codice per capire cosa vede l'AI
                st.code(res.text[:1000], language="html")
