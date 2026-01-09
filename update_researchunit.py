import os, re, io, sys
sys.path.append(os.path.abspath('..\\Dependencies\\'))
import pandas as pd
from dotenv import load_dotenv
from pathlib import Path

from RU_Req import etl_researchunit, sc_researchunit

import time
import gc



from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# Charger le fichier .env pour récupérer les variables d'environnement
load_dotenv()

pd.options.mode.copy_on_write = True

###################################################################### GESTION DES PARAMETRES

# Récupérer le chemin de sauvegarde depuis les variables d'environnement
SAVE_PATH = os.getenv('SAVE_PATH')

filename = 'Sugar_researchunits'  # Nom du fichier à utiliser pour la sauvegarde

# Charger le fichier CSV existant s'il existe, sinon mettre à None
file_path = Path(SAVE_PATH + filename +'_lastupdate.csv')
file_hist = Path(SAVE_PATH + filename +'_summary.csv')

######################################################### VALIDATION DES CONNEXION AUX BASES
# Affichage de la date de lancement du service
NOW = datetime.now()
print('________________________________________________________________')
print(f'service lancé le {NOW}')

try:
    df_ru = etl_researchunit()
    df_ru.to_csv(file_path,index=False, encoding='utf-8-sig')
except Exception as e:
    print(f"Erreur lors de la mise à jour de {file_path}: {e}")

print(f"Succés de la Mise à jour du fichier {file_path} Taille:  {os.path.getsize(file_path)/(1024 * 1024):.2f} Mo")

try:
    nowdate = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    #row_df = pd.DataFrame([ru.sc_researchunit(df_ru, datetime(2020,12,31))])
    row_df = pd.DataFrame([sc_researchunit(df_ru, nowdate)])


    if file_hist.exists():
        df = pd.read_csv(file_hist, encoding='utf-8')
        df["date"] = pd.to_datetime(df["date"], errors='coerce')
        df_summary = df[df["date"].dt.strftime('%m-%d').isin(["12-31", "03-31", "06-30", "09-30"])]
        df_summary = pd.concat([row_df, df_summary]).reset_index(drop=True)
        df_summary.to_csv(file_hist, index=False, encoding='utf-8')

    else:
        row_df.to_csv(file_hist, encoding='utf-8')

    print(f"{filename} a été créé avec succès. Taille:  {os.path.getsize(file_path)/(1024 * 1024):.2f} Mo")

except Exception as e:
    print(f"Erreur lors de la mise à jour de   {file_hist}: {e}")

#