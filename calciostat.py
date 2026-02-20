import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Scout U17 Roma - Manuel Mode", layout="wide")
st.title("⚽ Scout U17: Trasformatore Tabelle")

st.markdown("""
### 📝 Istruzioni per iPad:
1. Apri **Safari** sulla pagina della Gazzetta Regionale.
2. Seleziona con il dito tutta la tabella (nomi squadre e punti).
3. Torna qui e **incolla** nel box sotto.
""")

# Box di testo gigante per incollare i dati
raw_data = st.text_area("Incolla qui i dati della tabella:", height=300, placeholder="Pos Squadra G V N P...")

if st.button("🚀 Elabora e Pulisci Dati"):
    if raw_data:
        try:
            # Usiamo io.StringIO per far leggere a pandas il testo come se fosse un file
            # sep=None con engine='python' capisce da solo se sono tabulazioni o spazi
            df = pd.read_csv(io.StringIO(raw_data), sep='\t', header=None)
            
            if len(df.columns) < 2: # Se il tab non ha funzionato, proviamo con gli spazi
                df = pd.read_csv(io.StringIO(raw_data), sep=r'\s{2,}', engine='python', header=None)

            st.success("Dati elaborati correttamente!")
            st.dataframe(df, use_container_width=True)

            # Preparazione download
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Scarica Tabella Pulita (CSV)", csv, "classifica_scout.csv", "text/csv")
            
        except Exception as e:
            st.error(f"Errore durante l'elaborazione: {e}")
            st.info("Prova a selezionare la tabella in modo diverso o a includere l'intestazione.")
    else:
        st.warning("Il box è vuoto! Incolla qualcosa prima.")
