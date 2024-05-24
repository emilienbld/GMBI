import csv
import os
import time
import re
from thefuzz import fuzz
from thefuzz import process
from unidecode import unidecode
from datetime import datetime

import pandas as pd
from pandas import read_csv


# Chemins des fichiers CSV
chemin = 'C:/Users/internet/Documents/impots'  # Chemin où se trouvent les fichiers GMBI et G2GAI
nouveau_dossier = 'Traitement Rendu'  # Dossier où les fichiers seront retournés ! pas besoin de créer le dossier

# Noms des fichiers en entrée
nom_fichier_GMBI = '1_157000019_01_240226_100714_V2024.csv'  # Nom du fichier GMBI
nom_fichier_G2GAI = 'DGFIP_2023_2024_ain.csv'  # Nom du fichier G2GAI
nom_fichier_abandon = 'Domanial partie.csv'  # Nom du fichier des logements en abandon G2GAI

# Noms des fichiers en sortie
nom_nouveau_fichier = "8.1 TROISIEME " + nom_fichier_GMBI  # Fichier qui sera complet dans le dossier "rendu" ! pas besoin de créer le fichier
nom_G2GAI_non_trouve = '8.1 TROISIEME Ain G2GAI Reste.csv'  # Nom du fichier où les lignes de G2GAI n'ont pas été traitées à la fin ! pas besoin de créer le fichier
nom_GMBI_non_trouve = '8.1 TROISIEME Ain GMBI Reste.csv'  # Nom du fichier où les lignes de GMBI n'ont pas été traitées à la fin ! pas besoin de créer le fichier
nom_abandon_non_trouve = '8.1 TROISIEME Ain Abandon Reste.csv'

# Créer les chemins complets
dossier_rendu = os.path.join(chemin, nouveau_dossier)
fichier_GMBI = os.path.join(chemin, nom_fichier_GMBI)
fichier_G2GAI = os.path.join(chemin, nom_fichier_G2GAI)
fichier_abandon = os.path.join(chemin, nom_fichier_abandon)
nouveau_fichier = os.path.join(dossier_rendu, nom_nouveau_fichier)
G2GAI_non_trouve = os.path.join(dossier_rendu, nom_G2GAI_non_trouve)
GMBI_non_trouve = os.path.join(dossier_rendu, nom_GMBI_non_trouve)

# Vérifier si le dossier rendu existe, sinon le créer
if not os.path.exists(dossier_rendu):
    os.makedirs(dossier_rendu)

# Variabes des date de départs et arrivées
date_depart = "31/12/2023"
date_arrivee = "01/01/2024"

# Fonction pour ouvrir les fichiers GMBI et G2GAI et écrire les premières lignes dans les fichiers correspondants
def charger_ecrire_fichier(input_file, non_trouve_file):
    # Lire la première ligne du fichier d'entrée avec Pandas
    premiere_ligne = pd.read_csv(input_file, sep=';', encoding='ISO-8859-1', nrows=1, header=None)
    # Écrire la première ligne dans le fichier "non_trouve"
    premiere_ligne.to_csv(non_trouve_file, sep=';', index=False, header=False)
    # Lire toutes les données du fichier d'entrée sans la première ligne
    donnees = pd.read_csv(input_file, sep=';', encoding='ISO-8859-1', skiprows=1, header=None)
    # Retourner les données du fichier d'entrée sans la première ligne
    return donnees

# Charger les données du fichier GMBI
df_GMBI = charger_ecrire_fichier(fichier_GMBI, GMBI_non_trouve)
# Écrire la première ligne du fichier GMBI dans le nouveau fichier
charger_ecrire_fichier(fichier_GMBI, nouveau_fichier)
# Charger les données du fichier G2GAI
df_G2GAI = charger_ecrire_fichier(fichier_G2GAI, G2GAI_non_trouve)
# Charger les données du fichier des logements en abandons
df_abandon = charger_ecrire_fichier(fichier_abandon, nom_abandon_non_trouve)

# Fonction qui vérifie si le département est de la Corse pour le convertir comme écrit dans le fichier GMBI
def convertir_code_departement_corse(departement):
    if departement in ['201', '202']:
        if departement == '201':
            return '2A'
        elif departement == '202':
            return '2B'
    return departement

# Fonction pour convertir les caractères spéciaux en nornaux (EX : Ÿ -> Y)
def convertir_caracteres_speciaux(chaine):
    if isinstance(chaine, str):
        return unidecode(chaine)
    return chaine  # Retourne la valeur telle quelle si ce n'est pas une chaîne de caractères


