import streamlit as st
from datetime import date
import matplotlib
import pandas as pd
import plotly.express as px
import math

from data_loader import load_all_data
# --- Variables globales ---
MOIS = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Août", "Sep", "Oct", "Nov", "Déc"]
font_family = '"Source Sans", sans-serif'
REUSSITE_CMAP = matplotlib.colormaps["RdYlGn"]

def style_reussite_table(df):
    return (
        df.style.format("{:.1f}", na_rep="—")
        .text_gradient(cmap=REUSSITE_CMAP, vmin=0, vmax=100, axis=None)
    )
def sous_titre(text):
    return st.markdown(f"<h3 style='text-align: center; font-family: {font_family};'>{text}</h3>", unsafe_allow_html=True)

def sous_titre_small(text):
    return st.markdown(f"<h4 style='text-align: center; font-family: {font_family};'>{text}</h4>", unsafe_allow_html=True)

# --- Titre et introduction ---
st.title("🌿 Tableau de bord Fari'i Durable")

# --- Choix Année/Date ---
# --- Récupération des tables ---
df_profile, df_score_session, df_reponse_question, df_commune, df_question = load_all_data(
    st.session_state.use_test_data
)
# Filtrages
df_profile = df_profile[
    (df_profile["created_at"].dt.date >= st.session_state.d_debut)
    & (df_profile["created_at"].dt.date <= st.session_state.d_fin)
]
df_score_session = df_score_session[
    (df_score_session["date"].dt.date >= st.session_state.d_debut)
    & (df_score_session["date"].dt.date <= st.session_state.d_fin)
]
df_reponse_question = df_reponse_question[
    (df_reponse_question["created_at"].dt.date >= st.session_state.d_debut)
    & (df_reponse_question["created_at"].dt.date <= st.session_state.d_fin)
]
# Top des questions les mieux réussies
df_reponse_question_top = df_reponse_question.groupby("question_id").agg({"is_correct": "mean"}).reset_index()
df_reponse_question_top = df_reponse_question_top.merge(df_question, left_on="question_id", right_on="id")[["description", "is_correct"]]
df_reponse_question_top["is_correct"] = df_reponse_question_top["is_correct"] * 100
df_reponse_question_top["is_correct"] = df_reponse_question_top["is_correct"].round(1)
# df_reponse_question_top["is_correct"] = df_reponse_question_top["is_correct"].astype(str) + "%"
df_reponse_question_top.columns = ["Question", "Réussite"]
# --------------------------------------------------------------------
# --------------------------------------------------------------------
# --- Onglets ---
# --- Onglet Général ---
tab_general, tab_reussite = st.tabs(["Général","% Réussites"])
with tab_general:
    # --- Affichage des metrics ---
    col1, col2 = st.columns(2)
    with col1:
        # Users total
        st.metric("Users total", len(df_profile))
        # Utilisateurs par commune
        df_profile_commune = df_profile.merge(df_commune, left_on="commune_id", right_on="id")
        df_commune_count = df_profile_commune["nom_commune"].value_counts()
        df_commune_count = df_commune_count.reset_index()
        df_commune_count.columns = ["nom_commune", "count"]
        with st.container(border=True):
            sous_titre('Users par commune')
            fig1 = px.pie(df_commune_count, names="nom_commune", values="count", hole=0.35)
            st.plotly_chart(fig1)
            # Type de sessions
            df_type_session = df_score_session["type"].value_counts()
            df_type_session = df_type_session.reset_index()
            df_type_session.columns = ["type", "count"]
            df_type_session.loc[df_type_session["type"] == "OBJET", "type"] = "Objet"
            df_type_session.loc[df_type_session["type"] == "QUESTION", "type"] = "Quiz"
        with st.container(border=True):
            sous_titre('Type de sessions')
            fig2 = px.pie(df_type_session, names="type", values="count", hole=0.35)
            st.plotly_chart(fig2)
        # Type Objets
        # Durée moyenne de session (sous format XXminXXs )
        sous_titre('Type Objets')
        sous_titre_small('Durée moyenne de session')
        df_score_objets = df_score_session[(df_score_session["type"] == "OBJET") & (df_score_session["temps_total"] > 0)]
        col_duree_pedago, col_duree_court = st.columns(2)
        with col_duree_pedago:
            with st.container(border=True):
                st.markdown("##### Pédagogique")
                duree_moyenne = df_score_objets[df_score_objets["mode"] == "SERIE_P"]["temps_total"].mean()
                if math.isnan(duree_moyenne):
                    st.write("Aucune session pédagogique")
                else:
                    duree_moyenne = int(duree_moyenne)
                    st.write(f"{duree_moyenne // 60}min {duree_moyenne % 60 // 1}s")
        with col_duree_court:
            with st.container(border=True):
                st.markdown("##### Court")
                duree_moyenne = df_score_objets[df_score_objets["mode"] == "SERIE_C"]["temps_total"].mean()
                if math.isnan(duree_moyenne):
                    st.write("Aucune session court")
                else:
                    duree_moyenne = int(duree_moyenne)
                    st.write(f"{duree_moyenne // 60}min {duree_moyenne % 60 // 1}s")

    with col2:
        # Sessions total
        st.metric("Sessions total", len(df_score_session))
        # Sessions terminées
        with st.container(border=True):
            df_sessionterm = pd.DataFrame({
                "fini": ["Terminées", "Non terminées"], 
            "values": [len(df_score_session[df_score_session["a_fini"] == True]),
            len(df_score_session[df_score_session["a_fini"] == False])
            ]})
            sous_titre('Sessions terminées')
            fig = px.pie(df_sessionterm, names="fini", values="values", hole=0.35)
            st.plotly_chart(fig)
        # Mode de sessions   
        with st.container(border=True):     
            df_mode_session = df_score_session["mode"].value_counts()
            df_mode_session = df_mode_session.reset_index()
            df_mode_session.columns = ["mode", "count"]
            df_mode_session.loc[df_mode_session["mode"] == "SERIE_P", "mode"] = "Pédagogique"
            df_mode_session.loc[df_mode_session["mode"] == "SERIE_C", "mode"] = "Pédagogique"
            df_mode_session.loc[df_mode_session["mode"] == "CHRONO", "mode"] = "Chrono"
            df_mode_session.loc[df_mode_session["mode"] == "SPRINT", "mode"] = "Sprint"
            sous_titre('Modes de sessions')
            fig2 = px.pie(df_mode_session, names="mode", values="count", hole=0.35)
            st.plotly_chart(fig2)
        # Type Quiz
        # Durée moyenne de session
        sous_titre('Type Quiz')
        sous_titre_small('Durée moyenne de session')
        df_score_objets = df_score_session[(df_score_session["type"] == "QUESTION") & (df_score_session["temps_total"] > 0)]
        col_duree_pedago, col_duree_court = st.columns(2)
        with col_duree_pedago:
            with st.container(border=True):
                st.markdown("##### Pédagogique")
                duree_moyenne = df_score_objets[df_score_objets["mode"] == "SERIE_P"]["temps_total"].mean()
                if math.isnan(duree_moyenne):
                    st.write("Aucune session pédagogique")
                else:
                    duree_moyenne = int(duree_moyenne)
                    st.write(f"{duree_moyenne // 60}min {duree_moyenne % 60 // 1}s")
        with col_duree_court:
            with st.container(border=True):
                st.markdown("##### Court")
                duree_moyenne = df_score_objets[df_score_objets["mode"] == "SERIE_C"]["temps_total"].mean()
                if math.isnan(duree_moyenne):
                    st.write("Aucune session court")
                else:
                    duree_moyenne = int(duree_moyenne)
                    st.write(f"{duree_moyenne // 60}min {duree_moyenne % 60 // 1}s")

