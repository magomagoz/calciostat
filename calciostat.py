import streamlit as st
import pandas as pd
from datetime import date

# --- CONFIGURAZIONE ---
# Nota: st.set_page_config deve essere la PRIMA istruzione Streamlit assoluta
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

DB_FILE = "database_scouting.csv"

# --- FUNZIONI CORE ---
DB_PLAYERS = "database_scouting.csv"
DB_FATICA = "log_fatica.csv"

def carica_dati_relazionali():
    # Carica Giocatori
    try:
        df_p = pd.read_csv(DB_PLAYERS)
    except:
        df_p = pd.DataFrame(columns=["ID", "Squadra", "Cognome", "Nome", "Ruolo", "Rating"])
    
    # Carica Log Fatica
    try:
        df_f = pd.read_csv(DB_FATICA)
        df_f['Data'] = pd.to_datetime(df_f['Data']).dt.date
    except:
        df_f = pd.DataFrame(columns=["ID_Giocatore", "Data", "Fatica", "Note"])
    
    return df_p, df_f

def salva_tutto(df_p, df_f):
    df_p.to_csv(DB_PLAYERS, index=False)
    df_f.to_csv(DB_FATICA, index=False)

def carica_dati():
    try:
        df = pd.read_csv(DB_FILE)
        df['Data di nascita'] = pd.to_datetime(df['Data di nascita']).dt.date
        return df
    except:
        cols = ["Squadra", "Cognome", "Nome", "Ruolo", "Data di nascita", "Presenze", "Minutaggio", "Gol", "Fatica", "Gialli", "Rossi", "Rating", "Note"]
        return pd.DataFrame(columns=cols)

def salva_dati(df):
    df.to_csv(DB_FILE, index=False)

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
if 'players_db' not in st.session_state or 'fatica_db' not in st.session_state:
    p, f = carica_dati_relazionali()
    st.session_state['players_db'] = p
    st.session_state['fatica_db'] = f
if 'view' not in st.session_state:
    st.session_state['view'] = 'dashboard'
if 'camp_scelto' not in st.session_state:
    st.session_state['camp_scelto'] = list(GIRONI_SQUADRE.keys())[0]
if 'editing_index' not in st.session_state:
    st.session_state['editing_index'] = None
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

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

# --- NAVBAR ---
#st.title("⚽ Scouting Intelligence System")
c1, c2, c3, c4 = st.columns(4)
with c1:
    if st.button("🏆 Campionato", use_container_width=True): st.session_state['view'] = 'campionato'; st.rerun()
with c2:
    if st.button("➕ Aggiungi calciatore", use_container_width=True): st.session_state['view'] = 'aggiungi'; st.rerun()
with c3:
    if st.button("📋 Elenco giocatori", use_container_width=True): st.session_state['view'] = 'dashboard'; st.rerun()
with c4:
    if st.button("📊 Statistiche", use_container_width=True): st.session_state['view'] = 'stats'; st.rerun()

st.divider()

# --- PAGINE ---
if st.session_state['view'] == 'campionato':
    st.subheader("🏆 Selezione Girone")
    lista_g = list(GIRONI_SQUADRE.keys())
    st.session_state['camp_scelto'] = st.selectbox("Scegli girone:", lista_g, index=lista_g.index(st.session_state['camp_scelto']))
    if st.button("Conferma"): st.session_state['view'] = 'dashboard'; st.rerun()

elif st.session_state['view'] == 'dashboard':
    st.subheader(f"📋 {st.session_state['camp_scelto']}")
    df = st.session_state['players_db']
    if not df.empty:
        st.dataframe(df.sort_values(by="Rating", ascending=False), use_container_width=True, hide_index=True)
        
        st.divider()
        nomi = df.apply(lambda x: f"{x['Cognome']} {x['Nome']} ({x['Squadra']})", axis=1).tolist()
        mod = st.selectbox("Seleziona giocatore da modificare:", ["-- Seleziona --"] + nomi)
        if mod != "-- Seleziona --":
            if st.button("📝 Modifica Dati"):
                st.session_state['editing_index'] = nomi.index(mod)
                st.session_state['view'] = 'modifica'; st.rerun()

