import streamlit as st
import pandas as pd
from datetime import date

# Configurazione Pagina
st.set_page_config(page_title="Scouting Management", layout="wide")

# --- SISTEMA DI LOGIN ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.title("🔐 Accesso Scouting Management")
    user = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if user == "admin" and password == "scout2026": 
            st.session_state['logged_in'] = True
            st.rerun()
        else:
            st.error("Credenziali errate")
    st.stop()

# --- INIZIALIZZAZIONE DATABASE ---
if 'players_db' not in st.session_state:
    # Squadra inserita come prima colonna
    cols = ["Squadra", "Cognome", "Nome", "Ruolo", "Data di nascita", "Presenze", 
            "Minutaggio", "Gol fatti/subiti", "Fatica", "Cartellini Gialli", 
            "Cartellini Rossi", "Note"]
    st.session_state['players_db'] = pd.DataFrame(columns=cols)

# --- DASHBOARD PRINCIPALE ---
st.title("⚽ Scouting Management")

if 'view' not in st.session_state:
    st.session_state['view'] = 'dashboard'

# Mostriamo i pulsanti di navigazione
col1, col2 = st.columns(2)
with col1:
    if st.button("🏆 Scelta Campionato", use_container_width=True):
        st.session_state['view'] = 'campionato'
        st.rerun()
with col2:
    if st.button("➕ Aggiungi Giocatore", use_container_width=True):
        st.session_state['view'] = 'aggiungi'
        st.rerun()

st.divider()

# --- LOGICA DELLE PAGINE ---

# 1. SCHERMATA AGGIUNGI GIOCATORE
if st.session_state['view'] == 'aggiungi':
    st.subheader("➕ Inserisci Giocatore nel Database")
    if st.button("⬅️ Annulla e torna alla Home"):
        st.session_state['view'] = 'dashboard'
        st.rerun()
        
    with st.form("new_player", clear_on_submit=True):
        # Prima riga: Squadra e Dati Anagrafici
        c1, c2, c3 = st.columns([2, 2, 2])
        squadra = c1.text_input("Squadra") # Campo libero richiesto
        cognome = c2.text_input("Cognome")
        nome = c3.text_input("Nome")
        
        # Seconda riga: Ruolo e Nascita
        c4, c5, c6 = st.columns(3)
        ruolo = c4.selectbox("Ruolo", ["P", "D", "C", "A"])
        nascita = c5.date_input("Data di nascita", min_value=date(1900, 1, 1), value=date(2009, 1, 1))
        presenze = c6.number_input("Presenze", min_value=0, step=1)
        
        # Terza riga: Statistiche
        c7, c8, c9 = st.columns(3)
        minuti = c7.number_input("Minutaggio", min_value=0, step=1)
        gol = c8.number_input("Gol fatti/subiti", step=1)
        fatica = c9.slider("Fatica (%)", 0, 100, 0)
        
        # Quarta riga: Disciplina
        c10, c11 = st.columns(2)
        gialli = c10.number_input("Gialli", min_value=0, step=1)
        rossi = c11.number_input("Rossi", min_value=0, step=1)
        
        note = st.text_area("Note Tecniche (osservazioni, punti di forza/debolezza)")
        
        if st.form_submit_button("💾 Salva nel Database"):
            new_player = pd.DataFrame([[squadra, cognome, nome, ruolo, nascita, presenze, minuti, gol, fatica, gialli, rossi, note]], 
                                     columns=st.session_state['players_db'].columns)
            st.session_state['players_db'] = pd.concat([st.session_state['players_db'], new_player], ignore_index=True)
            
            st.session_state['view'] = 'dashboard' 
            st.success("Salvataggio completato!")
            st.rerun()

# 2. SCHERMATA CAMPIONATO
elif st.session_state['view'] == 'campionato':
    st.subheader("🏆 Impostazioni Campionato")
    if st.button("⬅️ Torna alla Home"):
        st.session_state['view'] = 'dashboard'
        st.rerun()
    st.selectbox("Seleziona Girone di riferimento:", ["U17 Elite - C", "U17 Regionali - B", "Provinciali Roma"])

# 3. HOME (DASHBOARD) - Mostra sempre la tabella
if st.session_state['view'] == 'dashboard':
    st.subheader("📋 Database Giocatori")
    if not st.session_state['players_db'].empty:
        # Visualizzazione della tabella con i dati salvati
        st.dataframe(st.session_state['players_db'], use_container_width=True)
        
        # Funzionalità di esportazione
        csv = st.session_state['players_db'].to_csv(index=False).encode('utf-8')
        st.download_button("📥 Esporta in CSV per Excel", csv, "scouting_data.csv", "text/csv")
    else:
        st.info("Il database è vuoto. Clicca su 'Aggiungi Giocatore' per iniziare.")
