![Mon Image](https://github.com/Steve-Doshas/BI/blob/main/Liseret%20Inserm%20T.png)

# Service : 
|-----------|-----------|
|-----------|-----------|
| **Nom** |**ETL_sc_ru**| 
| *Périodicité d’exécution*   | A 4h UTC. Tous les jours de la semaine|
| *Description* | Ce service automatise la création et mise à jour d'un fichier csv de reference contenant les informations actualisées et utiles concernant les unités de recherche. Il génère également un fichier de synthèse avec les statistiques de répartition des PI.
| *Version* | **1.0** |
| *Code* | RU_Req.py & update_reseachunit.py|
| *Log du service* |service_sc_ru$(date +'%Y-%m-%d').log|

# Sources :

|BD|Tables|
|-----------|-----------|
|Sugar|researchunits, contacts|

# Sorties :

## Fichier 1 : lastupdate

|Nom | **Sugar_researchunits_lastupdate.csv**|
|-----------|-----------|
|Chemin | Défini par la variable d'environnement SAVE_PATH|
|Type de fichiers| csv utf-8-sig|

|Données|Description|Comment|
|-----------|-----------|-----------|
|id| Identifiant de l'unité de recherche|Utilisé dans tous les rapports|
|name| Nom de l'unité de recherche|Utilisé dans tous les rapports|
|description| Description de l'unité de recherche|Rapport UR(IB info unité)|
|acronyme| Acronyme de l'unité de recherche|Utilisé dans tous les rapports|
|billing_address_postalcode| Code postal de l'adresse de facturation|Code postal corrigé si nécessaire ??|
|billing_address_city| Ville de l'adresse de facturation|??|
|delegation_regionale| Délégation régionale de rattachement| Utilisé dans tous les rapports Projets DR|
|cotutelles| Informations sur les cotutelles|Page UR(IB Info Unité)|
|thematique| Thématique de l'unité de recherche|??|
|vague_renouvellement| Informations sur les cotutelles|Utilisé dans plusieurs rapports|
|mandataire_unique_pi_valo| Type de mandataire unique pour la PI valorisation|Utilisé dans tous les rapports|
|title| Titre du directeur de l'unité|??|
|first_name| Prénom du directeur de l'unité|_directeur|
|last_name| Nom du directeur de l'unité|_directeur|
|region| Région calculée|Déterminée à partir du code postal et de la ville - Répartition Territoriale|
|departement| Département calculé|Déterminé à partir du code postal - Répartition Territoriale|

## Fichier 2 : summary

|Nom | **Sugar_researchunits_summary.csv**|
|-----------|-----------|
|Chemin | Défini par la variable d'environnement SAVE_PATH|
|Type de fichiers| csv utf-8-sig|
|Récurrence| Données Trimestrielles (31/03, 30/06, 30/09, 31/12, date du jour)|

|Données|Description| Comment|
|-----------|-----------|-----------|
|date| Date de l'extraction||
|total_unit|Nombre total d'unités de recherche|Rapport Scorecard(_Total)|
|mo_pi_it|Nombre d'unités avec mandataire INSERM|Unités contenant 'INSERM' dans mandataire_unique_pi_valo - Rapport Scorecard(_mo_pi_it, _PAR_it)|
|alliance|Nombre d'unités avec mandataire 'Alliance' - Rapport Scorecard(_Opport, _PAR_opp)|
|rep_equipe|Nombre d'unités avec mandataire 'Répartition par équipes'Rapport Scorecard(_RepEquipe)||
|opport|Nombre d'unités avec mandataire opportuniste|'Comité Projets' ou 'Comité tripartite' - Rapport Scorecard(_Opport, _PAR_opp)|
|nd|Nombre d'unités avec mandataire non défini|Valeurs nulles ou vides - Rapport Scorecard(_nd, _PAR_nd)|
|mo_tiers|Nombre d'unités avec mandataire tiers|Autres types de mandataires (hors INSERM, Alliance, etc.) - Rapport Scorecard(_PAR_tiers)|

# Fonctions  :

-`extract_department()` : Extrait le code département du code postal

-`nettoyer_ville()` : Nettoie et normalise les noms de ville, suprresion cedex

-`get_region()` : Détermine la région à partir du code département et de la ville

-`correct_cp()` : Corrige le code postal si manquant en utilisant la ville
