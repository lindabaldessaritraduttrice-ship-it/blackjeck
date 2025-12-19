import streamlit as st
import random
import time

st.set_page_config(page_title="Blackjack One-Card Pro", page_icon="🃏", layout="wide")

# --- DATABASE CONDIVISO (Server-Side) ---
@st.cache_resource
def get_server_data():
    return {
        "setup_finito": False,
        "posti_totali": 0,
        "nomi": [],
        "fiches": {},
        "banco_idx": 0,
        "sfidante_idx": 1,
        "fase": "PUNTATA",
        "carta_s": 0, "carta_b": 0, "puntata": 0,
        "ultimo_risultato": "", "vincitori": []
    }

data = get_server_data()

# --- REFRESH AUTOMATICO (Trigger per il multiplayer) ---
# Ogni secondo il browser controlla se qualcuno ha fatto una mossa
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()

# --- RESET DI EMERGENZA ---
if st.sidebar.button("🔄 Reset Totale Game"):
    data.update({"setup_finito": False, "posti_totali": 0, "nomi": [], "fiches": {}, "vincitori": [], "fase": "PUNTATA"})
    st.rerun()

# --- 🏆 SCHERMATA VITTORIA (Coriandoli) ---
if data["vincitori"]:
    st.balloons()
    st.title("🎊 CAMPIONATO CONCLUSO! 🎊")
    vincitori_str = " e ".join(data["vincitori"])
    st.header(f"🏆 I vincitori assoluti sono: {vincitori_str}")
    st.subheader("Qualcuno è andato in bancarotta. Il tavolo è chiuso!")
    if st.button("Ricomincia Nuova Partita"):
        data.update({"setup_finito": False, "posti_totali": 0, "nomi": [], "fiches": {}, "vincitori": [], "fase": "PUNTATA"})
        st.rerun()
    st.stop()

# --- 🚪 LOBBY DI INGRESSO ---
if not data["setup_finito"]:
    st.title("🎲 Sala d'Attesa Blackjack")
    if data["posti_totali"] == 0:
        n = st.number_input("In quanti giocate al tavolo?", 2, 8, 3)
        if st.button("Apri Tavolo"):
            data["posti_totali"] = int(n)
            st.rerun()
    else:
        st.write(f"👥 Posti occupati: {len(data['nomi'])} / {data['posti_totali']}")
        nome_utente = st.text_input("Inserisci il tuo nome per entrare:").strip()
        if st.button("Siediti al tavolo"):
            if nome_utente and nome_utente not in data["nomi"]:
                data["nomi"].append(nome_utente)
                data["fiches"][nome_utente] = 21
                if len(data["nomi"]) == data["posti_totali"]:
                    data["setup_finito"] = True
                st.rerun()
            else:
                st.error("Nome non valido o già preso!")
    time.sleep(1)
    st.rerun()

# --- 🃏 TAVOLO DA GIOCO ---
else:
    # Controllo Bancarotta (Trigger Fine Gioco)
    for n, f in data["fiches"].items():
        if f <= 0:
            data["vincitori"] = [g for g, fiches in data["fiches"].items() if fiches > 0]
            st.rerun()

    # Definizione Ruoli (Rotazione)
    nome_banco = data["nomi"][data["banco_idx"] % len(data["nomi"])]
    nome_sfidante = data["nomi"][data["sfidante_idx"] % len(data["nomi"])]
    
    # Barra laterale fiches
    st.sidebar.title("💰 Portafogli")
    for n, f in data["fiches"].items():
        st.sidebar.metric(n, f"{f} 🪙")

    st.title("🎰 Blackjack: Sfida Secca")
    st.info(f"👑 Banco: **{nome_banco}** | ⚔️ Sfidante: **{nome_sfidante}**")

    # --- FASE 1: PUNTATA (Solo Sfidante) ---
    if data["fase"] == "PUNTATA":
        st.subheader(f"Tocca a {nome_sfidante}: Quanto punti contro {nome_banco}?")
        p = st.selectbox("Scegli puntata:", [1, 2, 3, 5])
        if st.button("CONFERMA E GIRA"):
            data["puntata"] = p
            data["carta_s"] = random.randint(1, 11)
            # Controllo Asso Sfidante
            if data["carta_s"] == 1 or data["carta_s"] == 11:
                data["fase"] = "ASSO_S"
            else:
                data["fase"] = "TURNO_BANCO"
            st.rerun()

    # --- FASE ASSE SFIDANTE ---
    elif data["fase"] == "ASSO_S":
        st.warning(f"🃏 {nome_sfidante}, hai un Asso! Scegli il valore:")
        c1, c2 = st.columns(2)
        if c1.button("Vale 1"): data["carta_s"] = 1; data["fase"] = "TURNO_BANCO"; st.rerun()
        if c2.button("Vale 11"): data["carta_s"] = 11; data["fase"] = "TURNO_BANCO"; st.rerun()

    # --- FASE 2: RISPOSTA BANCO ---
    elif data["fase"] == "TURNO_BANCO":
        st.write(f"🎴 Carta di {nome_sfidante}: **{data['carta_s']}**")
        if st.button(f"Gira carta del Banco ({nome_banco})"):
            data["carta_b"] = random.randint(1, 11)
            # Controllo Asso Banco
            if data["carta_b"] == 1 or data["carta_b"] == 11:
                data["fase"] = "ASSO_B"
            else:
                data["fase"] = "CALCOLO"
            st.rerun()

    # --- FASE ASSE BANCO ---
    elif data["fase"] == "ASSO_B":
        st.warning(f"👑 {nome_banco} (Banco), hai un Asso! Scegli:")
        c1, c2 = st.columns(2)
        if c1.button("Vale 1 (Banco)"): data["carta_b"] = 1; data["fase"] = "CALCOLO"; st.rerun()
        if c2.button("Vale 11 (Banco)"): data["carta_b"] = 11; data["fase"] = "CALCOLO"; st.rerun()

    # --- FASE 3: CALCOLO E RISULTATO ---
    elif data["fase"] == "CALCOLO":
        cs, cb = data["carta_s"], data["carta_b"]
        st.write(f"📊 Risultato: **{nome_sfidante} ({cs})** vs **{nome_banco} ({cb})**")
        
        if cs > cb:
            data["ultimo_risultato"] = f"🏆 {nome_sfidante} vince {data['puntata']} fiches!"
            data["fiches"][nome_sfidante] += data["puntata"]
            data["fiches"][nome_banco] -= data["puntata"]
        elif cb > cs:
            data["ultimo_risultato"] = f"👑 Il Banco ({nome_banco}) vince!"
            data["fiches"][nome_sfidante] -= data["puntata"]
            data["fiches"][nome_banco] += data["puntata"]
        else:
            data["ultimo_risultato"] = "⚖️ Pareggio! Nessuno perde nulla."
        
        data["fase"] = "RISULTATO"
        st.rerun()

    elif data["fase"] == "RISULTATO":
        st.success(data["ultimo_risultato"])
        if st.button("Passa al Prossimo Turno ➡️"):
            # Rotazione: lo sfidante attuale diventa il banco, il prossimo della lista sfida
            data["banco_idx"] = data["sfidante_idx"]
            data["sfidante_idx"] = (data["sfidante_idx"] + 1) % len(data["nomi"])
            data["fase"] = "PUNTATA"
            st.rerun()

    # Sincronizzazione visiva (Trigger)
    time.sleep(1.5)
    st.rerun()
