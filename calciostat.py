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
    st.title("🔐 Login")
    u = st.text_input("User")
    p = st.text_input("Pass", type="password")
    if st.button("Entra"):
        if u == "Marco" and p == "Scout2026":
            st.session_state['logged_in'] = True
            st.rerun()
    st.stop()

# --- SCHERMATA INIZIALE CARICAMENTO (DOPO LOGIN) ---
if st.session_state['players_db'].empty and not st.session_state.get('setup_done'):
    st.title("🚀 Benvenuto Marco!")
    #st.info("Carica i file CSV per riprendere il lavoro o clicca 'Inizia' per un nuovo DB.")

    if st.button("Vai alla Dashboard oppure carica i file salvati in precedenza", use_container_width=True):
        st.session_state['setup_done'] = True
        st.rerun()
    
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

        st.stop()

# --- NAVBAR ---
c1, c2, c3, c4, c5, c6 = st.columns(6)
with c1:
    if st.button("🏆 Campionato", use_container_width=True): st.session_state['view'] = 'campionato'; st.rerun()
with c2:
    if st.button("➕ Nuovo 🏃", use_container_width=True): st.session_state['view'] = 'aggiungi'; st.rerun()
with c3:
    if st.button("📋 Elenco", use_container_width=True): st.session_state['view'] = 'dashboard'; st.rerun()
with c4:
    if st.button("📊 Statistiche", use_container_width=True): st.session_state['view'] = 'stats'; st.rerun()
with c5:
    if st.button("↩️ Torna all'inizio", use_container_width=True): 
        st.session_state['view'] = 'dashboard'
        st.rerun() 
with c6:
    if st.button("🚪 Esci", use_container_width=True): 
        st.session_state['logged_in'] = False  # Questo è il vero Logout
        st.session_state['view'] = 'dashboard' # Reset per il prossimo login
        st.rerun()    

st.divider()

# --- LOGICA PAGINE ---
if st.session_state['view'] == 'campionato':
    st.subheader("🏆 Selezione Girone")
    lista_g = list(GIRONI_SQUADRE.keys())
    st.session_state['camp_scelto'] = st.selectbox("Scegli girone:", lista_g, index=lista_g.index(st.session_state['camp_scelto']))
    if st.button("Conferma"): st.session_state['view'] = 'dashboard'; st.rerun()

