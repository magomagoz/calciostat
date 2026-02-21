import streamlit as st
import pandas as pd
from datetime import date

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Scouting Management Pro", layout="wide")

try:
    import plotly.express as px
except ImportError:
    st.error("Per favore aggiungi 'plotly' al file requirements.txt")

try:
    st.image("banner.png", use_container_width=True)
except:
    st.title("⚽ Scouting Management")

# --- LISTE SQUADRE ---
GIRONI_SQUADRE = {
    "ALLIEVI PROVINCIALI U17 ROMA - Girone C": ["City Football Club", "Atletico Morena", "Magnitudo FCCG", "ACR Football Club", "Academy T.T.T. Pro", "Academy Mundial", "Almas Roma", "Accademia Sporting Roma", "Calcio ULN Consalvo 1972", "Next Gen Lodigiani", "Atletico San Lorenzo", "Accademy Certosa", "Accademia Real Tuscolano C.", "Aquilotti Lazio C5"],
    "ALLIEVI PROVINCIALI U17 ROMA - Girone A": ["Aurelia Antica Aurelio", "Leocon", "Bracciano Calcio", "Real Campagnano", "Evergreen Civitavecchia", "Santa Marinella 1947", "Cortina Sporting Club", "Anguillara Calcio", "Nuova Valle Aurelia", "Formello Calcio C.R.", "DM 84 Cerveteri", "Accademy SVS Roma", "Virtus Marina di San Nicola", "Tolfa Calcio", "Borgo Palidoro", "Forte Bravetta"],
    "ALLIEVI PROVINCIALI U17 ROMA - Girone B": ["SVS Roma", "Fortitudo Roma Club 1908", "Vigna Pia", "MYSP", "Trigoria", "CVN Casal Bernocchi", "Quadraro Sport Roma", "Real Tirreno", "S.C. Due Ponti Calcio", "O.M.C. Calcio", "Garbatella 1920", "Polisportiva G. Castello", "Stella Polare De La Salle", "Infernetto calcio"],
    "ALLIEVI PROVINCIALI U17 ROMA - Girone D": ["Monterotondo 1935", "Nova 7", "Riano Calcio", "F.C. Rieti 1936", "Vigor Rignano Flaminio", "Santa Lucia Calcio", "Città di Fiano", "Mentana", "Accademia Calcio Sabina SL", "Gorilla", "Tor Lupara", "Rieti City Soccer Club", "Piazza Tevere"],
    "ALLIEVI PROVINCIALI U17 ROMA - Girone E": ["Nettuno", "Sporting Nuova Florida", "Castelverde Calcio", "Pol. Canarini 1926 RDP", "Academy Cynthia Genzano", "Colonna", "F.C. Grifone Soccer", "Labico Calcio", "Accademia Calcio Frascati", "Atletico Monteporzio", "Vis S. Maria delle Mole", "Valle Martella Calcio", "Semprevisa", "SS. Pietro e Paolo"],
    "ALLIEVI PROVINCIALI U17 ROMA - Girone F": ["Spes Artiglio", "Tor Tre Teste Next Gen", "S. Francesca Cabrini '98", "Vicovaro", "GDC Ponte di Nona", "Futbol Talenti", "FC Grotte Celoni Roma VII", "Virtus Torre Maura", "Setteville Caserosse", "Ledesma Academy", "Football Jus", "Vis Subiaco", "Villa Adriana", "Olimpica Roma"]
}

DB_PLAYERS = "database_scouting.csv"
DB_FATICA = "log_fatica.csv"

# --- FUNZIONI CORE ---
def carica_dati_relazionali():
    try:
        df_p = pd.read_csv(DB_PLAYERS)
    except:
        df_p = pd.DataFrame(columns=["Squadra", "Cognome", "Nome", "Ruolo", "Data di nascita", "Presenze", "Minutaggio", "Gol", "Fatica", "Gialli", "Rossi", "Rating", "Note"])
    
    try:
        df_f = pd.read_csv(DB_FATICA)
        df_f['Data'] = pd.to_datetime(df_f['Data']).dt.date
    except:
        df_f = pd.DataFrame(columns=["ID_Giocatore", "Data", "Fatica", "Note"])
    return df_p, df_f

def salva_tutto(df_p, df_f):
    df_p.to_csv(DB_PLAYERS, index=False)
    df_f.to_csv(DB_FATICA, index=False)

