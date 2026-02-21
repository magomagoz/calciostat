import streamlit as st
import pandas as pd
from datetime import date
import os

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Scouting & Fatigue System", layout="wide")

try:
    import plotly.express as px
except ImportError:
    st.error("Aggiungi 'plotly' al file requirements.txt")

# --- COSTANTI FILE ---
DB_PLAYERS = "database_scouting.csv"
DB_FATICA = "log_fatica.csv"

# --- FUNZIONI DI PERSISTENZA ---
def carica_giocatori():
    if os.path.exists(DB_PLAYERS):
        df = pd.read_csv(DB_PLAYERS)
        if 'Data di nascita' in df.columns:
            df['Data di nascita'] = pd.to_datetime(df['Data di nascita']).dt.date
        return df
    return pd.DataFrame(columns=["Squadra", "Cognome", "Nome", "Ruolo", "Data di nascita", "Presenze", "Minutaggio", "Gol", "Gialli", "Rossi", "Rating", "Note"])

def carica_fatica():
    if os.path.exists(DB_FATICA):
        df = pd.read_csv(DB_FATICA)
        df['Data'] = pd.to_datetime(df['Data']).dt.date
        return df
    return pd.DataFrame(columns=["ID_Giocatore", "Cognome", "Data", "Fatica", "Note"])

def salva_giocatori(df):
    df.to_csv(DB_PLAYERS, index=False)

def salva_fatica(df):
    df.to_csv(DB_FATICA, index=False)

# --- INIZIALIZZAZIONE SESSION STATE ---
if 'players_db' not in st.session_state:
    st.session_state['players_db'] = carica_giocatori()
if 'fatica_db' not in st.session_state:
    st.session_state['fatica_db'] = carica_fatica()
if 'view' not in st.session_state:
    st.session_state['view'] = 'dashboard'
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# --- LOGIN ---
if not st.session_state['logged_in']:
    st.title("🔐 Login Scouting")
    u = st.text_input("User")
    p = st.text_input("Pass", type="password")
    if st.button("Entra"):
        if u == "Marco" and p == "Scout2026":
            st.session_state['logged_in'] = True
            st.rerun()
    st.stop()

# --- SCHERMATA INIZIALE CARICAMENTO (DOPO LOGIN) ---
if st.session_state['players_db'].empty and not st.session_state.get('setup_done'):
    st.title("🚀 Configurazione Iniziale")
    st.info("Benvenuto! Carica i file CSV per riprendere il lavoro o clicca 'Inizia' per un nuovo DB.")
    
    col_a, col_b = st.columns(2)
    with col_a:
        up_p = st.file_uploader("Carica Lista Giocatori (CSV)", type="csv")
        if up_p:
            st.session_state['players_db'] = pd.read_csv(up_p)
            salva_giocatori(st.session_state['players_db'])
            st.success("Giocatori caricati!")
            
    with col_b:
        up_f = st.file_uploader("Carica Storico Fatica (CSV)", type="csv")
        if up_f:
            st.session_state['fatica_db'] = pd.read_csv(up_f)
            salva_fatica(st.session_state['fatica_db'])
            st.success("Storico fatica caricato!")

    if st.button("Vai alla Dashboard / Inizia da zero", use_container_width=True):
        st.session_state['setup_done'] = True
        st.rerun()
    st.stop()

# --- NAVBAR ---
c1, c2, c3, c4 = st.columns(4)
with c1:
    if st.button("🏆 Campionato", use_container_width=True): st.session_state['view'] = 'campionato'; st.rerun()
with c2:
    if st.button("➕ Aggiungi", use_container_width=True): st.session_state['view'] = 'aggiungi'; st.rerun()
with c3:
    if st.button("📋 Elenco/Fatica", use_container_width=True): st.session_state['view'] = 'dashboard'; st.rerun()
with c4:
    if st.button("📊 Statistiche", use_container_width=True): st.session_state['view'] = 'stats'; st.rerun()

st.divider()

# --- LOGICA DASHBOARD ---
if st.session_state['view'] == 'dashboard':
    st.subheader("📋 Gestione Database")
    
    # 1. VISUALIZZAZIONE TABELLA GIOCATORI
    if not st.session_state['players_db'].empty:
        st.write("### Lista Giocatori")
        st.dataframe(st.session_state['players_db'], use_container_width=True, hide_index=True)
        
        # 2. REGISTRAZIONE FATICA (FILE SEPARATO)
        st.divider()
        st.subheader("🏃 Registrazione Fatica")
        with st.expander("Apri modulo inserimento fatica"):
            df_p = st.session_state['players_db']
            nomi = df_p.apply(lambda x: f"{x['Cognome']} {x['Nome']}", axis=1).tolist()
            scelta = st.selectbox("Calciatore", nomi)
            data_f = st.date_input("Data", value=date.today())
            fatica_v = st.slider("Livello Fatica", 0, 100, 50)
            nota_f = st.text_input("Note (es: Assente)")
            
            if st.button("💾 REGISTRA FATICA (Salva su file Fatica)"):
                nuova_riga = pd.DataFrame({
                    "ID_Giocatore": [nomi.index(scelta)],
                    "Cognome": [scelta.split()[0]],
                    "Data": [data_f],
                    "Fatica": [fatica_v],
                    "Note": [nota_f]
                })
                st.session_state['fatica_db'] = pd.concat([st.session_state['fatica_db'], nuova_riga], ignore_index=True)
                salva_fatica(st.session_state['fatica_db'])
                st.success(f"Fatica registrata per {scelta} nel file separato!")
        
        # 3. PULSANTI EXPORT SEPARATI (A FIANCO)
        st.divider()
        st.subheader("📥 Esportazione File")
        col_ex1, col_ex2 = st.columns(2)
        
        with col_ex1:
            csv_p = st.session_state['players_db'].to_csv(index=False).encode('utf-8')
            st.download_button("📥 Scarica Lista Giocatori", csv_p, "giocatori.csv", "text/csv", use_container_width=True)
            
        with col_ex2:
            csv_f = st.session_state['fatica_db'].to_csv(index=False).encode('utf-8')
            st.download_button("📥 Scarica Storico Fatica", csv_f, "storico_fatica.csv", "text/csv", use_container_width=True)

    else:
        st.info("Database vuoto.")

# --- STATISTICHE ---
elif st.session_state['view'] == 'stats':
    st.subheader("📊 Analisi Dati")
    if not st.session_state['fatica_db'].empty:
        st.write("### Andamento Fatica nel Tempo")
        fig = px.line(st.session_state['fatica_db'], x="Data", y="Fatica", color="Cognome", markers=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Nessun dato di fatica registrato.")
