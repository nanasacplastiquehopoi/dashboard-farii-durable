import streamlit as st
import pandas as pd
from supabase_connexion import supabase
from dataset_test import (
    df_profile_test,
    df_score_session_test,
    df_reponse_question_test,
    df_commune_test,
    df_question_test,
)

TTL = 3600


@st.cache_data(ttl=TTL, show_spinner="Récupération des données...")
def load_all_data(use_test: bool):
    if use_test:
        df_profile = df_profile_test.copy()
        df_profile["created_at"] = pd.to_datetime(df_profile["created_at"])
        df_score_session = df_score_session_test.copy()
        df_score_session["date"] = pd.to_datetime(df_score_session["date"])
        df_reponse_question = df_reponse_question_test.copy()
        df_reponse_question["created_at"] = pd.to_datetime(df_reponse_question["created_at"])
        df_commune = df_commune_test.copy()
        df_question = df_question_test.copy()
    else:
        df_commune = pd.DataFrame(supabase.table("commune").select("*").execute().data)
        df_profile = pd.DataFrame(supabase.table("profile").select("*").execute().data)
        df_profile["created_at"] = pd.to_datetime(df_profile["created_at"])
        df_score_session = pd.DataFrame(supabase.table("score_session").select("*").execute().data)
        df_score_session["date"] = pd.to_datetime(df_score_session["date"])
        df_reponse_question = pd.DataFrame(
            supabase.table("reponse_question").select("*").execute().data
        )
        df_reponse_question["created_at"] = pd.to_datetime(df_reponse_question["created_at"])
        df_question = pd.DataFrame(supabase.table("question").select("*").execute().data)

    return df_profile, df_score_session, df_reponse_question, df_commune, df_question