# Fonction pour extraire les information du logement de G2GAI
def informations_logement_G2GAI(ligne_G2GAI):
    departement_logement_G2GAI = ligne_G2GAI[2]  # Colonne C, département du logement
    departement_logement_G2GAI = convertir_code_departement_corse(departement_logement_G2GAI)  # Appel de la focntion pour vérifier si le département est de la Corse
    numero_logement = ligne_G2GAI[12]  # Colonne M, numéro du logement
    return departement_logement_G2GAI, numero_logement

# Fonction pour extraire les information de l'occupant en N-1 de G2GAI
def informations_occupant_precedent(ligne_G2GAI):
    nigend_precedent = ligne_G2GAI[19]  # Colonne T, NIGEND N-1
    nom_precedent = ligne_G2GAI[20]  # Colonne U, NOM N-1
    nom_precedent = convertir_caracteres_speciaux(nom_precedent)
    prenom_precedent = ligne_G2GAI[21]  # Colonne V, PRÉNOM N-1

    # Vérifier si prenom_precedent est une chaîne de caractères
    if isinstance(prenom_precedent, str):
        # Appeler split() uniquement si prenom_precedent est une chaîne de caractères
        premier_prenom_precedent = prenom_precedent.split(' ')[0]  # Garder seulement le premier prénom
    else:
        # Si prenom_precedent n'est pas une chaîne de caractères, attribuer une valeur par défaut
        premier_prenom_precedent = ""

    date_naissance_precedente = ligne_G2GAI[22]  # Colonne W, DATE DE NAISSANCE
    return nigend_precedent, nom_precedent, prenom_precedent, premier_prenom_precedent, date_naissance_precedente


# Fonction pour extraire les information de l'occupant en N de G2GAI
def informations_occupant_courant(ligne_G2GAI):
    nigend_courant = ligne_G2GAI[26]  # Colonne AA, NIGEND N
    nom_courant = convertir_caracteres_speciaux(ligne_G2GAI[27])  # Colonne AB, NOM N
    prenom_courant = convertir_caracteres_speciaux(ligne_G2GAI[28])  # Colonne AC, PRÉNOM N
    if isinstance(prenom_courant, str):
        premier_prenom_courant_G2GAI = prenom_courant.split(' ')[0]
    else:
        premier_prenom_courant_G2GAI = ""  # Ou une autre valeur par défaut selon votre besoin
    date_naissance_courante = ligne_G2GAI[29]  # Colonne AD, DATE DE NAISSANCE
    return nigend_courant, nom_courant, prenom_courant, premier_prenom_courant_G2GAI, date_naissance_courante


# Fonction pour extraire les information du logement de GMBI
def informations_logement_GMBI(ligne_GMBI):
    departement_local_GMBI = ligne_GMBI[4]  # Colonne E, CODE DÉPARTEMENT
    numero_fiscal_GMBI = ligne_GMBI[2]  # Colonne C, NUMÉRO FISCAL DU LOCAL
    spi1_nom_GMBI = ligne_GMBI[35]  # Colonne AJ, NOM DU SPI 1
    spi1_prenom_GMBI = ligne_GMBI[37]  # Colonne AL, PRÉNOM DU SPI 1
    spi2_prenom_GMBI = ligne_GMBI[51]  # Colonne AL, PRÉNOM DU SPI 1
    return departement_local_GMBI, numero_fiscal_GMBI, spi1_nom_GMBI, spi1_prenom_GMBI, spi2_prenom_GMBI

def creer_nouvelle_ligne(ligne_GMBI):
    nouvelle_ligne = ligne_GMBI.copy()  # Copie de la ligne correspondante
    # Remplacer les valeurs NaN par des chaînes vides
    nouvelle_ligne = nouvelle_ligne.fillna('')
    nouvelle_ligne[0] = "X"  # Mettre "X" dans la colonne "declarer"
    return nouvelle_ligne

# Fonction pour écrire dans un fichier CSV
def ecrire_ligne_csv(fichier, ligne):
    with open(fichier, 'a', newline='') as fichier_csv:
        writer = csv.writer(fichier_csv, delimiter=';')
        # Convertir les nombres en chaînes de caractères avec un format spécifique
        ligne_formatee = [f'{v:.0f}' if isinstance(v, float) else v for v in ligne]
        writer.writerow(ligne_formatee)




# Initialiser un ensemble pour stocker les valeurs déjà traitées de GMBI
valeurs_gmbi_traitees = set()
# Initialiser un ensemble pour stocker les valeurs déjà traitées de G2GAI
valeurs_g2gai_traitees = set()
# Initialiser un ensemble pour stocker les valeurs déjà traitées de G2GAI de 2022
valeurs_g2gai_traitees2022 = set()
# Initialiser un ensemble pour stocker les valeurs déjà traitées de G2GAI de 2023
valeurs_g2gai_traitees2023 = set()
# Initialiser un ensemble pour stocker les valeurs déjà traitées des abandons
valeurs_abandon_traitees = set()

