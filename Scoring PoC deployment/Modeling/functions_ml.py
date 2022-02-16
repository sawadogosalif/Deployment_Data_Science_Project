# -*- coding: utf-8 -*-
"""
Created on Thu Feb 11 01:47:20 2022


@author: Salif sawadogo
11/02/2022    1ère version qui va vite évoluer
"""

import numpy as np
import pandas as pd
import scipy.stats as scipy_stats
import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, roc_auc_score


def valid_df(df, id_var='', df_name='', edit_head = True, edit_tail = True, edit_describe =  True):
    """
    calcul de stats de base sur un df pour faciliter sa validation
	
	df : pandas dataframe
	df_name : nom du data frame pour l'afficher
		optionnel : par défaut on met ''
	id_var : indiquer le nom de la colonne qui contient l'id
		si un nom est indiqué on vérifiera les doublons
		defaut = ''
	edit_head : Affichage des premières lignes
				Indiquez False pour ne pas les voir
		defaut : True
	edit_tail : Affichage des dernières lignes
				Indiquez False pour ne pas les voir
		defaut : True
	edit_describe : Affichage du describe
				Indiquez False pour ne pas le voir
		defaut : True
		
	Exemples:
	
	1. Exemple minimal
		valid_df(df)
		
	2. Exemple avec affichage du nom du dataframe et verif des doublons
		mais pas d'affichage du head, tail et describe
		valid_df(df, id_var='id_client', df_name='df_achats'
			, edit_head = False, edit_tail = False, edit_describe =  False)
		
	
    """
    print("===========================")
    print("===========================")
    print("Synthese de la table")
    if df_name != '':
        print("=== DF : " + df_name)
    print("===========================")
    print("===========================")
    
    print('============================')
    print("nb de lignes et de colonnes")
    print('============================')
    print(df.shape ) #pas de () c'est un attribut
    print("")
        
    print('=======================================')
    print("type, missing et nb de modalites <>")
    print('=======================================')
    info_list = []
    for c in df.columns:
        df_freq = df[c].value_counts().reset_index()
        df_freq['zzvalue'] =  df_freq['index'].astype(str) + " (" \
                            + df_freq[c].astype(str) + " obs)"
        #df_freq = df_freq[['zzvalue']][:20].T
           
        info_list.append( ( c, df[c].dtypes, df[c].isna().sum(), df[c].isna().sum()/len(df)
                         , len(pd.unique(df[c]))) 
                         + tuple(df_freq['zzvalue'][:20]))
        
    nb_zzvalues = max(map(len,info_list)) - 5
    #pd.unique(df[c]) renvoie la liste des valeurs unique de la colonne
    df_stats = pd.DataFrame(info_list, columns=['column','type','missing_count','missing_rate'
                                                , 'nb_labels']
                                + [f'value_{i}' for i in range(1,nb_zzvalues+1)])
    print(df_stats)
    
    if id_var != '':
        print('=======================================')
        print('Doublon')
        print('=======================================')
        print("aucun doublon d'ID si la valeur la + fréquente est égale à 1")
        print( df[id_var].value_counts()[:1] )

        print( 'nb duplicates :' , sum(df.duplicated(subset=[id_var], keep='first')) )
        print("")    
        
    if edit_head == True:
        print('============================')
        print("premieres lignes")
        print('============================')
        print( df.head() )  #head() c'est une fonction,  une méthode d'une classe
        print("")
        
    if edit_tail == True:
        print('============================')
        print("dernières lignes")
        print('============================')
        print( df.tail() )
        print("")
        
    if edit_describe == True:   
        print('=======================================')	
        print('résumé de chaque variable')
        print('=======================================')
        print( df.describe(include='all') )
        print("")
		
    return df_stats
    
    
def customize_corr(df: pd.DataFrame) :
    
    """ 
      Customize correlation matrix visually  
      
    Arguments:
        df - dataframe with features
    
    Returns: 
    """
    

    plt.figure(figsize=(16, 10))
    
    # define the mask to set the values in the upper triangle to True
    mask = np.triu(np.ones_like(df.corr()))
    heatmap = sns.heatmap(df.corr(), mask=mask, vmin=-1, vmax=1, annot=True, cmap='magma')
    heatmap.set_title('Lower Correlation Matrix', fontdict={'fontsize':18}, pad=16)


