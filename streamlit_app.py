import pandas as pd
import streamlit as st


# ---------------------------------------------------------
# Configuration générale de l'application
# ---------------------------------------------------------

st.set_page_config(
    page_title="NutriPhoto",
    page_icon="🍽️",
    layout="wide",
)


# ---------------------------------------------------------
# Petite base nutritionnelle temporaire
# Valeurs approximatives pour 100 g
# ---------------------------------------------------------

BASE_ALIMENTS = {
    "Blanc de poulet cuit": {
        "calories": 165.0,
        "proteines": 31.0,
    },
    "Riz basmati cuit": {
        "calories": 130.0,
        "proteines": 2.7,
    },
    "Pâtes cuites": {
        "calories": 150.0,
        "proteines": 5.0,
    },
    "Œuf entier": {
        "calories": 140.0,
        "proteines": 12.5,
    },
    "Saumon cuit": {
        "calories": 208.0,
        "proteines": 20.0,
    },
    "Steak haché 5 % cuit": {
        "calories": 170.0,
        "proteines": 26.0,
    },
    "Thon au naturel égoutté": {
        "calories": 116.0,
        "proteines": 26.0,
    },
    "Lentilles cuites": {
        "calories": 116.0,
        "proteines": 9.0,
    },
    "Brocoli cuit": {
        "calories": 35.0,
        "proteines": 2.4,
    },
    "Fromage blanc": {
        "calories": 75.0,
        "proteines": 8.0,
    },
}


# ---------------------------------------------------------
# Initialisation de la mémoire temporaire de l'application
# ---------------------------------------------------------

if "aliments_repas" not in st.session_state:
    st.session_state.aliments_repas = []

if "proteines_avant_repas" not in st.session_state:
    st.session_state.proteines_avant_repas = 0.0


# ---------------------------------------------------------
# Fonctions de calcul
# ---------------------------------------------------------

def calculer_nutriments(nom_aliment, quantite):
    """
    Calcule les calories et les protéines pour une quantité donnée.

    Les valeurs de la base sont exprimées pour 100 grammes.
    """

    valeurs = BASE_ALIMENTS[nom_aliment]

    calories = valeurs["calories"] * quantite / 100
    proteines = valeurs["proteines"] * quantite / 100

    return calories, proteines


def ajouter_aliment(nom_aliment, quantite):
    """
    Ajoute un aliment et ses valeurs calculées au repas courant.
    """

    calories, proteines = calculer_nutriments(
        nom_aliment,
        quantite,
    )

    nouvel_aliment = {
        "Aliment": nom_aliment,
        "Quantité (g)": quantite,
        "Calories (kcal)": round(calories, 1),
        "Protéines (g)": round(proteines, 1),
    }

    st.session_state.aliments_repas.append(nouvel_aliment)


def supprimer_dernier_aliment():
    """
    Supprime le dernier aliment ajouté au repas.
    """

    if st.session_state.aliments_repas:
        st.session_state.aliments_repas.pop()


def vider_repas():
    """
    Supprime tous les aliments du repas courant.
    """

    st.session_state.aliments_repas = []


# ---------------------------------------------------------
# En-tête
# ---------------------------------------------------------

st.title("🍽️ NutriPhoto")

st.write(
    "Photographier, corriger et comptabiliser "
    "les apports nutritionnels d'un repas."
)

st.info(
    "Cette première version utilise une saisie manuelle. "
    "L'analyse automatique des photographies sera ajoutée plus tard."
)


# ---------------------------------------------------------
# Mise en page principale
# ---------------------------------------------------------

colonne_repas, colonne_objectif = st.columns([2, 1])


# ---------------------------------------------------------
# Colonne de gauche : photographie et aliments
# ---------------------------------------------------------

