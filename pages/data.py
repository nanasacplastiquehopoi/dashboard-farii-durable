import streamlit as st
from data_loader import load_all_data

st.title("Données")

df_profile, df_score_session, df_reponse_question, df_commune, df_question = load_all_data(
    st.session_state.use_test_data
)

st.subheader("Communes")
st.dataframe(df_commune)

st.subheader("Utilisateurs (profile)")
st.dataframe(df_profile)

st.subheader("Sessions (score_session)")
st.dataframe(df_score_session)

st.subheader("Réponses (reponse_question)")
st.dataframe(df_reponse_question)

st.subheader("Questions")
st.dataframe(df_question)
