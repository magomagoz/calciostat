import streamlit as st
import pandas as pd
import io
import re

st.set_page_config(page_title="Scout Manual Mode", layout="wide")
st.title("⚽ Trasformatore Dati: Tuttocampo / Gazzetta")

st.info("💡 Questo metodo bypassa ogni blocco: Copia la tabella dal sito e incollala qui sotto.")

# Area di testo per l'inserimento manuale
raw_input = st.text_area("1. Incolla qui i dati copiati dal sito:", height=300, 
                        placeholder="Incolla qui la classifica o la rosa...")

def clean_scraped_data(text):
    # Rimuoviamo righe vuote e puliamo gli spazi
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # Tentativo di ricostruzione tabella: 
    # Spesso il copia-incolla da iPad mette ogni cella su una nuova riga
    # Se vediamo troppe righe singole, proviamo a raggrupparle
    data_rows = []
    current_row = []
    
    # Logica euristica: una riga di classifica solitamente ha 8-12 colonne
    # Proviamo a capire quante colonne ha la tabella incollata
    for line in lines:
        current_row.append(line)
        # Se la riga finisce con dei numeri (tipico dei punti/partite), 
        # potrebbe essere la fine di una riga di tabella
        if len(current_row) > 5 and re.search(r'\d+$', line):
            data_rows.append(current_row)
            current_row = []
    
    if not data_rows: # Se la logica sopra fallisce, carichiamo come testo semplice
        return pd.DataFrame(lines, columns=["Dati Estratti"])
        
    return pd.DataFrame(data_rows)

if st.button("🚀 Elabora Tabella"):
    if raw_input:
        df = clean_scraped_data(raw_input)
        st.success("Dati elaborati!")
        st.dataframe(df, use_container_width=True)
        
        # Download per Excel
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Scarica in Excel (CSV)", csv, "dati_scout.csv", "text/csv")
    else:
        st.warning("Incolla prima dei dati nel box!")

st.markdown("---")
st.markdown("### 📲 Come fare su iPad:")
st.markdown("""
1. Vai su **Tuttocampo** o **Gazzetta Regionale** con Safari.
2. Vai sulla pagina dell'**Accademia Real Tuscolano**.
3. Seleziona la tabella (classifica o rosa) tenendo premuto e trascinando.
4. Scegli **Copia**.
5. Torna qui, tocca nel box e scegli **Incolla**.
6. Premi il tasto **Elabora**.
""")
