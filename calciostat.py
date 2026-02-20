import streamlit as st
import pandas as pd
from datetime import date
import plotly.express as px # Necessario per i grafici

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Scouting Management Pro", layout="wide", page_icon="⚽")

# --- LISTE SQUADRE ---
SQUADRE_ELITE_C = ["Accademia Real Tuscolano", "Trastevere", "Vigor Perconti", "Urbetevere", "Grifone Grimaldi", "Nuova Tor Tre Teste", "Lodigiani", "Savio", "Cinecittà Bettini", "Campus EUR"]
SQUADRE_REGIONALI_B = ["Setteville", "Villalba", "Guidonia", "Tivoli", "Spes Montesacro", "Settecamini", "Riano"]
SQUADRE_PROVINCIALI = ["Squadra A", "Squadra B", "Squadra C"]

# --- INIZIALIZZAZIONE ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'players_db' not in st.session_state:
    cols = ["Squadra", "Cognome", "Nome", "Ruolo", "Data di nascita", "Presenze", 
            "Minutaggio", "Gol fatti/subiti", "Fatica", "Gialli", "Rossi", "Rating", "Note"]
    st.session_state['players_db'] = pd.DataFrame(columns=cols)
if 'view' not in st.session_state:
    st.session_state['view'] = 'dashboard'
if 'camp_scelto' not in st.session_state:
    st.session_state['camp_scelto'] = "U17 Elite - C"

def cambia_pagina(nome_pagina):
    st.session_state['view'] = nome_pagina
    st.rerun()

# --- LOGIN ---
if not st.session_state['logged_in']:
    st.title("🔐 Accesso Scouting Management")
    user = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login", use_container_width=True):
        if user == "admin" and password == "scout2026": 
            st.session_state['logged_in'] = True
            st.rerun()
    st.stop()

# --- NAVBAR ---
st.title("⚽ Scouting Management System")
c1, c2, c3 = st.columns(3)
with c1:
    if st.button("🏆 Campionato", use_container_width=True): cambia_pagina('campionato')
with c2:
    if st.button("➕ Aggiungi", use_container_width=True): cambia_pagina('aggiungi')
with c3:
    if st.button("📊 Statistiche", use_container_width=True): cambia_pagina('stats')

st.divider()

# --- 1. PAGINA AGGIUNGI (Con Rating Decimale) ---
if st.session_state['view'] == 'aggiungi':
    st.subheader(f"➕ Nuovo Giocatore - {st.session_state['camp_scelto']}")
    lista = SQUADRE_ELITE_C if st.session_state['camp_scelto'] == "U17 Elite - C" else SQUADRE_REGIONALI_B
    
    if st.button("⬅️ Torna alla Home"): cambia_pagina('dashboard')

    with st.form("form_giocatore", clear_on_submit=True):
        f1, f2, f3 = st.columns(3)
        squadra = f1.selectbox("Squadra", lista)
        cognome = f2.text_input("Cognome")
        nome = f3.text_input("Nome")
        
        f4, f5, f6 = st.columns(3)
        ruolo = f4.selectbox("Ruolo", ["P", "D", "C", "A"])
        nascita = f5.date_input("Data di nascita", min_value=date(1900, 1, 1), value=date(2025, 1, 1))
        # NUOVO CAMPO: Rating Decimale 1.0 - 10.0
        rating = f6.number_input("Valutazione Empirica (1-10)", min_value=1.0, max_value=10.0, value=6.0, step=0.1)
        
        f7, f8, f9 = st.columns(3)
        presenze = f7.number_input("Presenze", min_value=0)
        minuti = f8.number_input("Minutaggio", min_value=0)
        gol = f9.number_input("Gol fatti/subiti", step=1)
        
        note = st.text_area("Note Tecniche")
        
        if st.form_submit_button("💾 SALVA"):
            nuovo = pd.DataFrame([[squadra, cognome, nome, ruolo, nascita, presenze, minuti, gol, 0, 0, 0, rating, note]], 
                                columns=st.session_state['players_db'].columns)
            st.session_state['players_db'] = pd.concat([st.session_state['players_db'], nuovo], ignore_index=True)
            st.success("Salvato!")
            cambia_pagina('dashboard')

# --- 2. PAGINA STATISTICHE (Grafici) ---
elif st.session_state['view'] == 'stats':
    st.subheader("📊 Analisi Dati Scouting")
    if st.button("⬅️ Torna alla Home"): cambia_pagina('dashboard')
    
    if not st.session_state['players_db'].empty:
        df = st.session_state['players_db']
        g1, g2 = st.columns(2)
        with g1:
            st.write("**Distribuzione Ruoli**")
            fig_pie = px.pie(df, names='Ruolo', color='Ruolo', hole=0.3)
            st.plotly_chart(fig_pie, use_container_width=True)
        with g2:
            st.write("**Gol per Squadra**")
            fig_bar = px.bar(df, x='Squadra', y='Gol fatti/subiti', color='Squadra')
            st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.warning("Database vuoto. Inserisci dati per vedere i grafici.")

# --- 3. DASHBOARD E WARNING CANCELLAZIONE ---
elif st.session_state['view'] == 'dashboard' or st.session_state['view'] == 'campionato':
    if st.session_state['view'] == 'campionato':
        st.session_state['camp_scelto'] = st.selectbox("Cambia Campionato:", ["U17 Elite - C", "U17 Regionali - B"])
        if st.button("Conferma"): cambia_pagina('dashboard')
    
    st.subheader("📋 Database")
    if not st.session_state['players_db'].empty:
        st.dataframe(st.session_state['players_db'], use_container_width=True)
        
        # SISTEMA WARNING SVUOTA DB
        st.divider()
        if st.checkbox("⚠️ Attiva modalità cancellazione"):
            if st.button("❌ SVUOTA DEFINITIVAMENTE TUTTO IL DATABASE"):
                st.session_state['players_db'] = pd.DataFrame(columns=st.session_state['players_db'].columns)
                st.success("Database azzerato.")
                st.rerun()
    else:
        st.info("Nessun dato.")

