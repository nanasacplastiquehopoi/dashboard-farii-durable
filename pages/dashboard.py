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

def pivot_reussite_mensuelle(df, index_col, index_name=None):
    df_tous = df.groupby("periode", as_index=False).agg(
        is_correct=("is_correct", "sum"),
        count_tot=("count_tot", "sum"),
    )
    df_tous["%_reussite"] = df_tous["is_correct"] / df_tous["count_tot"] * 100
    df_tous[index_col] = "Tous"

    df_plot = pd.concat([
        df_tous[[index_col, "periode", "%_reussite"]],
        df[[index_col, "periode", "%_reussite"]],
    ])
    pivot = df_plot.pivot(index=index_col, columns="periode", values="%_reussite")
    autres = sorted(i for i in pivot.index if i != "Tous")
    pivot = pivot.reindex(["Tous"] + autres)
    if index_name:
        pivot.index.name = index_name
    return pivot
def color_background_gold_column(col):
    return ['background-color: #fce174' for _ in col]
def color_background_silver_column(col):
    return ['background-color: #dbdbdb' for _ in col]
def color_background_bronze_column(col):
    return ['background-color: #fcbb7c' for _ in col]
def bold_text_column(col):
    return ['font-weight: bold' for _ in col]

def sous_titre(text):
    return st.markdown(f"<h3 style='text-align: center; font-family: {font_family};'>{text}</h3>", unsafe_allow_html=True)

def sous_titre_small(text):
    return st.markdown(f"<h4 style='text-align: center; font-family: {font_family};'>{text}</h4>", unsafe_allow_html=True)

MODE_LABELS = {
    "SERIE_P": "Pédagogique",
    "SERIE_C": "Court",
    "CHRONO": "Chrono",
    "SPRINT": "Sprint",
}

def build_leaderboard(df_sessions, mode):
    df = df_sessions[df_sessions["mode"] == mode].copy()
    if df.empty:
        return pd.DataFrame(columns=["Rang", "Joueur", "Score", "Temps (s)", "Sessions"])

    df["nb_correct"] = pd.to_numeric(df["nb_correct"], errors="coerce").fillna(0).astype(int)
    df["temps_total"] = pd.to_numeric(df["temps_total"], errors="coerce")
    df = df.sort_values(
        ["profile_id", "nb_correct", "temps_total"],
        ascending=[True, False, True],
        na_position="last",
    )
    session_counts = df.groupby("profile_id").size()
    best = df.groupby("profile_id", as_index=False).first()
    best["Sessions"] = best["profile_id"].map(session_counts)
    leaderboard = best[["username", "nb_correct", "temps_total", "Sessions", "nom_commune"]].rename(
        columns={"username": "Joueur", "nb_correct": "Score", "temps_total": "Temps (s)"}
    )
    leaderboard = leaderboard.sort_values(
        ["Score", "Temps (s)"], ascending=[False, True]
    ).reset_index(drop=True)
    leaderboard.insert(0, "Rang", leaderboard.index + 1)
    return leaderboard

def format_temps(secondes):
    if pd.isna(secondes):
        return "—"
    secondes = int(secondes)
    return f"{secondes // 60}min {secondes % 60}s"

