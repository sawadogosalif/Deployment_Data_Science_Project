import requests
from pathlib import Path
import datetime as dt
import gzip
import os
import pandas as pd
## creation liste date
liste_mois_annee = [
    f'synop.{a}{m:02d}.csv.gz'
    for a in range(1996, 2023) for m in range(1, 13)
    if dt.datetime(a, m, 1) < dt.datetime.now()]
## Boucle pour télécharger l'ensemble des fichiers
for filename in liste_mois_annee:
    lien = f'https://donneespubliques.meteofrance.fr/donnees_libres/Txt/Synop/Archive/{filename}'
    if not Path('../output/', filename[:-3]).exists() :
        res = requests.get(lien)
        if res.status_code== 200:
            Path('../output', filename[:-3]).write_bytes(gzip.decompress(res.content))
# supprimer les dernier fichier excel            
list(Path('../output').glob('*csv'))[-1].unlink()
## Concaténation et lecture des csv
dfs = [pd.read_csv('../output/'+a[:-3],sep=";") for a in liste_mois_annee[:-1]]
df_final = pd.concat(dfs, ignore_index=True)
df_final.to_pickle('../output/weather_data_full.sav')