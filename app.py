import streamlit as st

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
        st.Page("pages/data.py", title="Données", icon="🗂️"),
    ],
}

pg = st.navigation(pages)

with st.sidebar:
    st.toggle("Données test", key="use_test_data")
    with st.container(horizontal=True, vertical_alignment="center"):
        if st.button("Actualiser", icon="🔄️"):
            st.cache_data.clear()
            st.rerun()
        st.write("Auto: 1h")

pg.run()
