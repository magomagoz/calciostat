import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import io

st.set_page_config(page_title="Scout Pro Lazio", layout="wide")
st.title("⚽ Database Under 17 - Lazio 2026")

# --- SEZIONE 1: DOWNLOAD AUTOMATICO ---
st.header("🌐 Scarica da Web")
url_target = st.text_input("Inserisci URL (Tuttocampo, IamCalcio, ecc.):", 
                          "https://roma.iamcalcio.it/social/squadre/7686/accademia-real-tuscolano/rosa.html")

if st.button("🚀 Tenta Download Automatico"):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.google.com/'
    }
    try:
        response = requests.get(url_target, headers=headers, timeout=15)
        tabelle = pd.read_html(response.text)
        if tabelle:
            df_web = max(tabelle, key=len)
            st.success("Dati scaricati con successo!")
            st.dataframe(df_web)
            st.download_button("📥 Salva CSV", df_web.to_csv(index=False).encode('utf-8'), "web_data.csv")
    except Exception as e:
        st.error(f"Il sito ha bloccato il download automatico. Usa il metodo 'Incolla' sotto. (Errore: {e})")

st.divider()

# --- SEZIONE 2: INCOLLO MANUALE INTELLIGENTE ---
st.header("📝 Metodo Incolla (Anti-Errore)")
st.info("Copia la tabella dal sito e incollala qui. Questo sistema corregge gli errori delle immagini precedenti.")

raw_text = st.text_area("Incolla qui i dati:", height=250)

if st.button("🛠️ Elabora e Pulisci Dati"):
    if raw_text:
        try:
            # Soluzione all'errore dell'immagine 13: 
            # leggiamo riga per riga e separiamo dove ci sono 2 o più spazi
            lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
            data = [line.split() for line in lines] # Divide per qualsiasi spazio
            
            # Creiamo il DataFrame adattando le lunghezze delle righe
            df_manual = pd.DataFrame(data)
            
            st.success("Dati elaborati!")
            st.dataframe(df_manual)
            
            csv_manual = df_manual.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Scarica Tabella Pulita", csv_manual, "scout_manuale.csv")
        except Exception as e:
            st.error(f"Errore: {e}")
