import pandas as pd
import streamlit as st


# =========================================================
# CONFIGURATION DE L'APPLICATION
# =========================================================

st.set_page_config(
    page_title="NutriPhoto",
    page_icon="🍽️",
    layout="wide",
)
# =========================================================
# PROTECTION DE L'APPLICATION PAR MOT DE PASSE
# =========================================================

def verifier_mot_de_passe():
    """
    Affiche un écran de connexion simple.

    Le véritable mot de passe est stocké dans les secrets
    de Streamlit et n'apparaît jamais dans GitHub.
    """

    if "authentifie" not in st.session_state:
        st.session_state.authentifie = False

    if st.session_state.authentifie:
        return True

    st.title("🔒 Connexion à NutriPhoto")

    mot_de_passe_saisi = st.text_input(
        "Mot de passe",
        type="password",
    )

    if st.button(
        "Se connecter",
        type="primary",
    ):
        if mot_de_passe_saisi == st.secrets["APP_PASSWORD"\]:
            st.session_state.authentifie = True
            st.rerun()
        else:
            st.error("Mot de passe incorrect.")

    return False


if not verifier_mot_de_passe():
    st.stop()

# =========================================================
# BASE NUTRITIONNELLE TEMPORAIRE
# Toutes les valeurs sont données pour 100 grammes.
# =========================================================

BASE_ALIMENTS = {
    "Blanc de poulet cuit": {
        "calories": 165.0,
        "proteines": 31.0,
        "glucides": 0.0,
        "lipides": 3.6,
    },
    "Riz basmati cuit": {
        "calories": 130.0,
        "proteines": 2.7,
        "glucides": 28.0,
        "lipides": 0.3,
    },
    "Pâtes cuites": {
        "calories": 150.0,
        "proteines": 5.0,
        "glucides": 30.0,
        "lipides": 1.1,
    },
    "Œuf entier": {
        "calories": 140.0,
        "proteines": 12.5,
        "glucides": 0.7,
        "lipides": 9.7,
    },
    "Saumon cuit": {
        "calories": 208.0,
        "proteines": 20.0,
        "glucides": 0.0,
        "lipides": 13.0,
    },
    "Steak haché 5 % cuit": {
        "calories": 170.0,
        "proteines": 26.0,
        "glucides": 0.0,
        "lipides": 7.0,
    },
    "Thon au naturel égoutté": {
        "calories": 116.0,
        "proteines": 26.0,
        "glucides": 0.0,
        "lipides": 1.0,
    },
    "Lentilles cuites": {
        "calories": 116.0,
        "proteines": 9.0,
        "glucides": 20.0,
        "lipides": 0.4,
    },
    "Brocoli cuit": {
        "calories": 35.0,
        "proteines": 2.4,
        "glucides": 7.0,
        "lipides": 0.4,
    },
    "Fromage blanc": {
        "calories": 75.0,
        "proteines": 8.0,
        "glucides": 4.0,
        "lipides": 3.0,
    },
    "Banane": {
        "calories": 89.0,
        "proteines": 1.1,
        "glucides": 22.8,
        "lipides": 0.3,
    },
    "Flocons d'avoine": {
        "calories": 370.0,
        "proteines": 13.0,
        "glucides": 60.0,
        "lipides": 7.0,
    },
}


# =========================================================
# INITIALISATION DE LA SESSION
# =========================================================

if "aliments_repas" not in st.session_state:
    st.session_state.aliments_repas = []

if "objectif_proteines" not in st.session_state:
    st.session_state.objectif_proteines = 120

if "proteines_avant_repas" not in st.session_state:
    st.session_state.proteines_avant_repas = 0.0


# =========================================================
# FONCTIONS
# =========================================================

def calculer_nutriments(nom_aliment, quantite):
    """
    Calcule les nutriments d'un aliment pour une quantité donnée.

    Les valeurs de BASE_ALIMENTS sont données pour 100 grammes.
    """

    valeurs = BASE_ALIMENTS[nom_aliment]
    coefficient = quantite / 100

    return {
        "Calories (kcal)": valeurs["calories"] * coefficient,
        "Protéines (g)": valeurs["proteines"] * coefficient,
        "Glucides (g)": valeurs["glucides"] * coefficient,
        "Lipides (g)": valeurs["lipides"] * coefficient,
    }


def creer_ligne_aliment(nom_aliment, quantite):
    """
    Crée une ligne complète pour le tableau du repas.
    """

    nutriments = calculer_nutriments(
        nom_aliment,
        quantite,
    )

    return {
        "Supprimer": False,
        "Aliment": nom_aliment,
        "Quantité (g)": float(quantite),
        "Calories (kcal)": round(
            nutriments["Calories (kcal)"],
            1,
        ),
        "Protéines (g)": round(
            nutriments["Protéines (g)"],
            1,
        ),
        "Glucides (g)": round(
            nutriments["Glucides (g)"],
            1,
        ),
        "Lipides (g)": round(
            nutriments["Lipides (g)"],
            1,
        ),
    }