def calcola_rating_empirico(presenze, gol, minuti, data_nascita, ruolo, gialli, rossi):
    rating = 5.0
    if ruolo == "Difensori": rating += (gol * 0.5)
    elif ruolo == "Centrocampista": rating += (gol * 0.3)
    else: rating += (gol * 0.2)
    rating += (presenze // 3) * 0.1
    rating += (minuti // 180) * 0.2
    anno = data_nascita.year
    if anno >= 2011: rating += 0.5
    elif anno == 2010: rating += 0.2
    rating -= (gialli * 0.3)
    rating -= (rossi * 0.75)
    return round(max(min(rating, 10.0), 0.0), 1)

# --- INIZIALIZZAZIONE ---
if 'skip_upload' not in st.session_state:
    st.session_state['skip_upload'] = False

if 'players_db' not in st.session_state or 'fatica_db' not in st.session_state:
    p, f = carica_dati_relazionali()
    st.session_state['players_db'] = p
    st.session_state['fatica_db'] = f

if 'view' not in st.session_state: st.session_state['view'] = 'dashboard'
if 'camp_scelto' not in st.session_state: st.session_state['camp_scelto'] = list(GIRONI_SQUADRE.keys())[0]
if 'editing_index' not in st.session_state: st.session_state['editing_index'] = None
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False

# --- LOGIN ---
if not st.session_state['logged_in']:
    st.title("🔐 Login")
    u = st.text_input("User")
    p = st.text_input("Pass", type="password")
    if st.button("Entra", use_container_width=True):
        if u == "Marco" and p == "Scout2026":
            st.session_state['logged_in'] = True
            st.rerun()
        else:
            st.error("Credenziali errate")
    st.stop()

# --- LOGICA DI NAVIGAZIONE POST-LOGIN ---
if st.session_state['logged_in']:
    # Se il database è vuoto e non abbiamo ancora scelto cosa fare, mostra l'upload iniziale
    if st.session_state['players_db'].empty and st.session_state.get('skip_upload') is not True:
        st.title("👋 Benvenuto nel Sistema Scouting")
        st.info("Il database attuale è vuoto. Desideri caricare un backup o iniziare una nuova sessione?")
        
        col_up, col_new = st.columns(2)
        
        with col_up:
            st.subheader("📤 Carica File")
            uploaded_initial = st.file_uploader("Trascina qui il tuo file .csv", type="csv", key="initial_upload")
            if uploaded_initial:
                try:
                    import_df = pd.read_csv(uploaded_initial)
                    # Verifica colonne minime
                    if "Cognome" in import_df.columns:
                        st.session_state['players_db'] = import_df
                        salva_tutto(st.session_state['players_db'], st.session_state['fatica_db'])
                        st.success("Database caricato con successo!")
                        st.rerun()
                    else:
                        st.error("Il file non sembra avere il formato corretto.")
                except Exception as e:
                    st.error(f"Errore: {e}")
        
        with col_new:
            st.subheader("🆕 Nuova Sessione")
            st.write("Inizia a inserire i dati manualmente da zero.")
            if st.button("Inizia ora", use_container_width=True):
                st.session_state['skip_upload'] = True
                st.rerun()
        
        st.stop() # Blocca l'esecuzione qui finché non viene fatta una scelta

# --- NAVBAR ---
c1, c2, c3, c4 = st.columns(4)
with c1:
    if st.button("🏆 Campionato", use_container_width=True): st.session_state['view'] = 'campionato'; st.rerun()
with c2:
    if st.button("➕ Aggiungi", use_container_width=True): st.session_state['view'] = 'aggiungi'; st.rerun()
with c3:
    if st.button("📋 Elenco", use_container_width=True): st.session_state['view'] = 'dashboard'; st.rerun()
with c4:
    if st.button("📊 Statistiche", use_container_width=True): st.session_state['view'] = 'stats'; st.rerun()

st.divider()

# --- LOGICA PAGINE ---

if st.session_state['view'] == 'campionato':
    st.subheader("🏆 Selezione Girone")
    lista_g = list(GIRONI_SQUADRE.keys())
    st.session_state['camp_scelto'] = st.selectbox("Scegli girone:", lista_g, index=lista_g.index(st.session_state['camp_scelto']))
    if st.button("Conferma"): st.session_state['view'] = 'dashboard'; st.rerun()

elif st.session_state['view'] == 'dashboard':
    st.subheader(f"📋 {st.session_state['camp_scelto']}")
    df_p = st.session_state['players_db']
    df_f = st.session_state['fatica_db']

    if not df_p.empty:
        st.dataframe(df_p.sort_values(by="Rating", ascending=False), use_container_width=True, hide_index=True)
        
        # --- MODIFICA ---
        nomi = df_p.apply(lambda x: f"{x['Cognome']} {x['Nome']} ({x['Squadra']})", axis=1).tolist()
        mod = st.selectbox("Seleziona giocatore da modificare:", ["-- Seleziona --"] + nomi)
        if mod != "-- Seleziona --" and st.button("📝 Modifica Dati"):
            st.session_state['editing_index'] = nomi.index(mod)
            st.session_state['view'] = 'modifica'; st.rerun()

        st.divider()

        # --- REGISTRAZIONE FATICA (UNITA QUI) ---
        st.subheader("🏃 Registrazione Fatica Giornaliera")
        with st.expander("➕ Registra nuova sessione/fatica"):
            scelta = st.selectbox("Seleziona Calciatore", nomi)
            data_all = st.date_input("Data Allenamento", value=date.today())
            livello_f = st.slider("Livello Fatica", 0, 100, 50)
            nota_f = st.text_input("Nota (es. 'Assente', 'Lavoro Differenziato')")
            
            if st.button("Salva sessione"):
                idx_giocatore = nomi.index(scelta)
                nuovo_log = pd.DataFrame([[idx_giocatore, data_all, livello_f, nota_f]], 
                                         columns=["ID_Giocatore", "Data", "Fatica", "Note"])
                st.session_state['fatica_db'] = pd.concat([st.session_state['fatica_db'], nuovo_log], ignore_index=True)
                salva_tutto(st.session_state['players_db'], st.session_state['fatica_db'])
                st.success("Dati salvati nello storico!")
                st.rerun()

        # --- EXPORT / IMPORT / RESET ---
        st.divider()
        st.subheader("📥 Salva in un file")
        csv = df_p.to_csv(index=False).encode('utf-8')
        st.download_button("💾 Scarica CSV", csv, "database.csv", "text/csv", use_container_width=True)
        
        
        st.divider()
        if st.checkbox("🗑️ Abilita cancellazione totale") and st.button("🔥🔥 CANCELLA TUTTO"):
            st.session_state['players_db'] = pd.DataFrame(columns=df_p.columns)
            st.session_state['fatica_db'] = pd.DataFrame(columns=["ID_Giocatore", "Data", "Fatica", "Note"])
            salva_tutto(st.session_state['players_db'], st.session_state['fatica_db'])
            st.rerun()
    else:
        st.info("Dati cancellati")

elif st.session_state['view'] == 'aggiungi':
    st.subheader("➕ Nuovo Giocatore")
    squadre = GIRONI_SQUADRE[st.session_state['camp_scelto']]
    with st.form("add_form"):
        sq = st.selectbox("Squadra", squadre)
        ru = st.selectbox("Ruolo", ["Portiere", "Difensori", "Centrocampista", "Attaccante"])
        cog = st.text_input("Cognome")
        nom = st.text_input("Nome")
        nas = st.date_input("Nascita", value=date(2009,1,1))
        c3, c4, c5 = st.columns(3)
        pr = c3.number_input("Presenze", 0)
        mi = c4.number_input("Minuti", 0)
        gl = c5.number_input("Gol", 0)
        gi = st.number_input("Gialli", 0)
        ro = st.number_input("Rossi", 0)
        nt = st.text_area("Note")
        if st.form_submit_button("SALVA"):
            rat = calcola_rating_empirico(pr, gl, mi, nas, ru, gi, ro)
            nuovo = [sq, cog, nom, ru, nas, pr, mi, gl, 0, gi, ro, rat, nt]
            st.session_state['players_db'].loc[len(st.session_state['players_db'])] = nuovo
            salva_tutto(st.session_state['players_db'], st.session_state['fatica_db'])
            st.session_state['view'] = 'dashboard'; st.rerun()

elif st.session_state['view'] == 'modifica':
    # ... (Codice modifica invariato, assicurati che usi salva_tutto)
    idx = st.session_state['editing_index']
    gio = st.session_state['players_db'].iloc[idx]
    with st.form("edit_form"):
        # (Qui inserisci i campi del tuo form di modifica esistente)
        st.write(f"Modifica: {gio['Cognome']}")
        n_gl = st.number_input("Gol", value=int(gio['Gol']))
        if st.form_submit_button("Aggiorna"):
            st.session_state['players_db'].at[idx, 'Gol'] = n_gl
            salva_tutto(st.session_state['players_db'], st.session_state['fatica_db'])
            st.session_state['view'] = 'dashboard'; st.rerun()

elif st.session_state['view'] == 'stats':
    st.subheader("📊 Statistiche e Analisi Fatica")
    df_p = st.session_state['players_db']
    df_f = st.session_state['fatica_db']
    
    if not df_p.empty:
        col_a, col_b = st.columns(2)
        with col_a:
            st.plotly_chart(px.pie(df_p, names='Ruolo', hole=0.3, title="Ruoli"), use_container_width=True)
        with col_b:
            st.plotly_chart(px.bar(df_p, x='Cognome', y='Rating', color='Squadra', title="Rating"), use_container_width=True)
        
        st.divider()
        if not df_f.empty:
            st.write("### 📈 Trend Fatica Storica")
            # Uniamo per i nomi
            df_f['Cognome'] = df_f['ID_Giocatore'].apply(lambda x: df_p.iloc[int(x)]['Cognome'] if int(x) < len(df_p) else "N.D.")
            
            sel_gio = st.selectbox("Dettaglio giocatore:", df_p['Cognome'].unique())
            df_p_f = df_f[df_f['Cognome'] == sel_gio].sort_values("Data")
            st.plotly_chart(px.line(df_p_f, x="Data", y="Fatica", markers=True, title=f"Fatica: {sel_gio}"), use_container_width=True)
            
            st.write("### ⚖️ Carico Medio")
            media_f = df_f.groupby('Cognome')['Fatica'].mean().reset_index()
            st.plotly_chart(px.bar(media_f, x='Cognome', y='Fatica', color='Fatica', color_continuous_scale='RdYlGn_r'), use_container_width=True)
    else:
        st.info("Nessun dato per le statistiche.")
