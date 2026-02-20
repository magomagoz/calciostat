import streamlit as st
import pandas as pd
from datetime import date

# Importiamo plotly in modo sicuro per i grafici
try:
    import plotly.express as px
except ImportError:
    st.error("Per favore aggiungi 'plotly' al file requirements.txt su GitHub!")

# --- CONFIGURAZIONE ---
st.image("banner.png", use_column_width=True, caption="Scouting Management")
#st.set_page_config(page_title="Scouting Management Pro", layout="wide")

# Liste Squadre Popolabili
ALLIEVI_PROVINCIALI_U17_ROMA_A = ["Aurelia Antica Aurelio", "Leocon", "Bracciano Calcio", "Real Campagnano", "Evergreen Civitavecchia", "Santa Marinella 1947", "Cortina Sporting Club", "Anguillara Calcio", "Nuova Valle Aurelia", "Formello Calcio C.R.", "DM 84 Cerveteri", "Accademy SVS Roma", "Virtus Marina di San Nicola", "Tolfa Calcio", "Borgo Palidoro", "Forte Bravetta"]
ALLIEVI_PROVINCIALI_U17_ROMA_B = ["SVS Roma", "Fortitudo Roma Club 1908", "Vigna Pia", "MYSP", " Trigoria", "CVN Casal Bernocchi", "Quadraro Sport Roma", "Real Tirreno", "S.C. Due Ponti Calcio", "O.M.C. Calcio", "Garbatella 1920", "Polisportiva G. Castello", "Stella Polare De La Salle", "Infernetto calcio"]
ALLIEVI_PROVINCIALI_U17_ROMA_C = ["City Football Club", "Atletico Morena", "Magnitudo FCCG", "ACR Football Club", "Academy T.T.T. Pro", "Academy Mundial", "Almas Roma", "Accademia Sporting Roma", "Calcio ULN Consalvo 1972", "Next Gen Lodigiani", "Atletico San Lorenzo", "Accademy Certosa", "Accademia Real Tuscolano C.", "Aquilotti Lazio C5"]
ALLIEVI_PROVINCIALI_U17_ROMA_D = ["Monterotondo 1935", "Nova 7", "Riano Calcio", "F.C. Rieti 1936" "Vigor Rignano Flaminio", "Santa Lucia Calcio", "Città di Fiano", "Mentana", "Accademia Calcio Sabina SL", "Gorilla", "Tor Lupara", "Rieti City Soccer Club", "Piazza Tevere"]
ALLIEVI_PROVINCIALI_U17_ROMA_E = ["Nettuno", "Sporting Nuova Florida", "Castelverde Calcio", "Pol. Canarini 1926 RDP", "Academy Cynthia Genzano", "Colonna", "F.C. Grifone Soccer", "Labico Calcio", "Accademia Calcio Frascati", "Atletico Monteporzio", "Vis S. Maria delle Mole", "Valle Martella Calcio", "Semprevisa", "SS. Pietro e Paolo"]
ALLIEVI_PROVINCIALI_U17_ROMA_F = ["Spes Artiglio", "Tor Tre Teste Next Gen", "S. Francesca Cabrini '98", "Vicovaro", "GDC Ponte di Nona", "Futbol Talenti", "FC Grotte Celoni Roma VII", "Virtus Torre Maura", "Setteville Caserosse", "Ledesma Academy", "Football Jus", "Vis Subiaco", "Villa Adriana", "Olimpica Roma"]

# Inizializzazione Database in Session State
if 'players_db' not in st.session_state:
    cols = ["Squadra", "Cognome", "Nome", "Ruolo", "Data di nascita", "Presenze", 
            "Minutaggio", "Gol", "Fatica", "Gialli", "Rossi", "Rating", "Note"]
    st.session_state['players_db'] = pd.DataFrame(columns=cols)

if 'view' not in st.session_state:
    st.session_state['view'] = 'dashboard'
if 'camp_scelto' not in st.session_state:
    st.session_state['camp_scelto'] = list(GIRONI_SQUADRE.keys())[0]

# --- LOGIN ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.title("🔐 Login Scouting")
    u = st.text_input("User")
    p = st.text_input("Pass", type="password")
    if st.button("Entra", use_container_width=True):
        if u == "Marco" and p == "Scout2026":
            st.session_state['logged_in'] = True
            st.rerun()
        else:
            st.error("Credenziali errate")
    st.stop()