# --- Affichage des graphiques ---
    # --- Graphique: utilisateurs et sessions par mois ---
    df_profile_c1 = df_profile.copy()
    df_profile_c1["month"] = df_profile_c1["created_at"].dt.month
    df_profile_c1["year"] = df_profile_c1["created_at"].dt.year

    df_grouped = (
        df_profile_c1.groupby(["year", "month"], as_index=False)
        .size()
        .rename(columns={"size": "nb"})
        .sort_values(["year", "month"])
    )
    df_grouped["periode"] = (
        df_grouped["month"].apply(lambda m: MOIS[m - 1])
        + "-"
        + df_grouped["year"].astype(str)
    )
    df_grouped["type"] = "Nouveaux utilisateurs"

    df_session_c1 = df_score_session.copy()
    df_session_c1["month"] = df_session_c1["date"].dt.month
    df_session_c1["year"] = df_session_c1["date"].dt.year

    df_active_grouped = (
        df_session_c1.groupby(["year", "month"], as_index=False)["profile_id"]
        .nunique()
        .rename(columns={"profile_id": "nb"})
        .sort_values(["year", "month"])
    )
    df_active_grouped["periode"] = (
        df_active_grouped["month"].apply(lambda m: MOIS[m - 1])
        + "-"
        + df_active_grouped["year"].astype(str)
    )
    df_active_grouped["type"] = "Joueurs actifs"

    df_session_grouped = (
        df_session_c1.groupby(["year", "month"], as_index=False)
        .size()
        .rename(columns={"size": "nb"})
        .sort_values(["year", "month"])
    )
    df_session_grouped["periode"] = (
        df_session_grouped["month"].apply(lambda m: MOIS[m - 1])
        + "-"
        + df_session_grouped["year"].astype(str)
    )
    df_session_grouped["type"] = "Sessions"

    df_users_chart = pd.concat(
        [
            df_grouped[["periode", "year", "month", "nb", "type"]],
            df_active_grouped[["periode", "year", "month", "nb", "type"]],
            df_session_grouped[["periode", "year", "month", "nb", "type"]],
        ],
        ignore_index=True,
    )
    periodes_users = (
        df_users_chart.drop_duplicates(["year", "month"])
        .sort_values(["year", "month"])["periode"]
        .tolist()
    )
    sous_titre('Utilisateurs et sessions par mois')
    fig = px.bar(
        df_users_chart,
        x="periode",
        y="nb",
        color="type",
        barmode="group",
        category_orders={
            "type": ["Nouveaux utilisateurs", "Joueurs actifs", "Sessions"]
        },
        labels={"periode": "Période", "nb": "Nombre", "type": ""},
    )
    fig.update_xaxes(categoryorder="array", categoryarray=periodes_users)
    fig.update_traces(texttemplate="%{y}", textposition="outside")
    st.plotly_chart(fig, width="stretch")
