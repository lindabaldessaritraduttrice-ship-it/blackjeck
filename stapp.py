import streamlit as st
import random

st.set_page_config(page_title="Blackjack Party", page_icon="🍻")

# --- CONFIGURAZIONE INIZIALE ---
if 'giocatori' not in st.session_state:
    # Qui puoi aggiungere i nomi dei tuoi amici!
    st.session_state.nomi = ["Giocatore 1", "Giocatore 2", "Giocatore 3"]
    st.session_state.fiches = {nome: 21 for nome in st.session_state.nomi}
    st.session_state.mazziere_idx = 0
    st.session_state.turno_idx = 1 # Inizia il primo giocatore dopo il banco
    st.session_state.fase = "PUNTATA"
    st.session_state.puntate = {}

def get_mazziere():
    return st.session_state.nomi[st.session_state.mazziere_idx]

def get_giocatore_corrente():
    idx = st.session_state.turno_idx % len(st.session_state.nomi)
    return st.session_state.nomi[idx]

st.title("🃏 Blackjack Party: Turno al Banco!")
st.sidebar.title("💰 Classifica Fiches")
for nome, f in st.session_state.fiches.items():
    st.sidebar.write(f"{nome}: {f} 🪙")

mazziere = get_mazziere()
giocatore = get_giocatore_corrente()

st.info(f"👑 Il Banco oggi è: **{mazziere}**")

# --- FASE 1: PUNTATA ---
if st.session_state.fase == "PUNTATA":
    if giocatore == mazziere: # Se il turno torna al mazziere, la sfida è finita
        st.session_state.mazziere_idx = (st.session_state.mazziere_idx + 1) % len(st.session_state.nomi)
        st.session_state.turno_idx = (st.session_state.mazziere_idx + 1)
        st.write("🔄 Il giro è finito! Il ruolo di Banco passa al prossimo.")
        if st.button("Inizia Nuovo Giro"): st.rerun()
    else:
        st.subheader(f"Tocca a **{giocatore}**: Quanto punti contro {mazziere}?")
        col1, col2, col3 = st.columns(3)
        if col1.button("1 🪙"): st.session_state.puntata = 1; st.session_state.fase = "GIOCO"
        if col2.button("2 🪙"): st.session_state.puntata = 2; st.session_state.fase = "GIOCO"
        if col3.button("3 🪙"): st.session_state.puntata = 3; st.session_state.fase = "GIOCO"
        if st.session_state.fase == "GIOCO": st.rerun()

# --- FASE 2: GIOCO (1 CARTA) ---
elif st.session_state.fase == "GIOCO":
    st.write(f"🔥 **{giocatore}** vs **{mazziere}** (Puntata: {st.session_state.puntata})")
    
    if st.button("SCOPRI LE CARTE 🃏"):
        valori = [2,3,4,5,6,7,8,9,10,10,10,10,11]
        carta_g = random.choice(valori)
        carta_b = random.choice(valori)
        
        st.write(f"Tua carta: **{carta_g}**")
        st.write(f"Carta del Banco: **{carta_b}**")
        
        if carta_g > carta_b:
            st.success(f"{giocatore} VINCE!")
            st.session_state.fiches[giocatore] += st.session_state.puntata
            st.session_state.fiches[mazziere] -= st.session_state.puntata
        elif carta_g < carta_b:
            st.error(f"{mazziere} VINCE!")
            st.session_state.fiches[giocatore] -= st.session_state.puntata
            st.session_state.fiches[mazziere] += st.session_state.puntata
        else:
            st.warning("PAREGGIO!")
            
        st.session_state.fase = "PROSSIMO"
        st.rerun()

# --- FASE 3: PASSA TURNO ---
elif st.session_state.fase == "PROSSIMO":
    if st.button(f"Passa il turno al prossimo giocatore"):
        st.session_state.turno_idx += 1
        st.session_state.fase = "PUNTATA"
        st.rerun()