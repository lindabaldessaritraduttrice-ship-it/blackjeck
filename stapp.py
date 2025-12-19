import streamlit as st
import random
import time

st.set_page_config(page_title="Blackjack Real Rules", page_icon="🃏", layout="wide")

# --- DATABASE CONDIVISO ---
@st.cache_resource
def get_shared_data():
    valori = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11] * 8 # 104 carte
    mazzo = valori[:]
    random.shuffle(mazzo)
    return {
        "setup": False, "nomi": [], "fiches": {}, "posti": 0,
        "mazzo": mazzo, "b_idx": 0, "s_idx": 1, "fase": "PUNTATA",
        "mano_s": [], "mano_b": [], "puntata": 0, "risultato": ""
    }

data = get_shared_data()

if "mio_nome" not in st.session_state:
    st.session_state.mio_nome = ""

def pesca():
    if len(data["mazzo"]) < 5:
        data["mazzo"] = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11] * 8
        random.shuffle(data["mazzo"])
    return data["mazzo"].pop()

# --- LOBBY ---
if not data["setup"]:
    st.title("🎰 Blackjack Lobby")
    if data["posti"] == 0:
        n = st.number_input("In quanti giocate?", 2, 5, 3)
        if st.button("Conferma"): data["posti"] = n; st.rerun()
    else:
        nome = st.text_input("Tuo Nome:").strip()
        if st.button("Entra"):
            if nome and nome not in data["nomi"]:
                st.session_state.mio_nome = nome
                data["nomi"].append(nome); data["fiches"][nome] = 21
                if len(data["nomi"]) == data["posti"]: data["setup"] = True
                st.rerun()
    time.sleep(1); st.rerun()

# --- GIOCO ---
else:
    banco = data["nomi"][data["b_idx"] % len(data["nomi"])]
    sfidante = data["nomi"][data["s_idx"] % len(data["nomi"])]
    io = st.session_state.mio_nome

    st.sidebar.title("💰 Saldi")
    for n, f in data["fiches"].items(): st.sidebar.metric(n, f"{f} 🪙")
    
    st.title("🃏 Blackjack Real Rules")

    # --- FASE 1: PUNTATA ---
    if data["fase"] == "PUNTATA":
        if io == sfidante:
            st.subheader(f"{io}, quanto vuoi puntare?")
            c1, c2, c3, c4 = st
