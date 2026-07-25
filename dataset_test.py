import pandas as pd
from pathlib import Path

# Schéma SQL table ile:
#   id uuid not null default gen_random_uuid (),
#   nom_ile text not null,
#   constraint ile_pkey primary key (id)
# );

# Schéma SQL table commune:
# create table public.commune (
#   id uuid not null default gen_random_uuid (),
#   ile_id uuid not null,
#   nom_commune text not null,
#   constraint commune_pkey primary key (id),
#   constraint fk_commune_ile foreign KEY (ile_id) references ile (id)
# );

# Schéma SQL table question:
# create table public.question (
#   id uuid not null default gen_random_uuid (),
#   nom_question text not null,
#   reponse boolean not null,
#   date_application timestamp with time zone not null,
#   categorie text null,
#   description text null,
#   constraint question_pkey primary key (id)
# );

# Schéma SQL table reponse_question:
# create table public.reponse_question (
#   id uuid not null default gen_random_uuid (),
#   score_session_id uuid not null,
#   question_id uuid not null,
#   user_reponse boolean not null,
#   is_correct boolean not null,
#   created_at timestamp with time zone null default CURRENT_TIMESTAMP,
#   constraint reponse_question_pkey primary key (id),
#   constraint fk_reponse_question_score_session foreign KEY (score_session_id) references score_session (id) on delete CASCADE,
#   constraint fk_reponse_question_question foreign KEY (question_id) references question (id)
# );

# Schéma SQL table score_session:
# create table public.score_session (
#   id uuid not null default gen_random_uuid (),
#   profile_id uuid not null,
#   date timestamp with time zone null default CURRENT_TIMESTAMP,
#   temps_total integer null,
#   nb_correct integer null,
#   mode public.game_mode not null default 'SERIE'::game_mode,
#   nb_questions integer null default 0,
#   type public.question_categorie null,
#   a_fini boolean not null default false,
#   updated_at timestamp with time zone not null default now(),
#   constraint score_session_pkey primary key (id),
#   constraint fk_score_session_profile foreign KEY (profile_id) references profile (id) on delete CASCADE
# ) TABLESPACE pg_default;

# create index IF not exists idx_score_session_profile_id on public.score_session using btree (profile_id) TABLESPACE pg_default;

# create trigger update_score_session_updated_at BEFORE
# update on score_session for EACH row
# execute FUNCTION update_updated_at_column ();

_ILES = [
    ("33333333-3333-3333-3333-000000000001", "Tahiti"),
    ("33333333-3333-3333-3333-000000000002", "Moorea"),
    ("33333333-3333-3333-3333-000000000003", "Bora Bora"),
    ("33333333-3333-3333-3333-000000000004", "Raiatea"),
    ("33333333-3333-3333-3333-000000000005", "Huahine"),
]

_COMMUNES = [
    ("ae7c31a1-932d-4d41-ad72-47bcc616469d", "33333333-3333-3333-3333-000000000001", "Papeete"),
    ("44444444-4444-4444-4444-000000000001", "33333333-3333-3333-3333-000000000001", "Faaa"),
    ("44444444-4444-4444-4444-000000000002", "33333333-3333-3333-3333-000000000001", "Pirae"),
    ("44444444-4444-4444-4444-000000000003", "33333333-3333-3333-3333-000000000001", "Punaauia"),
    ("44444444-4444-4444-4444-000000000004", "33333333-3333-3333-3333-000000000002", "Paea"),
    ("44444444-4444-4444-4444-000000000005", "33333333-3333-3333-3333-000000000002", "Mahina"),
    ("44444444-4444-4444-4444-000000000006", "33333333-3333-3333-3333-000000000003", "Iles Sous-le-Vent"),
    ("44444444-4444-4444-4444-000000000007", "33333333-3333-3333-3333-000000000004", "Taiarapu-Est"),
    ("44444444-4444-4444-4444-000000000008", "33333333-3333-3333-3333-000000000005", "Papara"),
]

_COMMUNE_IDS = [c[0] for c in _COMMUNES]

