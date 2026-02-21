import streamlit as st
import pandas as pd
from datetime import date
import os

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

# --- COSTANTI FILE ---
DB_PLAYERS = "database_scouting.csv"
DB_FATICA = "log_fatica.csv"

# --- FUNZIONI DI PERSISTENZA ---
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

def carica_giocatori():
    if os.path.exists(DB_PLAYERS):
        df = pd.read_csv(DB_PLAYERS)
        if 'Data di nascita' in df.columns:
            df['Data di nascita'] = pd.to_datetime(df['Data di nascita']).dt.date
        return df
    return pd.DataFrame(columns=["Squadra", "Cognome", "Nome", "Ruolo", "Data di nascita", "Presenze", "Minutaggio", "Gol", "Gialli", "Rossi", "Rating", "Note"])

def carica_fatica():
    if os.path.exists(DB_FATICA):
        df = pd.read_csv(DB_FATICA)
        df['Data'] = pd.to_datetime(df['Data']).dt.date
        return df
    return pd.DataFrame(columns=["ID_Giocatore", "Cognome", "Data", "Fatica", "Note"])

def salva_giocatori(df):
    df.to_csv(DB_PLAYERS, index=False)

def salva_fatica(df):
    df.to_csv(DB_FATICA, index=False)

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

# --- INIZIALIZZAZIONE SESSION STATE ---
if 'players_db' not in st.session_state:
    st.session_state['players_db'] = carica_giocatori()
if 'fatica_db' not in st.session_state:
    st.session_state['fatica_db'] = carica_fatica()
if 'view' not in st.session_state:
    st.session_state['view'] = 'dashboard'
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'skip_upload' not in st.session_state:
    st.session_state['skip_upload'] = False

if 'view' not in st.session_state: st.session_state['view'] = 'dashboard'
if 'camp_scelto' not in st.session_state: st.session_state['camp_scelto'] = list(GIRONI_SQUADRE.keys())[0]
if 'editing_index' not in st.session_state: st.session_state['editing_index'] = None

# --- LOGIN ---
if not st.session_state['logged_in']:
    st.title("🔐 Login Scouting")
    u = st.text_input("User")
    p = st.text_input("Pass", type="password")
    if st.button("Entra"):
        if u == "Marco" and p == "Scout2026":
            st.session_state['logged_in'] = True
            st.rerun()
    st.stop()

# --- SCHERMATA INIZIALE CARICAMENTO (DOPO LOGIN) ---
if st.session_state['players_db'].empty and not st.session_state.get('setup_done'):
    st.title("🚀 Configurazione Iniziale")
    st.info("Benvenuto! Carica i file CSV per riprendere il lavoro o clicca 'Inizia' per un nuovo DB.")
    
    col_a, col_b = st.columns(2)
    with col_a:
        up_p = st.file_uploader("Carica Lista Giocatori (CSV)", type="csv")
        if up_p:
            st.session_state['players_db'] = pd.read_csv(up_p)
            salva_giocatori(st.session_state['players_db'])
            st.success("Giocatori caricati!")
            
    with col_b:
        up_f = st.file_uploader("Carica Storico Fatica (CSV)", type="csv")
        if up_f:
            st.session_state['fatica_db'] = pd.read_csv(up_f)
            salva_fatica(st.session_state['fatica_db'])
            st.success("Storico fatica caricato!")

    if st.button("Vai alla Dashboard / Inizia da zero", use_container_width=True):
        st.session_state['setup_done'] = True
        st.rerun()
    st.stop()

# --- NAVBAR ---
c1, c2, c3, c4 = st.columns(4)
with c1:
    if st.button("🏆 Campionato", use_container_width=True): st.session_state['view'] = 'campionato'; st.rerun()
with c2:
    if st.button("➕ Aggiungi", use_container_width=True): st.session_state['view'] = 'aggiungi'; st.rerun()
