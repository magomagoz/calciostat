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

# --- LISTE SQUADRE POPOLATE ---
GIRONI_SQUADRE = {
    "ALLIEVI PROVINCIALI U17 ROMA - Girone A": ["Aurelia Antica Aurelio", "Leocon", "Bracciano Calcio", "Real Campagnano", "Evergreen Civitavecchia", "Santa Marinella 1947", "Cortina Sporting Club", "Anguillara Calcio", "Nuova Valle Aurelia", "Formello Calcio C.R.", "DM 84 Cerveteri", "Accademy SVS Roma", "Virtus Marina di San Nicola", "Tolfa Calcio", "Borgo Palidoro", "Forte Bravetta"],
    "ALLIEVI PROVINCIALI U17 ROMA - Girone B": ["SVS Roma", "Fortitudo Roma Club 1908", "Vigna Pia", "MYSP", "Trigoria", "CVN Casal Bernocchi", "Quadraro Sport Roma", "Real Tirreno", "S.C. Due Ponti Calcio", "O.M.C. Calcio", "Garbatella 1920", "Polisportiva G. Castello", "Stella Polare De La Salle", "Infernetto calcio"],
    "ALLIEVI PROVINCIALI U17 ROMA - Girone C": ["City Football Club", "Atletico Morena", "Magnitudo FCCG", "ACR Football Club", "Academy T.T.T. Pro", "Academy Mundial", "Almas Roma", "Accademia Sporting Roma", "Calcio ULN Consalvo 1972", "Next Gen Lodigiani", "Atletico San Lorenzo", "Accademy Certosa", "Accademia Real Tuscolano C.", "Aquilotti Lazio C5"],
    "ALLIEVI PROVINCIALI U17 ROMA - Girone D": ["Monterotondo 1935", "Nova 7", "Riano Calcio", "F.C. Rieti 1936", "Vigor Rignano Flaminio", "Santa Lucia Calcio", "Città di Fiano", "Mentana", "Accademia Calcio Sabina SL", "Gorilla", "Tor Lupara", "Rieti City Soccer Club", "Piazza Tevere"],
    "ALLIEVI PROVINCIALI U17 ROMA - Girone E": ["Nettuno", "Sporting Nuova Florida", "Castelverde Calcio", "Pol. Canarini 1926 RDP", "Academy Cynthia Genzano", "Colonna", "F.C. Grifone Soccer", "Labico Calcio", "Accademia Calcio Frascati", "Atletico Monteporzio", "Vis S. Maria delle Mole", "Valle Martella Calcio", "Semprevisa", "SS. Pietro e Paolo"],
    "ALLIEVI PROVINCIALI U17 ROMA - Girone F": ["Spes Artiglio", "Tor Tre Teste Next Gen", "S. Francesca Cabrini '98", "Vicovaro", "GDC Ponte di Nona", "Futbol Talenti", "FC Grotte Celoni Roma VII", "Virtus Torre Maura", "Setteville Caserosse", "Ledesma Academy", "Football Jus", "Vis Subiaco", "Villa Adriana", "Olimpica Roma"]
}

# Nome del file dove verranno salvati i dati
DB_FILE = "database_scouting.csv"

def carica_dati():
    """Carica i dati dal file CSV se esiste, altrimenti crea un DF vuoto"""
    try:
        df = pd.read_csv(DB_FILE)
        # Convertiamo la colonna data per evitare errori
        df['Data di nascita'] = pd.to_datetime(df['Data di nascita']).dt.date
        return df
    except FileNotFoundError:
        cols = ["Squadra", "Cognome", "Nome", "Ruolo", "Data di nascita", "Presenze", 
                "Minutaggio", "Gol", "Fatica", "Gialli", "Rossi", "Rating", "Note"]
        return pd.DataFrame(columns=cols)

def salva_dati(df):
    """Salva il DataFrame su file CSV"""
    df.to_csv(DB_FILE, index=False)

# Inizializzazione Database con persistenza
if 'players_db' not in st.session_state:
    st.session_state['players_db'] = carica_dati()
    
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
    st.subheader("📋 Elenco Completo Giocatori")
    
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

# --- LOGICA PAGINA CAMPIONATO ---
if st.session_state['view'] == 'campionato':
    st.subheader("🏆 Selezione Girone Allievi Provinciali U17")
    
    # Estraiamo automaticamente i nomi dei gironi dalle chiavi del dizionario GIRONI_SQUADRE
    lista_gironi = list(GIRONI_SQUADRE.keys())
    
    # Il menu a tendina ora mostrerà: "U17 Roma - Girone A", "U17 Roma - Girone B", ecc.
    scelta_girone = st.selectbox(
        "Scegli il girone da monitorare:", 
        options=lista_gironi,
        index=lista_gironi.index(st.session_state['camp_scelto']) if st.session_state['camp_scelto'] in lista_gironi else 0
    )
    
    if st.button("Conferma e Vai alla Dashboard", use_container_width=True): 
        # Salviamo la scelta e torniamo alla dashboard
        st.session_state['camp_scelto'] = scelta_girone
        st.session_state['view'] = 'dashboard'
        st.rerun()

