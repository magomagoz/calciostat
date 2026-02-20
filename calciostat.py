import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Scout IamCalcio", layout="wide")
st.title("⚽ Estrattore Rosa - Accademia Real Tuscolano")

st.info("I siti come IamCalcio bloccano l'accesso diretto. Segui questi passaggi:")
st.markdown("""
1. Apri [questa pagina](https://roma.iamcalcio.it/social/squadre/7686/accademia-real-tuscolano/rosa.html) su Safari.
2. Seleziona con il dito tutta la tabella dei giocatori.
3. Torna qui e **Incolla** tutto nel box sotto.
""")

# Box per incollare i dati
testo_incollato = st.text_area("Incolla qui la rosa copiata:", height=300)

if st.button("🛠️ Genera Tabella Pulita"):
    if testo_incollato:
        try:
            # Pulizia: IamCalcio spesso mette molti spazi o invii tra nome e ruolo
            linee = [l.strip() for l in testo_incollato.split('\n') if l.strip()]
            
            # Proviamo a ricostruire la tabella (Nome, Ruolo, Anno, ecc.)
            # IamCalcio di solito mette i dati in sequenza
            giocatori = []
            # Esempio di raggruppamento ogni 4-5 elementi se sono incollate in colonna singola
            # Oppure lettura diretta se è rimasto il formato tabella
            
            df = pd.read_csv(io.StringIO(testo_incollato), sep='\t', header=None)
            if len(df.columns) < 2:
                 # Se il copia-incolla è andato a capo per ogni cella
                 st.warning("I dati sembrano incollati riga per riga. Sto provando a riordinarli...")
                 # Qui puoi aggiungere logica extra se vedi che i dati sono tutti in fila
            
            st.success("Tabella generata!")
            st.dataframe(df, use_container_width=True)
            
            # Export Excel per il tuo scouting
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Scarica Excel (CSV)", csv, "rosa_tuscolano.csv", "text/csv")
            
        except Exception as e:
            st.error(f"Errore nella lettura: {e}")
    else:
        st.warning("Copia e incolla i dati prima di premere il tasto.")

