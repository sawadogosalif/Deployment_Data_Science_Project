# -*- coding: utf-8 -*-

import os
import pandas as pd
import pickle5 as pickle




###########################################################################
###########################################################################
# Constantes vers les répertoires et les pickles
###########################################################################
###########################################################################
#les pickles sont stockés dans le sous-répertoire deployment
PROJECT_DIR = os.path.dirname(os.path.realpath("__file__"))
MODEL_PATH    = os.path.join(PROJECT_DIR , "scoring.pkl")
REF_PATH    = os.path.join(PROJECT_DIR , "treshold.pkl")


############################################################################
############################################################################
# Rechargement de la pipeline de transformation et du modèle V1
#  (seulement au lancement de l'application)
############################################################################
modele = pickle.load( open( MODEL_PATH, "rb" ) )
ref = pickle.load( open( REF_PATH, "rb" ) )




############################################################################

############################################################################
# Partie spécifique à streamlit
############################################################################
############################################################################
import streamlit as st

Status_of_existing_checking_account  = st.sidebar.selectbox("Status of existing checking_account", ['no checking account', '<0 DM', '0 <= <200 DM','>= 200 DM'])
Credit_history  = st.sidebar.selectbox("Credit  history", ['existing credits paid back duly till now','critical account','delay in paying off','all credits at this bank paid back duly','no credits taken'])
Duration_in_month_q  = st.sidebar.selectbox("Duration in month", ['(3.999, 12.0]' ,'(12.0, 15.0]','(15.0, 24.0]', '(24.0, 30.0]','(30.0, 72.0]'])
Savings_account_bonds  = st.sidebar.selectbox("Savings account bonds", ['<100 DM', 'no savings account', '100 <= <500 DM','500 <= < 1000 DM','>= 1000 DM'])
Housing  = st.sidebar.selectbox("Housing", ['rent', 'own', 'for free'])
Purpose  = st.sidebar.selectbox("Purpose", ['radio/télévision', 'car (new)', 'furniture/equipment','car (used)','business','education','repairs','domestic appliances','retraining','others'])
Other_installment_plans = st.sidebar.selectbox("Other installment plans", ['none', 'bank', 'store'])






#page principale
st.header("**Prédiction probabilité d'être un mauvais payeur**")

st.subheader("Paramètres renseignés")
st.write(f"Status of existing checking account: {Status_of_existing_checking_account}")
st.write(f"Credit history: {Credit_history}")
st.write(f"Duration in month_q: {Duration_in_month_q}")
st.write(f"Savings account bonds: {Savings_account_bonds}")
st.write(f"Housing: {Housing}")
st.write(f"Other installment plans: {Other_installment_plans}")


X_profil = pd.DataFrame(     [[          Status_of_existing_checking_account, 
                                                Credit_history,
                                                Duration_in_month_q,
                                                Savings_account_bonds, 
                                                Housing,
                                                Purpose,
                                                Other_installment_plans,
                               ]],
                                    columns=[ 'Status_of_existing_checking_account', 
                                             'Credit_history', 'Duration_in_month_q',
                                             'Savings_account_bonds','Housing',
                                             'Purpose', 'Other_installment_plans'
                                            ]
                        )

  
if(st.button("Calculer le score")): 
    proba = round(modele.predict(X_profil).iloc[0],3)


    # appeler la fonclion cliked_button lorsqu'on appui sur cliquer
    st.subheader("Résultat du score")
    st.write(f"Probabilité calculée {proba}")
    if proba< ref:
       st.success("Client crédible  : 👍 Go pour le crédit")
    else:
       st.error("Probabilité >= 20% : 😭 Refus du crédit")