# --------------------------------------------------------------------
# --------------------------------------------------------------------
# --- Onglet Réussite ---
with tab_reussite:
    col_t_objets, col_t_quiz = st.columns(2)
    with col_t_objets:
        # Top des questions les mieux réussies
        sous_titre('Top des questions les mieux réussies')
        slider_best_top = st.slider("  ", min_value=3, max_value=len(df_reponse_question_top), value=5, step=1)
        df_reponse_question_top_b = df_reponse_question_top.sort_values("Réussite", ascending=False).head(slider_best_top)
        st.dataframe(style_reussite_table(df_reponse_question_top_b.set_index("Question")))
    with col_t_quiz:
        # Top des questions les moins bien réussies
        sous_titre('Top des questions les moins bien réussies')
        slider_worse_top = st.slider(" ", min_value=3, max_value=len(df_reponse_question_top), value=5, step=1)
        df_reponse_question_top_w = df_reponse_question_top.sort_values("Réussite", ascending=True).head(slider_worse_top)
        st.dataframe(style_reussite_table(df_reponse_question_top_w.set_index("Question")))


    with st.container(horizontal_alignment="center"):
        sous_titre("% de réussite des objets/questions par mois")
        sc_objet_quiz = st.segmented_control(" ", ["Objets", "Quiz", "Les deux"], default="Les deux")
        df_reponse_question_c1 = df_reponse_question.copy()
        df_reponse_question_c1["month"] = df_reponse_question_c1["created_at"].dt.month
        df_reponse_question_c1["year"] = df_reponse_question_c1["created_at"].dt.year
        df_reponse_question_c1.groupby(["year", "month"])
        df_reponse_question_c1["is_correct"] = df_reponse_question_c1["is_correct"].astype(int)
        df_reponse_question_id_count = df_reponse_question_c1.groupby(["question_id","year", "month"]).count()
        df_reponse_question_c1 = df_reponse_question_c1.groupby(["question_id","year", "month"]).agg({"is_correct": "sum"}).reset_index()
        df_reponse_question_id_count = df_reponse_question_id_count.drop(
            columns=["score_session_id", "user_reponse", "created_at","id"]
        )
        df_reponse_question_id_count = df_reponse_question_id_count.rename(columns={"is_correct": "count_tot"})
        df_reponse_question_c1 = df_reponse_question_c1.merge(df_reponse_question_id_count, on=[
            "question_id","year", "month"
        ])
        df_reponse_question_c1["%_reussite"] = df_reponse_question_c1["is_correct"] / df_reponse_question_c1["count_tot"] * 100
        df_reponse_question_c1["periode"] = df_reponse_question_c1["year"].astype(str) + "-" + df_reponse_question_c1["month"].astype(str)
        df_reponse_question_c1 = df_reponse_question_c1.merge(df_question, left_on="question_id", right_on="id")[["description", "periode", "%_reussite", "categorie"]].rename(columns={"description": "Question"})
        if sc_objet_quiz == "Objets":
            df_reponse_question_c1 = df_reponse_question_c1[df_reponse_question_c1["categorie"] == "OBJET"]
        elif sc_objet_quiz == "Quiz":
            df_reponse_question_c1 = df_reponse_question_c1[df_reponse_question_c1["categorie"] == "QUESTION"]
        else:
            df_reponse_question_c1 = df_reponse_question_c1
        df_reponse_question_c1 = df_reponse_question_c1.pivot(
            index="Question", columns="periode", values="%_reussite"
        )
        st.dataframe(style_reussite_table(df_reponse_question_c1))

        st.divider()
        sous_titre("% de réussite des communes par mois")
        sc_objet_quiz2 = st.segmented_control("  ", ["Objets", "Quiz", "Les deux"], default="Les deux")
        df_reponse_commune_c1 = df_reponse_question.copy()
        df_reponse_commune_c1["month"] = df_reponse_commune_c1["created_at"].dt.month
        df_reponse_commune_c1["year"] = df_reponse_commune_c1["created_at"].dt.year
        df_reponse_commune_c1["is_correct"] = df_reponse_commune_c1["is_correct"].astype(int)
        df_reponse_commune_c1 = df_reponse_commune_c1.merge(
            df_score_session[["id", "profile_id"]].rename(columns={"id": "score_session_id"}),
            on="score_session_id",
        )
        df_reponse_commune_c1 = df_reponse_commune_c1.merge(
            df_profile[["id", "commune_id"]].rename(columns={"id": "profile_id"}),
            on="profile_id",
        )
        df_reponse_commune_c1 = df_reponse_commune_c1.merge(
            df_commune[["id", "nom_commune"]].rename(columns={"id": "commune_id"}),
            on="commune_id",
        )
        df_reponse_commune_c1 = df_reponse_commune_c1.merge(
            df_question[["id", "categorie"]].rename(columns={"id": "question_id"}),
            on="question_id",
        )
        if sc_objet_quiz2 == "Objets":
            df_reponse_commune_c1 = df_reponse_commune_c1[df_reponse_commune_c1["categorie"] == "OBJET"]
        elif sc_objet_quiz2 == "Quiz":
            df_reponse_commune_c1 = df_reponse_commune_c1[df_reponse_commune_c1["categorie"] == "QUESTION"]
        df_reponse_commune_count = df_reponse_commune_c1.groupby(["nom_commune", "year", "month"]).size().reset_index(name="count_tot")
        df_reponse_commune_c1 = df_reponse_commune_c1.groupby(["nom_commune", "year", "month"]).agg({"is_correct": "sum"}).reset_index()
        df_reponse_commune_c1 = df_reponse_commune_c1.merge(
            df_reponse_commune_count, on=["nom_commune", "year", "month"]
        )
        df_reponse_commune_c1["%_reussite"] = df_reponse_commune_c1["is_correct"] / df_reponse_commune_c1["count_tot"] * 100
        df_reponse_commune_c1["periode"] = (
            df_reponse_commune_c1["year"].astype(str) + "-" + df_reponse_commune_c1["month"].astype(str)
        )
        df_reponse_commune_c1 = df_reponse_commune_c1.pivot(
            index="nom_commune", columns="periode", values="%_reussite"
        ).sort_index()
        df_reponse_commune_c1.index.name = "Commune"
        st.dataframe(style_reussite_table(df_reponse_commune_c1))