elif st.session_state['view'] == 'aggiungi':
    st.subheader(f"➕ Nuovo Profilo - {st.session_state['camp_scelto']}")
    
    # 1. Recupero la lista corretta
    squadre_disponibili = GIRONI_SQUADRE[st.session_state['camp_scelto']]
    
    if st.button("⬅️ Annulla e torna all'Elenco"):
        st.session_state['view'] = 'dashboard'
        st.rerun()

    # Usiamo il form per raggruppare i dati
    with st.form("add_player_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        squadra = col1.selectbox("Squadra", squadre_disponibili)
        ruolo = col2.selectbox("Ruolo", ["Portiere", "Difensori", "Centrocampista", "Attaccante"])
        
        cognome = st.text_input("Cognome")
        nome = st.text_input("Nome")
        nascita = st.date_input("Data di Nascita", min_value=date(1900,1,1), value=date(2025,1,1))
        
        c_p, c_m, c_g = st.columns(3)
        pres = c_p.number_input("Presenze", min_value=0, step=1)
        minuti = c_m.number_input("Minutaggio totale", min_value=0, step=1)
        gol = c_g.number_input("Gol segnati", step=1)
        
        c_gi, c_ro = st.columns(2)
        gialli = c_gi.number_input("Cartellini Gialli", min_value=0, step=1)
        rossi = c_ro.number_input("Cartellini Rossi", min_value=0, step=1)
        
        note = st.text_area("Note Tecniche")
        
        submit = st.form_submit_button("💾 CALCOLA RATING E SALVA NEL DB")
        
        if submit:
            if cognome == "" or nome == "":
                st.error("Per favore, inserisci almeno Cognome e Nome.")
            else:
                # 2. CALCOLO IL RATING
                rating_f = calcola_rating_empirico(pres, gol, minuti, nascita, ruolo, gialli, rossi)
                
                # 3. CREO IL NUOVO RECORD
                nuovo_giocatore = {
                    "Squadra": squadra,
                    "Cognome": cognome,
                    "Nome": nome,
                    "Ruolo": ruolo,
                    "Data di nascita": nascita,
                    "Presenze": pres,
                    "Minutaggio": minuti,
                    "Gol": gol,
                    "Fatica": 0, # Valore di default
                    "Gialli": gialli,
                    "Rossi": rossi,
                    "Rating": rating_f,
                    "Note": note
                }
                
                # 4. AGGIORNO IL DATABASE IN SESSION STATE
                # Usiamo loc[len(...)] che è più stabile di concat per singoli inserimenti
                st.session_state['players_db'].loc[len(st.session_state['players_db'])] = nuovo_giocatore
            
                # --- NOVITÀ: Salvataggio fisico su file ---
                salva_dati(st.session_state['players_db'])
                                
                # 5. CAMBIO VISTA E FORZO IL REFRESH
                st.session_state['view'] = 'dashboard'
                st.success(f"Giocatore {cognome} salvato con successo!")
                st.rerun() # Questo comando è fondamentale per tornare alla home


elif st.session_state['view'] == 'stats':
    st.subheader("📊 Analisi Performance")
    if not st.session_state['players_db'].empty:
        df = st.session_state['players_db']
        # Grafici
        fig_pie = px.pie(df, names='Ruolo', title="Distribuzione Ruoli in Rosa", hole=0.3)
        st.plotly_chart(fig_pie, use_container_width=True)
        
        fig_bar = px.bar(df, x='', y='Rating', color='Squadra', 
                         title="Classifica Valore Empirico (Rating)", text_auto=True)
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("Aggiungi giocatori per generare i grafici.")

        # --- SEZIONE CANCELLAZIONE SICURA ---
        st.divider()
        st.warning("⚠️ **Zona di Pericolo**")
        
        # Primo passaggio: Checkbox di sblocco
        conferma_sblocco = st.checkbox("Voglio abilitare la cancellazione totale dei dati")
        
        if conferma_sblocco:
            # Secondo passaggio: Pulsante rosso che appare solo se il checkbox è attivo
            st.error("Attenzione: questa operazione è irreversibile!")

            if st.button("🗑️ SVUOTA DEFINITIVAMENTE IL DATABASE"):
                # Svuota memoria
                st.session_state['players_db'] = pd.DataFrame(columns=st.session_state['players_db'].columns)
                
                # --- NOVITÀ: Svuota file fisico ---
                salva_dati(st.session_state['players_db'])
                
                st.success("Database azzerato.")
                st.rerun()