def features_ordering(df , feature_names, target):
    """
    Retourne un df avec une ligne par feature par ordre décroissant des T de Schupprow en fonction d'une variable cible Y
    
    Parametres :
        X : pandas dataframe
        feature_names : liste des nom des colonnes dont l'on souhaite avoir les stats du chi2
            => ne pas mettre d'id ou de variables numériques avec trop de modalité
        target : nom de la variable cible (Y)
    
    Exemple d'appel :
        
        features_ordering =  features_ordering(  df = df_xy 
                                               , feature_names = ['gender','csp','region']
                                               , target        = 'target' )   
    """

    
    #déclaration de la liste qui contiendra les résultats
    l_stats = []
    
    #boucle sur chaque variable
    for i,col in enumerate(feature_names):
        if col != target:
        
            #calcul du tableau de contingence
            cont = pd.crosstab(df[col], df[target],)
                
            #calcul des stats du chi-2 pour ce tableau de contingence
            chi2, proba, vc, ts = get_chi2_vc_ts(cont)
            
            #ajouts des indicateurs
            l_stats.append( (target,col, round(vc, 4), round(ts, 4), round(chi2, 4), round(proba, 4) ))
            
    #compilation des stats démandées dans un dataframe et tri selon le critère de T de Schupprow
    df_vc_ts = pd.DataFrame(data = l_stats, columns = [ 'target','variable', 'VC', 'TS', 'CHI2', 'p_value'])    
    df_vc_ts = df_vc_ts.sort_values(by=['TS','variable'], ascending=[False, True])
        
    return df_vc_ts

def get_chi2_vc_ts(crosstab):
    """
        Le calcul du VC et TS doit être revu !! mais bon pour le moment on va s'en servir quand même :-)
    
        FONCTION DE CALCUL DU CHI2, T DE TSCHUPROW ET V DE CRAMER
        
        return 4 values : chi2, proba of chi2, V of Cramer, T of Tschuprow
        
        parameters :      
        crosstab  = crosstab dataframe
        
    """
    
    nb_obs = crosstab.values.sum()
    k1 = crosstab.shape[0]
    k2 = crosstab.shape[1]
    if min(crosstab.shape) >1:
        khi2, proba, _,_ = scipy_stats.chi2_contingency(crosstab)
        vc = np.sqrt(khi2 / (nb_obs*(min(crosstab.shape)-1)))
        ts = np.sqrt(khi2 / (nb_obs*np.sqrt((k1-1)*(k2-1))))
    else:
        khi2, proba, vc, ts = -1, 10000, -1, -1
    
    return khi2, proba, vc, ts


def corr_features(df: pd.DataFrame, threshold: float) :
    
    """  
      A function to suggest features that are highly correlated (one among two). 
            
      Arguments:
          df - dataframe with features
          treshold - lower limit to consider that features are not highly correlated
    
    Returns:  
        List of features to drop
    """
    
    correlation = df.corr().abs()
    upper = correlation .where(np.triu(np.ones(correlation .shape), k=1).astype(np.bool))
    to_drop = [column for column in upper.columns if any(upper[column] > threshold)]
    
    return to_drop
    

def confusio_matrix(y_test, y_predicted):
  cm = confusion_matrix(y_test, y_predicted)
  tn, fp, fn, tp = confusion_matrix(y_test, y_predicted).astype(int).ravel()
  print("Accuracy:", round((tp + tn)/(tp+tn+fp+fn),2))
  print("Recall:", round(tp /(tp+fn),2))
  print("precision:", round( tp/(tp+fp),2))
  plt.figure(figsize=(5,5))
  plt.clf()
  plt.imshow(cm, interpolation='nearest',cmap=plt.cm.Wistia)
  classNames = ['Negative','Positive']
  plt.title('Matrice de confusion')
  plt.ylabel('True label')
  plt.xlabel('Predicted label')
  tick_marks = np.arange(len(classNames))
  plt.xticks(tick_marks, classNames, rotation=45)
  plt.yticks(tick_marks, classNames)
  s = [['TN','FP'], ['FN', 'TP']]
  
  for i in range(2):
      for j in range(2):
          plt.text(j,i, str(s[i][j])+" = "+str(cm[i][j]))
  plt.show()
  
  
    
 