# Fonction pour mettre le type d'occupation et le numéro de logement dans la case observation
def determiner_type_occupation(nouvelle_ligne, numero_logement_G2GAI):
    if nouvelle_ligne[35] != '':
        nouvelle_ligne[32] = "4"
        nouvelle_ligne[33] = "1"
        nouvelle_ligne[42:45] = [""] * 3
    else:
        nouvelle_ligne[32] = "3"
        # nouvelle_ligne[33] = "2"
        nouvelle_ligne[33] = ""
    nouvelle_ligne[64] = numero_logement_G2GAI

# Fonction pour les locaux associés au logement des dates 01/01/2024 de GMBI
def date_gmbi(ligne_GMBI, nouveau_fichier, numero_logement_G2GAI, date_naissance_courante, date_arrivee, valeurs_gmbi_traitees):
    # nouvelle_ligne = creer_nouvelle_ligne(ligne_GMBI)
    nouvelle_ligne = ligne_GMBI.copy()  
    nouvelle_ligne = nouvelle_ligne.fillna('')
    nouvelle_ligne[0] = "2"  
    # Déterminer le type d'occupation
    determiner_type_occupation(nouvelle_ligne, numero_logement_G2GAI)
    # Mettre la date de naissance en fonction du Spi du gendare
    if premier_prenom_courant_G2GAI == ligne_GMBI[37]:
        nouvelle_ligne[38] = date_naissance_courante
    else:
        nouvelle_ligne[52] = date_naissance_courante
    nouvelle_ligne[45] = date_arrivee  
    # Mettre la date d'arrivée dans la colonne correspondante si nécessaire
    if ligne_GMBI[49] != '':
        ligne_GMBI[59] = date_arrivee
    ecrire_ligne_csv(nouveau_fichier, nouvelle_ligne)
    valeurs_gmbi_traitees.add(ligne_GMBI[2]) 




# Fonction pour vérifier si la date d'arrivée est présente et inférieur à la date de départ
def verifier_date_arrivee(ligne, date_arrivee):
    # Vérifier si la cellule en indice 45 est présente et si la date est inférieure à date_arrivee
    if ligne[45] and datetime.strptime(ligne[45], "%d/%m/%Y") < datetime.strptime(date_arrivee, "%d/%m/%Y"):
        return True
    return False

# Écriture des lignes si la ligne est déclarée comme vacante et occupée ou vacante deux fois
def verifier_vacance_occupation(ligne):
    if ligne[33] != '' and ((ligne[44] != '' and ligne[49] == '' and ligne[58] == '') or (ligne[44] == '' and ligne[35] != '' and ligne[58] == '')):
        return True
    return False

# Fonction pour trouver le gendarme en Spi 1 ou 2 pour lui mettre sa date de naissance
def mettre_date_naissance_gendarme(nouvelle_ligne, nom_precedent, premier_prenom_precedent_G2GAI, date_naissance_precedente, spi1_nom_GMBI, spi1_prenom_GMBI, date_naissance_spi_1=38, date_naissance_spi_2=52):
    if nom_precedent in nouvelle_ligne and premier_prenom_precedent_G2GAI in nouvelle_ligne:
        if nom_precedent == spi1_nom_GMBI and premier_prenom_precedent_G2GAI == spi1_prenom_GMBI:
            nouvelle_ligne[date_naissance_spi_1] = date_naissance_precedente
        else:
            nouvelle_ligne[date_naissance_spi_2] = date_naissance_precedente

# Écriture des lignes si le format de la date d'arrviée n'est pas bonne
def ajouter_gendarme_cause(nouveau_fichier, ligne_GMBI, nom_courant_G2GAI, premier_prenom_courant_G2GAI, date_naissance_courante, numero_logement_G2GAI, date_arrivee, valeurs_gmbi_traitees, valeurs_g2gai_traitees):
    nouvelle_ligne = ligne_GMBI.copy()
    nouvelle_ligne = nouvelle_ligne.fillna('')
    nouvelle_ligne[1] = "Cause date ou occ"
    ecrire_ligne_csv(nouveau_fichier, nouvelle_ligne)
    nouvelle_ligne[0] = "Cause date ou occ Ajout"
    nouvelle_ligne[1] = ""
    nouvelle_ligne[35] = nom_courant_G2GAI
    nouvelle_ligne[37] = premier_prenom_courant_G2GAI
    nouvelle_ligne[38] = date_naissance_courante  # Mettre la Date de naissance du nouveau gendarme
    determiner_type_occupation(nouvelle_ligne, numero_logement_G2GAI)
    nouvelle_ligne[45] = date_arrivee
    nouvelle_ligne[46:61] = [""] * 15
    ecrire_ligne_csv(nouveau_fichier, nouvelle_ligne)
    valeurs_gmbi_traitees.add(ligne_GMBI[2])  # Ajouter la ligne de GMBI à celles déjà traitées
    valeurs_g2gai_traitees.add(numero_logement_G2GAI)