elif st.session_state['view'] == 'dashboard':
    st.subheader("🏃 Registrazione Fatica Giornaliera")
    
    df_p = st.session_state['players_db']
    df_f = st.session_state['fatica_db']
    
    if not df_p.empty:
        with st.expander("➕ Registra nuova sessione/fatica"):
            nomi = df_p.apply(lambda x: f"{x['Cognome']} {x['Nome']}", axis=1).tolist()
            scelta = st.selectbox("Giocatore", nomi)
            data_all = st.date_input("Data Allenamento", value=date.today())
            livello_f = st.slider("Livello Fatica", 0, 100, 50)
            nota_f = st.text_input("Nota (es. 'Assente', 'Lavoro Differenziato')")
            
            if st.button("Salva sessione"):
                idx_giocatore = nomi.index(scelta)
                # Usiamo l'indice o un ID per collegare le tabelle
                nuovo_log = pd.DataFrame([[idx_giocatore, data_all, livello_f, nota_f]], 
                                         columns=["ID_Giocatore", "Data", "Fatica", "Note"])
                st.session_state['fatica_db'] = pd.concat([st.session_state['fatica_db'], nuovo_log], ignore_index=True)
                salva_tutto(st.session_state['players_db'], st.session_state['fatica_db'])
                st.success("Dati salvati nello storico!")
        
        # --- SEZIONE ESPORTA ---
        st.write("---")
        st.subheader("📥 Esporta Dati")
        
        # Convertiamo il DataFrame in CSV (formato stringa)
        csv = df.to_csv(index=False).encode('utf-8')
        
        st.download_button(
            label="💾 Salva lista giocatori",
            data=csv,
            file_name=f"scouting_{st.session_state['camp_scelto']}.csv",
            mime="text/csv",
            use_container_width=True
        )

# --- SEZIONE IMPORTA ---
st.subheader("📤 Importa Dati")
uploaded_file = st.file_uploader("Scegli un file CSV da caricare nel database", type="csv")
        
if uploaded_file is not None:
    if st.button("🚀 CARICA E UNISCI AL DATABASE"):
        try:
            # Leggiamo il file caricato
            import_df = pd.read_csv(uploaded_file)
                    
            # Uniamo i dati nuovi a quelli esistenti
            st.session_state['players_db'] = pd.concat([st.session_state['players_db'], import_df], ignore_index=True)
                    
            # Salviamo fisicamente sul file locale
            salva_dati(st.session_state['players_db'])
                    
            st.success(f"Importati correttamente {len(import_df)} giocatori!")
            st.rerun()
        except Exception as e:
            st.error(f"Errore durante il caricamento: {e}")
        
        st.divider()
        check = st.checkbox("🗑️ Abilita cancellazione totale")
        if check and st.button("🔥🔥🔥 ATTENZIONE: CANCELLA TUTTO"):
            st.session_state['players_db'] = pd.DataFrame(columns=df.columns)
            salva_dati(st.session_state['players_db'])
            st.rerun()
    else:
        st.info("DB Vuoto.")

