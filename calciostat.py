import streamlit as st
import pandas as pd
from datetime import date
import os

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Scouting & Fatigue System", layout="wide")

try:
    import plotly.express as px
except ImportError:
    st.error("Aggiungi 'plotly' al file requirements.txt")

# --- COSTANTI FILE ---
DB_PLAYERS = "database_scouting.csv"
DB_FATICA = "log_fatica.csv"

# --- FUNZIONI DI PERSISTENZA ---
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

# --- INIZIALIZZAZIONE SESSION STATE ---
if 'players_db' not in st.session_state:
    st.session_state['players_db'] = carica_giocatori()
if 'fatica_db' not in st.session_state:
    st.session_state['fatica_db'] = carica_fatica()
if 'view' not in st.session_state:
    st.session_state['view'] = 'dashboard'
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

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
            # Creiamo una lista "Cognome Nome" per il selettore
            nomi_completi = df_p.apply(lambda x: f"{x['Cognome']} {x['Nome']}", axis=1).tolist()
            
            c1, c2 = st.columns([2, 1])
            with c1:
                scelta = st.selectbox("Seleziona il calciatore:", nomi_completi)
            with c2:
                data_f = st.date_input("Data sessione:", value=date.today())
            
            f_col, n_col = st.columns([2, 2])
            with f_col:
                fatica_v = st.slider("Livello Fatica (0-100):", 0, 100, 50)
            with n_col:
                nota_f = st.text_input("Note/Assenze:", placeholder="es: Lavoro differenziato")

            c_tipo = st.radio("Stato sessione:", ["Presente", "Assente"], horizontal=True)
            
            if c_tipo == "Presente":
                fatica_v = st.slider("Voto/Fatica:", 0.0, 10.0, 6.0, step=0.5)
            else:
                fatica_v = "ass" # Salviamo come stringa proprio come nel tuo Excel

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

        # 3. TABELLA FATICA (VISUALIZZAZIONE EXCEL PIVOT)
        st.subheader("📅 Tabella Presenze e Valutazioni (Stile Excel)")
        if not st.session_state['fatica_db'].empty:
            df_f = st.session_state['fatica_db'].copy()

            # Creiamo la tabella Pivot: Date sulle righe, Giocatori sulle colonne
            # fillna("") serve per lasciare vuoto dove non c'è allenamento
            pivot_df = df_f.pivot_table(
                index='Data', 
                columns='Cognome', 
                values='Fatica', 
                aggfunc='first'
            ).fillna("-")

            # Ordiniamo le date in modo che l'ultima sia sempre in alto
            pivot_df = pivot_df.sort_index(ascending=False)

            # Funzione per colorare le celle (Verde se voto alto, Rosso basso, Grigio ASS)
            def color_voti(val):
                if val == "ass":
                    return 'background-color: #d3d3d3; color: black;' # Grigio per assenti
                try:
                    voto = float(val)
                    if voto >= 7: return 'background-color: #228b22; color: white;' # Verde scuro
                    if voto >= 6: return 'background-color: #90ee90; color: black;' # Verde chiaro
                    if voto >= 5: return 'background-color: #ffffe0; color: black;' # Giallo
                    return 'background-color: #ffcccb; color: black;' # Rosso
                except:
                    return ''

            # Visualizzazione con stile applicato
            try:
                st.dataframe(
                    pivot_df.style.applymap(color_voti),
                    use_container_width=True
                )
            except:
                # Fallback se lo stile dà problemi
                st.dataframe(pivot_df, use_container_width=True)
            
            st.caption("Legenda: Verde (Ottimo), Giallo (Sufficiente), Rosso (Affaticato), Grigio (Assente)")


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

# --- STATISTICHE ---
elif st.session_state['view'] == 'stats':
    st.subheader("📊 Analisi Dati")
    if not st.session_state['fatica_db'].empty:
        st.write("### Andamento Fatica nel Tempo")
        fig = px.line(st.session_state['fatica_db'], x="Data", y="Fatica", color="Cognome", markers=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Nessun dato di fatica registrato.")