with colonne_repas:

    st.header("1. Photographie du repas")

    mode_photo = st.radio(
        "Comment veux-tu ajouter la photographie ?",
        [
            "Importer une image",
            "Utiliser la caméra",
        ],
        horizontal=True,
    )

    photo = None

    if mode_photo == "Importer une image":
        photo = st.file_uploader(
            "Sélectionne une photographie",
            type=["jpg", "jpeg", "png"],
        )

    else:
        photo = st.camera_input(
            "Prendre une photographie du repas"
        )

    if photo is not None:
        st.image(
            photo,
            caption="Photographie du repas",
            width="stretch",
        )

        st.warning(
            "Pour le moment, la photographie est uniquement affichée. "
            "Elle n'est pas encore analysée automatiquement."
        )

    st.divider()

    st.header("2. Ajouter les aliments")

    nom_aliment = st.selectbox(
        "Aliment",
        options=list(BASE_ALIMENTS.keys()),
    )

    quantite = st.number_input(
        "Quantité estimée en grammes",
        min_value=1,
        max_value=2000,
        value=100,
        step=10,
    )

    valeurs_selection = BASE_ALIMENTS[nom_aliment]

    st.caption(
        f"Pour 100 g : "
        f"{valeurs_selection['calories']:.1f} kcal et "
        f"{valeurs_selection['proteines']:.1f} g de protéines."
    )

    calories_previsualisation, proteines_previsualisation = (
        calculer_nutriments(
            nom_aliment,
            quantite,
        )
    )

    col_calories, col_proteines = st.columns(2)

    with col_calories:
        st.metric(
            "Calories estimées",
            f"{calories_previsualisation:.1f} kcal",
        )

    with col_proteines:
        st.metric(
            "Protéines estimées",
            f"{proteines_previsualisation:.1f} g",
        )

    if st.button(
        "Ajouter cet aliment au repas",
        type="primary",
        use_container_width=True,
    ):
        ajouter_aliment(
            nom_aliment,
            quantite,
        )

        st.success(
            f"{nom_aliment} ajouté au repas."
        )

    st.divider()

    st.header("3. Contenu du repas")

    if st.session_state.aliments_repas:

        tableau_repas = pd.DataFrame(
            st.session_state.aliments_repas
        )

        st.dataframe(
            tableau_repas,
            width="stretch",
            hide_index=True,
        )

        total_calories = tableau_repas[
            "Calories (kcal)"
        ].sum()

        total_proteines = tableau_repas[
            "Protéines (g)"
        ].sum()

        col_total_calories, col_total_proteines = st.columns(2)

        with col_total_calories:
            st.metric(
                "Total du repas",
                f"{total_calories:.1f} kcal",
            )

        with col_total_proteines:
            st.metric(
                "Protéines du repas",
                f"{total_proteines:.1f} g",
            )

        col_supprimer, col_vider = st.columns(2)

        with col_supprimer:
            if st.button(
                "Supprimer le dernier aliment",
                use_container_width=True,
            ):
                supprimer_dernier_aliment()
                st.rerun()

        with col_vider:
            if st.button(
                "Vider le repas",
                use_container_width=True,
            ):
                vider_repas()
                st.rerun()

    else:
        total_calories = 0.0
        total_proteines = 0.0

        st.info(
            "Aucun aliment n'a encore été ajouté au repas."
        )


# ---------------------------------------------------------
# Colonne de droite : objectif quotidien
# ---------------------------------------------------------

with colonne_objectif:

    st.header("🎯 Objectif quotidien")

    objectif_proteines = st.number_input(
        "Objectif quotidien de protéines",
        min_value=1,
        max_value=500,
        value=120,
        step=5,
        help="Valeur personnelle modifiable.",
    )

    proteines_avant_repas = st.number_input(
        "Protéines déjà consommées aujourd'hui",
        min_value=0.0,
        max_value=500.0,
        value=float(
            st.session_state.proteines_avant_repas
        ),
        step=5.0,
    )

    st.session_state.proteines_avant_repas = (
        proteines_avant_repas
    )

    total_journee = (
        proteines_avant_repas
        + total_proteines
    )

    progression = min(
        total_journee / objectif_proteines,
        1.0,
    )

    st.progress(progression)

    st.metric(
        "Protéines consommées",
        f"{total_journee:.1f} g",
        delta=(
            f"{total_journee - objectif_proteines:.1f} g "
            "par rapport à l'objectif"
        ),
    )

    proteines_restantes = max(
        objectif_proteines - total_journee,
        0.0,
    )

    if proteines_restantes > 0:
        st.write(
            f"Il reste **{proteines_restantes:.1f} g** "
            "de protéines pour atteindre l'objectif."
        )

    else:
        st.success(
            "Objectif quotidien atteint !"
        )

    st.divider()

    st.subheader("Limites de cette version")

    st.write(
        "- Les portions sont saisies manuellement.\n"
        "- Les valeurs nutritionnelles sont indicatives.\n"
        "- Le repas disparaît si la session est réinitialisée.\n"
        "- La photographie n'est pas encore analysée.\n"
        "- L'historique n'est pas encore enregistré."
    )


# ---------------------------------------------------------
# Pied de page
# ---------------------------------------------------------

st.divider()

st.caption(
    "NutriPhoto est un outil personnel d'estimation. "
    "Les résultats ne constituent pas une mesure médicale."
)