# --- FUNZIONE CALCOLO RATING AUTOMATICO AGGIORNATA ---
def calcola_rating_empirico(presenze, gol, minuti, data_nascita, ruolo, gialli, rossi):
    # Punto di partenza richiesto
    rating = 5.0
    
    # Bonus Gol differenziato per Ruolo
    if ruolo == "D":
        rating += (gol * 0.8)  # Un difensore che segna è raro
    elif ruolo == "C":
        rating += (gol * 0.5)
    else:
        rating += (gol * 0.2)  # Attaccanti
        
    # Bonus Esperienza e Minutaggio
    rating += (presenze // 3) * 0.2    # 0.2 punti ogni 3 presenze
    rating += (minuti // 200) * 0.33   # 0.33 punti ogni 200 minuti
    
    # Bonus Età (Potenziale giovani)
    anno_nascita = data_nascita.year
    if anno_nascita >= 2010: 
        rating += 0.5
    elif anno_nascita == 2009: 
        rating += 0.2

    # --- AGGIUNTA MALUS DISCIPLINARI ---
    rating -= (gialli * 0.3)  # -0.3 per ogni ammonizione
    rating -= (rossi * 0.75)   # -0.75 per ogni espulsione
        
    # Il rating non può scendere sotto l'1.0 e non può superare il 10.0
    return round(max(min(rating, 10.0), 1.0), 1)

# --- NAVBAR AGGIORNATA ---
st.title("⚽ Scouting Intelligence System")
st.write(f"Campionato Attuale: **{st.session_state['camp_scelto']}**")

# Layout a 4 colonne per i pulsanti
c1, c2, c3, c4 = st.columns(4)
with c1:
    if st.button("🏆 Campionato", use_container_width=True): 
        st.session_state['view'] = 'campionato'; st.rerun()
with c2:
    if st.button("➕ Aggiungi", use_container_width=True): 
        st.session_state['view'] = 'aggiungi'; st.rerun()
with c3:
    if st.button("📋 Elenco DB", use_container_width=True): 
        st.session_state['view'] = 'dashboard'; st.rerun()
with c4:
    if st.button("📊 Statistiche", use_container_width=True): 
        st.session_state['view'] = 'stats'; st.rerun()

st.divider()

# --- LOGICA DELLA PAGINA ELENCO (DASHBOARD) ---
if st.session_state['view'] == 'dashboard':
    st.subheader("📋 Elenco Completo Giocatori nel Database")
    
    if not st.session_state['players_db'].empty:
        # Visualizzazione tabella con possibilità di ordinamento cliccando sulle colonne
        st.dataframe(
            st.session_state['players_db'].sort_values(by="Rating", ascending=False), 
            use_container_width=True,
            hide_index=True
        )
        
        # Conteggio rapido
        tot_giocatori = len(st.session_state['players_db'])
        st.write(f"Totale profili analizzati: **{tot_giocatori}**")
        
        # Bottone per scaricare i dati
        csv = st.session_state['players_db'].to_csv(index=False).encode('utf-8')
        st.download_button("📥 Esporta Elenco in CSV", csv, "elenco_scouting.csv", "text/csv")
    else:
        st.info("L'elenco è vuoto. Inizia ad aggiungere giocatori per popolare il database.")

# --- LOGICA PAGINE ---

if st.session_state['view'] == 'campionato':
    st.subheader("Seleziona Campionato")
    st.session_state['camp_scelto'] = st.selectbox("Girone:", ["U17 Elite - C", "U17 Regionali - B"])
    if st.button("Conferma e Vai alla Dashboard"): 
        st.session_state['view'] = 'dashboard'; st.rerun()

elif st.session_state['view'] == 'aggiungi':
    st.subheader(f"Scheda Giocatore - {st.session_state['camp_scelto']}")
    lista = SQUADRE_ELITE_C if st.session_state['camp_scelto'] == "U17 Elite - C" else SQUADRE_REGIONALI_B
    
    with st.form("add_player", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        squadra = col_a.selectbox("Squadra", lista)
        ruolo = col_b.selectbox("Ruolo", ["P", "D", "C", "A"])
        
        cognome = st.text_input("Cognome")
        nome = st.text_input("Nome")
        nascita = st.date_input("Data di Nascita", min_value=date(1900,1,1), value=date(2009,1,1))
        
        col_c, col_d, col_e = st.columns(3)
        pres = col_c.number_input("Presenze", 0)
        minuti = col_d.number_input("Minuti", 0)
        gol = col_e.number_input("Gol segnati", 0)
        
        fatica = st.slider("Livello Fatica (%)", 0, 100, 0)
        note = st.text_area("Note Tecniche / Osservazioni")
        
        if st.form_submit_button("💾 CALCOLA RATING E SALVA"):
            rating_finale = calcola_rating_empirico(pres, gol, minuti, nascita, ruolo)
            
            nuovo_record = pd.DataFrame([[
                squadra, cognome, nome, ruolo, nascita, pres, 
                minuti, gol, fatica, 0, 0, rating_finale, note
            ]], columns=st.session_state['players_db'].columns)
            
            st.session_state['players_db'] = pd.concat([st.session_state['players_db'], nuovo_record], ignore_index=True)
            st.success(f"Salvataggio riuscito! Rating calcolato: {rating_finale}")
            st.session_state['view'] = 'dashboard'
            st.rerun()

elif st.session_state['view'] == 'stats':
    st.subheader("📊 Analisi Performance")
    if not st.session_state['players_db'].empty:
        df = st.session_state['players_db']
        # Grafici
        fig_pie = px.pie(df, names='Ruolo', title="Distribuzione Ruoli in Rosa", hole=0.3)
        st.plotly_chart(fig_pie, use_container_width=True)
        
        fig_bar = px.bar(df, x='Cognome', y='Rating', color='Squadra', 
                         title="Classifica Valore Empirico (Rating)", text_auto=True)
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("Aggiungi giocatori per generare i grafici.")

else: # DASHBOARD
    st.subheader("📋 Database Scouting Attivo")
    if not st.session_state['players_db'].empty:
        st.dataframe(st.session_state['players_db'], use_container_width=True)
        
        # Download dei dati per backup
        csv = st.session_state['players_db'].to_csv(index=False).encode('utf-8')
        st.download_button("📥 Esporta in CSV", csv, "scouting_data.csv", "text/csv")
        
        # Warning Svuota DB
        st.divider()
        st.warning("⚠️ Zona Pericolosa")
        check = st.checkbox("Confermo di voler abilitare la cancellazione")
        if check and st.button("🗑️ CANCELLA TUTTI I DATI"):
            st.session_state['players_db'] = pd.DataFrame(columns=st.session_state['players_db'].columns)
            st.rerun()
    else:
        st.write("Nessun giocatore in archivio. Usa il tasto 'Aggiungi' per iniziare.")