if st.session_state['view'] == 'aggiungi':
    st.subheader("➕ Nuovo Calciatore")
    squadre = GIRONI_SQUADRE[st.session_state['camp_scelto']]
    with st.form("add_form"):
        sq = st.selectbox("Squadra", squadre)
        ru = st.selectbox("Ruolo", ["Portiere", "Difensore", "Centrocampista", "Attaccante"])
        cog = st.text_input("Cognome")
        nom = st.text_input("Nome")
        nas = st.date_input("Data di Nascita", value=date(2009,1,1))
        c3, c4, c5 = st.columns(3)
        pr = c3.number_input("Presenze", 0)
        mi = c4.number_input("Minuti giocati", 0)
        gl = c5.number_input("Gol fatti", 0)
        gi = st.number_input("Cartellini Gialli", 0)
        ro = st.number_input("Cartellini Rossi", 0)
        nt = st.text_area("Note")


        if st.form_submit_button("SALVA"):
            if not cog.strip():
                st.error("⚠️ Il campo 'Cognome' è obbligatorio.")
            
            else:
                # 2. Verifica se esiste già un giocatore con lo stesso Nome e Cognome nella stessa Squadra
                duplicato = st.session_state['players_db'][
                    (st.session_state['players_db']['Cognome'].str.lower() == cog.strip().lower()) & 
                    (st.session_state['players_db']['Nome'].str.lower() == nom.strip().lower()) & 
                    (st.session_state['players_db']['Squadra'] == sq)
                ]
                
                if not duplicato.empty:
                    st.warning(f"⚠️ Attenzione: {cog} {nom} è già presente nel database per la squadra {sq}.")
                else:
  
                    # Calcoliamo il rating
                    rat = calcola_rating_empirico(pr, gl, mi, nas, ru, gi, ro)
                    
                    # LA LISTA DEVE AVERE 13 ELEMENTI PER COMBACIARE CON IL DB
                    nuovo = [
                        sq,       # 1. Squadra
                        cog,      # 2. Cognome
                        nom,      # 3. Nome
                        ru,       # 4. Ruolo
                        nas,      # 5. Data di nascita
                        pr,       # 6. Presenze
                        mi,       # 7. Minutaggio
                        gl,       # 8. Gol
                        0,        # 9. Fatica (valore iniziale)
                        gi,       # 10. Gialli
                        ro,       # 11. Rossi
                        rat,      # 12. Rating
                        nt        # 13. Note
                    ]
                    
                # Inserimento nel database
                st.session_state['players_db'].loc[len(st.session_state['players_db'])] = nuovo
                salva_giocatori(st.session_state['players_db'])
                st.success(f"Calciatore {cog} salvato!")
                st.session_state['view'] = 'dashboard'
                st.rerun()
        
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
                                index=["Portiere", "Difensori", "Centrocampista", "Attaccante"].index(gio['Ruolo']))
        
        nuovo_cog = st.text_input("Cognome", value=gio['Cognome'])
        nuovo_nom = st.text_input("Nome", value=gio['Nome'])
        
        c3, c4, c5 = st.columns(3)
        nuovo_pr = c3.number_input("Presenze", value=int(gio['Presenze']))
        nuovo_mi = c4.number_input("Minuti", value=int(gio['Minutaggio']))
        nuovo_gl = c5.number_input("Gol", value=int(gio['Gol']))
        
        c6, c7 = st.columns(2)
        nuovo_gi = c6.number_input("Gialli", value=int(gio['Gialli']))
        nuovo_ro = c7.number_input("Rossi", value=int(gio['Rossi']))
        
        nuovo_nt = st.text_area("Note", value=gio['Note'])
        
        if st.form_submit_button("💾 AGGIORNA E RISALVA"):
            # Ricalcolo il rating con i nuovi dati modificati
            nuovo_rat = calcola_rating_empirico(nuovo_pr, nuovo_gl, nuovo_mi, gio['Data di nascita'], nuovo_ru, nuovo_gi, nuovo_ro)
            
            # Aggiorniamo la riga nel Database
            st.session_state['players_db'].iloc[idx] = [
                nuova_sq, nuovo_cog, nuovo_nom, nuovo_ru, gio['Data di nascita'], 
                nuovo_pr, nuovo_mi, nuovo_gl, gio['Fatica'], nuovo_gi, nuovo_ro, nuovo_rat, nuovo_nt
            ]
            
            salva_giocatori(st.session_state['players_db'])
            st.success("Scheda aggiornata!")
            st.session_state['view'] = 'dashboard'
            st.rerun()