# Recherche des 01/01/2024 de GMBI
for index_GMBI, ligne_GMBI in df_GMBI.iterrows():

    if ligne_GMBI[45] == '01/01/2024' and "partie" in ligne_GMBI[18].lower() and ligne_GMBI[2] not in valeurs_gmbi_traitees:
        print("Touvé")
        departement_local_GMBI = ligne_GMBI[4]
        numero_fiscal_GMBI = ligne_GMBI[2]
        nom_GMBI = ligne_GMBI[35]
        prenom_GMBI = ligne_GMBI[37]
        adresse_GMBI = ligne_GMBI[8]

        for index_G2GAI, ligne_G2GAI in df_G2GAI.iterrows():

            if ligne_G2GAI[27] != '':
                nigend_courant, nom_courant_G2GAI, prenom_courant_G2GAI, premier_prenom_courant_G2GAI, date_naissance_courante = informations_occupant_courant(ligne_G2GAI)
                departement_logement_G2GAI, numero_logement_G2GAI = informations_logement_G2GAI(ligne_G2GAI)

                if (departement_local_GMBI == departement_logement_G2GAI and
                    numero_logement_G2GAI not in valeurs_g2gai_traitees and
                    (((fuzz.partial_token_sort_ratio(nom_courant_G2GAI, ligne_GMBI[35]) == 100 or fuzz.partial_token_sort_ratio(nom_courant_G2GAI, ligne_GMBI[35]) == 100) and
                    premier_prenom_courant_G2GAI == ligne_GMBI[37]) or
                    ((fuzz.partial_token_sort_ratio(nom_courant_G2GAI, ligne_GMBI[49]) == 100 or fuzz.partial_token_sort_ratio(nom_courant_G2GAI, ligne_GMBI[49]) == 100) and
                    premier_prenom_courant_G2GAI == ligne_GMBI[51]))):
                                        
                    # date_naissance_trouvee = date_naissance_courante

                    # nouvelle_ligne = creer_nouvelle_ligne(ligne_GMBI)
                    nouvelle_ligne = ligne_GMBI.copy()  # Copie de la ligne correspondante
                    nouvelle_ligne = nouvelle_ligne.fillna('')
                    nouvelle_ligne[0] = "Recherche 01/01/2024"  # Mettre "X" dans la colonne "declarer"
                    determiner_type_occupation(nouvelle_ligne, numero_logement_G2GAI)
                    if premier_prenom_courant_G2GAI == prenom_GMBI:
                        nouvelle_ligne[38] = date_naissance_courante
                    else:
                        nouvelle_ligne[52] = date_naissance_courante

                    # Écrire la ligne modifiée dans le nouveau fichier 
                    ecrire_ligne_csv(nouveau_fichier, nouvelle_ligne)
                    valeurs_gmbi_traitees.add(numero_fiscal_GMBI)  # Ajouter la ligne de GMBI à celles déjà traité
                    valeurs_g2gai_traitees.add(numero_logement_G2GAI)  # Ajouter la ligne de G2GAI à celles déjà traitées

                    if numero_fiscal_GMBI in valeurs_gmbi_traitees:

                        for index_GMBI, ligne_GMBI in df_GMBI.iterrows():

                            if (ligne_GMBI[2] not in valeurs_gmbi_traitees and
                                "partie" not in ligne_GMBI[18].lower() and
                                ligne_GMBI[3] != ''):

                                if ligne_GMBI[3] == numero_fiscal_GMBI and ligne_GMBI[2] not in valeurs_gmbi_traitees:

                                    date_gmbi(ligne_GMBI, nouveau_fichier, numero_logement_G2GAI, date_naissance_courante, date_arrivee, valeurs_gmbi_traitees)

                                if (ligne_GMBI[2] not in valeurs_gmbi_traitees and
                                    ((ligne_GMBI[35] == nom_GMBI and ligne_GMBI[37] == prenom_GMBI) or
                                    (ligne_GMBI[49] == nom_GMBI and ligne_GMBI[51] == prenom_GMBI)) and
                                    ligne_GMBI[4] == departement_local_GMBI and
                                    ligne_GMBI[8] == adresse_GMBI):

                                    date_gmbi(ligne_GMBI, nouveau_fichier, numero_logement_G2GAI, date_naissance_courante, date_arrivee, valeurs_gmbi_traitees)
# Recherche des 01/01/2024 de GMBI