with c3:
    if st.button("📋 Elenco/Fatica", use_container_width=True): st.session_state['view'] = 'dashboard'; st.rerun()
with c4:
    if st.button("📊 Statistiche", use_container_width=True): st.session_state['view'] = 'stats'; st.rerun()

st.divider()

# --- LOGICA PAGINE ---

if st.session_state['view'] == 'aggiungi':
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
            salva_giocatori(st.session_state['players_db'])
            st.session_state['view'] = 'dashboard'; st.rerun()

# --- LOGICA DASHBOARD AGGIORNATA ---
if st.session_state['view'] == 'dashboard':
    st.subheader(f"📋 Gestione Database - {st.session_state.get('camp_scelto', 'U17')}")
    
    # 1. TABELLA GIOCATORI
    if not st.session_state['players_db'].empty:
        st.write("### 👥 Elenco Anagrafica Giocatori")
        st.dataframe(
            st.session_state['players_db'].sort_values(by="Rating", ascending=False), 
            use_container_width=True, 
            hide_index=True
        )
        
        st.divider()

        # 2. MODULO NUOVA FATICA
        st.subheader("🏃 Inserimento Sessione Fatica")
        with st.container():
            df_p = st.session_state['players_db']
            nomi_completi = df_p.apply(lambda x: f"{x['Cognome']} {x['Nome']}", axis=1).tolist()
            
            c1, c2 = st.columns([2, 1])
            with c1:
                scelta = st.selectbox("Seleziona il calciatore:", nomi_completi)
            with c2:
                data_f = st.date_input("Data sessione:", value=date.today())
            
            c_tipo = st.radio("Stato sessione:", ["Presente", "Assente"], horizontal=True)
            
            if c_tipo == "Presente":
                fatica_v = st.slider("Voto/Fatica (0-10):", 0.0, 10.0, 6.0, step=0.5)
            else:
                fatica_v = "ass" 

            nota_f = st.text_input("Note aggiuntive:", placeholder="es: Lavoro differenziato")

            if st.button("💾 REGISTRA VALORE FATICA", use_container_width=True):
                nuova_riga = pd.DataFrame({
                    "ID_Giocatore": [nomi_completi.index(scelta)],
                    "Cognome": [scelta.split()[0]],
                    "Nome": [scelta.split()[1] if len(scelta.split()) > 1 else ""],
                    "Data": [data_f],
                    "Fatica": [fatica_v],
                    "Note": [nota_f]
                })
                st.session_state['fatica_db'] = pd.concat([st.session_state['fatica_db'], nuova_riga], ignore_index=True)
                salva_fatica(st.session_state['fatica_db'])
                st.success(f"Dato registrato per {scelta}!")
                st.rerun()

        st.divider()

        # 3. TABELLA FATICA (STILE EXCEL CON MEDIA FINALE)
        st.subheader("📅 Tabella Presenze e Valutazioni (Stile Excel)")
        if not st.session_state['fatica_db'].empty:
            df_f = st.session_state['fatica_db'].copy()

            # Creiamo la tabella Pivot
            pivot_df = df_f.pivot_table(
                index='Data', 
                columns='Cognome', 
                values='Fatica', 
                aggfunc='first'
            )

            # Calcoliamo la media per ogni colonna (ignorando "ass")
            def calcola_media(colonna):
                numerici = pd.to_numeric(colonna, errors='coerce').dropna()
                return numerici.mean() if not numerici.empty else 0

            medie = pivot_df.apply(calcola_media)
            
            # Aggiungiamo la riga MEDIA in fondo
            pivot_df.loc['--- MEDIA ---'] = medie
            
            # Riordiniamo: Media in alto (o in basso), qui la mettiamo in alto per comodità
            pivot_df = pivot_df.fillna("-")

            # Funzione colore (aggiornata per gestire la riga media)
            # Funzione di colore aggiornata per ignorare la riga media e gli assenti
            def color_voti_safe(val):
                if val == "ass" or val == "-" or val == "":
                    return 'color: #777777;'
                try:
                    voto = float(val)
                    if voto >= 7: return 'background-color: #228b22; color: white;'
                    if voto >= 6: return 'background-color: #90ee90; color: black;'
                    if voto >= 5: return 'background-color: #ffffe0; color: black;'
                    return 'background-color: #ffcccb; color: black;'
                except:
                    return ''
            
            # Visualizzazione sicura
            st.dataframe(pivot_df.style.apply(lambda x: [color_voti_safe(v) for v in x], axis=None).format(precision=1), use_container_width=True)

        # 4. TASTI ESPORTAZIONE (A FIANCO)
        st.divider()
        st.subheader("📥 Esporta Dati in CSV")
        col_ex1, col_ex2 = st.columns(2)
        
        with col_ex1:
            csv_p = st.session_state['players_db'].to_csv(index=False).encode('utf-8')
            st.download_button("📥 Scarica Lista Giocatori", csv_p, "giocatori.csv", "text/csv", use_container_width=True)
            
        with col_ex2:
            csv_f = st.session_state['fatica_db'].to_csv(index=False).encode('utf-8')
            st.download_button("📥 Scarica Registro Fatica", csv_f, "storico_fatica.csv", "text/csv", use_container_width=True)

    else:
        st.info("Il database giocatori è vuoto. Aggiungi un calciatore per iniziare.")

