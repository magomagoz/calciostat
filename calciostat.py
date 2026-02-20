import streamlit as st
import pandas as pd
from datetime import date

# Importiamo plotly in modo sicuro
try:
    import plotly.express as px
except ImportError:
    st.error("Per favore aggiungi 'plotly' al file requirements.txt su GitHub!")

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Scouting Management Pro", layout="wide")

# Liste Squadre
SQUADRE_ELITE_C = ["Accademia Real Tuscolano", "Trastevere", "Vigor Perconti", "Urbetevere", "Grifone Grimaldi", "Nuova Tor Tre Teste"]
SQUADRE_REGIONALI_B = ["Setteville", "Villalba", "Guidonia", "Tivoli", "Spes Montesacro"]

# Inizializzazione Database
if 'players_db' not in st.session_state:
    cols = ["Squadra", "Cognome", "Nome", "Ruolo", "Data di nascita", "Presenze", 
            "Minutaggio", "Gol fatti/subiti", "Fatica", "Gialli", "Rossi", "Rating", "Note"]
    st.session_state['players_db'] = pd.DataFrame(columns=cols)

if 'view' not in st.session_state:
    st.session_state['view'] = 'dashboard'
if 'camp_scelto' not in st.session_state:
    st.session_state['camp_scelto'] = "U17 Elite - C"

# --- LOGIN ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.title("🔐 Login Scouting")
    u = st.text_input("User")
    p = st.text_input("Pass", type="password")
    if st.button("Entra"):
        if u == "admin" and p == "scout2026":
            st.session_state['logged_in'] = True
            st.rerun()
    st.stop()

# --- NAVBAR ---
st.title("⚽ Scouting System")
c1, c2, c3 = st.columns(3)
with c1:
    if st.button("🏆 Campionato", use_container_width=True): st.session_state['view'] = 'campionato'; st.rerun()
with c2:
    if st.button("➕ Aggiungi", use_container_width=True): st.session_state['view'] = 'aggiungi'; st.rerun()
with c3:
    if st.button("📊 Statistiche", use_container_width=True): st.session_state['view'] = 'stats'; st.rerun()

st.divider()

# --- LOGICA PAGINE ---

if st.session_state['view'] == 'campionato':
    st.subheader("Seleziona Campionato")
    st.session_state['camp_scelto'] = st.selectbox("Girone:", ["U17 Elite - C", "U17 Regionali - B"])
    if st.button("Conferma"): st.session_state['view'] = 'dashboard'; st.rerun()

elif st.session_state['view'] == 'aggiungi':
    st.subheader(f"Aggiungi Giocatore - {st.session_state['camp_scelto']}")
    lista = SQUADRE_ELITE_C if st.session_state['camp_scelto'] == "U17 Elite - C" else SQUADRE_REGIONALI_B
    
    with st.form("add_player"):
        col_a, col_b = st.columns(2)
        squadra = col_a.selectbox("Squadra", lista)
        ruolo = col_b.selectbox("Ruolo", ["P", "D", "C", "A"])
        
        cognome = st.text_input("Cognome")
        nome = st.text_input("Nome")
        nascita = st.date_input("Data di Nascita", min_value=date(1900,1,1), value=date(2009,1,1))
        
        # Rating Decimale 1-10
        rating = st.number_input("Rating Empirico (1.0 - 10.0)", 1.0, 10.0, 6.0, 0.1)
        
        col_c, col_d, col_e = st.columns(3)
        pres = col_c.number_input("Presenze", 0)
        minuti = col_d.number_input("Minuti", 0)
        gol = col_e.number_input("Gol", 0)
        
        note = st.text_area("Note")
        
        if st.form_submit_button("💾 SALVA"):
            new_row = [squadra, cognome, nome, ruolo, nascita, pres, minuti, gol, 0, 0, 0, rating, note]
            st.session_state['players_db'].loc[len(st.session_state['players_db'])] = new_row
            st.session_state['view'] = 'dashboard'
            st.rerun()

elif st.session_state['view'] == 'stats':
    if not st.session_state['players_db'].empty:
        df = st.session_state['players_db']
        st.plotly_chart(px.pie(df, names='Ruolo', title="Distribuzione Ruoli"), use_container_width=True)
        st.plotly_chart(px.bar(df, x='Cognome', y='Rating', color='Squadra', title="Rating Giocatori"), use_container_width=True)
    else:
        st.info("Aggiungi dati per vedere i grafici.")

else: # DASHBOARD
    st.subheader("📋 Database Scouting")
    if not st.session_state['players_db'].empty:
        st.dataframe(st.session_state['players_db'], use_container_width=True)
        
        # Warning Svuota DB
        st.divider()
        check = st.checkbox("Abilita cancellazione totale")
        if check and st.button("🗑️ SVUOTA TUTTO"):
            st.session_state['players_db'] = pd.DataFrame(columns=st.session_state['players_db'].columns)
            st.rerun()
    else:
        st.write("Nessun giocatore inserito.")
