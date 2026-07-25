from supabase import create_client, Client
import streamlit as st

# --- Connexion Supabase ---
@st.cache_resource
def get_supabase() -> Client:
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["anon_key"]
    return create_client(url, key)

supabase = get_supabase()
