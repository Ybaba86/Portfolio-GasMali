import streamlit as st
import pandas as pd
from supabase import create_client, Client
from streamlit_folium import st_folium
import folium
import logging
from datetime import datetime
import bcrypt

# ==========================================
# 0. CONFIGURATION & STYLE
# ==========================================
st.set_page_config(page_title="GAS-MALI • Démo Officielle", layout="wide", page_icon="⛽")

st.markdown("""
<style>
    .block-container { padding-top: 1rem; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e2e8f0; }
    .pompiste-card { border: 1px solid #cbd5e1; padding: 15px; border-radius: 8px; margin-bottom: 10px; background: white; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. INITIALISATION DES DONNÉES (SESSION STATE)
# ==========================================
if 'db_stations' not in st.session_state:
    st.session_state.db_stations = [
        {"id": 1, "nom": "Shell Daoudabougou", "lat": 12.615, "lon": -7.992, "dispo": True, "stock": 2500},
        {"id": 2, "nom": "Total Faladié", "lat": 12.622, "lon": -7.985, "dispo": True, "stock": 850}
    ]

if 'db_queue' not in st.session_state:
    # On pré-remplit une file de test
    st.session_state.db_queue = [
        {"id": i, "plaque": f"BKO-{100+i}-AM", "tel": "74000000", "statut": "notifie" if i <= 5 else "en_attente", "station_id": 1}
        for i in range(1, 16)
    ]

# Détection Mode Prod/Démo
@st.cache_resource
def check_mode():
    try:
        return create_client(st.secrets["supabase"]["url"], st.secrets["supabase"]["key"]), False
    except: return None, True

supabase, is_demo = check_mode()

# ==========================================
# 2. LOGIQUE MÉTIER (FONCTIONS DÉMO)
# ==========================================

def call_virtual_clients(station_id, num=10):
    """Appelle 'num' clients de la file virtuelle vers la file physique."""
    count = 0
    for client in st.session_state.db_queue:
        if client['statut'] == "en_attente" and client['station_id'] == station_id:
            client['statut'] = "notifie"
            count += 1
            if count >= num: break
    return count

def serve_client(file_id, station_id, litres):
    # 1. Marquer comme servi (supprimer de la file)
    st.session_state.db_queue = [c for c in st.session_state.db_queue if c['id'] != file_id]
    # 2. Déduire le stock
    for s in st.session_state.db_stations:
        if s['id'] == station_id:
            s['stock'] -= litres
    # 3. Appel automatique du suivant pour maintenir le flux
    call_virtual_clients(station_id, num=1)

# ==========================================
# 3. INTERFACE UTILISATEUR
# ==========================================

def client_view():
    st.title("📱 Espace Citoyen")
    tab1, tab2 = st.tabs(["🗺️ Localiser & S'inscrire", "🔍 Mon Statut"])
    
    with tab1:
        m = folium.Map(location=[12.6392, -8.0029], zoom_start=13)
        for s in st.session_state.db_stations:
            folium.Marker([s['lat'], s['lon']], popup=s['nom'], icon=folium.Icon(color="green")).add_to(m)
        st_folium(m, width="100%", height=300)
        
        with st.form("inscription"):
            st.subheader("🎟️ Prendre un rang")
            st_name = st.selectbox("Station", [s['nom'] for s in st.session_state.db_stations])
            plaque = st.text_input("N° Plaque / Cadre").upper()
            tel = st.text_input("Téléphone (Ex: 70000000)")
            if st.form_submit_button("S'inscrire"):
                if plaque and tel:
                    new_id = len(st.session_state.db_queue) + 100
                    st.session_state.db_queue.append({"id": new_id, "plaque": plaque, "tel": tel, "statut": "en_attente", "station_id": 1})
                    st.success(f"✅ Inscrit ! Suivez votre progression dans l'onglet 'Mon Statut'.")
                else: st.error("Veuillez remplir tous les champs.")

    with tab2:
        st.subheader("🔍 Vérifier ma position")
        search_plaque = st.text_input("Entrez votre N° de plaque").upper()
        if search_plaque:
            # Trouver le client
            user_data = next((c for c in st.session_state.db_queue if c['plaque'] == search_plaque), None)
            if user_data:
                # Calculer la position (combien sont devant lui dans la même station)
                pos = [c['id'] for c in st.session_state.db_queue if c['station_id'] == user_data['station_id']].index(user_data['id'])
                
                col1, col2 = st.columns(2)
                col1.metric("Statut", user_data['statut'].replace('_', ' ').capitalize())
                col2.metric("Position estimée", pos if pos > 0 else "C'est votre tour !")
                
                if user_data['statut'] == "notifie":
                    st.balloons()
                    st.success("🔔 VOTRE TOUR ! Présentez-vous à la station maintenant.")
                else:
                    st.info("ℹ️ Veuillez rester à l'écoute. Un SMS vous sera envoyé dès que vous devrez vous déplacer.")
            else:
                st.warning("⚠️ Aucune inscription active trouvée pour cette plaque.")

def pompiste_view():
    st.title("🧑‍💼 Interface Pompiste")
    
    # Métriques
    physique = [c for c in st.session_state.db_queue if c['statut'] == "notifie"]
    virtuelle = [c for c in st.session_state.db_queue if c['statut'] == "en_attente"]
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Stock Restant", f"{st.session_state.db_stations[0]['stock']} L")
    col2.metric("En station", f"{len(physique)} / 10")
    col3.metric("En attente", len(virtuelle))
    
    st.divider()
    
    # Action : Appel manuel
    if st.button("🔔 Appeler 10 nouveaux clients (SMS Massif)"):
        nb = call_virtual_clients(1, 10)
        st.success(f"✅ {nb} SMS de convocation envoyés aux prochains véhicules.")
        st.rerun()

    st.subheader("🚗 File Physique (À servir)")
    if not physique:
        st.info("La file est vide. Appelez des clients virtuels.")
    else:
        for c in physique:
            with st.container():
                st.markdown(f"**Véhicule : {c['plaque']}** (Tel: {c['tel']})")
                col_btn, col_inp = st.columns([1, 1])
                litres = col_inp.number_input("Litres", 5, 100, 20, key=f"inp_{c['id']}")
                if col_btn.button(f"Marquer Servi", key=f"srv_{c['id']}"):
                    serve_client(c['id'], 1, litres)
                    st.rerun()
                st.markdown("---")

def admin_view():
    st.title("👑 Admin : État du Réseau")
    df = pd.DataFrame(st.session_state.db_stations)
    st.data_editor(df, use_container_width=True)
    
    st.subheader("Journal des flux")
    st.caption("Historique des services (Simulation)")
    st.code("2024-05-20 10:15 - BKO-102-AM : 45L servi (Station Shell)")

# ==========================================
# 4. ROUTEUR
# ==========================================
def main():
    st.sidebar.title("⛽ GAS-MALI")
    if is_demo: st.sidebar.info("🚀 VERSION DÉMONSTRATION")
    
    role = st.sidebar.radio("Navigation :", ["Client", "Pompiste", "Administrateur"])
    
    if role == "Client": client_view()
    elif role == "Pompiste": pompiste_view()
    else: admin_view()

if __name__ == "__main__":
    main()