elif st.session_state['view'] == 'stats':
    st.subheader("📊 Analisi Carichi di Lavoro")
    
    if not st.session_state['fatica_db'].empty:
        df_stats = st.session_state['fatica_db'].copy()
        df_stats['Data'] = pd.to_datetime(df_stats['Data']).dt.date
        
        # --- FILTRO DATE ---
        st.write("### 📅 Seleziona Periodo")
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            data_inizio = st.date_input("Dalla data:", df_stats['Data'].min())
        with col_d2:
            data_fine = st.date_input("Alla data:", date.today())
        
        # Filtraggio del dataframe
        mask = (df_stats['Data'] >= data_inizio) & (df_stats['Data'] <= data_fine)
        df_filtrato = df_stats.loc[mask].copy()
        
        if not df_filtrato.empty:
            # Calcolo medie nel periodo selezionato
            # All'interno di elif st.session_state['view'] == 'stats':
            df_filtrato['Voto_Num'] = pd.to_numeric(df_filtrato['Fatica'], errors='coerce')
            # Rimuovi le righe senza voto numerico prima di calcolare la classifica
            medie_periodo = df_filtrato.dropna(subset=['Voto_Num']).groupby('Cognome')['Voto_Num'].mean().reset_index()
            medie_periodo.columns = ['Giocatore', 'Media Voto nel Periodo']
            
            # Visualizzazione Risultati
            c_graf, c_tab = st.columns([2, 1])
            
            with c_graf:
                st.write(f"**Andamento dal {data_inizio} al {data_fine}**")
                fig = px.line(df_filtrato.dropna(subset=['Voto_Num']), 
                             x="Data", y="Voto_Num", color="Cognome", markers=True,
                             labels={"Voto_Num": "Valutazione Fatica"})
                st.plotly_chart(fig, use_container_width=True)
            
            with c_tab:
                st.write("**Classifica Medie**")
                st.dataframe(medie_periodo.style.background_gradient(cmap='RdYlGn', subset=['Media Voto nel Periodo']), 
                             hide_index=True, use_container_width=True)
                
            # Numero allenamenti fatti nel periodo
            st.info(f"💡 In questo periodo sono state registrate {df_filtrato['Data'].nunique()} sessioni di allenamento.")
        else:
            st.warning("Nessun dato trovato per il periodo selezionato.")
    else:
        st.info("Registra dei dati nella Dashboard per vedere le statistiche.")
