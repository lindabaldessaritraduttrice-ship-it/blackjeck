import streamlit as st
import random
import time

# Configurazione veloce
st.set_page_config(page_title="Blackjack Live", page_icon="🃏", layout="wide")

# --- DATABASE CONDIVISO (Mazzo 104 carte e Fiches) ---
@st.cache_resource
def get_shared_data():
    valori = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11] * 8 
    mazzo = valori[:]
    random.shuffle(mazzo)
    return {
        "setup": False, "nomi": [], "fiches": {}, "posti": 0,
        "mazzo": mazzo, "b_idx": 0, "s_idx": 1, "fase": "PUNTATA",
        "mano_s": [], "mano_b": [], "puntata": 0, "risultato": ""
    }

data = get_shared_data()

# Identità locale
if "mio_nome" not in st.session_state:
    st.session_state.mio_nome = ""

def pesca():
    if len(data["mazzo"]) < 5:
        data["mazzo"] = ([2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11] * 8)
        random.shuffle(data["mazzo"])
    return data["mazzo"].pop()

# --- LOBBY ---
if not data["setup"]:
    st.title("🎰 Lobby Blackjack")
    if data["posti"] == 0:
        n = st.number_input("Quanti giocatori?", 2, 5, 3)
        if st.button("Conferma Numero"): 
            data["posti"] = n
            st.rerun()
    else:
        st.write(f"Giocatori registrati: {len(data['nomi'])}/{data['posti']}")
        nome = st.text_input("Tuo Nome:").strip()
        if st.button("Entra"):
            if nome and nome not in data["nomi"]:
                st.session_state.mio_nome = nome
                data["nomi"].append(nome)
                data["fiches"][nome] = 21
                if len(data["nomi"]) == data["posti"]: data["setup"] = True
                st.rerun()
    time.sleep(1)
    st.rerun()

# --- GIOCO ATTIVO ---
else:
    banco = data["nomi"][data["b_idx"] % len(data["nomi"])]
    sfidante = data["nomi"][data["s_idx"] % len(data["nomi"])]
    io = st.session_state.mio_nome

    st.sidebar.title("💰 Saldi")
    for n, f in data["fiches"].items(): st.sidebar.metric(n, f"{f} 🪙")
    
    st.title("🃏 Blackjack Real Rules")

    # --- FASE 1: PUNTATA ---
    if data["fase"] == "PUNTATA":
        st.subheader(f"Tocca a **{sfidante}** puntare contro **{banco}**")
        if io == sfidante:
            c1, c2, c3, c4 = st.columns(4)
            if c1.button("Punta 1"): data["puntata"] = 1; data["mano_s"] = [pesca()]; data["fase"] = "TURNO_S"; st.rerun()
            if c2.button("Punta 2"): data["puntata"] = 2; data["mano_s"] = [pesca()]; data["fase"] = "TURNO_S"; st.rerun()
            if c3.button("Punta 3"): data["puntata"] = 3; data["mano_s"] = [pesca()]; data["fase"] = "TURNO_S"; st.rerun()
            if c4.button("Punta 5"): data["puntata"] = 5; data["mano_s"] = [pesca()]; data["fase"] = "TURNO_S"; st.rerun()
        else:
            st.info(f"⏳ In attesa della puntata di {sfidante}...")

    # --- FASE 2: TURNO SFIDANTE ---
    elif data["fase"] == "TURNO_S":
        punti = sum(data["mano_s"])
        st.subheader(f"Mano di {sfidante}: {data['mano_s']} (Totale: **{punti}**)")
        if io == sfidante:
            if punti > 21:
                st.error("💥 HAI SBALLATO!")
                if st.button("Fine Turno"):
                    data["fiches"][sfidante] -= data["puntata"]
                    data["fiches"][banco] += data["puntata"]
                    data["risultato"] = "SBALLATO"; data["fase"] = "RISULTATO"; st.rerun()
            else:
                col1, col2 = st.columns(2)
                if col1.button("➕ CHIEDI CARTA"): data["mano_s"].append(pesca()); st.rerun()
                if col2.button("✋ STAI"): data["mano_b"] = [pesca()]; data["fase"] = "TURNO_B"; st.rerun()
        else:
            st.info(f"⏳ {sfidante} sta decidendo...")

    # --- FASE 3: TURNO BANCO ---
    elif data["fase"] == "TURNO_B":
        punti_b = sum(data["mano_b"])
        st.subheader(f"Mano Banco ({banco}): {data['mano_b']} (Totale: **{punti_b}**)")
        if io == banco:
            col1, col2 = st.columns(2)
            if punti_b <= 21:
                if col1.button("➕ Pesca"): data["mano_b"].append(pesca()); st.rerun()
                if col2.button("✋ Confronta"): data["fase"] = "CALCOLO"; st.rerun()
            else:
                if st.button("Vedi Risultato"): data["fase"] = "CALCOLO"; st.rerun()
        else:
            st.warning(f"⏳ Il Banco ({banco}) sta giocando...")

    # --- FASE 4: CALCOLO ---
    elif data["fase"] == "CALCOLO":
        ps, pb = sum(data["mano_s"]), sum(data["mano_b"])
        if pb > 21 or ps > pb:
            data["risultato"] = f"🏆 {sfidante} VINCE {data['puntata']}!"
            data["fiches"][sfidante] += data["puntata"]
            data["fiches"][banco] -= data["puntata"]
        elif pb > ps:
            data["risultato"] = f"💀 {banco} VINCE!"
            data["fiches"][sfidante] -= data["puntata"]
            data["fiches"][banco] += data["puntata"]
        else:
            data["risultato"] = "⚖️ PAREGGIO!"
        data["fase"] = "RISULTATO"; st.rerun()

    # --- FASE 5: RISULTATO ---
    elif data["fase"] == "RISULTATO":
        st.header(data["risultato"])
        if any(f <= 0 for f in data["fiches"].values()):
            st.balloons()
            st.error("🎰 BANCAROTTA!")
            if st.button("Reset Totale"): 
                data.update({"setup": False, "posti": 0, "nomi": [], "fiches": {}, "fase": "PUNTATA"})
                st.rerun()
        if st.button("Prossima Mano ➡️"):
            data["b_idx"] = (data["b_idx"] + 1) % len(data["nomi"])
            data["s_idx"] = (data["b_idx"] + 1) % len(data["nomi"])
            data["mano_s"], data["mano_b"] = [], []
            data["fase"] = "PUNTATA"; data["risultato"] = ""; st.rerun()

    # REFRESH OGNI SECONDO
    time.sleep(1)
    st.rerun()
