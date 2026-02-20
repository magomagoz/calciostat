import streamlit as st
import pandas as pd

# Configurazione Pagina
st.set_page_config(page_title="Scout Manager U17", layout="wide")

# --- SISTEMA DI LOGIN ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.title("🔐 Accesso Scout System")
    user = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if user == "admin" and password == "scout2026": # Puoi cambiare queste credenziali
            st.session_state['logged_in'] = True
            st.rerun()
        else:
            st.error("Credenziali errate")
    st.stop()

# --- INIZIALIZZAZIONE DATABASE ---
if 'players_db' not in st.session_state:
    # Intestazione richiesta
    cols = ["Cognome", "Nome", "Ruolo", "Data di nascita", "Presenze", 
            "Minutaggio", "Fatica", "Cartellini Gialli", "Cartellini Rossi", "Note"]
    st.session_state['players_db'] = pd.DataFrame(columns=cols)

# --- DASHBOARD PRINCIPALE ---
st.title("⚽ Dashboard Scouting - Accademia Real Tuscolano")

# Creazione dei tre pulsanti richiesti
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🏆 Scelta Campionato"):
        st.session_state['view'] = 'campionato'

with col2:
    if st.button("🛡️ Nome Squadra"):
        st.session_state['view'] = 'squadra'

with col3:
    if st.button("➕ Aggiungi Giocatore"):
        st.session_state['view'] = 'aggiungi'

st.divider()

# --- LOGICA DELLE PAGINE ---
view = st.session_state.get('view', 'squadra')

if view == 'aggiungi':
    st.subheader("Inserisci Nuovo Giocatore")
    with st.form("new_player"):
        c1, c2, c3 = st.columns(3)
        cognome = c1.text_input("Cognome")
        nome = c2.text_input("Nome")
        ruolo = c3.selectbox("Ruolo", ["P", "D", "C", "A"])
        
        c4, c5, c6 = st.columns(3)
        nascita = c4.date_input("Data di nascita")
        presenze = c5.number_input("Presenze", min_value=0, step=1)
        minuti = c6.number_input("Minutaggio", min_value=0, step=1)
        
        c7, c8, c9 = st.columns(3)
        fatica = c7.slider("Fatica", 0, 100, 0)
        gialli = c8.number_input("Gialli", min_value=0, step=1)
        rossi = c9.number_input("Rossi", min_value=0, step=1)
        
        note = st.text_area("Note")
        
        if st.form_submit_button("Salva nel Database"):
            new_data = pd.DataFrame([[cognome, nome, ruolo, nascita, presenze, minuti, fatica, gialli, rossi, note]], 
                                    columns=st.session_state['players_db'].columns)
            st.session_state['players_db'] = pd.concat([st.session_state['players_db'], new_data], ignore_index=True)
            st.success("Giocatore aggiunto!")

elif view == 'squadra':
    st.subheader("📋 Rosa e Statistiche")
    if not st.session_state['players_db'].empty:
        # Tabella con l'intestazione richiesta
        st.dataframe(st.session_state['players_db'], use_container_width=True)
        
        # Export per Excel
        csv = st.session_state['players_db'].to_csv(index=False).encode('utf-8')
        st.download_button("📥 Esporta Database (CSV)", csv, "database_scout.csv", "text/csv")
    else:
        st.info("Il database è vuoto. Aggiungi i primi giocatori per visualizzare la tabella.")

elif view == 'campionato':
    st.subheader("🏆 Selezione Campionato")
    camp = st.selectbox("Seleziona il girone di riferimento:", 
                        ["U17 Elite - Girone C", "U17 Regionali - Girone B", "U17 Provinciali"])
    st.write(f"Campionato attivo: **{camp}**")
