import streamlit as st
import pandas as pd
from datetime import date

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Scouting Management Pro", layout="wide")

if 'players_db' not in st.session_state:
    cols = ["Squadra", "Cognome", "Nome", "Ruolo", "Data di nascita", "Presenze", 
            "Minutaggio", "Gol fatti/subiti", "Fatica", "Gialli", "Rossi", "Rating", "Note"]
    st.session_state['players_db'] = pd.DataFrame(columns=cols)

if 'view' not in st.session_state:
    st.session_state['view'] = 'dashboard'
if 'camp_scelto' not in st.session_state:
    st.session_state['camp_scelto'] = "U17 Elite - C"

# --- FUNZIONE CALCOLO RATING AUTOMATICO ---
def calcola_rating_empirico(presenze, gol, minuti, data_nascita):
    # Punto di partenza richiesto
    rating = 5.0
    
    # Bonus Statistiche
    rating += (gol * 0.2)             # 0.2 punti per ogni gol
    rating += (presenze // 3) * 0.1   # 0.1 punti ogni 3 presenze
    rating += (minuti // 200) * 0.1   # 0.1 punti ogni 200 minuti
    
    # Bonus Età (Empirico: più è giovane, più il potenziale alza il rating)
    anno_nascita = data_nascita.year
    if anno_nascita >= 2010:          # Giocatore sotto quota
        rating += 0.5
    elif anno_nascita == 2009:
        rating += 0.2
        
    # Limite massimo 10.0
    return round(min(rating, 10.0), 1)

# --- NAVBAR ---
st.title("⚽ Scouting Intelligence System")
c1, c2, c3 = st.columns(3)
with c1:
    if st.button("🏆 Campionato", use_container_width=True): st.session_state['view'] = 'campionato'; st.rerun()
with c2:
    if st.button("➕ Aggiungi Giocatore", use_container_width=True): st.session_state['view'] = 'aggiungi'; st.rerun()
with c3:
    if st.button("📊 Statistiche", use_container_width=True): st.session_state['view'] = 'stats'; st.rerun()

st.divider()

# --- PAGINA AGGIUNGI CON AUTO-RATING ---
if st.session_state['view'] == 'aggiungi':
    st.subheader(f"Nuovo Inserimento - {st.session_state['camp_scelto']}")
    
    with st.form("form_giocatore", clear_on_submit=True):
        f1, f2, f3 = st.columns(3)
        squadra = f1.text_input("Squadra") # O selectbox come prima
        cognome = f2.text_input("Cognome")
        nome = f3.text_input("Nome")
        
        f4, f5, f6 = st.columns(3)
        ruolo = f4.selectbox("Ruolo", ["P", "D", "C", "A"])
        nascita = f5.date_input("Data di nascita", min_value=date(1900, 1, 1), value=date(2009, 1, 1))
        fatica = f6.slider("Fatica (%)", 0, 100, 0)
        
        f7, f8, f9 = st.columns(3)
        presenze = f7.number_input("Presenze", min_value=0, step=1)
        minuti = f8.number_input("Minutaggio totale", min_value=0, step=1)
        gol = f9.number_input("Gol fatti/subiti", step=1)
        
        note = st.text_area("Note Tecniche")
        
        if st.form_submit_button("💾 CALCOLA RATING E SALVA"):
            # Calcolo automatico prima del salvataggio
            rating_finale = calcola_rating_empirico(presenze, gol, minuti, nascita)
            
            nuovo_record = pd.DataFrame([[
                squadra, cognome, nome, ruolo, nascita, presenze, 
                minuti, gol, fatica, 0, 0, rating_finale, note
            ]], columns=st.session_state['players_db'].columns)
            
            st.session_state['players_db'] = pd.concat([st.session_state['players_db'], nuovo_record], ignore_index=True)
            st.success(f"Giocatore salvato! Rating calcolato: {rating_finale}")
            st.session_state['view'] = 'dashboard'
            st.rerun()

# --- PAGINA DASHBOARD ---
elif st.session_state['view'] == 'dashboard':
    st.subheader("📋 Database Scouting")
    if not st.session_state['players_db'].empty:
        st.dataframe(st.session_state['players_db'], use_container_width=True)
        
        # Sistema di sicurezza Svuota DB
        st.divider()
        safe_check = st.checkbox("Sblocca cancellazione")
        if safe_check and st.button("🗑️ ELIMINA TUTTI I DATI"):
            st.session_state['players_db'] = pd.DataFrame(columns=st.session_state['players_db'].columns)
            st.rerun()
    else:
        st.info("Nessun giocatore in lista.")

# --- PAGINA STATISTICHE ---
elif st.session_state['view'] == 'stats':
    st.subheader("📊 Analisi Performance")
    if not st.session_state['players_db'].empty:
        df = st.session_state['players_db']
        import plotly.express as px
        # Grafico Rating vs Cognome
        fig = px.bar(df, x='Cognome', y='Rating', color='Ruolo', title="Classifica Rating Empirico")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Dati insufficienti per i grafici.")