df_question_test = pd.read_csv(Path(__file__).parent / "question.csv")
df_question_test["reponse"] = (
    df_question_test["reponse"].astype(str).str.lower().eq("true")
)

_PROFILES = [
    ("11111111-1111-1111-1111-000000000001", "alice", "alice@hopoi.test", "2026-01-08T10:00:00+00:00", _COMMUNE_IDS[0]),
    ("11111111-1111-1111-1111-000000000002", "bob", "bob@hopoi.test", "2026-01-15T14:30:00+00:00", _COMMUNE_IDS[1]),
    ("11111111-1111-1111-1111-000000000003", "chloe", "chloe@hopoi.test", "2026-01-22T09:15:00+00:00", _COMMUNE_IDS[2]),
    ("11111111-1111-1111-1111-000000000004", "david", "david@hopoi.test", "2026-02-03T11:00:00+00:00", _COMMUNE_IDS[3]),
    ("11111111-1111-1111-1111-000000000005", "emma", "emma@hopoi.test", "2026-02-18T16:45:00+00:00", _COMMUNE_IDS[4]),
    ("11111111-1111-1111-1111-000000000006", "félix", "felix@hopoi.test", "2026-03-05T08:20:00+00:00", _COMMUNE_IDS[5]),
    ("11111111-1111-1111-1111-000000000007", "gina", "gina@hopoi.test", "2026-03-12T13:10:00+00:00", _COMMUNE_IDS[6]),
    ("11111111-1111-1111-1111-000000000008", "hugo", "hugo@hopoi.test", "2026-03-25T17:00:00+00:00", _COMMUNE_IDS[7]),
    ("11111111-1111-1111-1111-000000000009", "ines", "ines@hopoi.test", "2026-03-28T10:30:00+00:00", _COMMUNE_IDS[8]),
    ("11111111-1111-1111-1111-00000000000a", "jules", "jules@hopoi.test", "2026-04-10T12:00:00+00:00", _COMMUNE_IDS[0]),
    ("11111111-1111-1111-1111-00000000000b", "karla", "karla@hopoi.test", "2026-05-02T09:45:00+00:00", _COMMUNE_IDS[1]),
    ("11111111-1111-1111-1111-00000000000c", "léo", "leo@hopoi.test", "2026-05-14T15:20:00+00:00", _COMMUNE_IDS[2]),
    ("11111111-1111-1111-1111-00000000000d", "mia", "mia@hopoi.test", "2026-05-27T11:55:00+00:00", _COMMUNE_IDS[3]),
    ("11111111-1111-1111-1111-00000000000e", "noa", "noa@hopoi.test", "2026-06-06T08:10:00+00:00", _COMMUNE_IDS[4]),
    ("11111111-1111-1111-1111-00000000000f", "olivia", "olivia@hopoi.test", "2026-06-19T14:40:00+00:00", _COMMUNE_IDS[5]),
    ("11111111-1111-1111-1111-000000000010", "paul", "paul@hopoi.test", "2026-07-01T10:05:00+00:00", _COMMUNE_IDS[6]),
    ("11111111-1111-1111-1111-000000000011", "rosa", "rosa@hopoi.test", "2026-07-12T16:25:00+00:00", _COMMUNE_IDS[7]),
    ("11111111-1111-1111-1111-000000000012", "sam", "sam@hopoi.test", "2026-07-18T09:50:00+00:00", _COMMUNE_IDS[8]),
    ("11111111-1111-1111-1111-000000000013", "tina", "tina@hopoi.test", "2026-07-23T13:35:00+00:00", _COMMUNE_IDS[0]),
]