def recalculer_tableau(tableau):
    """
    Recalcule les nutriments après modification des quantités.

    Cette fonction évite que l'utilisateur modifie directement
    les calories ou les protéines.
    """

    tableau_recalcule = tableau.copy()

    for index, ligne in tableau_recalcule.iterrows():

        nom_aliment = ligne["Aliment"]
        quantite = float(ligne["Quantité (g)"])

        nutriments = calculer_nutriments(
            nom_aliment,
            quantite,
        )

        tableau_recalcule.at[
            index,
            "Calories (kcal)",
        ] = round(nutriments["Calories (kcal)"], 1)

        tableau_recalcule.at[
            index,
            "Protéines (g)",
        ] = round(nutriments["Protéines (g)"], 1)

        tableau_recalcule.at[
            index,
            "Glucides (g)",
        ] = round(nutriments["Glucides (g)"], 1)

        tableau_recalcule.at[
            index,
            "Lipides (g)",
        ] = round(nutriments["Lipides (g)"], 1)

    return tableau_recalcule


def vider_repas():
    """
    Supprime tous les aliments du repas courant.
    """

    st.session_state.aliments_repas = []


# =========================================================
# EN-TÊTE
# =========================================================

st.title("🍽️ NutriPhoto")

st.write(
    "Photographier, corriger et comptabiliser "
    "les apports nutritionnels d'un repas."
)

st.info(
    "Version 2 : ajout des glucides et lipides, "
    "modification des portions et suppression individuelle."
)


# =========================================================
# DISPOSITION GÉNÉRALE
# =========================================================

colonne_repas, colonne_objectif = st.columns(
    [2, 1],
    gap="large",
)


# =========================================================
# COLONNE DE GAUCHE
# =========================================================

with colonne_repas:

    # -----------------------------------------------------
    # PHOTO
    # -----------------------------------------------------

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
            "La photographie est affichée, mais elle n'est "
            "pas encore analysée automatiquement."
        )

    st.divider()

    # -----------------------------------------------------
    # AJOUT D'UN ALIMENT
    # -----------------------------------------------------

    st.header("2. Ajouter un aliment")

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
        f"Valeurs pour 100 g : "
        f"{valeurs_selection['calories']:.1f} kcal, "
        f"{valeurs_selection['proteines']:.1f} g de protéines, "
        f"{valeurs_selection['glucides']:.1f} g de glucides et "
        f"{valeurs_selection['lipides']:.1f} g de lipides."
    )

    previsualisation = calculer_nutriments(
        nom_aliment,
        quantite,
    )

    col_kcal, col_prot, col_gluc, col_lip = st.columns(4)

    with col_kcal:
        st.metric(
            "Calories",
            f"{previsualisation['Calories (kcal)']:.1f}",
        )

    with col_prot:
        st.metric(
            "Protéines",
            f"{previsualisation['Protéines (g)']:.1f} g",
        )

    with col_gluc:
        st.metric(
            "Glucides",
            f"{previsualisation['Glucides (g)']:.1f} g",
        )

    with col_lip:
        st.metric(
            "Lipides",
            f"{previsualisation['Lipides (g)']:.1f} g",
        )

    if st.button(
        "Ajouter cet aliment au repas",
        type="primary",
        use_container_width=True,
    ):

        nouvelle_ligne = creer_ligne_aliment(
            nom_aliment,
            quantite,
        )

        st.session_state.aliments_repas.append(
            nouvelle_ligne
        )

        st.rerun()

    st.divider()

    # -----------------------------------------------------
    # TABLEAU MODIFIABLE
    # -----------------------------------------------------

    st.header("3. Vérifier et corriger le repas")

    if st.session_state.aliments_repas:

        tableau_initial = pd.DataFrame(
            st.session_state.aliments_repas
        )

        tableau_modifie = st.data_editor(
            tableau_initial,
            width="stretch",
            hide_index=True,
            num_rows="fixed",
            disabled=[
                "Aliment",
                "Calories (kcal)",
                "Protéines (g)",
                "Glucides (g)",
                "Lipides (g)",
            ],
            column_config={
                "Supprimer": st.column_config.CheckboxColumn(
                    "Supprimer",
                    help=(
                        "Coche cette case pour supprimer "
                        "l'aliment du repas."
                    ),
                    default=False,
                ),
                "Quantité (g)": st.column_config.NumberColumn(
                    "Quantité (g)",
                    help="Quantité estimée en grammes",
                    min_value=1,
                    max_value=2000,
                    step=10,
                    format="%.0f g",
                ),
                "Calories (kcal)": st.column_config.NumberColumn(
                    "Calories",
                    format="%.1f kcal",
                ),
                "Protéines (g)": st.column_config.NumberColumn(
                    "Protéines",
                    format="%.1f g",
                ),
                "Glucides (g)": st.column_config.NumberColumn(
                    "Glucides",
                    format="%.1f g",
                ),
                "Lipides (g)": st.column_config.NumberColumn(
                    "Lipides",
                    format="%.1f g",
                ),
            },
            key="editeur_repas",
        )

        tableau_modifie = recalculer_tableau(
            tableau_modifie
        )

        st.caption(
            "Après avoir modifié une quantité, clique sur "
            "« Appliquer les modifications » pour recalculer le repas."
        )

        col_appliquer, col_supprimer, col_vider = st.columns(3)

        with col_appliquer:

            if st.button(
                "Appliquer les modifications",
                type="primary",
                use_container_width=True,
            ):

                st.session_state.aliments_repas = (
                    tableau_modifie.to_dict("records")
                )

                st.rerun()

        with col_supprimer:

            if st.button(
                "Supprimer les lignes cochées",
                use_container_width=True,
            ):

                tableau_conserve = tableau_modifie[
                    tableau_modifie["Supprimer"] == False
                ].copy()

                tableau_conserve["Supprimer"] = False

                st.session_state.aliments_repas = (
                    tableau_conserve.to_dict("records")
                )

                st.rerun()

        with col_vider:

            if st.button(
                "Vider le repas",
                use_container_width=True,
            ):

                vider_repas()
                st.rerun()

        tableau_totaux = recalculer_tableau(
            tableau_modifie
        )

        total_calories = tableau_totaux[
            "Calories (kcal)"
        ].sum()

        total_proteines = tableau_totaux[
            "Protéines (g)"
        ].sum()

        total_glucides = tableau_totaux[
            "Glucides (g)"
        ].sum()

        total_lipides = tableau_totaux[
            "Lipides (g)"
        ].sum()

        st.subheader("Total du repas")

        col_total_1, col_total_2 = st.columns(2)
        col_total_3, col_total_4 = st.columns(2)

        with col_total_1:
            st.metric(
                "Énergie",
                f"{total_calories:.1f} kcal",
            )

        with col_total_2:
            st.metric(
                "Protéines",
                f"{total_proteines:.1f} g",
            )

        with col_total_3:
            st.metric(
                "Glucides",
                f"{total_glucides:.1f} g",
            )

        with col_total_4:
            st.metric(
                "Lipides",
                f"{total_lipides:.1f} g",
            )

        # Contrôle par les facteurs énergétiques classiques :
        # protéines : 4 kcal/g
        # glucides : 4 kcal/g
        # lipides : 9 kcal/g

        calories_calculees_macros = (
            total_proteines * 4
            + total_glucides * 4
            + total_lipides * 9
        )

        st.caption(
            "Contrôle énergétique calculé à partir des "
            f"macronutriments : environ "
            f"{calories_calculees_macros:.1f} kcal."
        )

    else:

        total_calories = 0.0
        total_proteines = 0.0
        total_glucides = 0.0
        total_lipides = 0.0

        st.info(
            "Aucun aliment n'a encore été ajouté au repas."
        )