elif st.session_state['view'] == 'aggiungi':
    st.subheader(f"➕ Nuovo elemento")
    squadre = GIRONI_SQUADRE[st.session_state['camp_scelto']]
    with st.form("add_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        sq = c1.selectbox("Squadra", squadre)
        ru = c2.selectbox("Ruolo", ["Portiere", "Difensori", "Centrocampista", "Attaccante"])
        cog = st.text_input("Cognome")
        nom = st.text_input("Nome")
        nas = st.date_input("Nascita", value=date(2009,1,1))
        
        c3, c4, c5 = st.columns(3)
        pr = c3.number_input("Presenze", 0)
        mi = c4.number_input("Minuti", 0)
        gl = c5.number_input("Gol", 0)
        
        c6, c7 = st.columns(2)
        gi = c6.number_input("Gialli", 0)
        ro = c7.number_input("Rossi", 0)
        nt = st.text_area("Note")
        
        if st.form_submit_button("SALVA"):
            rat = calcola_rating_empirico(pr, gl, mi, nas, ru, gi, ro)
            nuovo = [sq, cog, nom, ru, nas, pr, mi, gl, 0, gi, ro, rat, nt]
            st.session_state['players_db'].loc[len(st.session_state['players_db'])] = nuovo
            salva_dati(st.session_state['players_db'])
            st.session_state['view'] = 'dashboard'; st.rerun()

elif st.session_state['view'] == 'modifica':
    idx = st.session_state['editing_index']
    gio = st.session_state['players_db'].iloc[idx]
    
    st.subheader(f"📝 Modifica Scheda: {gio['Cognome']} {gio['Nome']}")
    
    if st.button("⬅️ Annulla e torna indietro"):
        st.session_state['view'] = 'dashboard'
        st.rerun()

    with st.form("edit_form_completo"):
        squadre_attuali = GIRONI_SQUADRE[st.session_state['camp_scelto']]
        
        c1, c2 = st.columns(2)
        # Cerchiamo di preselezionare la squadra corretta
        try:
            sq_idx = squadre_attuali.index(gio['Squadra'])
        except:
            sq_idx = 0
            
        nuova_sq = c1.selectbox("Squadra", squadre_attuali, index=sq_idx)
        nuovo_ru = c2.selectbox("Ruolo", ["Portiere", "Difensori", "Centrocampista", "Attaccante"], 
                                index=["Portiere", "Difensore", "Centrocampista", "Attaccante"].index(gio['Ruolo']))
        
        nuovo_cog = st.text_input("Cognome", value=gio['Cognome'])
        nuovo_nom = st.text_input("Nome", value=gio['Nome'])
        
        c3, c4, c5 = st.columns(3)
        nuovo_pr = c3.number_input("Presenze", value=int(gio['Presenze']))
        nuovo_mi = c4.number_input("Minuti", value=int(gio['Minutaggio']))
        nuovo_gl = c5.number_input("Gol", value=int(gio['Gol']))
        
        c6, c7 = st.columns(2)
        nuovo_gi = c6.number_input("Cartellini Gialli", value=int(gio['Gialli']))
        nuovo_ro = c7.number_input("Cartellini Rossi", value=int(gio['Rossi']))
        
        nuovo_nt = st.text_area("Note", value=gio['Note'])
        
        if st.form_submit_button("💾 AGGIORNA E RISALVA"):
            # Ricalcolo il rating con i nuovi dati modificati
            nuovo_rat = calcola_rating_empirico(nuovo_pr, nuovo_gl, nuovo_mi, gio['Data di nascita'], nuovo_ru, nuovo_gi, nuovo_ro)
            
            # Aggiorniamo la riga nel Database
            st.session_state['players_db'].iloc[idx] = [
                nuova_sq, nuovo_cog, nuovo_nom, nuovo_ru, gio['Data di nascita'], 
                nuovo_pr, nuovo_mi, nuovo_gl, gio['Fatica'], nuovo_gi, nuovo_ro, nuovo_rat, nuovo_nt
            ]
            
            salva_dati(st.session_state['players_db'])
            st.success("Scheda aggiornata!")
            st.session_state['view'] = 'dashboard'
            st.rerun()

elif st.session_state['view'] == 'stats':
    if not st.session_state['players_db'].empty:
        df = st.session_state['players_db']
        st.plotly_chart(px.pie(df, names='Ruolo', hole=0.3), use_container_width=True)
        st.plotly_chart(px.bar(df, x='Cognome', y='Rating', color='Squadra'), use_container_width=True)

elif st.session_state['view'] == 'stats':
    st.subheader("📊 Analisi Storica Fatica")
    df_p = st.session_state['players_db']
    df_f = st.session_state['fatica_db']
    
    if not df_f.empty:
        # Uniamo le tabelle per avere i nomi nel grafico
        df_f['Cognome'] = df_f['ID_Giocatore'].apply(lambda x: df_p.iloc[int(x)]['Cognome'])
        
        # Grafico 1: Andamento temporale (Line Chart)
        st.write("### 📈 Trend Fatica nel tempo")
        giocatore_target = st.selectbox("Seleziona Giocatore per il dettaglio", df_p['Cognome'].unique())
        df_player = df_f[df_f['Cognome'] == giocatore_target].sort_values(by="Data")
        
        fig_line = px.line(df_player, x="Data", y="Fatica", markers=True, 
                           title=f"Evoluzione Fatica: {giocatore_target}")
        st.plotly_chart(fig_line, use_container_width=True)
        
        # Grafico 2: Media Fatica Settimanale
        st.write("### ⚖️ Carico Medio Lavoro")
        media_f = df_f.groupby('Cognome')['Fatica'].mean().reset_index()
        fig_bar = px.bar(media_f, x='Cognome', y='Fatica', color='Fatica',
                         title="Media Fatica Totale (Chi è più sotto sforzo?)",
                         color_continuous_scale='RdYlGn_r')
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("Registra almeno una sessione per vedere i grafici.")