_SESSIONS = [
    ("22222222-2222-2222-2222-000000000001", "11111111-1111-1111-1111-000000000001", "2026-01-09T11:00:00+00:00", 420, 8, "SERIE_P", 10, "QUESTION", True),
    ("22222222-2222-2222-2222-000000000002", "11111111-1111-1111-1111-000000000001", "2026-01-20T15:30:00+00:00", 380, 7, "SERIE_P", 10, "QUESTION", True),
    ("22222222-2222-2222-2222-000000000003", "11111111-1111-1111-1111-000000000001", "2026-04-20T15:30:00+00:00", 380, 7, "SERIE_P", 10, "OBJET", True),
    ("22222222-2222-2222-2222-000000000004", "11111111-1111-1111-1111-000000000002", "2026-01-16T10:15:00+00:00", 200, 6, "SERIE_C", 10, "QUESTION", False),
    ("22222222-2222-2222-2222-000000000005", "11111111-1111-1111-1111-000000000002", "2026-02-16T10:15:00+00:00", 510, 6, "CHRONO", 10, "QUESTION", False),
    ("22222222-2222-2222-2222-000000000006", "11111111-1111-1111-1111-000000000002", "2026-03-16T10:15:00+00:00", 210, 6, "SERIE_C", 10, "OBJET", False),
    ("22222222-2222-2222-2222-000000000007", "11111111-1111-1111-1111-000000000002", "2026-04-16T10:15:00+00:00", 510, 6, "SPRINT", 10, "QUESTION", False),
    ("22222222-2222-2222-2222-000000000008", "11111111-1111-1111-1111-000000000002", "2026-05-16T10:15:00+00:00", 510, 6, "CHRONO", 10, "OBJET", False),
    ("22222222-2222-2222-2222-000000000009", "11111111-1111-1111-1111-000000000003", "2026-01-23T09:00:00+00:00", 290, 9, "SERIE_P", 10, "QUESTION", True),
    ("22222222-2222-2222-2222-00000000000a", "11111111-1111-1111-1111-000000000004", "2026-02-04T14:20:00+00:00", 250, 5, "SERIE_C", 10, "QUESTION", True),
    ("22222222-2222-2222-2222-00000000000b", "11111111-1111-1111-1111-000000000004", "2026-02-11T16:00:00+00:00", 320, 4, "SERIE_P", 10, "OBJET", False),
    ("22222222-2222-2222-2222-00000000000c", "11111111-1111-1111-1111-000000000005", "2026-02-19T08:45:00+00:00", 600, 10, "SERIE_P", 1, "QUESTION", True),
    ("22222222-2222-2222-2222-00000000000d", "11111111-1111-1111-1111-000000000006", "2026-03-06T12:30:00+00:00", 340, 6, "SERIE_P", 10, "QUESTION", True),
    ("22222222-2222-2222-2222-00000000000e", "11111111-1111-1111-1111-000000000007", "2026-03-13T17:10:00+00:00", 175, 3, "SERIE_C", 10, "OBJET", False),
    ("22222222-2222-2222-2222-00000000000f", "11111111-1111-1111-1111-000000000008", "2026-03-26T10:00:00+00:00", 490, 8, "SERIE_P", 10, "QUESTION", True),
    ("22222222-2222-2222-2222-000000000010", "11111111-1111-1111-1111-000000000008", "2026-03-29T11:20:00+00:00", 210, 7, "SERIE_C", 10, "QUESTION", True),
    ("22222222-2222-2222-2222-000000000011", "11111111-1111-1111-1111-000000000009", "2026-03-30T09:40:00+00:00", 360, 5, "SERIE_P", 10, "QUESTION", False),
    ("22222222-2222-2222-2222-000000000012", "11111111-1111-1111-1111-00000000000a", "2026-04-11T13:15:00+00:00", 520, 9, "SERIE_P", 10, "OBJET", True),
    ("22222222-2222-2222-2222-000000000013", "11111111-1111-1111-1111-00000000000b", "2026-05-03T10:50:00+00:00", 300, 4, "CHRONO", 10, "QUESTION", True),
    ("22222222-2222-2222-2222-000000000014", "11111111-1111-1111-1111-00000000000c", "2026-05-15T15:05:00+00:00", 240, 6, "SERIE_C", 10, "OBJET", False),
    ("22222222-2222-2222-2222-000000000015", "11111111-1111-1111-1111-00000000000d", "2026-05-28T08:35:00+00:00", 390, 7, "SERIE_P", 10, "QUESTION", True),
    ("22222222-2222-2222-2222-000000000016", "11111111-1111-1111-1111-00000000000d", "2026-05-30T18:00:00+00:00", 280, 2, "CHRONO", 10, "OBJET", False),
    ("22222222-2222-2222-2222-000000000017", "11111111-1111-1111-1111-00000000000e", "2026-06-07T11:25:00+00:00", 270, 8, "SERIE_C", 10, "QUESTION", True),
    ("22222222-2222-2222-2222-000000000018", "11111111-1111-1111-1111-00000000000f", "2026-06-20T14:55:00+00:00", 330, 5, "SERIE_P", 10, "OBJET", True),
    ("22222222-2222-2222-2222-000000000019", "11111111-1111-1111-1111-000000000010", "2026-07-02T09:10:00+00:00", 250, 9, "SERIE_C", 10, "OBJET", True),
    ("22222222-2222-2222-2222-00000000001a", "11111111-1111-1111-1111-000000000011", "2026-07-13T16:40:00+00:00", 310, 4, "SERIE_P", 10, "QUESTION", False),
    ("22222222-2222-2222-2222-00000000001b", "11111111-1111-1111-1111-000000000012", "2026-07-19T10:20:00+00:00", 200, 6, "SERIE_C", 10, "OBJET", True),
    ("22222222-2222-2222-2222-00000000001c", "11111111-1111-1111-1111-000000000012", "2026-07-21T12:45:00+00:00", 425, 7, "SERIE_P", 10, "OBJET", True),
    ("22222222-2222-2222-2222-00000000001d", "11111111-1111-1111-1111-000000000013", "2026-07-24T15:00:00+00:00", 295, 3, "CHRONO", 10, "OBJET", False),
]