# --- LOGICA DASHBOARD AGGIORNATA ---
if st.session_state['view'] == 'dashboard':
    st.subheader(f"📋 {st.session_state.get('camp_scelto')}")
    
    # 1. TABELLA GIOCATORI
    if not st.session_state['players_db'].empty:
        st.write("### 👥 Tabella Calciatori")
        st.dataframe(
            st.session_state['players_db'].sort_values(by="Rating", ascending=False), 
            use_container_width=True, 
            hide_index=True
        )
        # Inserisci questo pezzo subito dopo st.dataframe(...) della Tabella Giocatori
        # Usa players_db invece di df_p
        nomi = st.session_state['players_db'].apply(lambda x: f"{x['Cognome']} {x['Nome']} ({x['Squadra']})", axis=1).tolist()
        mod = st.selectbox("Seleziona calciatore da modificare:", ["-- Seleziona --"] + nomi)
        if mod != "-- Seleziona --":
            if st.button("📝 Modifica Dati"):
                st.session_state['editing_index'] = nomi.index(mod)
                st.session_state['view'] = 'modifica'
                st.rerun()
        
        check = st.checkbox("Abilita cancellazione totale")
        if check and st.button("🗑️ SVUOTA DB CALCIATORI"):
            st.session_state['players_db'] = pd.DataFrame(columns=df_p.columns)
            salva_giocatori(st.session_state['players_db'])
            st.rerun()

        st.divider()

        # 2. MODULO NUOVA FATICA
        st.subheader("🏃 Inserimento Fatica")
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
                fatica_v = st.slider("Fatica (0-10):", 0.0, 10.0, 0.0, step=0.5)
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

        # --- 3. TABELLONE FATICA ---
        st.subheader("📅 Tabellone Presenze e Valutazioni")
        if not st.session_state['fatica_db'].empty:
            df_f = st.session_state['fatica_db'].copy()
        
            # Formattazione data
            df_f['Data'] = pd.to_datetime(df_f['Data']).dt.strftime('%d/%m/%Y')
        
            # Creazione Pivot
            pivot_df = df_f.pivot_table(
                index='Cognome', 
                columns='Data', 
                values='Fatica', 
                aggfunc='first'
            ).fillna("-")
        
            # Calcolo Media
            def check_media(riga):
                numeri = pd.to_numeric(riga, errors='coerce').dropna()
                return numeri.mean() if not numeri.empty else 0
        
            pivot_df['MEDIA'] = pivot_df.apply(check_media, axis=1)
            pivot_df = pivot_df.sort_values(by='MEDIA', ascending=False)
        
            # Visualizzazione sicura
            st.dataframe(pivot_df, use_container_width=True)
        else:
            st.info("Nessun dato di fatica registrato. Inserisci una sessione sopra per vedere la tabella.")


        if st.button("🗑️ Elimina Ultima Registrazione Fatica", use_container_width=True):
            if not st.session_state['fatica_db'].empty:
                st.session_state['fatica_db'] = st.session_state['fatica_db'].iloc[:-1]
                salva_fatica(st.session_state['fatica_db'])
                st.success("Ultima riga eliminata!")
                st.rerun()

        # 4. TASTI ESPORTAZIONE (A FIANCO)
        st.divider()
        st.subheader("📥 Salvataggio Dati")
        col_ex1, col_ex2 = st.columns(2)
        
        with col_ex1:
            csv_p = st.session_state['players_db'].to_csv(index=False).encode('utf-8')
            st.download_button("📥 Salva Lista Giocatori", csv_p, "giocatori.csv", "text/csv", use_container_width=True)
            
        with col_ex2:
            csv_f = st.session_state['fatica_db'].to_csv(index=False).encode('utf-8')
            st.download_button("📥 Salva Registro Fatica", csv_f, "storico_fatica.csv", "text/csv", use_container_width=True)

    else:
        st.info("Il database giocatori è vuoto. Aggiungi un calciatore per iniziare.")

elif st.session_state['view'] == 'stats':
    st.subheader("✨ Analisi Rating AI")
    
    if not st.session_state['players_db'].empty:
        df = st.session_state['players_db']
        st.plotly_chart(px.pie(df, names='Ruolo', hole=0.3), use_container_width=True)
        st.plotly_chart(px.bar(df, x='Cognome', y='Rating', color='Squadra'), use_container_width=True)
    
    st.subheader("📊 Analisi Storica Fatica")
    df_p = st.session_state['players_db']
    df_f = st.session_state['fatica_db']
    
    if not df_f.empty:
    # Usiamo il cognome già salvato nel log fatica invece di cercarlo per indice
        pass # Il cognome è già presente nel df_stats creato dopo
    
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
            medie_periodo.columns = ['Cognome', 'Media Voto nel Periodo']
            
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
