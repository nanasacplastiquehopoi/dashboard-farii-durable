import streamlit as st
from datetime import date
st.set_page_config(
    page_title="Tableau de bord Fari'i Durable",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "use_test_data" not in st.session_state:
    st.session_state.use_test_data = False

pages = {
    "Menu": [
        st.Page("pages/dashboard.py", title="Dashboard", icon="📊"),
        st.Page("pages/data.py", title="Données brutes", icon="🗂️"),
    ],
}

pg = st.navigation(pages)

with st.sidebar:
    st.toggle("Données test", key="use_test_data")
    with st.container(horizontal=True, vertical_alignment="center"):
        if st.button("Actualiser", icon="🔄️"):
            with st.status(""):
                st.cache_data.clear()
                st.rerun()
        st.write("(Auto: 1h)")
    with st.container(border=True):
        with st.container(horizontal_alignment="center"):
            mode = st.segmented_control(
                "Période",
                ["Années", "Dates"],
                default="Années",
                key="s_toggle_dates",
                label_visibility="collapsed",
            )
        col_date1, col_date2 = st.columns(2)
        annee_courante = date.today().year
        annees = list(range(2026, annee_courante + 1))

        with col_date2:
            if mode == "Années":
                annee_fin = st.selectbox("Année fin", annees)
                st.session_state.d_fin = date(annee_fin, 12, 31)
            else:
                st.session_state.d_fin = st.date_input("Date fin", value=date.today())

        with col_date1:
            if mode == "Années":
                annee_debut = st.selectbox("Année début", annees)
                st.session_state.d_debut = date(annee_debut, 1, 1)
            else:
                st.session_state.d_debut = st.date_input("Date début", value=date(2026, 1, 1))
        t_exclure_juillet26 = st.toggle("Exclure Juillet 2026", value=False)
        if t_exclure_juillet26:
            st.session_state.d_debut = date(2026, 8, 1)
        else:
            st.session_state.d_debut = date(2026, 1, 1)
pg.run()
