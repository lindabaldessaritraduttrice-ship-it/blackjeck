import streamlit as st
import random
import time

st.set_page_config(page_title="Blackjack Real Deck", page_icon="🃏", layout="wide")

# --- INIZIALIZZAZIONE MAZZO E DATI ---
@st.cache_resource
def get_shared_data():
    # 104 carte (2 mazzi)
    valori_base = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11] * 4
    mazzo_completo = valori_base * 2 
    random.shuffle(mazzo_completo)
    
    return {
        "setup": False, "nomi": [], "fiches": {}, "posti": 0,
        "mazzo": mazzo_completo,
        "b_idx": 0, "s_idx": 1, "fase": "PUNTATA",
        "mano_s": [], "mano_b": [], "puntata": 0, "risultato": ""
    }

data = get_shared_data()

if "mio_nome" not in st.session_state:
    st.session_state.mio_nome = ""

# --- LOGICA MAZZO ---
def pesca_carta():
    if len(data["mazzo"]) < 10:
        valori_base = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11] * 8
        data["mazzo"] = valori_base
        random.shuffle(data["mazzo"])
    return data["mazzo"].pop()

# --- LOBBY ---
if not data["setup"]:
    st.title("🎰 Registrazione Tavolo")
    if data["posti"] == 0:
        n = st.number_input("Quanti siete?", 2, 5, 3)
        if st.button("Conferma Numero"): data["posti"] = n; st.rerun()
    else:
        st.write(f"Giocatori: {len(data['nomi'])}/{data['posti']}")
        nome = st.text_input("Tuo Nome:").strip()
        if st.button("Partecipa"):
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

    st.sidebar.title("💰 Fiches")
    for n, f in data["fiches"].items(): st.sidebar.metric(n, f"{f} 🪙")
    st.sidebar.write(f"🎴 Carte nel mazzo: {len(data['mazzo'])}")

    st.title("🃏 Blackjack Real Deck")
    st.caption(f"Giocatore: {io}")

    # FASE 1: PUNTATA
    if data["fase"] == "PUNTATA":
        st.subheader(f"Tocca a **{sfidante}** puntare")
        if io == sfidante:
            p = st.selectbox("Quanto vuoi puntare?", [1, 2, 3, 5])
            if st.button("Conferma Puntata e Ricevi Carte"):
                data["puntata"] = p
                data["mano_s"] = [pesca_carta(), pesca_carta()]
                data["mano_b"] = [pesca_carta()]
                data["fase"] = "TURNO_SFIDANTE"; st.rerun()
        else:
            st.warning(f"Attendi la puntata di {sfidante}...")

    # FASE 2: TURNO SFIDANTE (Con visione privata)
    elif data["fase"] == "TURNO_SFIDANTE":
        punti = sum(data["mano_s"])
        
        if io == sfidante:
            st.subheader(f"🃏 Le tue carte: {data['mano_s']} (Totale: {punti})")
            c1, col2 = st.columns(2)
            if punti <= 21:
                if c1.button("CHIEDI CARTA (Hit)"):
                    data["mano_s"].append(pesca_carta())
                    if sum(data["mano_s"]) > 21:
                        data["risultato"] = f"💥 {sfidante} ha sballato!"
                        data["fiches"][sfidante] -= data["puntata"]
                        data["fiches"][banco] += data["puntata"]
                        data["fase"] = "RISULTATO"
                    st.rerun()
                if col2.button("STAI (Stand)"):
                    data["fase"] = "TURNO_BANCO"; st.rerun()
            else:
                st.error("Hai sballato!")
        else:
            st.info(f"Ognuno vede solo le proprie carte. **{sfidante}** sta giocando...")
            st.write(f"Carte scoperte del Banco: {data['mano_b']}")

    # FASE 3: TURNO BANCO
    elif data["fase"] == "TURNO_BANCO":
        punti_b = sum(data["mano_b"])
        st.subheader(f"Mano Banco ({banco}): {data['mano_b']} (Totale: {punti_b})")
        if io == banco:
            if punti_b < 17:
                if st.button("Il Banco deve pescare"):
                    data["mano_b"].append(pesca_carta()); st.rerun()
            else:
                if st.button("Confronta Punteggi"):
                    ps, pb = sum(data["mano_s"]), sum(data["mano_b"])
                    if pb > 21 or ps > pb:
                        data["risultato"] = f"✅ {sfidante} vince!"
                        data["fiches"][sfidante] += data["puntata"]
                        data["fiches"][banco] -= data["puntata"]
                    elif pb > ps:
                        data["risultato"] = f"❌ {banco} vince!"
                        data["fiches"][sfidante] -= data["puntata"]
                        data["fiches"][banco] += data["puntata"]
                    else:
                        data["risultato"] = "⚖️ Pareggio!"
                    data["fase"] = "RISULTATO"; st.rerun()
        else:
            st.warning(f"Il Banco ({banco}) sta completando la mano...")

    # FASE 4: RISULTATO E CORIANDOLI
    elif data["fase"] == "RISULTATO":
        st.header(data["risultato"])
        st.write(f"Sfidante: {sum(data['mano_s'])} | Banco: {sum(data['mano_b'])}")
        
        # Controllo Bancarotta
        bancarotta = [n for n, f in data["fiches"].items() if f <= 0]
        if bancarotta:
            st.balloons()
            st.error(f"GAME OVER: {bancarotta[0]} è fuori!")
            if st.button("Nuovo Torneo"):
                data.update({"setup": False, "posti": 0, "nomi": [], "fiches": {}, "fase": "PUNTATA"})
                st.rerun()
            st.stop()
            
        if st.button("Prossima Mano"):
            data["b_idx"] = (data["b_idx"] + 1) % len(data["nomi"])
            data["s_idx"] = (data["b_idx"] + 1) % len(data["nomi"])
            data["fase"] = "PUNTATA"; st.rerun()

    time.sleep(1.5); st.rerun()