# =========================================================
# COLONNE DE DROITE : OBJECTIF QUOTIDIEN
# =========================================================

with colonne_objectif:

    st.header("🎯 Objectif quotidien")

    objectif_proteines = st.number_input(
        "Objectif quotidien de protéines",
        min_value=1,
        max_value=500,
        value=int(st.session_state.objectif_proteines),
        step=5,
    )

    st.session_state.objectif_proteines = (
        objectif_proteines
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
    )

    proteines_restantes = max(
        objectif_proteines - total_journee,
        0.0,
    )

    if proteines_restantes > 0:

        st.write(
            f"Il reste **{proteines_restantes:.1f} g** "
            "pour atteindre ton objectif."
        )

    else:

        depassement = (
            total_journee - objectif_proteines
        )

        st.success(
            "Objectif quotidien atteint !"
        )

        if depassement > 0:

            st.write(
                f"Objectif dépassé de "
                f"**{depassement:.1f} g**."
            )

    st.divider()

    st.subheader("Résumé du repas")

    st.write(
        f"**Énergie :** {total_calories:.1f} kcal"
    )

    st.write(
        f"**Protéines :** {total_proteines:.1f} g"
    )

    st.write(
        f"**Glucides :** {total_glucides:.1f} g"
    )

    st.write(
        f"**Lipides :** {total_lipides:.1f} g"
    )

    st.divider()

    st.subheader("Limites actuelles")

    st.write(
        "- Les valeurs alimentaires sont indicatives.\n"
        "- Les portions sont encore saisies manuellement.\n"
        "- Le repas n'est pas enregistré définitivement.\n"
        "- La photographie n'est pas encore analysée.\n"
        "- La recette et le mode de cuisson ne sont pas pris en compte."
    )


# =========================================================
# PIED DE PAGE
# =========================================================

st.divider()

st.caption(
    "NutriPhoto est un outil personnel d'estimation. "
    "Les résultats ne constituent pas une mesure médicale."
)
