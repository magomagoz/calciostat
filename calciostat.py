import streamlit as st
import pandas as pd
from datetime import date

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Scouting Management", layout="wide", page_icon="⚽")

# --- 1. CONFIGURAZIONE SQUADRE (Aggiungi qui tutte le squadre che vuoi) ---
SQUADRE_ELITE_C = [
    "Accademia Real Tuscolano", "Trastevere", "Vigor Perconti", 
    "Urbetevere", "Grifone Grimaldi", "Nuova Tor Tre Teste",
    "Lodigiani", "Savio", "Cinecittà Bettini", "Campus EUR"
]

SQUADRE_REGIONALI_B = [
    "Setteville", "Villalba", "Guidonia", "Tivoli", 
    "Spes Montesacro", "Settecamini", "Riano"
]

SQUADRE_PROVINCIALI = [
    "Squadra Esempio A", "Squadra Esempio B", "Squadra Esempio C"
]

# --- INIZIALIZZAZIONE SESSION STATE (Memoria dell'App) ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'players_db' not in st.session_state:
    cols = ["Squadra", "Cognome", "Nome", "Ruolo", "Data di nascita", "Presenze", 
            "Minutaggio", "Gol fatti/subiti", "Fatica", "Cartellini Gialli", 
            "Cartellini Rossi", "Note"]
    st.session_state['players_db'] = pd.DataFrame(columns=cols)
if 'view' not in st.session_state:
    st.session_state['view'] = 'dashboard'
if 'camp_scelto' not in st.session_state:
    st.session_state['camp_scelto'] = "U17 Elite - C"

# --- FUNZIONE DI NAVIGAZIONE ---
def cambia_pagina(nome_pagina):
    st.session_state['view'] = nome_pagina
    st.rerun()

# --- SISTEMA DI LOGIN ---
if not st.session_state['logged_in']:
    st.title("🔐 Accesso Scouting Management")
    with st.container():
        user = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login", use_container_width=True):
            if user == "admin" and password == "scout2026": 
                st.session_state['logged_in'] = True
                st.rerun()
            else:
                st.error("Credenziali errate")
    st.stop()

# --- DASHBOARD PRINCIPALE ---
st.title("⚽ Scouting Management System")
st.write(f"Campionato attivo: **{st.session_state['camp_scelto']}**")

# Pulsanti di navigazione sempre visibili
c1, c2 = st.columns(2)
with c1:
    if st.button("🏆 Scelta Campionato", use_container_width=True):
        cambia_pagina('campionato')
with c2:
    if st.button("➕ Aggiungi Giocatore", use_container_width=True):
        cambia_pagina('aggiungi')

st.divider()

# --- GESTIONE DELLE PAGINE ---

# 1. PAGINA: SCELTA CAMPIONATO
if st.session_state['view'] == 'campionato':
    st.subheader("🏆 Impostazioni Campionato")
    scelta = st.selectbox(
        "Seleziona il Campionato di riferimento:", 
        ["U17 Elite - C", "U17 Regionali - B", "Provinciali Roma"],
        index=0
    )
    if st.button("Conferma Scelta"):
        st.session_state['camp_scelto'] = scelta
        cambia_pagina('dashboard')

# 2. PAGINA: AGGIUNGI GIOCATORE
elif st.session_state['view'] == 'aggiungi':
    st.subheader(f"➕ Nuovo Inserimento - {st.session_state['camp_scelto']}")
    
    # Selezione dinamica della lista squadre
    if st.session_state['camp_scelto'] == "U17 Elite - C":
        lista_squadre = SQUADRE_ELITE_C
    elif st.session_state['camp_scelto'] == "U17 Regionali - B":
        lista_squadre = SQUADRE_REGIONALI_B
    else:
        lista_squadre = SQUADRE_PROVINCIALI

    if st.button("⬅️ Annulla e torna alla Home"):
        cambia_pagina('dashboard')

    with st.form("form_giocatore", clear_on_submit=True):
        f1, f2, f3 = st.columns(3)
        squadra = f1.selectbox("Squadra", lista_squadre)
        cognome = f2.text_input("Cognome")
        nome = f3.text_input("Nome")
        
        f4, f5, f6 = st.columns(3)
        ruolo = f4.selectbox("Ruolo", ["P", "D", "C", "A"])
        # Data di nascita sbloccata dal 1900
        nascita = f5.date_input("Data di nascita", min_value=date(1900, 1, 1), value=date(2009, 1, 1))
        presenze = f6.number_input("Presenze", min_value=0, step=1)
        
        f7, f8, f9 = st.columns(3)
        minuti = f7.number_input("Minutaggio totale", min_value=0, step=1)
        gol = f8.number_input("Gol fatti/subiti", step=1)
        fatica = f9.slider("Livello Fatica (%)", 0, 100, 0)
        
        f10, f11 = st.columns(2)
        gialli = f10.number_input("Cartellini Gialli", min_value=0, step=1)
        rossi = f11.number_input("Cartellini Rossi", min_value=0, step=1)
        
        note = st.text_area("Note e Osservazioni Tecniche")
        
        if st.form_submit_button("💾 SALVA NEL DATABASE"):
            nuovo_record = pd.DataFrame([[
                squadra, cognome, nome, ruolo, nascita, presenze, 
                minuti, gol, fatica, gialli, rossi, note
            ]], columns=st.session_state['players_db'].columns)
            
            st.session_state['players_db'] = pd.concat([st.session_state['players_db'], nuovo_record], ignore_index=True)
            st.success("Giocatore salvato correttamente!")
            cambia_pagina('dashboard')

# 3. PAGINA: DASHBOARD (Visualizzazione Tabella)
if st.session_state['view'] == 'dashboard':
    st.subheader("📋 Database Scouting Attuale")
    if not st.session_state['players_db'].empty:
        # Mostra la tabella
        st.dataframe(st.session_state['players_db'], use_container_width=True)
        
        # Bottone per scaricare i dati
        csv = st.session_state['players_db'].to_csv(index=False).encode('utf-8')
        st.download_button("📥 Scarica Database Excel (CSV)", csv, "scouting_2026.csv", "text/csv")
        
        if st.button("🗑️ Svuota Database (Attenzione!)"):
            st.session_state['players_db'] = pd.DataFrame(columns=st.session_state['players_db'].columns)
            st.rerun()
    else:
        st.info("Il database è vuoto. Inizia aggiungendo un giocatore.")
