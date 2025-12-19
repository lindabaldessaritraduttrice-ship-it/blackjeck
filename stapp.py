import streamlit as st
import random

st.set_page_config(page_title="Blackjack Party", page_icon="🃏")

# --- DATABASE CONDIVISO ---
if 'gioco' not in st.session_state:
    st.session_state.gioco = {
        "setup": False, 
        "nomi": [], 
        "fiches": {}, 
        "posti": 0,
        "fase": "PUNTATA",
        "banco_idx": 0,
        "sfidante_idx": 1
    }

db = st.session_state.db if 'db' in st.session_state else st.session_state.gioco

# --- CORIANDOLI E VITTORIA ---
# Se qualcuno arriva a 0 fiches, il gioco finisce per tutti
persone_a_zero = [n for n, f in db["fiches"].items() if f <= 0]
if db["setup"] and persone_a_zero:
    st.balloons()
    st.title("🎊 VITTORIA FINALE! 🎊")
    vincitori = [n for n, f in db["fiches"].items() if f > 0]
    st.header(f"🏆 Vincitori: {' e '.join(vincitori)}")
    if st.button("Nuovo Torneo"):
        st.session_state.clear()
        st.rerun()
    st.stop()

# --- LOBBY ---
if not db["setup"]:
    st.title("🎲 Lobby Blackjack")
    if db["posti"] == 0:
        n = st.number_input("In quanti giocate?", 2, 5, 3)
        if st.button("Conferma Posti"):
            db["posti"] = n
            st.rerun()
    else:
        st.write(f"Giocatori pronti: {len(db['nomi'])}/{db['posti']}")
        nome = st.text_input("Tuo Nome:").strip()
        if st.button("Entra"):
            if nome and nome not in db["nomi"]:
                db["nomi"].append(nome)
                db["fiches"][nome] = 21
                if len(db["nomi"]) == db["posti"]:
                    db["setup"] = True
                st.rerun()
else:
    # --- GIOCO A UNA CARTA CON TURNO BANCO ---
    banco = db["nomi"][db["banco_idx"] % len(db["nomi"])]
    sfidante = db["nomi"][db["sfidante_idx"] % len(db["nomi"])]
    
    st.title("🃏 Sfida a Una Carta")
    st.sidebar.write("💰 FICHES:", db["fiches"])
    st.info(f"👑 Banco: {banco} | ⚔️ Sfidante: {sfidante}")

    if db["fase"] == "PUNTATA":
        puntata = st.selectbox(f"{sfidante}, quanto punti?", [1, 2, 3, 5])
        if st.button("GIRA LE CARTE"):
            c_s = random.randint(2, 11)
            c_b = random.randint(2, 11)
            st.write(f"🎴 {sfidante}: **{c_s}** | 👑 {banco}: **{c_b}**")
            
            if c_s > c_b:
                st.success(f"VINCE {sfidante}!")
                db["fiches"][sfidante] += puntata
                db["fiches"][banco] -= puntata
            elif c_b > c_s:
                st.error(f"VINCE IL BANCO ({banco})!")
                db["fiches"][sfidante] -= puntata
                db["fiches"][banco] += puntata
            else:
                st.warning("PAREGGIO!")
            
            db["fase"] = "PROSSIMO"
            st.rerun()
            
    elif db["fase"] == "PROSSIMO":
        if st.button("Passa al prossimo turno"):
            # Il banco ruota tra i giocatori
            db["banco_idx"] = (db["banco_idx"] + 1) % len(db["nomi"])
            db["sfidante_idx"] = (db["banco_idx"] + 1) % len(db["nomi"])
            db["fase"] = "PUNTATA"
            st.rerun()