def _build_reponses():
    reponses = []
    reponse_idx = 1
    questions_by_categorie = {
        categorie: group.to_dict("records")
        for categorie, group in df_question_test.groupby("categorie")
    }
    for session_id, _, session_date, _, nb_correct, _, nb_questions, session_type, a_fini in _SESSIONS:
        pool = questions_by_categorie.get(session_type, df_question_test.to_dict("records"))
        nb_reponses = nb_questions if a_fini else max(nb_correct + 2, 5)
        nb_reponses = min(nb_reponses, nb_questions)
        for i in range(nb_reponses):
            question = pool[i % len(pool)]
            question_id = question["id"]
            bonne_reponse = question["reponse"]
            is_correct = i < nb_correct
            user_reponse = bonne_reponse if is_correct else not bonne_reponse
            reponses.append(
                (
                    f"66666666-6666-6666-6666-{reponse_idx:012x}",
                    session_id,
                    question_id,
                    user_reponse,
                    is_correct,
                    session_date,
                )
            )
            reponse_idx += 1
    return reponses


_REPONSES = _build_reponses()

df_ile_test = pd.DataFrame(
    [{"id": ile_id, "nom_ile": nom_ile} for ile_id, nom_ile in _ILES]
)

df_commune_test = pd.DataFrame(
    [
        {"id": commune_id, "ile_id": ile_id, "nom_commune": nom_commune}
        for commune_id, ile_id, nom_commune in _COMMUNES
    ]
)

df_profile_test = pd.DataFrame(
    [
        {
            "id": profile_id,
            "username": username,
            "email": email,
            "commune_id": commune_id,
            "created_at": created_at,
            "updated_at": created_at,
        }
        for profile_id, username, email, created_at, commune_id in _PROFILES
    ]
)

df_score_session_test = pd.DataFrame(
    [
        {
            "id": session_id,
            "profile_id": profile_id,
            "date": session_date,
            "temps_total": temps_total,
            "nb_correct": nb_correct,
            "mode": mode,
            "nb_questions": nb_questions,
            "type": type,
            "a_fini": a_fini,
            "updated_at": session_date,
        }
        for session_id, profile_id, session_date, temps_total, nb_correct, mode, nb_questions, type,a_fini in _SESSIONS
    ]
)

df_reponse_question_test = pd.DataFrame(
    [
        {
            "id": reponse_id,
            "score_session_id": score_session_id,
            "question_id": question_id,
            "user_reponse": user_reponse,
            "is_correct": is_correct,
            "created_at": created_at,
        }
        for reponse_id, score_session_id, question_id, user_reponse, is_correct, created_at in _REPONSES
    ]
)
