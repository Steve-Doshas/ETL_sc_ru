import os, re, io
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text
import pymysql

from datetime import datetime
from dateutil.relativedelta import relativedelta
from IT_data_dictionnaries import region_d, ville_region_d, departements_d


pd.options.mode.copy_on_write = True

def extract_department(cp):
    if cp is None:
        return "00"
    if cp.startswith(("97", "98")):  # Cas des DOM-TOM
        return cp[:3]
    return cp[:2]  # Cas classique en métropole


def nettoyer_ville(chaine):
    if not chaine or not isinstance(chaine, str):  # Vérifier si la chaîne est vide ou non valide
        return None
    
    chaine = chaine.lower().strip()  # Convertir en minuscule et enlever espaces inutiles
    chaine = chaine.capitalize()  # Mettre la première lettre en majuscule

    # Supprimer "Cedex" et tout ce qui suit (insensible à la casse)
    chaine = re.sub(r'\bcedex\b.*', '', chaine, flags=re.IGNORECASE).strip()

    return chaine

def get_region(code, city):
    if code == "00":
        return ville_region_d.get(nettoyer_ville(city))
        
    for reg, deps in region_d.items():
        if code in deps:
            return reg
        
def etl_researchunit():
    # Charger le fichier .env pour récupérer les variables d'environnement
    load_dotenv()
    # Récupérer les informations de connexion aux bases de données depuis les variables d'environnement
    SUGAR_URL_CONNECT = os.getenv('SUGAR_URL_CONNECT')

    # Créer une connexion à la base de données SUGAR
    engine_sug = create_engine(f"mysql+pymysql://{os.getenv('SUGAR_USER')}:{os.getenv('SUGAR_PWORD')}@{os.getenv('SUGAR_HOST')}/{os.getenv('SUGAR_DB')}")

    try:
        connection_sug = engine_sug.connect()
        print("Connexion réussie à la base de données SUGAR distante.")
    except Exception as e:
        print(f"Erreur lors de la connexion : {e}")


    ########################################## CHARGEMENT DES DONNÉES SUGAR DE CONTRACTS
    sql_query = ''' 
        SELECT
            ru.id, ru.name, ru.description, ru.acronyme, ru.billing_address_postalcode, ru.billing_address_city,
            ru.delegation_regionale, ru.cotutelles, 
            ru.thematique,ru.vague_renouvellement, ru.mandataire_unique_pi_valo,
            c.title, c.first_name, c.last_name
        FROM researchunits AS ru, contacts AS c
        WHERE ru.deleted = 0
        AND ru.delegation_regionale_id IS NOT NULL
        AND ru.status = 'actif'
        AND c.deleted=0
        AND c.id=ru.directeur_unite_id;  
    '''
    # Exécuter la requête SQL
    result = connection_sug.execute(text(sql_query))
    # Charger le résultat dans un DataFrame pandas
    df = pd.read_sql_query(text(sql_query), connection_sug)
    df["region"] = df.apply(lambda x: get_region(extract_department(x['billing_address_postalcode']),x['billing_address_city']), axis=1)
    df["departement"] = df['billing_address_postalcode'].apply(lambda x: departements_d.get(extract_department(x)))
    return df


def sc_researchunit(df_ru, date):
    # Construction du dictionnaire d'agrégation
    alliance = len(df_ru[df_ru['mandataire_unique_pi_valo'].apply(lambda x: str(x) == 'Alliance')])
    rep_equipe = len(df_ru[df_ru['mandataire_unique_pi_valo'].apply(lambda x: str(x) =="Répartition par équipes")])
    opport = len(df_ru[df_ru['mandataire_unique_pi_valo'].apply(lambda x: str(x) in ['Comité Projets', 'Comité tripartite'])])
    nd = len(df_ru[df_ru['mandataire_unique_pi_valo'].apply(lambda x: x is None or x=='')])
    mo_tiers = len(df_ru[df_ru['mandataire_unique_pi_valo'].apply(lambda x: 'INSERM' not in str(x))]) - opport - alliance - rep_equipe - nd

    result = {
        "date": date,
        "total_unit": len(df_ru),
        "mo_pi_it": len(df_ru[df_ru['mandataire_unique_pi_valo'].apply(lambda x: 'INSERM' in str(x))]),
        "alliance": alliance,
        "rep_equipe": rep_equipe,
        "opport": opport,
        "nd": nd,
        "mo_tiers": mo_tiers
    }
    return result