# 2023
# Parcourir les lignes du fichier G2GAI
for index_G2GAI, ligne_G2GAI in df_G2GAI.iterrows():

    # Si le logement est Domaniale
    if ligne_G2GAI[16] == "D" and ligne_G2GAI[12] not in valeurs_g2gai_traitees:

        # Appel des focntion pour initialisation des variable de G2GAI
        departement_logement_G2GAI, numero_logement_G2GAI = informations_logement_G2GAI(ligne_G2GAI)
        nigend_precedent, nom_precedent_G2GAI, prenom_precedent_G2GAI, premier_prenom_precedent_G2GAI, date_naissance_precedente = informations_occupant_precedent(ligne_G2GAI)
        nigend_courant, nom_courant_G2GAI, prenom_courant_G2GAI, premier_prenom_courant_G2GAI, date_naissance_courante = informations_occupant_courant(ligne_G2GAI)

        # S'il y a quelqu'un en N-1 dans G2GAI
        if nigend_precedent != '':

            # Si les nigneds sont égaux en N-1 et N dans G2GAI
            if nigend_precedent == nigend_courant:

                # Parcourir les lignes du fichier GMBI
                for index_GMBI, ligne_GMBI in df_GMBI.iterrows():

                    # S'il s'agit d'une partie principale 
                    if ("partie" in ligne_GMBI[18].lower() and
                        pd.isnull(ligne_GMBI[3]) and 
                        ligne_GMBI[2] not in valeurs_gmbi_traitees):

                        # Appel de la  focntion pour initialisation des variable de GMBI
                        departement_local_GMBI, numero_fiscal_GMBI, spi1_nom_GMBI, spi1_prenom_GMBI, spi2_prenom_GMBI = informations_logement_GMBI(ligne_GMBI)

                        # Chercher une correspondance entre la line de G2GAI avec celle de GMBI
                        if (departement_logement_G2GAI == departement_local_GMBI  and
                            (fuzz.partial_token_sort_ratio(nom_precedent_G2GAI, ligne_GMBI[35]) == 100 or fuzz.partial_token_sort_ratio(nom_precedent_G2GAI, ligne_GMBI[49]) == 100) and((premier_prenom_precedent_G2GAI == spi1_prenom_GMBI) or (premier_prenom_precedent_G2GAI == spi2_prenom_GMBI))):

                            # Appel de la fonction pour vérifier la date d'arrivée
                            if verifier_date_arrivee(ligne_GMBI, date_arrivee) and verifier_vacance_occupation(ligne_GMBI):

                                # Appel de la fonction pour copier la ligne et mettre "X" dans la cellule declarer
                                nouvelle_ligne = creer_nouvelle_ligne(ligne_GMBI)

                                # Appel de la fonction qui cherche où la correspondance a été trouvée pour mettre la date de naissance du gendarme
                                mettre_date_naissance_gendarme(nouvelle_ligne, nom_precedent_G2GAI, premier_prenom_precedent_G2GAI, date_naissance_precedente, spi1_nom_GMBI, spi1_prenom_GMBI)

                                # Appel de la pour remplire la ligne en fonction de la vacance ou non et remplisage de la cellule observation
                                determiner_type_occupation(nouvelle_ligne, numero_logement_G2GAI)

                                # Écrire la ligne modifiée dans le nouveau fichier 
                                ecrire_ligne_csv(nouveau_fichier, nouvelle_ligne)
                                valeurs_gmbi_traitees.add(numero_fiscal_GMBI)  # Ajouter la ligne de GMBI à celles déjà traité
                                valeurs_g2gai_traitees.add(numero_logement_G2GAI)  # Ajouter la ligne de G2GAI à celles déjà traitées
                                valeurs_g2gai_traitees2023.add(numero_logement_G2GAI)  # Ajouter la ligne de G2GAI à celles déjà traitées
                            
                            else:
                                ajouter_gendarme_cause(nouveau_fichier, ligne_GMBI, nom_courant_G2GAI, premier_prenom_courant_G2GAI, date_naissance_courante, numero_logement_G2GAI, date_arrivee, valeurs_gmbi_traitees, valeurs_g2gai_traitees)
                                valeurs_g2gai_traitees2023.add(numero_logement_G2GAI)  # Ajouter la ligne de G2GAI à celles déjà traitées

                            for index_GMBI, ligne_GMBI in df_GMBI.iterrows():
                                
                                # S'il ne s'agit pas d'une partie principale 
                                if "partie" not in ligne_GMBI[18].lower() and ligne_GMBI[3] != '':

                                    # Recherhcer les "dépendances" affectées à ce local
                                    if (departement_local_GMBI == ligne_GMBI[4] and
                                        ligne_GMBI[2] not in valeurs_gmbi_traitees and
                                        numero_fiscal_GMBI == ligne_GMBI[3]):

                                        if verifier_date_arrivee(ligne_GMBI, date_arrivee) and verifier_vacance_occupation(ligne_GMBI):

                                            # Créer une nouvelle ligne avec les modifications
                                            nouvelle_ligne = creer_nouvelle_ligne(ligne_GMBI)

                                            if((fuzz.partial_token_sort_ratio(nom_precedent_G2GAI, ligne_GMBI[35]) == 100 or fuzz.partial_token_sort_ratio(nom_precedent_G2GAI, ligne_GMBI[49]) == 100) and
                                            ((premier_prenom_precedent_G2GAI == spi1_prenom_GMBI) or (premier_prenom_precedent_G2GAI == spi2_prenom_GMBI))):

                                                # Appel de la fonction qui cherche où la correspondance a été trouvée pour mettre la date de naissance du gendarme
                                                mettre_date_naissance_gendarme(nouvelle_ligne, nom_precedent_G2GAI, premier_prenom_precedent_G2GAI, date_naissance_precedente, spi1_nom_GMBI, spi1_prenom_GMBI)

                                                # Appel de la pour remplire la ligne en fonction de la vacance ou non et remplisage de la cellule observation
                                                determiner_type_occupation(nouvelle_ligne, numero_logement_G2GAI)

                                                # Écrire la ligne modifiée dans le nouveau fichier
                                                ecrire_ligne_csv(nouveau_fichier, nouvelle_ligne)
                                                valeurs_gmbi_traitees.add(ligne_GMBI[2])  # Ajouter la ligne de GMBI à celles déjà traité

                                            else:
                                                # Créer une nouvelle ligne avec les modifications nécessaires
                                                # nouvelle_ligne = creer_nouvelle_ligne(ligne_GMBI)
                                                nouvelle_ligne = ligne_GMBI.copy()  # A ENLEVER
                                                nouvelle_ligne = nouvelle_ligne.fillna('')
                                                nouvelle_ligne[0] = "Pareil Surpime L"  # A ENLEVER
                                                nouvelle_ligne[46] = date_depart  # Mettre la date de départ pour spi_1

                                                # Appel de la fonction qui cherche où la correspondance a été trouvée pour mettre la date de naissance du gendarme
                                                mettre_date_naissance_gendarme(nouvelle_ligne, nom_precedent_G2GAI, premier_prenom_precedent_G2GAI, date_naissance_precedente, spi1_nom_GMBI, spi1_prenom_GMBI)

                                                # Appel de la pour remplire la ligne en fonction de la vacance ou non et remplisage de la cellule observation
                                                determiner_type_occupation(nouvelle_ligne, numero_logement_G2GAI)

                                                # Vérifier s'il y a quelqu'un en Spi_2 pour mettre une date de départ
                                                if nouvelle_ligne[49] != '':
                                                    nouvelle_ligne[60] = date_depart  # Mettre la date de départ pour spi_2

                                                # Écrire la ligne modifiée dans le nouveau fichier
                                                ecrire_ligne_csv(nouveau_fichier, nouvelle_ligne)

                                                # Renseigner le nouvel occupant
                                                nouvelle_ligne[0] = "Pareil Ajout L"  # A ENLEVER
                                                nouvelle_ligne[35] = nom_courant_G2GAI  # Mettre le Nom du nouveau gendarme
                                                # premier_prenom_courant_G2GAI = prenom_courant_G2GAI.split(' ')[0]
                                                nouvelle_ligne[37] = premier_prenom_courant_G2GAI  # Mettre le Prénom du nouveau gendarme
                                                nouvelle_ligne[38] = date_naissance_courante  # Mettre la Date de naissaince du nouveau gendarme

                                                # Appel de la pour remplire la ligne en fonction de la vacance ou non et remplisage de la cellule observation
                                                determiner_type_occupation(nouvelle_ligne, numero_logement_G2GAI)

                                                nouvelle_ligne[45] = date_arrivee  # Mettre la date d'arrivée pour Spi_1
                                                # nouvelle_ligne[34] = ""  # Suppression de l'Id (dans la version 2023-2024 iln'y en a pas)
                                                nouvelle_ligne[42:45] = [""] * 3  # Vider AQ; AR; AS
                                                nouvelle_ligne[46:61] = [""] * 15  # Vider toutes les données du Spi_2

                                                # Écrire la ligne modifiée dans le nouveau fichier
                                                ecrire_ligne_csv(nouveau_fichier, nouvelle_ligne)
                                                valeurs_gmbi_traitees.add(ligne_GMBI[2])  # Ajouter la ligne de GMBI à celles déjà traité
                                                valeurs_g2gai_traitees.add(numero_logement_G2GAI)  # Ajouter la ligne de G2GAI à celles déjà traitées
                                                valeurs_g2gai_traitees2023.add(numero_logement_G2GAI)  # Ajouter la ligne de G2GAI à celles déjà traitées

                                        else:
                                            ajouter_gendarme_cause(nouveau_fichier, ligne_GMBI, nom_courant_G2GAI, premier_prenom_courant_G2GAI, date_naissance_courante, numero_logement_G2GAI, date_arrivee, valeurs_gmbi_traitees, valeurs_g2gai_traitees)
                                            valeurs_g2gai_traitees2023.add(numero_logement_G2GAI)  # Ajouter la ligne de G2GAI à celles déjà traitées

                            break

            else:
                # Parcourir les lignes du fichier GMBI
                for index_GMBI, ligne_GMBI in df_GMBI.iterrows():

                    # S'il s'agit d'une partie principale
                    if ("partie" in ligne_GMBI[18].lower() and
                        ligne_GMBI[3]==""and 
                        ligne_GMBI[2] not in valeurs_gmbi_traitees):

                        # Appel de la  focntion pour initialisation des variable de GMBI
                        departement_local_GMBI, numero_fiscal_GMBI, spi1_nom_GMBI, spi1_prenom_GMBI, spi2_prenom_GMBI = informations_logement_GMBI(ligne_GMBI)

                        # Chercher une correspondance entre la ligne de G2GAI avec celle de GMBI
                        if (departement_logement_G2GAI == departement_local_GMBI  and
                            (fuzz.partial_token_sort_ratio(nom_precedent_G2GAI, ligne_GMBI[35]) == 100 or fuzz.partial_token_sort_ratio(nom_precedent_G2GAI, ligne_GMBI[49]) == 100) and((premier_prenom_precedent_G2GAI == spi1_prenom_GMBI) or (premier_prenom_precedent_G2GAI == spi2_prenom_GMBI))):

                            if verifier_date_arrivee(ligne_GMBI, date_arrivee) and verifier_vacance_occupation(ligne_GMBI):

                                # Créer une nouvelle ligne avec les modifications nécessaires
                                # nouvelle_ligne = creer_nouvelle_ligne(ligne_GMBI)
                                nouvelle_ligne = ligne_GMBI.copy()  # A ENLEVER
                                nouvelle_ligne = nouvelle_ligne.fillna('')
                                nouvelle_ligne[0] = "Different Supprime PP"  # A ENLEVER
                                nouvelle_ligne[46] = date_depart  # Mettre la date de départ pour spi_1

                                # Appel de la fonction qui cherche où la correspondance a été trouvée pour mettre la date de naissance du gendarme
                                mettre_date_naissance_gendarme(nouvelle_ligne, nom_precedent_G2GAI, premier_prenom_precedent_G2GAI, date_naissance_precedente, spi1_nom_GMBI, spi1_prenom_GMBI)

                                # Appel de la pour remplire la ligne en fonction de la vacance ou non et remplisage de la cellule observation
                                determiner_type_occupation(nouvelle_ligne, numero_logement_G2GAI)

                                # Vérifier s'il y a quelqu'un en Spi_2 pour mettre une date de départ
                                if nouvelle_ligne[49] != '':
                                    nouvelle_ligne[60] = date_depart  # Mettre la date de départ pour spi_2

                                # Écrire la ligne modifiée dans le nouveau fichier
                                ecrire_ligne_csv(nouveau_fichier, nouvelle_ligne)

                                # Renseigner le nouvel occupant
                                nouvelle_ligne[0] = "Different Ajout PP"  # A ENLEVER
                                nouvelle_ligne[35] = nom_courant_G2GAI  # Mettre le Nom du nouveau gendarme
                                # premier_prenom_courant_G2GAI = prenom_courant_G2GAI.split(' ')[0]
                                nouvelle_ligne[37] = premier_prenom_courant_G2GAI  # Mettre le Prénom du nouveau gendarme
                                nouvelle_ligne[38] = date_naissance_courante  # Mettre la Date de naissaince du nouveau gendarme

                                # Appel de la pour remplire la ligne en fonction de la vacance ou non et remplisage de la cellule observation
                                determiner_type_occupation(nouvelle_ligne, numero_logement_G2GAI)
                                nouvelle_ligne[45] = date_arrivee  # Mettre la date d'arrivée pour Spi_1

                                # Vider le Spi_2
                                nouvelle_ligne[46:61] = [""] * 15  # Vider toutes les données du Spi_2

                                # Écrire la ligne modifiée dans le nouveau fichier
                                ecrire_ligne_csv(nouveau_fichier, nouvelle_ligne)
                                valeurs_gmbi_traitees.add(numero_fiscal_GMBI)  # Ajouter la ligne de GMBI à celles déjà traité
                                valeurs_g2gai_traitees.add(numero_logement_G2GAI)  # Ajouter la ligne de G2GAI à celles déjà traitées
                                valeurs_g2gai_traitees2023.add(numero_logement_G2GAI)  # Ajouter la ligne de G2GAI à celles déjà traitées

                            else:
                                ajouter_gendarme_cause(nouveau_fichier, ligne_GMBI, nom_courant_G2GAI, premier_prenom_courant_G2GAI, date_naissance_courante, numero_logement_G2GAI, date_arrivee, valeurs_gmbi_traitees, valeurs_g2gai_traitees)
                                valeurs_g2gai_traitees2023.add(numero_logement_G2GAI)  # Ajouter la ligne de G2GAI à celles déjà traitées

                            for index_GMBI, ligne_GMBI in df_GMBI.iterrows():
                                
                                # S'il ne s'agit pas d'une partie principale 
                                if "partie" not in ligne_GMBI[18].lower() and ligne_GMBI[3] != '':

                                    # Recherhcer les "dépendances" affectées à ce local
                                    if (departement_local_GMBI == ligne_GMBI[4] and
                                        ligne_GMBI[2] not in valeurs_gmbi_traitees and
                                        numero_fiscal_GMBI == ligne_GMBI[3]):

                                        if verifier_date_arrivee(ligne_GMBI, date_arrivee) and verifier_vacance_occupation(ligne_GMBI):

                                            # Créer une nouvelle ligne avec les modifications nécessaires
                                            # nouvelle_ligne = creer_nouvelle_ligne(ligne_GMBI)
                                            nouvelle_ligne = ligne_GMBI.copy()  # A ENLEVER
                                            nouvelle_ligne = nouvelle_ligne.fillna('')
                                            nouvelle_ligne[0] = "Different Supprime L"  # A ENLEVER
                                            nouvelle_ligne[46] = date_depart  # Mettre la date de départ pour spi_1

                                            # Appel de la fonction qui cherche où la correspondance a été trouvée pour mettre la date de naissance du gendarme
                                            mettre_date_naissance_gendarme(nouvelle_ligne, nom_precedent_G2GAI, premier_prenom_precedent_G2GAI, date_naissance_precedente, spi1_nom_GMBI, spi1_prenom_GMBI)

                                            # Appel de la pour remplire la ligne en fonction de la vacance ou non et remplisage de la cellule observation
                                            determiner_type_occupation(nouvelle_ligne, numero_logement_G2GAI)

                                            # Vérifier s'il y a quelqu'un en Spi_2 pour mettre une date de départ
                                            if nouvelle_ligne[49] != '':
                                                nouvelle_ligne[60] = date_depart  # Mettre la date de départ pour spi_2

                                            # Écrire la ligne modifiée dans le nouveau fichier
                                            ecrire_ligne_csv(nouveau_fichier, nouvelle_ligne)

                                            nouvelle_ligne[0] = "Different Ajout L"  # A ENLEVER
                                            nouvelle_ligne[35] = nom_courant_G2GAI  # Mettre le Nom du nouveau gendarme
                                            # premier_prenom_courant_G2GAI = prenom_courant_G2GAI.split(' ')[0]
                                            nouvelle_ligne[37] = premier_prenom_courant_G2GAI  # Mettre le Prénom du nouveau gendarme
                                            nouvelle_ligne[38] = date_naissance_courante  # Mettre la Date de naissaince du nouveau gendarme

                                            # Appel de la pour remplire la ligne en fonction de la vacance ou non et remplisage de la cellule observation
                                            determiner_type_occupation(nouvelle_ligne, numero_logement_G2GAI)
                                            nouvelle_ligne[45] = date_arrivee  # Mettre la date d'arrivée pour Spi_1

                                            # Vider le Spi_2
                                            nouvelle_ligne[46:61] = [""] * 15  # Vider toutes les données du Spi_2

                                            # Écrire la ligne modifiée dans le nouveau fichier
                                            ecrire_ligne_csv(nouveau_fichier, nouvelle_ligne)
                                            valeurs_gmbi_traitees.add(ligne_GMBI[2])  # Ajouter la ligne de GMBI à celles déjà traité
                                        
                                        else:
                                            ajouter_gendarme_cause(nouveau_fichier, ligne_GMBI, nom_courant_G2GAI, premier_prenom_courant_G2GAI, date_naissance_courante, numero_logement_G2GAI, date_arrivee, valeurs_gmbi_traitees, valeurs_g2gai_traitees)
                                            valeurs_g2gai_traitees2023.add(numero_logement_G2GAI)  # Ajouter la ligne de G2GAI à celles déjà traitées