def afficher_leaderboard(df_sessions, mode, show_commune=False):
    leaderboard = build_leaderboard(df_sessions, mode)
    if leaderboard.empty:
        st.info(f"Aucune session en mode {MODE_LABELS.get(mode, mode)} sur cette période.")
        return
    affichage = leaderboard.copy()
    affichage["Temps"] = affichage["Temps (s)"].apply(format_temps)
    for col in ("Rang", "Score", "Sessions"):
        affichage[col] = pd.to_numeric(affichage[col], errors="coerce").fillna(0).astype(int)
    colonnes = ["Rang", "Joueur", "Score", "Temps", "Sessions"]
    if show_commune:
        affichage = affichage.rename(columns={"nom_commune": "Commune"})
        colonnes = ["Rang", "Joueur", "Commune", "Score", "Temps", "Sessions"]
    affichage = affichage[colonnes]
    format_entiers = {"Rang": "{:.0f}", "Score": "{:.0f}", "Sessions": "{:.0f}"}
    if len(affichage)>2:
        affichage = (affichage.style.apply(color_background_gold_column, subset=pd.IndexSlice[affichage.index[0], affichage.columns[:]])
        .apply(color_background_silver_column, subset=pd.IndexSlice[affichage.index[1], affichage.columns[:]])
        .apply(color_background_bronze_column, subset=pd.IndexSlice[affichage.index[2], affichage.columns[:]])
        .apply(bold_text_column, subset=pd.IndexSlice[affichage.index[0:3], affichage.columns[:]])
        .format(format_entiers))
    elif len(affichage)>1:
        affichage = (affichage.style.apply(color_background_silver_column, subset=pd.IndexSlice[affichage.index[1], affichage.columns[:]])
        .apply(color_background_gold_column, subset=pd.IndexSlice[affichage.index[0], affichage.columns[:]])
        .apply(bold_text_column, subset=pd.IndexSlice[affichage.index[0:3], affichage.columns[:]])
        .format(format_entiers))
    elif len(affichage)>0:
        affichage = (affichage.style.apply(color_background_gold_column, subset=pd.IndexSlice[affichage.index[0], affichage.columns[:]])
        .apply(bold_text_column, subset=pd.IndexSlice[affichage.index[0:3], affichage.columns[:]])
        .format(format_entiers))
    else:
        affichage = affichage.style.format(format_entiers)
    st.dataframe(
        affichage,
        hide_index=True,
        width="stretch",

    )

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
tab_general, tab_reussite, tab_leaderboard= st.tabs(["Général","% Réussites","Leaderboard"])
with tab_general:
    # --- Affichage des metrics ---
    with st.container(border=False):
        kpi_users, kpi_sessions = st.columns(2)
        with kpi_users:
            with st.container(horizontal_alignment="center"):
                st.metric("Nouveaux users total", len(df_profile))
        with kpi_sessions:
            with st.container(horizontal_alignment="center"):
                st.metric("Sessions total", len(df_score_session))

    col1, col2 = st.columns(2)
    with col1:
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
            df_mode_session.loc[df_mode_session["mode"] == "SERIE_P", "mode"] = "Pédagogique (Long)"
            df_mode_session.loc[df_mode_session["mode"] == "SERIE_C", "mode"] = "Pédagogique (Court)"
            df_mode_session.loc[df_mode_session["mode"] == "CHRONO", "mode"] = "Chrono"
            df_mode_session.loc[df_mode_session["mode"] == "SPRINT", "mode"] = "Sprint"
            sous_titre('Modes de sessions')
            fig2 = px.pie(df_mode_session, names="mode", values="count", hole=0.35, category_orders={"mode": ["Pédagogique (Long)", "Pédagogique (Court)", "Chrono", "Sprint"]})
            st.plotly_chart(fig2, theme="streamlit")
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
    
    left, right = st.columns([25, 1], vertical_alignment="center")
    with left:
        sous_titre('Utilisateurs et sessions par mois')
    with right:
        with st.popover("❓", help="Aide"):
            st.markdown("__Nouveaux utilisateurs__ = Utilisateurs créés pendant la période")
            st.markdown("__Joueurs actifs__ =  Utilisateurs ayant effectué au moins une session pendant la période")
            st.markdown("__Sessions__ =  Nombre de sessions effectuées pendant la période")
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
        df_reponse_question_c1 = df_reponse_question_c1.merge(df_question, left_on="question_id", right_on="id")[
            ["description", "periode", "%_reussite", "categorie", "is_correct", "count_tot"]
        ].rename(columns={"description": "Question"})
        if sc_objet_quiz == "Objets":
            df_reponse_question_c1 = df_reponse_question_c1[df_reponse_question_c1["categorie"] == "OBJET"]
        elif sc_objet_quiz == "Quiz":
            df_reponse_question_c1 = df_reponse_question_c1[df_reponse_question_c1["categorie"] == "QUESTION"]
        else:
            df_reponse_question_c1 = df_reponse_question_c1
        df_reponse_question_c1 = pivot_reussite_mensuelle(
            df_reponse_question_c1, index_col="Question", index_name="Question"
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
        df_reponse_commune_c1 = pivot_reussite_mensuelle(
            df_reponse_commune_c1, index_col="nom_commune", index_name="Commune"
        )
        st.dataframe(style_reussite_table(df_reponse_commune_c1))
# --------------------------------------------------------------------
# --- Onglet Leaderboard ---
with tab_leaderboard:
    df_sessions_lb = df_score_session.merge(
        df_profile[["id", "username", "commune_id"]].rename(columns={"id": "profile_id"}),
        on="profile_id",
    ).merge(
        df_commune[["id", "nom_commune"]].rename(columns={"id": "commune_id"}),
        on="commune_id",
    )

    sous_titre("Leaderboard")
    mode_filtre = st.segmented_control(
        "Mode",
        options=MODE_LABELS.values(),
        default=MODE_LABELS["SERIE_P"],
    )

    communes_disponibles = sorted(df_commune["nom_commune"].unique())
    with st.container(border=True):
        col_lb_commune, col_lb_global = st.columns(2)
        with col_lb_commune:
            sous_titre_small("Par commune")
            commune_choisie = st.selectbox(
                "Commune",
                options=communes_disponibles,
                label_visibility="collapsed",
            )
            df_commune_lb = df_sessions_lb[
                df_sessions_lb["nom_commune"] == commune_choisie
            ]
            mode_choisi = [k for k, v in MODE_LABELS.items() if v == mode_filtre][0]
            afficher_leaderboard(df_commune_lb, mode_choisi)

        with col_lb_global:
            sous_titre_small("Global")
            afficher_leaderboard(df_sessions_lb, mode_choisi, show_commune=True)