def correlation_list_to_matrix(df_corr, criterion):
    """
    Transformation de la liste des corrélation en matrice des corrélations
        afin de l'intégrer dans un heatmap ou pour l'exporter dans un rapport
        
    La fonction renvoie un dataframe.
    
    Si un couple de variables n'est pas trouvé => c'est une erreur
        la valeur écrite dans la matrice sera 1000 (pour alerter l'utilisateur)
    
    -------------------
    Paramètres :
        
    df_corr : dataframe issu de la fonction features_correlation
                il doit avoir les deux variables 'variable_1' et 'variable_2'
                  + la variable indiquée dans le paramètre criterion (par ex 'TS', 'VC')
              
    criterion = une colonne numérique de la matrice df_corr
            C'est la valeur de ce critère qui sera affiché dans la matrice
        
    -------------------
    Exemples d'appels :
        df_corr =  utils_ml.features_correlation(df_train, feature_names = ['foreign worker'
                                            , 'Personal status and sex', 'Other debtors])

        df_corr_matrix = utils_ml.correlation_list_to_matrix(df_corr, criterion = 'TS')
    """
    
    # Récupération de la liste des variables
    columns = sorted(df_corr['variable_1'].unique())

    #Création de la matrice vide
    corr_matrix = np.zeros(shape=(len(columns),len(columns)))
    
    #Remplissage de la matrice
    for i,c1 in enumerate(columns):
        for j,c2 in enumerate(columns):
            if c1 == c2:
                corr_matrix[i,j] = 1
            else:
                df_corr_temp = df_corr[  (df_corr['variable_1'] == c1) & (df_corr['variable_2'] == c2) \
                                       | (df_corr['variable_2'] == c1) & (df_corr['variable_1'] == c2) ]
                if len(df_corr_temp)>0:
                    df_corr_temp = df_corr_temp.reset_index()
                    corr_matrix[i,j] = df_corr_temp.loc[0,criterion]
                else:
                    corr_matrix[i,j] = 1000
                    
    df_corr_matrix = pd.DataFrame(corr_matrix, columns=columns, index=columns)

    return df_corr_matrix
	

def summary_table(train_Xy, cols_list , target):
    """
    La fonction renvoie un df de synthèse des variables explicatives en fonction d'une target numérique (binaire ok)
    On calcule pour chaque modalité de chaque variable : sa fréquence et fréquence relative et sa moyenne
    
    en + 2 variables :
        - 'nb_values' : nb de modalités de la variables
        - 'nb_rows'   : nb de lignes dans la table (=> identique sur toutes les lignes)
    
    remarque : les valeurs manquantes ne sont pas considérées par défaut
               => si besoin utilisez df=df.fillna('') avant cette fonction
               
        parametres obligatoires:
             train_Xy   : nom du df contenant les variables explicatives et la variable cible
             cols_list  : liste des variables explicatives (plutôt discrètes ou continues avec peu de moda)
                          car la table créé en sortie contiendra une ligne par valeur
                          EVITEZ la variable d'identifiant de ligne :-)
            target      : variable cible qui doit être numérique (binaire ok également)
            
             
    """
    nb_rows   = len(train_Xy)
    all_synth = pd.DataFrame()
    
    for c in cols_list:
        if c != target:
            print(c)
            synth = train_Xy[c].value_counts().reset_index().rename(columns={'index':c, c:'freq'})
            mean  = train_Xy.groupby([c])[target].mean().reset_index()

    
            synth = pd.merge(synth,mean, on=c)
            synth.columns = ['value', 'freq','pct_target']
            
            synth['variable'] = c
            synth['nb_values']= len(synth)
            synth['pct_freq'] = synth['freq'] / nb_rows
            synth['nb_rows'] =  nb_rows
            synth['target'] =  target
                 
            #les 3 colonnes suivantes serviront pour le recodage effectué dans excel
            synth['code_recode']=''
            synth['code_recode2']=''
            synth['code_recode3']=''       
            
            all_synth= pd.concat([all_synth, synth])
        
        all_synth = all_synth.sort_values(by=['variable', 'pct_target'], ascending=[True, False])
        all_synth = all_synth[ ['nb_values', 'variable', 'value', 'freq', 'pct_freq', 'pct_target'
                                , 'nb_rows','target', 'code_recode', 'code_recode2', 'code_recode3' ]]    
        
    return all_synth
	
def stamp(message='', log_file='', refresh=0):
    """
	Petite fonction de log
	
    Elle affiche un message dans l'output (prefixé par un horodatage)
    Optionnellement, elle écrit dans un fichier de log si le paramètre log_file est différent de ''
	
	Parametres
	----------
	
	message : str 
		message à afficher (et à écrire dans le fichier de log s'il y en a un d'indiqué) 
	log_file : str
		chemin complet du fichier de log
	refresh : int, default : 0
		Indiquez 1 pour vider le fichier de log avant d'écrire le message	
    """
    log_line = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ":  " + str(message)
    print(log_line)  
    if log_file != '':  
        if refresh!=1:    
            with open(log_file, "a") as myfile:
                myfile.write(log_line+ '\n')         
        else:
            with open(log_file, "w") as myfile:           
                myfile.write(log_line+ '\n')
