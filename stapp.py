import streamlit as st
import random
import time

# Configurazione della pagina per evitare bug grafici
st.set_page_config(page_title="Blackjack Real Tournament", page_icon="🃏", layout="wide")

# --- INIZIALIZZAZIONE DATABASE CONDIVISO ---
# Usiamo cache_resource per far sì che tutti i giocatori vedano lo stesso mazzo e le stesse fiches
@st.cache_resource
def get_shared_data():
    # Creazione del mazzo reale: 2 mazzi da 52 carte = 104 carte
    # Valori: 2-10, J(10), Q(10), K(10), A(11)
    semi = 8 # 4 semi per mazzo * 2 mazzi
    valori_base = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11]
    mazzo_completo = valori_base * semi
    random.shuffle(mazzo_completo)
    
    return {
        "setup": False,
        "nomi": [],
        "fiches": {},
        "posti": 0,
        "mazzo": mazzo_completo,
        "b_idx": 0,       # Indice di chi fa il banco
        "s_idx": 1,       # Indice di chi sfida
        "fase": "PUNTATA",
        "mano_s": [],     # Carte dello sfidante
        "mano_b": [],     # Carte del banco
        "puntata": 0,
        "risultato": ""
    }

data = get_shared_data()

# Identità locale del giocatore (salvata nel browser di ognuno)
if "mio_nome" not in st.session_state:
    st.session_state.mio_nome = ""

# Funzione per pescare dal mazzo comune
def pesca_dal_mazzo():
    if len(data["mazzo"]) < 10:
        # Se il mazzo finisce, rimescoliamo 104 carte nuove
        nuovo_mazzo = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11] * 8
        random.shuffle(nuovo_mazzo)
        data["mazzo"] = nuovo_mazzo
    return data["mazzo"].pop()

# --- LOGICA DELLA LOBBY (Registrazione) ---
if not data["setup"]:
    st.title("🎰 Benvenuti al Tavolo di Blackjack")
    st.write("Configura il tavolo per iniziare a giocare con i tuoi amici.")
    
    if data["posti"] == 0:
        n = st.number_input("Quanti giocatori partecipano al torneo?", min_value=2, max_value=6, value=3)
        if st.button("Conferma Numero Giocatori"):
            data["posti"] = n
            st.rerun()
    else:
        st.subheader(f"Registrazione: {len(data['nomi'])} / {data['posti']}")
        nome_inserito = st.text_input("Inserisci il tuo nome unico:").strip()
        
        if st.button("Unisciti al Gioco"):
            if nome_
