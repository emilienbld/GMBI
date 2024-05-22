# Dans cette verison, traitement des lignes avce la librairie (donc personne en N-1 G2GAI)
# Et traitement des lignes annuler_occupation
# Recherche des abandons pour les mettre vacants
# Recherche avec 2022

# Ce programme créait trois nouveaux fichiers :
# 1 fichier a rendre à la DGFiP
# 1 fichier avec les lignes de G2GAI qui n'ont pas été traitées ou pas trouvées de correspondances
# 1 fichier avec les lignes de GMBI qui n'ont pas été traitées

import csv
import os
import time
from thefuzz import fuzz
from thefuzz import process
import re
from datetime import datetime
from unidecode import unidecode

start = time.time()

# IMPORTANT DE CHANGER LES CHEMINS !!!
# Chemins des fichiers CSV
chemin = 'C:/Users/internet/Documents/impots'  # Chemin où se trouve les fichiers GMBI et G2GAI
nouveau_dossier = 'Traitement Rendu'  # Dossier où les fichiers seront retournés ! pas besoin de créer le dossier

# TESTE SUR LE DÉPARTEMENT AIN
# Noms des fichiers en entée
# nom_fichier_GMBI = '1_157000019_01_240226_100714_V2024 - Copie.csv'  # Nom du fichier GMBI
nom_fichier_GMBI = '1_157000019_01_240226_100714_V2024.csv'  # Nom du fichier GMBI
# nom_fichier_G2GAI = 'DGFIP_2023_2024_ain - Copie.csv'  # Nom du fichier G2GAI
nom_fichier_G2GAI = 'DGFIP_2023_2024_ain.csv'  # Nom du fichier G2GAI
nom_fichier_abandon = 'Domanial partie.csv'  # Nom du fichier des logemsnts en abandons G2GAI
# Nom des fichiers en sortie
nom_nouveau_fichier = "6.1 TROISIEME " + nom_fichier_GMBI  # Fichier qui sera complet dans le dossier "rendu" ! pas besoin de créer le fichier
nom_G2GAI_non_trouve = '6.1 TROISIEME Ain G2GAI Reste.csv'  # Nom du fichier où les lignes de G2GAI n'ont pas été traité à la fin ! pas besoin de créer le fichier
nom_GMBI_non_trouve = '6.1 TROISIEME Ain GMBI Reste.csv'  # Nom du fichier où les lignes de GMBI n'ont pas été traité à la fin ! pas besoin de créer le fichier
nom_abandon_non_trouve = '6.1 TROISIEME Ain Abandon Reste.csv'

# # TESTE SUR TOUS LES LOGEMENTS
# # Noms des fichiers en entée
# nom_fichier_GMBI = '1_157000019_999_240521_112433_V2024.csv'  # Nom du fichier GMBI
# nom_fichier_G2GAI = 'DGFIP_2022_2023_2024.csv'  # Nom du fichier G2GAI
# nom_fichier_abandon = 'Domanial partie.csv'  # Nom du fichier des logemsnts en abandons G2GAI
# # Nom des fichiers en sortie
# nom_nouveau_fichier = "6.1 TROISIEME " + nom_fichier_GMBI  # Fichier qui sera complet dans le dossier "rendu" ! pas besoin de créer le fichier
# nom_G2GAI_non_trouve = '6.1 TROISIEME G2GAI Reste.csv'  # Nom du fichier où les lignes de G2GAI n'ont pas été traité à la fin ! pas besoin de créer le fichier
# nom_GMBI_non_trouve = '6.1 TROISIEME GMBI Reste.csv'  # Nom du fichier où les lignes de GMBI n'ont pas été traité à la fin ! pas besoin de créer le fichier
# nom_abandon_non_trouve = '6.1 TROISIEME Abandon Reste.csv'

# # TESTE PARTI
# # Noms des fichiers en entée
# nom_fichier_GMBI = 'GMBIpartie.csv'  # Nom du fichier GMBI
# nom_fichier_G2GAI = 'DGFIP_2023_2024_ain.csv'  # Nom du fichier G2GAI
# nom_fichier_abandon = 'Domanial partie.csv'  # Nom du fichier des logemsnts en abandons G2GAI
# # Nom des fichiers en sortie
# nom_nouveau_fichier = "5.1PARTI NOUVEAU" + nom_fichier_GMBI  # Fichier qui sera complet dans le dossier "rendu" ! pas besoin de créer le fichier
# nom_G2GAI_non_trouve = '5.1PARTI G2GAI Reste.csv'  # Nom du fichier où les lignes de G2GAI n'ont pas été traité à la fin ! pas besoin de créer le fichier
# nom_GMBI_non_trouve = '5.1PARTI GMBI Reste.csv'  # Nom du fichier où les lignes de GMBI n'ont pas été traité à la fin ! pas besoin de créer le fichier
# nom_abandon_non_trouve = '5.1PARTI Abandon Reste.csv'

# Créer les chemins complets
dossier_rendu = os.path.join(chemin, nouveau_dossier)
fichier_GMBI = os.path.join(chemin, nom_fichier_GMBI)
fichier_G2GAI = os.path.join(chemin, nom_fichier_G2GAI)
fichier_abandon = os.path.join(chemin, nom_fichier_abandon)
nouveau_fichier = os.path.join(dossier_rendu, nom_nouveau_fichier)
G2GAI_non_trouve = os.path.join(dossier_rendu, nom_G2GAI_non_trouve)
GMBI_non_trouve = os.path.join(dossier_rendu, nom_GMBI_non_trouve)

# Variabes des date de départs et arrivées
date_depart = "31/12/2023"
date_arrivee = "01/01/2024"

# Vérifier si le dossier rendu existe, sinon le créer
if not os.path.exists(dossier_rendu):
    os.makedirs(dossier_rendu)

# Fonction pour trouver le gendarme en Spi 1 ou 2 pour lui mettre sa date de naissance
def mettre_date_naissance_gendarme(nouvelle_ligne, nom_precedent, premier_prenom_precedent_G2GAI, date_naissance_precedente, spi1_nom_GMBI, spi1_prenom_GMBI, date_naissance_spi_1=38, date_naissance_spi_2=52):
    if nom_precedent in nouvelle_ligne and premier_prenom_precedent_G2GAI in nouvelle_ligne:
        if nom_precedent == spi1_nom_GMBI and premier_prenom_precedent_G2GAI == spi1_prenom_GMBI:
            nouvelle_ligne[date_naissance_spi_1] = date_naissance_precedente
        else:
            nouvelle_ligne[date_naissance_spi_2] = date_naissance_precedente

# Fonction pour récupérer l'idGrouLoc et l'assigner à la nouvelle ligne (A utiliser quand il n'est pas déjà present)
def recuperer_idGroupLoc_et_assigner(donnees_fichierGMBI, departement_local_GMBI, valeurs_gmbi_traitees, nom_precedent_G2GAI, premier_prenom_precedent_G2GAI, nouvelle_ligne):
    for ligne_GMBI in donnees_fichierGMBI:
        # Vérifier les conditions pour récupérer idGroupLoc
        if (departement_local_GMBI == ligne_GMBI[4] and
                ligne_GMBI[2] in valeurs_gmbi_traitees and
                "partie" in ligne_GMBI[18].lower() and
                # nom_precedent_G2GAI in ligne_GMBI and
                (fuzz.partial_token_sort_ratio(nom_precedent_G2GAI, ligne_GMBI[35]) == 100 or fuzz.partial_token_sort_ratio(nom_precedent_G2GAI, ligne_GMBI[49]) == 100) and
                premier_prenom_precedent_G2GAI in ligne_GMBI):

            nouvelle_ligne[3] = ligne_GMBI[2]  # Écrire l'idGroupLoc dans nouvelle_ligne
            break  # Sortir de la boucle une fois que la première correspondance est trouvée

# Fonction pour mettre le type d'occupation et le numéro de logement dans la case observation
def determiner_type_occupation(nouvelle_ligne, numero_logement_G2GAI):
    if nouvelle_ligne[35].strip() != '':
        nouvelle_ligne[32] = "4"
        nouvelle_ligne[33] = "1"
        nouvelle_ligne[42:45] = [""] * 3
    else:
        nouvelle_ligne[32] = "3"
        # nouvelle_ligne[33] = "2"
        nouvelle_ligne[33] = ""
    nouvelle_ligne[64] = numero_logement_G2GAI

# Fonction pour copier la ligne et mettre "X" dans la première cellule
def creer_nouvelle_ligne(ligne_GMBI):
    nouvelle_ligne = ligne_GMBI[:]  # Copie de la ligne correspondante
    nouvelle_ligne[0] = "X"  # Mettre "X" dans la colonne "declarer"
    return nouvelle_ligne

# Fonction pour écrire dans un fichier CSV
def ecrire_ligne_csv(fichier, ligne):
    with open(fichier, 'a', newline='') as fichier_csv:
        writer = csv.writer(fichier_csv, delimiter=';')
        writer.writerow(ligne)

# Fonction pour ouvrir les fichier GMBI et G2GAI et écrire les premières lignes dans les fchiers correspondants
def charger_ecrire_fichier(input_file, output_file, non_trouve_file):
    # Ouvrir le fichier d'entrée en mode lecture
    with open(input_file, 'r', newline='') as fichier_entree:
        lecteur_fichier_entree = csv.reader(fichier_entree, delimiter=';')
        premiere_ligne_fichier_entree = next(lecteur_fichier_entree)  # Lire la première ligne du fichier d'entrée

        # Ouvrir le fichier de sortie en mode écriture
        with open(output_file, 'w', newline='') as fichier_sortie:
            writer = csv.writer(fichier_sortie, delimiter=';')
            writer.writerow(premiere_ligne_fichier_entree)  # Écrire la première ligne dans le fichier de sortie

        # Ouvrir le fichier "non_trouve" en mode écriture
        with open(non_trouve_file, 'w', newline='') as non_trouve:
            writer = csv.writer(non_trouve, delimiter=';')
            writer.writerow(premiere_ligne_fichier_entree)  # Écrire la première ligne dans le fichier "non_trouve"

        donnees_fichier_entree = list(lecteur_fichier_entree)  # Lire toutes les données du fichier d'entrée et les stocker dans une liste
    
    # Retourner la première ligne et les données du fichier d'entrée
    return premiere_ligne_fichier_entree, donnees_fichier_entree

# Charger les données du fichier GMBI
premiere_ligne_GMBI, donnees_fichierGMBI = charger_ecrire_fichier(fichier_GMBI, nouveau_fichier, GMBI_non_trouve)
# Charger les données du fichier G2GAI
premiere_ligne_G2GAI, donnees_fichierG2GAI = charger_ecrire_fichier(fichier_G2GAI, G2GAI_non_trouve, G2GAI_non_trouve)
# Charger les données du fichier des logements en abandons
premiere_ligne_abandon, donnees_fichierAbandon = charger_ecrire_fichier(fichier_abandon, nom_abandon_non_trouve, nom_abandon_non_trouve)

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
    premier_prenom_precedent = prenom_precedent.split(' ')[0]  # Garder seulement le premier prénom
    date_naissance_precedente = ligne_G2GAI[22]  # Colonne W, DATE DE NAISSANCE
    return nigend_precedent, nom_precedent, prenom_precedent, premier_prenom_precedent, date_naissance_precedente

# Fonction pour extraire les information de l'occupant en N de G2GAI
def informations_occupant_courant(ligne_G2GAI):
    nigend_courant = ligne_G2GAI[26]  # Colonne AA, NIGEND N
    nom_courant = ligne_G2GAI[27]  # Colonne AB, NOM N
    nom_courant = convertir_caracteres_speciaux(nom_courant)
    prenom_courant = ligne_G2GAI[28]  # Colonne AC, PRÉNOM N
    premier_prenom_courant_G2GAI = prenom_courant.split(' ')[0]
    date_naissance_courante = ligne_G2GAI[29]  # Colonne AD, DATE DE NAISSANCE
    return nigend_courant, nom_courant, prenom_courant,premier_prenom_courant_G2GAI, date_naissance_courante

# Fonction pour extraire les information du logement de GMBI
def informations_logement_GMBI(ligne_GMBI):
    departement_local_GMBI = ligne_GMBI[4]  # Colonne E, CODE DÉPARTEMENT
    numero_fiscal_GMBI = ligne_GMBI[2]  # Colonne C, NUMÉRO FISCAL DU LOCAL
    spi1_nom_GMBI = ligne_GMBI[35]  # Colonne AJ, NOM DU SPI 1
    spi1_prenom_GMBI = ligne_GMBI[37]  # Colonne AL, PRÉNOM DU SPI 1
    return departement_local_GMBI, numero_fiscal_GMBI, spi1_nom_GMBI, spi1_prenom_GMBI

# Fonction pour initialiser les variables nécessaires pour traiter les lignes avec l'adresse
def initialiser_variables_adresse(ligne_G2GAI):
    departement_logement_G2GAI, numero_logement_G2GAI = informations_logement_G2GAI(ligne_G2GAI)
    nigend_courant, nom_courant_G2GAI, prenom_courant_G2GAI,premier_prenom_courant_G2GAI, date_naissance_courante = informations_occupant_courant(ligne_G2GAI)

    adresse_G2GAI = ligne_G2GAI[8]
    adresse_G2GAI_caracteres = re.sub(r'\d', '', adresse_G2GAI)
    adresse_G2GAI_chiffres = re.sub(r'\D', '', adresse_G2GAI)

    etage = ligne_G2GAI[11]

    surface_G2GAI = ligne_G2GAI[13]
    ecart_maximal_surface = 5
    nbr_pieces_G2GAI = ligne_G2GAI[14]
    ecart_maximal_piece = 2

    return departement_logement_G2GAI, numero_logement_G2GAI, nigend_courant, nom_courant_G2GAI, prenom_courant_G2GAI, premier_prenom_courant_G2GAI, date_naissance_courante, adresse_G2GAI, adresse_G2GAI_caracteres, adresse_G2GAI_chiffres, etage, surface_G2GAI, ecart_maximal_surface, nbr_pieces_G2GAI, ecart_maximal_piece

# Fonction qui traite les lignes trouvées avec la recherche par adresse
def traiter_correspondance_adresse(adresse_G2GAI_caracteres, adresse_GMBI, valeurs_g2gai_traitees, valeurs_gmbi_traitees, donnees_fichierG2GAI, donnees_fichierGMBI, nouveau_fichier, date_depart, date_arrivee):
    # Utiliser la bibliothèque pour trouver la meilleure correspondance
    meilleure_correspondance, score = process.extractOne(adresse_G2GAI_caracteres, adresse_GMBI)

    # Si le score est supérieur au seuil de similarité minimum
    if score >= similarite_minimum:
        print(f"Valeur trouvée: {meilleure_correspondance}, Score: {score}, Pour {adresse_G2GAI}")

        # Récupérer la première ligne correspondante dans GMBI
        ligne_GMBI = next((ligne for ligne in donnees_fichierGMBI
                            if meilleure_correspondance in ligne
                            and ligne[2] not in valeurs_gmbi_traitees
                            and ligne[3] == ""
                            and "partie" in ligne[18].lower()), None)

        if ligne_GMBI:
            # Traitement de la correspondance
            departement_local_GMBI, numero_fiscal_GMBI, spi1_nom_GMBI, spi1_prenom_GMBI = informations_logement_GMBI(ligne_GMBI)

            if ligne_GMBI[33:44] != [""] * 11 :

                if verifier_date_arrivee(ligne_GMBI, date_arrivee) and verifier_vacance_occupation(ligne_GMBI):

                    # nouvelle_ligne = creer_nouvelle_ligne(ligne_GMBI)
                    nouvelle_ligne = ligne_GMBI[:]  # A ENLEVER
                    nouvelle_ligne[0] = " test 3 Adresse Supprime PP"  # A ENLEVER
                    nouvelle_ligne[46] = date_depart  # Mettre la date de départ pour spi_1
                    # Vérifier s'il y a quelqu'un en Spi_2 pour mettre une date de départ
                    if nouvelle_ligne[49].strip() != '':
                        nouvelle_ligne[60] = date_depart  # Mettre la date de départ pour spi_2

                    determiner_type_occupation(nouvelle_ligne, numero_logement_G2GAI)
                    nouvelle_ligne[64] = numero_logement_G2GAI + adresse_G2GAI_caracteres  # A ENLEVER
                    ecrire_ligne_csv(nouveau_fichier, nouvelle_ligne)

                    nouvelle_ligne[0] = "test 3Adresse Ajout PP"  # A ENLEVER
                    nouvelle_ligne[35] = nom_courant_G2GAI  # Mettre le Nom du nouveau gendarme
                    # premier_prenom_courant_G2GAI = prenom_courant_G2GAI.split(' ')[0]
                    nouvelle_ligne[37] = premier_prenom_courant_G2GAI  # Mettre le Prénom du nouveau gendarme
                    nouvelle_ligne[38] = date_naissance_courante  # Mettre la Date de naissaince du nouveau gendarme

                    # Appel de la pour remplire la ligne en fonction de la vacance ou non et remplisage de la cellule observation
                    determiner_type_occupation(nouvelle_ligne, numero_logement_G2GAI)
                    nouvelle_ligne[64] = numero_logement_G2GAI + adresse_G2GAI_caracteres  # A ENLEVER
                    nouvelle_ligne[45] = date_arrivee  # Mettre la date d'arrivée pour Spi_1

                    # Vider le Spi_2
                    nouvelle_ligne[46:61] = [""] * 15  # Vider toutes les données du Spi_2
                    ecrire_ligne_csv(nouveau_fichier, nouvelle_ligne)

                    valeurs_gmbi_traitees.add(numero_fiscal_GMBI)
                    valeurs_g2gai_traitees.add(numero_logement_G2GAI)

                else:
                    ajouter_gendarme_cause(nouveau_fichier, ligne_GMBI, nom_courant_G2GAI, premier_prenom_courant_G2GAI, date_naissance_courante, numero_logement_G2GAI, date_arrivee, valeurs_gmbi_traitees, valeurs_g2gai_traitees)

            else:
                nouvelle_ligne = ligne_GMBI[:]  # A ENLEVER
                nouvelle_ligne[0] = "test 3 Adresse Ajout PP"  # A ENLEVER
                nouvelle_ligne[35] = nom_courant_G2GAI  # Mettre le Nom du nouveau gendarme
                # premier_prenom_courant_G2GAI = prenom_courant_G2GAI.split(' ')[0]
                nouvelle_ligne[37] = premier_prenom_courant_G2GAI  # Mettre le Prénom du nouveau gendarme
                nouvelle_ligne[38] = date_naissance_courante  # Mettre la Date de naissaince du nouveau gendarme

                # Appel de la pour remplire la ligne en fonction de la vacance ou non et remplisage de la cellule observation
                determiner_type_occupation(nouvelle_ligne, numero_logement_G2GAI)
                nouvelle_ligne[64] = numero_logement_G2GAI + adresse_G2GAI_caracteres  # A ENLEVER
                nouvelle_ligne[45] = date_arrivee  # Mettre la date d'arrivée pour Spi_1

                # Vider le Spi_2
                nouvelle_ligne[46:61] = [""] * 15  # Vider toutes les données du Spi_2
                ecrire_ligne_csv(nouveau_fichier, nouvelle_ligne)

                valeurs_gmbi_traitees.add(numero_fiscal_GMBI)
                valeurs_g2gai_traitees.add(numero_logement_G2GAI)

            for ligne_GMBI in donnees_fichierGMBI:
                
                # S'il ne s'agit pas d'une partie principale 
                if "partie" not in ligne_GMBI[18].lower() and ligne_GMBI[3].strip() != '':

                    # Recherhcer les "dépendances" affectées à ce local
                    if (departement_local_GMBI == ligne_GMBI[4] and
                        ligne_GMBI[2] not in valeurs_gmbi_traitees and
                        numero_fiscal_GMBI == ligne_GMBI[3]):

                        if ligne_GMBI[33:44] != [""] * 11 :

                            if verifier_date_arrivee(ligne_GMBI, date_arrivee) and verifier_vacance_occupation(ligne_GMBI):

                                # nouvelle_ligne = creer_nouvelle_ligne(ligne_GMBI)
                                nouvelle_ligne = ligne_GMBI[:]  # A ENLEVER

                                nouvelle_ligne[0] = "test Adresse Supprime L"  # A ENLEVER
                                nouvelle_ligne[46] = date_depart  # Mettre la date de départ pour spi_1
                                # Vérifier s'il y a quelqu'un en Spi_2 pour mettre une date de départ
                                if nouvelle_ligne[49].strip() != '':
                                    nouvelle_ligne[60] = date_depart  # Mettre la date de départ pour spi_2

                                determiner_type_occupation(nouvelle_ligne, numero_logement_G2GAI)
                                nouvelle_ligne[64] = numero_logement_G2GAI + adresse_G2GAI_caracteres  # A ENLEVER

                                ecrire_ligne_csv(nouveau_fichier, nouvelle_ligne)

                                nouvelle_ligne[0] = "test Adresse Ajout L"  # A ENLEVER
                                nouvelle_ligne[35] = nom_courant_G2GAI  # Mettre le Nom du nouveau gendarme
                                # premier_prenom_courant_G2GAI = prenom_courant_G2GAI.split(' ')[0]
                                nouvelle_ligne[37] = premier_prenom_courant_G2GAI  # Mettre le Prénom du nouveau gendarme
                                nouvelle_ligne[38] = date_naissance_courante  # Mettre la Date de naissaince du nouveau gendarme

                                # Appel de la pour remplire la ligne en fonction de la vacance ou non et remplisage de la cellule observation
                                determiner_type_occupation(nouvelle_ligne, numero_logement_G2GAI)
                                nouvelle_ligne[64] = numero_logement_G2GAI + adresse_G2GAI_caracteres  # A ENLEVER
                                nouvelle_ligne[45] = date_arrivee  # Mettre la date d'arrivée pour Spi_1

                                # Vider le Spi_2
                                nouvelle_ligne[46:61] = [""] * 15  # Vider toutes les données du Spi_2
                                ecrire_ligne_csv(nouveau_fichier, nouvelle_ligne)

                                valeurs_gmbi_traitees.add(ligne_GMBI[2])  # Ajouter la ligne de GMBI à celles déjà traité

                            else:
                                ajouter_gendarme_cause(nouveau_fichier, ligne_GMBI, nom_courant_G2GAI, premier_prenom_courant_G2GAI, date_naissance_courante, numero_logement_G2GAI, date_arrivee, valeurs_gmbi_traitees, valeurs_g2gai_traitees)

                        else:
                            nouvelle_ligne = ligne_GMBI[:]  # A ENLEVER
                            nouvelle_ligne[0] = "test Adresse Ajout L"  # A ENLEVER
                            nouvelle_ligne[35] = nom_courant_G2GAI  # Mettre le Nom du nouveau gendarme
                            # premier_prenom_courant_G2GAI = prenom_courant_G2GAI.split(' ')[0]
                            nouvelle_ligne[37] = premier_prenom_courant_G2GAI  # Mettre le Prénom du nouveau gendarme
                            nouvelle_ligne[38] = date_naissance_courante  # Mettre la Date de naissaince du nouveau gendarme

                            # Appel de la pour remplire la ligne en fonction de la vacance ou non et remplisage de la cellule observation
                            determiner_type_occupation(nouvelle_ligne, numero_logement_G2GAI)
                            nouvelle_ligne[64] = numero_logement_G2GAI + adresse_G2GAI_caracteres  # A ENLEVER
                            nouvelle_ligne[45] = date_arrivee  # Mettre la date d'arrivée pour Spi_1

                            # Vider le Spi_2
                            nouvelle_ligne[46:61] = [""] * 15  # Vider toutes les données du Spi_2
                            ecrire_ligne_csv(nouveau_fichier, nouvelle_ligne)

                            valeurs_gmbi_traitees.add(ligne_GMBI[2])  # Ajouter la ligne de GMBI à celles déjà traité


                if spi1_nom_GMBI and spi1_prenom_GMBI:
                    if (departement_local_GMBI == ligne_GMBI[4] and
                        ligne_GMBI[2] not in valeurs_gmbi_traitees and
                        spi1_nom_GMBI in ligne_GMBI and 
                        spi1_prenom_GMBI in ligne_GMBI):

                        if ligne_GMBI[33:44] != [""] * 11 :

                            if verifier_date_arrivee(ligne_GMBI, date_arrivee) and verifier_vacance_occupation(ligne_GMBI):
                                # nouvelle_ligne = creer_nouvelle_ligne(ligne_GMBI)
                                nouvelle_ligne = ligne_GMBI[:]  # A ENLEVER

                                nouvelle_ligne[0] = "test 2 Local avec adresse Suprimme"  # A ENLEVER
                                nouvelle_ligne[3] = numero_fiscal_GMBI
                                nouvelle_ligne[46] = date_depart  # Mettre la date de départ pour spi_1
                                # Vérifier s'il y a quelqu'un en Spi_2 pour mettre une date de départ
                                if nouvelle_ligne[49].strip() != '':
                                    nouvelle_ligne[60] = date_depart  # Mettre la date de départ pour spi_2

                                determiner_type_occupation(nouvelle_ligne, numero_logement_G2GAI)
                                nouvelle_ligne[64] = numero_logement_G2GAI + adresse_G2GAI_caracteres  # A ENLEVER

                                ecrire_ligne_csv(nouveau_fichier, nouvelle_ligne)

                                nouvelle_ligne[0] = "test 2 Local avec adresse Ajout"  # A ENLEVER
                                nouvelle_ligne[35] = nom_courant_G2GAI  # Mettre le Nom du nouveau gendarme
                                # premier_prenom_courant_G2GAI = prenom_courant_G2GAI.split(' ')[0]
                                nouvelle_ligne[37] = premier_prenom_courant_G2GAI  # Mettre le Prénom du nouveau gendarme
                                nouvelle_ligne[38] = date_naissance_courante  # Mettre la Date de naissaince du nouveau gendarme

                                # Appel de la pour remplire la ligne en fonction de la vacance ou non et remplisage de la cellule observation
                                determiner_type_occupation(nouvelle_ligne, numero_logement_G2GAI)
                                nouvelle_ligne[64] = numero_logement_G2GAI + adresse_G2GAI_caracteres  # A ENLEVER
                                nouvelle_ligne[45] = date_arrivee  # Mettre la date d'arrivée pour Spi_1

                                # Vider le Spi_2
                                nouvelle_ligne[46:61] = [""] * 15  # Vider toutes les données du Spi_2
                                ecrire_ligne_csv(nouveau_fichier, nouvelle_ligne)

                                valeurs_gmbi_traitees.add(ligne_GMBI[2])  # Ajouter la ligne de GMBI à celles déjà traité

                            else:
                                ajouter_gendarme_cause(nouveau_fichier, ligne_GMBI, nom_courant_G2GAI, premier_prenom_courant_G2GAI, date_naissance_courante, numero_logement_G2GAI, date_arrivee, valeurs_gmbi_traitees, valeurs_g2gai_traitees)

                        else:
                            nouvelle_ligne = ligne_GMBI[:]  # A ENLEVER
                            nouvelle_ligne[0] = "test 2 Local avec adresse Ajout"  # A ENLEVER
                            nouvelle_ligne[35] = nom_courant_G2GAI  # Mettre le Nom du nouveau gendarme
                            # premier_prenom_courant_G2GAI = prenom_courant_G2GAI.split(' ')[0]
                            nouvelle_ligne[37] = premier_prenom_courant_G2GAI  # Mettre le Prénom du nouveau gendarme
                            nouvelle_ligne[38] = date_naissance_courante  # Mettre la Date de naissaince du nouveau gendarme

                            # Appel de la pour remplire la ligne en fonction de la vacance ou non et remplisage de la cellule observation
                            determiner_type_occupation(nouvelle_ligne, numero_logement_G2GAI)
                            nouvelle_ligne[64] = numero_logement_G2GAI + adresse_G2GAI_caracteres  # A ENLEVER
                            nouvelle_ligne[45] = date_arrivee  # Mettre la date d'arrivée pour Spi_1

                            # Vider le Spi_2
                            nouvelle_ligne[46:61] = [""] * 15  # Vider toutes les données du Spi_2
                            ecrire_ligne_csv(nouveau_fichier, nouvelle_ligne)

                            valeurs_gmbi_traitees.add(ligne_GMBI[2])  # Ajouter la ligne de GMBI à celles déjà traité


# Fonction qui vérifie si le département est de la Corse pour le convertir comme écrit dans le fichier GMBI
def convertir_code_departement_corse(departement):
    if departement in ['201', '202']:
        if departement == '201':
            return '2A'
        elif departement == '202':
            return '2B'
    return departement

# Fonction pour vérifier si la date d'arrivée est présente et inférieur à la date de départ
def verifier_date_arrivee(ligne, date_arrivee):
    # Vérifier si la cellule en indice 45 est présente et si la date est inférieure à date_arrivee
    if ligne[45] and datetime.strptime(ligne[45], "%d/%m/%Y") < datetime.strptime(date_arrivee, "%d/%m/%Y"):
        return True
    return False

# Écriture des lignes si le format de la date d'arrviée n'est pas bonne
def ajouter_gendarme_cause(nouveau_fichier, ligne_GMBI, nom_courant_G2GAI, premier_prenom_courant_G2GAI, date_naissance_courante, numero_logement_G2GAI, date_arrivee, valeurs_gmbi_traitees, valeurs_g2gai_traitees):
    nouvelle_ligne = ligne_GMBI[:]
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

# Écriture des lignes si la ligne est déclarée comme vacante et occupée ou vacante deux fois
# def verifier_vacance_occupation(ligne):
#     # Vérifier si la cellule en indice 45 est présente et si la date est inférieure à date_arrivee
#     if ligne[44].strip() != '':
#         if ligne[49].strip() == '' and ligne[58].strip() == '':
#             return True
#         return False
#     # return True
#     else:
#         if ligne[35].strip() != '':
#             if ligne[58].strip() == '':
#                 return True
#         return False
def verifier_vacance_occupation(ligne):
    if ligne[33].strip() != '' and ((ligne[44].strip() != '' and ligne[49].strip() == '' and ligne[58].strip() == '') or (ligne[44].strip() == '' and ligne[35].strip() != '' and ligne[58].strip() == '')):
        return True
    return False

# Fonction pour convertir les caractères spéciaux en nornaux (EX : Ÿ -> Y)
def convertir_caracteres_speciaux(chaine):
    return unidecode(chaine)

# Fonction pour les locaux associés au logement des dates 01/01/2024 de GMBI
def date_gmbi(ligne_GMBI, nouveau_fichier, numero_logement_G2GAI, date_naissance_courante, date_arrivee, valeurs_gmbi_traitees):
    print("local")
    # nouvelle_ligne = creer_nouvelle_ligne(ligne_GMBI)
    nouvelle_ligne = ligne_GMBI[:]  
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
    if ligne_GMBI[49].strip() != '':
        ligne_GMBI[59] = date_arrivee
    ecrire_ligne_csv(nouveau_fichier, nouvelle_ligne)
    valeurs_gmbi_traitees.add(ligne_GMBI[2])  

# Recherche des 01/01/2024 de GMBI
for ligne_GMBI in donnees_fichierGMBI:

    if ligne_GMBI[45] == '01/01/2024' and "partie" in ligne_GMBI[18].lower() and ligne_GMBI[2] not in valeurs_gmbi_traitees:
        print("Touvé")
        departement_local_GMBI = ligne_GMBI[4]
        numero_fiscal_GMBI = ligne_GMBI[2]
        nom_GMBI = ligne_GMBI[35]
        prenom_GMBI = ligne_GMBI[37]
        adresse_GMBI = ligne_GMBI[8]

        for ligne_G2GAI in donnees_fichierG2GAI:

            if ligne_G2GAI[27].strip() != '':
                nigend_courant, nom_courant_G2GAI, prenom_courant_G2GAI, premier_prenom_courant_G2GAI, date_naissance_courante = informations_occupant_courant(ligne_G2GAI)
                departement_logement_G2GAI, numero_logement_G2GAI = informations_logement_G2GAI(ligne_G2GAI)

                if (departement_local_GMBI == departement_logement_G2GAI and
                    numero_logement_G2GAI not in valeurs_g2gai_traitees and
                    (((fuzz.partial_token_sort_ratio(nom_courant_G2GAI, ligne_GMBI[35]) == 100 or fuzz.partial_token_sort_ratio(nom_courant_G2GAI, ligne_GMBI[35]) == 100) and
                    premier_prenom_courant_G2GAI == ligne_GMBI[37]) or
                    ((fuzz.partial_token_sort_ratio(nom_courant_G2GAI, ligne_GMBI[49]) == 100 or fuzz.partial_token_sort_ratio(nom_courant_G2GAI, ligne_GMBI[49]) == 100) and
                    premier_prenom_courant_G2GAI == ligne_GMBI[51]))):
                    print("correspondance")
                                        
                    date_naissance_trouvee = date_naissance_courante


                    # nouvelle_ligne = creer_nouvelle_ligne(ligne_GMBI)
                    nouvelle_ligne = ligne_GMBI[:]  # Copie de la ligne correspondante
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

                        for ligne_GMBI in donnees_fichierGMBI:

                            if (ligne_GMBI[2] not in valeurs_gmbi_traitees and
                                "partie" not in ligne_GMBI[18].lower() and
                                ligne_GMBI[3].strip() != ''):

                                if ligne_GMBI[3] == numero_fiscal_GMBI and ligne_GMBI[2] not in valeurs_gmbi_traitees:

                                    date_gmbi(ligne_GMBI, nouveau_fichier, numero_logement_G2GAI, date_naissance_courante, date_arrivee, valeurs_gmbi_traitees)

                                if (ligne_GMBI[2] not in valeurs_gmbi_traitees and
                                    ((ligne_GMBI[35] == nom_GMBI and ligne_GMBI[37] == prenom_GMBI) or
                                    (ligne_GMBI[49] == nom_GMBI and ligne_GMBI[51] == prenom_GMBI)) and
                                    ligne_GMBI[4] == departement_local_GMBI and
                                    ligne_GMBI[8] == adresse_GMBI):

                                    date_gmbi(ligne_GMBI, nouveau_fichier, numero_logement_G2GAI, date_naissance_courante, date_arrivee, valeurs_gmbi_traitees)
# Recherche des 01/01/2024 de GMBI

# 2022
# Parcourir les lignes du fichier G2GAI
for ligne_G2GAI in donnees_fichierG2GAI:

    # Si le logement est Domaniale
    if ligne_G2GAI[16] == "D" and ligne_G2GAI[12] not in valeurs_g2gai_traitees:

        # Appel des focntion pour initialisation des variable de G2GAI
        departement_logement_G2GAI, numero_logement_G2GAI = informations_logement_G2GAI(ligne_G2GAI)
        nigend_precedent, nom_precedent_G2GAI, prenom_precedent_G2GAI, premier_prenom_precedent_G2GAI, date_naissance_precedente = informations_occupant_precedent(ligne_G2GAI)
        nigend_2022 = ligne_G2GAI[33]
        nom_2022_G2GAI = ligne_G2GAI[34]
        prenom_2022_G2GAI = ligne_G2GAI[35]
        premier_prenom_2022_G2GAI = prenom_2022_G2GAI.split(' ')[0]
        date_naissance_2022 = ligne_G2GAI[36]
        nigend_courant, nom_courant_G2GAI, prenom_courant_G2GAI, premier_prenom_courant_G2GAI, date_naissance_courante = informations_occupant_courant(ligne_G2GAI)

        # S'il y a quelqu'un en 2022 dans G2GAI
        if nigend_2022.strip() != '':

            # Si les nigneds sont égaux en 2022 et 2023 dans G2GAI
            if nigend_2022 != nigend_precedent:

                # Parcourir les lignes du fichier GMBI
                for ligne_GMBI in donnees_fichierGMBI:

                    # S'il s'agit d'une partie principale
                    if ("partie" in ligne_GMBI[18].lower() and
                        ligne_GMBI[2] not in valeurs_gmbi_traitees and 
                        ligne_GMBI[3]==""):

                        # Appel de la  focntion pour initialisation des variable de GMBI
                        departement_local_GMBI, numero_fiscal_GMBI, spi1_nom_GMBI, spi1_prenom_GMBI = informations_logement_GMBI(ligne_GMBI)

                        # Chercher une correspondance entre la ligne de G2GAI avec celle de GMBI
                        if (departement_logement_G2GAI == departement_local_GMBI and
                            (fuzz.partial_token_sort_ratio(nom_2022_G2GAI, ligne_GMBI[35]) == 100 or fuzz.partial_token_sort_ratio(nom_2022_G2GAI, ligne_GMBI[49]) == 100) and
                            premier_prenom_2022_G2GAI in ligne_GMBI):

                            if verifier_date_arrivee(ligne_GMBI, date_arrivee) and verifier_vacance_occupation(ligne_GMBI):

                                # Créer une nouvelle ligne avec les modifications nécessaires
                                # nouvelle_ligne = creer_nouvelle_ligne(ligne_GMBI)
                                nouvelle_ligne = ligne_GMBI[:]  # A ENLEVER
                                nouvelle_ligne[0] = "2022Parti PP"  # A ENLEVER
                                nouvelle_ligne[46] = date_depart  # Mettre la date de départ pour spi_1

                                # Appel de la fonction qui cherche où la correspondance a été trouvée pour mettre la date de naissance du gendarme
                                mettre_date_naissance_gendarme(nouvelle_ligne, nom_2022_G2GAI, premier_prenom_2022_G2GAI, date_naissance_2022, spi1_nom_GMBI, spi1_prenom_GMBI)

                                # Appel de la pour remplire la ligne en fonction de la vacance ou non et remplisage de la cellule observation
                                determiner_type_occupation(nouvelle_ligne, numero_logement_G2GAI)

                                # Vérifier s'il y a quelqu'un en Spi_2 pour mettre une date de départ
                                if nouvelle_ligne[49].strip() != '':
                                    nouvelle_ligne[60] = date_depart  # Mettre la date de départ pour spi_2

                                # Écrire la ligne modifiée dans le nouveau fichier
                                ecrire_ligne_csv(nouveau_fichier, nouvelle_ligne)

                                # Renseigner le nouvel occupant
                                nouvelle_ligne[0] = "2022Decla PP"  # A ENLEVER
                                nouvelle_ligne[35] = nom_courant_G2GAI  # Mettre le Nom du nouveau gendarme
                                nouvelle_ligne[37] = premier_prenom_courant_G2GAI  # Mettre le Prénom du nouveau gendarme
                                nouvelle_ligne[38] = date_naissance_courante  # Mettre la Date de naissaince du nouveau gendarme

                                # Appel de la pour remplire la ligne en fonction de la vacance ou non et remplisage de la cellule observation
                                determiner_type_occupation(nouvelle_ligne, numero_logement_G2GAI)

                                # Mettre la date d'arrivée
                                nouvelle_ligne[45] = date_arrivee  # Mettre la date d'arrivée pour Spi_1

                                # Vider l'Id Spi_1
                                # nouvelle_ligne[34] = ""  # Suppression de l'Id (dans la version 2023-2024 iln'y en a pas)

                                # Vider le Spi_2
                                nouvelle_ligne[46:61] = [""] * 15  # Vider toutes les données du Spi_2

                                # Écrire la ligne modifiée dans le nouveau fichier
                                ecrire_ligne_csv(nouveau_fichier, nouvelle_ligne)
                                valeurs_gmbi_traitees.add(numero_fiscal_GMBI)  # Ajouter la ligne de GMBI à celles déjà traité
                                valeurs_g2gai_traitees.add(numero_logement_G2GAI)  # Ajouter la ligne de G2GAI à celles déjà traitées
                                valeurs_g2gai_traitees2022.add(numero_logement_G2GAI)
                            
                            else:
                                ajouter_gendarme_cause(nouveau_fichier, ligne_GMBI, nom_courant_G2GAI, premier_prenom_courant_G2GAI, date_naissance_courante, numero_logement_G2GAI, date_arrivee, valeurs_gmbi_traitees, valeurs_g2gai_traitees)
                                valeurs_g2gai_traitees2022.add(numero_logement_G2GAI)
                                
                            for ligne_GMBI in donnees_fichierGMBI:
                                
                                # S'il ne s'agit pas d'une partie principale 
                                if "partie" not in ligne_GMBI[18].lower() and ligne_GMBI[3].strip() != '':

                                    # Recherhcer les "dépendances" affectées à ce local
                                    if (departement_local_GMBI == ligne_GMBI[4] and
                                        ligne_GMBI[2] not in valeurs_gmbi_traitees and
                                        numero_fiscal_GMBI == ligne_GMBI[3]):

                                        if verifier_date_arrivee(ligne_GMBI, date_arrivee) and verifier_vacance_occupation(ligne_GMBI):

                                            # Créer une nouvelle ligne avec les modifications nécessaires
                                            # nouvelle_ligne = creer_nouvelle_ligne(ligne_GMBI)
                                            nouvelle_ligne = ligne_GMBI[:]  # A ENLEVER
                                            nouvelle_ligne[0] = "2022Parti L"  # A ENLEVER
                                            nouvelle_ligne[46] = date_depart  # Mettre la date de départ pour spi_1

                                            # Appel de la fonction qui cherche où la correspondance a été trouvée pour mettre la date de naissance du gendarme
                                            mettre_date_naissance_gendarme(nouvelle_ligne, nom_2022_G2GAI, premier_prenom_2022_G2GAI, date_naissance_2022, spi1_nom_GMBI, spi1_prenom_GMBI)

                                            # Appel de la pour remplire la ligne en fonction de la vacance ou non et remplisage de la cellule observation
                                            determiner_type_occupation(nouvelle_ligne, numero_logement_G2GAI)

                                            # Vérifier s'il y a quelqu'un en Spi_2 pour mettre une date de départ
                                            if nouvelle_ligne[49].strip() != '':
                                                nouvelle_ligne[60] = date_depart  # Mettre la date de départ pour spi_2

                                            # Écrire la ligne modifiée dans le nouveau fichier
                                            ecrire_ligne_csv(nouveau_fichier, nouvelle_ligne)

                                            nouvelle_ligne[0] = "2022Decla PP"  # A ENLEVER
                                            nouvelle_ligne[35] = nom_courant_G2GAI  # Mettre le Nom du nouveau gendarme
                                            nouvelle_ligne[37] = premier_prenom_courant_G2GAI  # Mettre le Prénom du nouveau gendarme
                                            nouvelle_ligne[38] = date_naissance_courante  # Mettre la Date de naissaince du nouveau gendarme

                                            # Appel de la pour remplire la ligne en fonction de la vacance ou non et remplisage de la cellule observation
                                            determiner_type_occupation(nouvelle_ligne, numero_logement_G2GAI)

                                            # Mettre la date d'arrivée
                                            nouvelle_ligne[45] = date_arrivee  # Mettre la date d'arrivée pour Spi_1

                                            # Vider l'Id Spi_1
                                            # nouvelle_ligne[34] = ""  # Suppression de l'Id (dans la version 2023-2024 iln'y en a pas)

                                            # Vider le Spi_2
                                            nouvelle_ligne[46:61] = [""] * 15  # Vider toutes les données du Spi_2

                                            # Écrire la ligne modifiée dans le nouveau fichier
                                            ecrire_ligne_csv(nouveau_fichier, nouvelle_ligne)
                                            valeurs_gmbi_traitees.add(ligne_GMBI[2])  # Ajouter la ligne de GMBI à celles déjà traité
                                        
                                        else:
                                            ajouter_gendarme_cause(nouveau_fichier, ligne_GMBI, nom_courant_G2GAI, premier_prenom_courant_G2GAI, date_naissance_courante, numero_logement_G2GAI, date_arrivee, valeurs_gmbi_traitees, valeurs_g2gai_traitees)
                                            valeurs_g2gai_traitees2022.add(numero_logement_G2GAI)

# Recherche des locaux assiciés aux logements traités 2022
for ligne_G2GAI in donnees_fichierG2GAI:

    # Si le logement est Domaniale
    if ligne_G2GAI[16] == "D" and ligne_G2GAI[12] in valeurs_g2gai_traitees2022:
        
        # Appel des focntion pour initialisation des variable de G2GAI
        departement_logement_G2GAI, numero_logement_G2GAI = informations_logement_G2GAI(ligne_G2GAI)
        nigend_precedent, nom_precedent_G2GAI, prenom_precedent_G2GAI, premier_prenom_precedent_G2GAI, date_naissance_precedente = informations_occupant_precedent(ligne_G2GAI)
        nigend_2022 = ligne_G2GAI[33]
        nom_2022_G2GAI = ligne_G2GAI[34]
        prenom_2022_G2GAI = ligne_G2GAI[35]
        premier_prenom_2022_G2GAI = prenom_2022_G2GAI.split(' ')[0]
        date_naissance_2022 = ligne_G2GAI[36]
        nigend_courant, nom_courant_G2GAI, prenom_courant_G2GAI, premier_prenom_courant_G2GAI, date_naissance_courante = informations_occupant_courant(ligne_G2GAI)

        # Parcourir les lignes du fichier GMBI
        for ligne_GMBI in donnees_fichierGMBI:

            # S'il s'agit d'une partie principale 
            if ("partie" not in ligne_GMBI[18].lower() and
                ligne_GMBI[3].strip() == '' and
                ligne_GMBI[2] not in valeurs_gmbi_traitees):

                # Appel de la  focntion pour initialisation des variable de GMBI
                departement_local_GMBI, numero_fiscal_GMBI, spi1_nom_GMBI, spi1_prenom_GMBI = informations_logement_GMBI(ligne_GMBI)

                # Chercher une correspondance entre la ligne de G2GAI avec celle de GMBI
                if (departement_logement_G2GAI == departement_local_GMBI and 
                    # nom_2022_G2GAI in ligne_GMBI and
                    (fuzz.partial_token_sort_ratio(nom_2022_G2GAI, ligne_GMBI[35]) == 100 or fuzz.partial_token_sort_ratio(nom_2022_G2GAI, ligne_GMBI[49]) == 100) and
                    premier_prenom_2022_G2GAI in ligne_GMBI):

                    if verifier_date_arrivee(ligne_GMBI, date_arrivee) and verifier_vacance_occupation(ligne_GMBI):

                        # Si les nigneds sont égaux en N-1 et N dans G2GAI
                        if nigend_2022 == nigend_courant:

                            # Créer une nouvelle ligne avec les modifications
                            # nouvelle_ligne = creer_nouvelle_ligne(ligne_GMBI)
                            nouvelle_ligne = ligne_GMBI[:]  # A ENLEVER
                            nouvelle_ligne[0] = "2022Decla L"  # A ENLEVER

                            # Appel de la fonction qui cherche où la correspondance a été trouvée pour mettre la date de naissance du gendarme
                            mettre_date_naissance_gendarme(nouvelle_ligne, nom_2022_G2GAI, premier_prenom_2022_G2GAI, date_naissance_2022, spi1_nom_GMBI, spi1_prenom_GMBI)

                            # Appel de la pour remplire la ligne en fonction de la vacance ou non et remplisage de la cellule observation
                            determiner_type_occupation(nouvelle_ligne, numero_logement_G2GAI)

                            recuperer_idGroupLoc_et_assigner(donnees_fichierGMBI, departement_local_GMBI, valeurs_gmbi_traitees, nom_2022_G2GAI, premier_prenom_2022_G2GAI, nouvelle_ligne)

                            # Écrire la ligne modifiée dans le nouveau fichier 
                            ecrire_ligne_csv(nouveau_fichier, nouvelle_ligne)
                            valeurs_gmbi_traitees.add(numero_fiscal_GMBI)  # Ajouter la ligne de GMBI à celles déjà traité

                        else:
                            # Créer une nouvelle ligne avec les modifications nécessaires
                            # nouvelle_ligne = creer_nouvelle_ligne(ligne_GMBI)
                            nouvelle_ligne = ligne_GMBI[:]  # A ENLEVER
                            nouvelle_ligne[0] = "2022Parti L"  # A ENLEVER
                            nouvelle_ligne[46] = date_depart  # Mettre la date de départ pour spi_1

                            # Appel de la fonction qui cherche où la correspondance a été trouvée pour mettre la date de naissance du gendarme
                            mettre_date_naissance_gendarme(nouvelle_ligne, nom_2022_G2GAI, premier_prenom_2022_G2GAI, date_naissance_2022, spi1_nom_GMBI, spi1_prenom_GMBI)

                            # Appel de la pour remplire la ligne en fonction de la vacance ou non et remplisage de la cellule observation
                            determiner_type_occupation(nouvelle_ligne, numero_logement_G2GAI)

                            # Vérifier s'il y a quelqu'un en Spi_2 pour mettre une date de départ
                            if nouvelle_ligne[49].strip() != '':
                                nouvelle_ligne[60] = date_depart  # Mettre la date de départ pour spi_2

                            recuperer_idGroupLoc_et_assigner(donnees_fichierGMBI, departement_local_GMBI, valeurs_gmbi_traitees, nom_2022_G2GAI, premier_prenom_2022_G2GAI, nouvelle_ligne)

                            # Écrire la ligne modifiée dans le nouveau fichier
                            ecrire_ligne_csv(nouveau_fichier, nouvelle_ligne)

                            # Renseigner le nouvel occupant
                            nouvelle_ligne[0] = "2022Decla L"  # A ENLEVER
                            nouvelle_ligne[35] = nom_courant_G2GAI  # Mettre le Nom du nouveau gendarme
                            # premier_prenom_courant_G2GAI = prenom_courant_G2GAI.split(' ')[0]
                            nouvelle_ligne[37] = premier_prenom_courant_G2GAI  # Mettre le Prénom du nouveau gendarme
                            nouvelle_ligne[38] = date_naissance_courante  # Mettre la Date de naissaince du nouveau gendarme

                            # Appel de la pour remplire la ligne en fonction de la vacance ou non et remplisage de la cellule observation
                            determiner_type_occupation(nouvelle_ligne, numero_logement_G2GAI)

                            # CHANGER L'ID SPI
                            nouvelle_ligne[45] = date_arrivee  # Mettre la date d'arrivée pour Spi_1

                            # Vider l'Id Spi_1
                            # nouvelle_ligne[34] = ""  # Suppression de l'Id (dans la version 2023-2024 iln'y en a pas)

                            # Vider le Spi_2
                            nouvelle_ligne[46:61] = [""] * 15  # Vider toutes les données du Spi_2

                            # Écrire la ligne modifiée dans le nouveau fichier
                            ecrire_ligne_csv(nouveau_fichier, nouvelle_ligne)
                            valeurs_gmbi_traitees.add(numero_fiscal_GMBI)  # Ajouter la ligne de GMBI à celles déjà traité

                    else:
                        nouvelle_ligne = ligne_GMBI[:]
                        nouvelle_ligne[1] = "2022Parti Erreur L"
                        ecrire_ligne_csv(nouveau_fichier, nouvelle_ligne)
                        nouvelle_ligne[0] = "2022Decla Erreur L"
                        nouvelle_ligne[1] = ""
                        nouvelle_ligne[35] = nom_courant_G2GAI
                        nouvelle_ligne[37] = premier_prenom_courant_G2GAI
                        nouvelle_ligne[38] = date_naissance_courante  # Mettre la Date de naissaince du nouveau gendarme
                        determiner_type_occupation(nouvelle_ligne, numero_logement_G2GAI)
                        recuperer_idGroupLoc_et_assigner(donnees_fichierGMBI, departement_local_GMBI, valeurs_gmbi_traitees, nom_2022_G2GAI, premier_prenom_2022_G2GAI, nouvelle_ligne)
                        nouvelle_ligne[45] = date_arrivee
                        nouvelle_ligne[46:61] = [""] * 15
                        ecrire_ligne_csv(nouveau_fichier, nouvelle_ligne)
                        valeurs_gmbi_traitees.add(ligne_GMBI[2])  # Ajouter la ligne de GMBI à celles déjà traité
                        # valeurs_g2gai_traitees.add(numero_logement_G2GAI)
                        # valeurs_g2gai_traitees2022.add(numero_logement_G2GAI)
# 2022

# 2023
# Parcourir les lignes du fichier G2GAI
for ligne_G2GAI in donnees_fichierG2GAI:

    # Si le logement est Domaniale
    if ligne_G2GAI[16] == "D" and ligne_G2GAI[12] not in valeurs_g2gai_traitees:

        # Appel des focntion pour initialisation des variable de G2GAI
        departement_logement_G2GAI, numero_logement_G2GAI = informations_logement_G2GAI(ligne_G2GAI)
        nigend_precedent, nom_precedent_G2GAI, prenom_precedent_G2GAI, premier_prenom_precedent_G2GAI, date_naissance_precedente = informations_occupant_precedent(ligne_G2GAI)
        nigend_courant, nom_courant_G2GAI, prenom_courant_G2GAI, premier_prenom_courant_G2GAI, date_naissance_courante = informations_occupant_courant(ligne_G2GAI)

        # S'il y a quelqu'un en N-1 dans G2GAI
        if nigend_precedent.strip() != '':

            # Si les nigneds sont égaux en N-1 et N dans G2GAI
            if nigend_precedent == nigend_courant:

                # Parcourir les lignes du fichier GMBI
                for ligne_GMBI in donnees_fichierGMBI:

                    # S'il s'agit d'une partie principale 
                    if ("partie" in ligne_GMBI[18].lower() and
                        ligne_GMBI[3].strip() == ''and 
                        ligne_GMBI[2] not in valeurs_gmbi_traitees):

                        # Appel de la  focntion pour initialisation des variable de GMBI
                        departement_local_GMBI, numero_fiscal_GMBI, spi1_nom_GMBI, spi1_prenom_GMBI = informations_logement_GMBI(ligne_GMBI)

                        # Chercher une correspondance entre la line de G2GAI avec celle de GMBI
                        if (departement_logement_G2GAI == departement_local_GMBI  and
                            (fuzz.partial_token_sort_ratio(nom_precedent_G2GAI, ligne_GMBI[35]) == 100 or fuzz.partial_token_sort_ratio(nom_precedent_G2GAI, ligne_GMBI[49]) == 100) and
                            premier_prenom_precedent_G2GAI in ligne_GMBI):

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

                            for ligne_GMBI in donnees_fichierGMBI:
                                
                                # S'il ne s'agit pas d'une partie principale 
                                if "partie" not in ligne_GMBI[18].lower() and ligne_GMBI[3].strip() != '':

                                    # Recherhcer les "dépendances" affectées à ce local
                                    if (departement_local_GMBI == ligne_GMBI[4] and
                                        ligne_GMBI[2] not in valeurs_gmbi_traitees and
                                        numero_fiscal_GMBI == ligne_GMBI[3]):

                                        if verifier_date_arrivee(ligne_GMBI, date_arrivee) and verifier_vacance_occupation(ligne_GMBI):

                                            # Créer une nouvelle ligne avec les modifications
                                            nouvelle_ligne = creer_nouvelle_ligne(ligne_GMBI)

                                            # if (nom_precedent_G2GAI in ligne_GMBI and
                                            if((fuzz.partial_token_sort_ratio(nom_precedent_G2GAI, ligne_GMBI[35]) == 100 or fuzz.partial_token_sort_ratio(nom_precedent_G2GAI, ligne_GMBI[49]) == 100) and
                                                premier_prenom_precedent_G2GAI in ligne_GMBI):

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
                                                nouvelle_ligne = ligne_GMBI[:]  # A ENLEVER
                                                nouvelle_ligne[0] = "Pareil Surpime L"  # A ENLEVER
                                                nouvelle_ligne[46] = date_depart  # Mettre la date de départ pour spi_1

                                                # Appel de la fonction qui cherche où la correspondance a été trouvée pour mettre la date de naissance du gendarme
                                                mettre_date_naissance_gendarme(nouvelle_ligne, nom_precedent_G2GAI, premier_prenom_precedent_G2GAI, date_naissance_precedente, spi1_nom_GMBI, spi1_prenom_GMBI)

                                                # Appel de la pour remplire la ligne en fonction de la vacance ou non et remplisage de la cellule observation
                                                determiner_type_occupation(nouvelle_ligne, numero_logement_G2GAI)

                                                # Vérifier s'il y a quelqu'un en Spi_2 pour mettre une date de départ
                                                if nouvelle_ligne[49].strip() != '':
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
                for ligne_GMBI in donnees_fichierGMBI:

                    # S'il s'agit d'une partie principale
                    if ("partie" in ligne_GMBI[18].lower() and
                        ligne_GMBI[3]==""and 
                        ligne_GMBI[2] not in valeurs_gmbi_traitees):

                        # Appel de la  focntion pour initialisation des variable de GMBI
                        departement_local_GMBI, numero_fiscal_GMBI, spi1_nom_GMBI, spi1_prenom_GMBI = informations_logement_GMBI(ligne_GMBI)

                        # Chercher une correspondance entre la ligne de G2GAI avec celle de GMBI
                        if (departement_logement_G2GAI == departement_local_GMBI  and
                            # nom_precedent_G2GAI in ligne_GMBI and
                            (fuzz.partial_token_sort_ratio(nom_precedent_G2GAI, ligne_GMBI[35]) == 100 or fuzz.partial_token_sort_ratio(nom_precedent_G2GAI, ligne_GMBI[49]) == 100) and
                            premier_prenom_precedent_G2GAI in ligne_GMBI):

                            if verifier_date_arrivee(ligne_GMBI, date_arrivee) and verifier_vacance_occupation(ligne_GMBI):

                                # Créer une nouvelle ligne avec les modifications nécessaires
                                # nouvelle_ligne = creer_nouvelle_ligne(ligne_GMBI)
                                nouvelle_ligne = ligne_GMBI[:]  # A ENLEVER
                                nouvelle_ligne[0] = "Different Supprime PP"  # A ENLEVER
                                nouvelle_ligne[46] = date_depart  # Mettre la date de départ pour spi_1

                                # Appel de la fonction qui cherche où la correspondance a été trouvée pour mettre la date de naissance du gendarme
                                mettre_date_naissance_gendarme(nouvelle_ligne, nom_precedent_G2GAI, premier_prenom_precedent_G2GAI, date_naissance_precedente, spi1_nom_GMBI, spi1_prenom_GMBI)

                                # Appel de la pour remplire la ligne en fonction de la vacance ou non et remplisage de la cellule observation
                                determiner_type_occupation(nouvelle_ligne, numero_logement_G2GAI)

                                # Vérifier s'il y a quelqu'un en Spi_2 pour mettre une date de départ
                                if nouvelle_ligne[49].strip() != '':
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

                                # CHANGER L'ID SPI
                                nouvelle_ligne[45] = date_arrivee  # Mettre la date d'arrivée pour Spi_1

                                # Vider l'Id Spi_1
                                # nouvelle_ligne[34] = ""  # Suppression de l'Id (dans la version 2023-2024 iln'y en a pas)

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

                            for ligne_GMBI in donnees_fichierGMBI:
                                
                                # S'il ne s'agit pas d'une partie principale 
                                if "partie" not in ligne_GMBI[18].lower() and ligne_GMBI[3].strip() != '':

                                    # Recherhcer les "dépendances" affectées à ce local
                                    if (departement_local_GMBI == ligne_GMBI[4] and
                                        ligne_GMBI[2] not in valeurs_gmbi_traitees and
                                        numero_fiscal_GMBI == ligne_GMBI[3]):

                                        if verifier_date_arrivee(ligne_GMBI, date_arrivee) and verifier_vacance_occupation(ligne_GMBI):

                                            # Créer une nouvelle ligne avec les modifications nécessaires
                                            # nouvelle_ligne = creer_nouvelle_ligne(ligne_GMBI)
                                            nouvelle_ligne = ligne_GMBI[:]  # A ENLEVER
                                            nouvelle_ligne[0] = "Different Supprime L"  # A ENLEVER
                                            nouvelle_ligne[46] = date_depart  # Mettre la date de départ pour spi_1

                                            # Appel de la fonction qui cherche où la correspondance a été trouvée pour mettre la date de naissance du gendarme
                                            mettre_date_naissance_gendarme(nouvelle_ligne, nom_precedent_G2GAI, premier_prenom_precedent_G2GAI, date_naissance_precedente, spi1_nom_GMBI, spi1_prenom_GMBI)

                                            # Appel de la pour remplire la ligne en fonction de la vacance ou non et remplisage de la cellule observation
                                            determiner_type_occupation(nouvelle_ligne, numero_logement_G2GAI)

                                            # Vérifier s'il y a quelqu'un en Spi_2 pour mettre une date de départ
                                            if nouvelle_ligne[49].strip() != '':
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

                                            # CHANGER L'ID SPI
                                            nouvelle_ligne[45] = date_arrivee  # Mettre la date d'arrivée pour Spi_1

                                            # Vider l'Id Spi_1
                                            # nouvelle_ligne[34] = ""  # Suppression de l'Id (dans la version 2023-2024 iln'y en a pas)

                                            # Vider le Spi_2
                                            nouvelle_ligne[46:61] = [""] * 15  # Vider toutes les données du Spi_2

                                            # Écrire la ligne modifiée dans le nouveau fichier
                                            ecrire_ligne_csv(nouveau_fichier, nouvelle_ligne)
                                            valeurs_gmbi_traitees.add(ligne_GMBI[2])  # Ajouter la ligne de GMBI à celles déjà traité
                                        
                                        else:
                                            ajouter_gendarme_cause(nouveau_fichier, ligne_GMBI, nom_courant_G2GAI, premier_prenom_courant_G2GAI, date_naissance_courante, numero_logement_G2GAI, date_arrivee, valeurs_gmbi_traitees, valeurs_g2gai_traitees)
                                            valeurs_g2gai_traitees2023.add(numero_logement_G2GAI)  # Ajouter la ligne de G2GAI à celles déjà traitées

# Locaux associers aux logements traités 
# Parcourir les lignes du fichier G2GAI
for ligne_G2GAI in donnees_fichierG2GAI:

    # Si le logement est Domaniale
    if ligne_G2GAI[16] == "D" and ligne_G2GAI[12] in valeurs_g2gai_traitees2023:
        
        # Appel des focntion pour initialisation des variable de G2GAI
        departement_logement_G2GAI, numero_logement_G2GAI = informations_logement_G2GAI(ligne_G2GAI)
        nigend_precedent, nom_precedent_G2GAI, prenom_precedent_G2GAI, premier_prenom_precedent_G2GAI, date_naissance_precedente = informations_occupant_precedent(ligne_G2GAI)
        nigend_courant, nom_courant_G2GAI, prenom_courant_G2GAI, premier_prenom_courant_G2GAI, date_naissance_courante = informations_occupant_courant(ligne_G2GAI)

        # Parcourir les lignes du fichier GMBI
        for ligne_GMBI in donnees_fichierGMBI:

            # S'il s'agit d'une partie principale 
            if "partie" not in ligne_GMBI[18].lower() and ligne_GMBI[3].strip() == '':

                # Appel de la  focntion pour initialisation des variable de GMBI
                departement_local_GMBI, numero_fiscal_GMBI, spi1_nom_GMBI, spi1_prenom_GMBI = informations_logement_GMBI(ligne_GMBI)

                # Chercher une correspondance entre la ligne de G2GAI avec celle de GMBI
                if (departement_logement_G2GAI == departement_local_GMBI and 
                    numero_fiscal_GMBI not in valeurs_gmbi_traitees and
                    # nom_precedent_G2GAI in ligne_GMBI and
                    (fuzz.partial_token_sort_ratio(nom_precedent_G2GAI, ligne_GMBI[35]) == 100 or fuzz.partial_token_sort_ratio(nom_precedent_G2GAI, ligne_GMBI[49]) == 100) and
                    premier_prenom_precedent_G2GAI in ligne_GMBI):

                    if verifier_date_arrivee(ligne_GMBI, date_arrivee) and verifier_vacance_occupation(ligne_GMBI):

                        # Si les nigneds sont égaux en N-1 et N dans G2GAI
                        if nigend_precedent == nigend_courant:

                            # Créer une nouvelle ligne avec les modifications
                            nouvelle_ligne = creer_nouvelle_ligne(ligne_GMBI)

                            # Appel de la fonction qui cherche où la correspondance a été trouvée pour mettre la date de naissance du gendarme
                            mettre_date_naissance_gendarme(nouvelle_ligne, nom_precedent_G2GAI, premier_prenom_precedent_G2GAI, date_naissance_precedente, spi1_nom_GMBI, spi1_prenom_GMBI)

                            # Appel de la pour remplire la ligne en fonction de la vacance ou non et remplisage de la cellule observation
                            determiner_type_occupation(nouvelle_ligne, numero_logement_G2GAI)

                            recuperer_idGroupLoc_et_assigner(donnees_fichierGMBI, departement_local_GMBI, valeurs_gmbi_traitees, nom_precedent_G2GAI, premier_prenom_precedent_G2GAI, nouvelle_ligne)

                            # Écrire la ligne modifiée dans le nouveau fichier 
                            ecrire_ligne_csv(nouveau_fichier, nouvelle_ligne)
                            valeurs_gmbi_traitees.add(numero_fiscal_GMBI)  # Ajouter la ligne de GMBI à celles déjà traité

                        else:
                            # Créer une nouvelle ligne avec les modifications nécessaires
                            # nouvelle_ligne = creer_nouvelle_ligne(ligne_GMBI)
                            nouvelle_ligne = ligne_GMBI[:]  # A ENLEVER
                            nouvelle_ligne[0] = "Local Nom Supprime"  # A ENLEVER
                            nouvelle_ligne[46] = date_depart  # Mettre la date de départ pour spi_1

                            # Appel de la fonction qui cherche où la correspondance a été trouvée pour mettre la date de naissance du gendarme
                            mettre_date_naissance_gendarme(nouvelle_ligne, nom_precedent_G2GAI, premier_prenom_precedent_G2GAI, date_naissance_precedente, spi1_nom_GMBI, spi1_prenom_GMBI)

                            # Appel de la pour remplire la ligne en fonction de la vacance ou non et remplisage de la cellule observation
                            determiner_type_occupation(nouvelle_ligne, numero_logement_G2GAI)

                            # Vérifier s'il y a quelqu'un en Spi_2 pour mettre une date de départ
                            if nouvelle_ligne[49].strip() != '':
                                nouvelle_ligne[60] = date_depart  # Mettre la date de départ pour spi_2

                            recuperer_idGroupLoc_et_assigner(donnees_fichierGMBI, departement_local_GMBI, valeurs_gmbi_traitees, nom_precedent_G2GAI, premier_prenom_precedent_G2GAI, nouvelle_ligne)

                            # Écrire la ligne modifiée dans le nouveau fichier
                            ecrire_ligne_csv(nouveau_fichier, nouvelle_ligne)

                            # Renseigner le nouvel occupant
                            nouvelle_ligne[0] = "Local Nom Ajout"  # A ENLEVER
                            nouvelle_ligne[35] = nom_courant_G2GAI  # Mettre le Nom du nouveau gendarme
                            # premier_prenom_courant_G2GAI = prenom_courant_G2GAI.split(' ')[0]
                            nouvelle_ligne[37] = premier_prenom_courant_G2GAI  # Mettre le Prénom du nouveau gendarme
                            nouvelle_ligne[38] = date_naissance_courante  # Mettre la Date de naissaince du nouveau gendarme

                            # Appel de la pour remplire la ligne en fonction de la vacance ou non et remplisage de la cellule observation
                            determiner_type_occupation(nouvelle_ligne, numero_logement_G2GAI)

                            # CHANGER L'ID SPI
                            nouvelle_ligne[45] = date_arrivee  # Mettre la date d'arrivée pour Spi_1

                            # Vider l'Id Spi_1
                            # nouvelle_ligne[34] = ""  # Suppression de l'Id (dans la version 2023-2024 iln'y en a pas)

                            # Vider le Spi_2
                            nouvelle_ligne[46:61] = [""] * 15  # Vider toutes les données du Spi_2

                            # Écrire la ligne modifiée dans le nouveau fichier
                            ecrire_ligne_csv(nouveau_fichier, nouvelle_ligne)
                            valeurs_gmbi_traitees.add(numero_fiscal_GMBI)  # Ajouter la ligne de GMBI à celles déjà traité

                    else:
                        nouvelle_ligne = ligne_GMBI[:]
                        nouvelle_ligne[1] = "Erreur Local Nom"
                        ecrire_ligne_csv(nouveau_fichier, nouvelle_ligne)
                        nouvelle_ligne[0] = "Ajout Erreur Local Nom"
                        nouvelle_ligne[1] = ""
                        nouvelle_ligne[35] = nom_courant_G2GAI
                        nouvelle_ligne[37] = premier_prenom_courant_G2GAI
                        nouvelle_ligne[38] = date_naissance_courante  # Mettre la Date de naissaince du nouveau gendarme
                        determiner_type_occupation(nouvelle_ligne, numero_logement_G2GAI)
                        recuperer_idGroupLoc_et_assigner(donnees_fichierGMBI, departement_local_GMBI, valeurs_gmbi_traitees, nom_precedent_G2GAI, premier_prenom_precedent_G2GAI, nouvelle_ligne)
                        nouvelle_ligne[45] = date_arrivee
                        nouvelle_ligne[46:61] = [""] * 15
                        ecrire_ligne_csv(nouveau_fichier, nouvelle_ligne)
                        valeurs_gmbi_traitees.add(ligne_GMBI[2])  # Ajouter la ligne de GMBI à celles déjà traité
                        valeurs_g2gai_traitees.add(numero_logement_G2GAI)
                        valeurs_g2gai_traitees2023.add(numero_logement_G2GAI)  # Ajouter la ligne de G2GAI à celles déjà traitées
# Locaux associers aux logements traités 
# 2023

# En cours d'abandon G2GAI
# Parcourir les lignes du fichier abandon
similarite_minimum = 100
while similarite_minimum >= 70:
    print(f"{similarite_minimum} total")
    # Parcourir les lignes du fichier abandon
    for ligne_abandon in donnees_fichierAbandon:

        # Si le logement n'a pas déjà été traité
        if ligne_abandon[0] not in valeurs_abandon_traitees:

            numero_logement_abandon = ligne_abandon[0]
            code_ui_abandon = ligne_abandon[1]
            if numero_logement_abandon.startswith("1 0") and numero_logement_abandon[4] == "0":
                departement_logement_abandon = numero_logement_abandon[3:4]
            elif numero_logement_abandon.startswith("1"):
                departement_logement_abandon = numero_logement_abandon[2:4]
            else:
                departement_logement_abandon = numero_logement_abandon[2:5]
            departement_logement_abandon = convertir_code_departement_corse(departement_logement_abandon)
            commune_abandon = ligne_abandon[5]
            adresse_abandon = ligne_abandon[3]

            # Extraire les valeurs de l'adresse de la colonne J de GMBI
            adresse_GMBI = [ligne for ligne in donnees_fichierGMBI
                            if ligne[4] == departement_logement_abandon
                                and (fuzz.partial_token_sort_ratio(ligne[6], ligne_abandon[5] ) >= 85 or fuzz.token_set_ratio(ligne[6], ligne_abandon[5] ) >= 85)
                                and ligne[2] not in valeurs_gmbi_traitees
                                and ligne[3] == ""
                                and "partie" in ligne[18].lower()]

            if adresse_GMBI:
                for ligne_GMBI in adresse_GMBI:
                    meilleure_correspondance, score = process.extractOne(adresse_abandon, [ligne_GMBI[9]])

                    # Si le score est supérieur au seuil de similarité minimum
                    if score >= similarite_minimum:
                        print(f"Valeur trouvée: {meilleure_correspondance} Score: {score}, Pour {adresse_abandon}")

                        # Dupliquer toutes les lignes avec le même libellé d'adresse de GMBI
                        for ligne_similaire_GMBI in donnees_fichierGMBI:
                            if (ligne_similaire_GMBI[9] == ligne_GMBI[9] and
                                ligne_similaire_GMBI[2] not in valeurs_gmbi_traitees):  # Vérifier si les adresses sont les mêmes et que la ligne n'a pas encore été traitée
                                # Traitement de la correspondance
                                departement_local_GMBI, numero_fiscal_GMBI, spi1_nom_GMBI, spi1_prenom_GMBI = informations_logement_GMBI(ligne_similaire_GMBI)
                                commune_GMBI = ligne_similaire_GMBI[6]
                                adresse_GMBI = ligne_similaire_GMBI[9]

                                if verifier_date_arrivee(ligne_similaire_GMBI, date_arrivee) and verifier_vacance_occupation(ligne_similaire_GMBI):

                                    nouvelle_ligne = ligne_similaire_GMBI[:]  # Dupliquer la ligne pour éviter de modifier l'original
                                    nouvelle_ligne[0] = "abandonPARTI"  # A ENLEVER
                                    determiner_type_occupation(nouvelle_ligne, numero_logement_G2GAI)
                                    nouvelle_ligne[46] = date_depart  # Mettre la date de départ pour spi_1
                                    if nouvelle_ligne[49].strip() != '':
                                        nouvelle_ligne[60] = date_depart  # Mettre la date de départ pour spi_2
                                    nouvelle_ligne[64] = f"Abandon nom de rue G2GAI : {adresse_abandon} numero UI : {code_ui_abandon}"
                                    ecrire_ligne_csv(nouveau_fichier, nouvelle_ligne)

                                    # # Créer une nouvelle ligne avec les modifications nécessaires
                                    # nouvelle_ligne[0] = "abandonARRIVE"  # A ENLEVER
                                    # nouvelle_ligne[33:61] = [""] * 28
                                    # nouvelle_ligne[32] = "3"
                                    # nouvelle_ligne[33] = ""
                                    # nouvelle_ligne[45] = date_arrivee 

                                    # ecrire_ligne_csv(nouveau_fichier, nouvelle_ligne)

                                    # Marquer la ligne de GMBI comme traitée
                                    valeurs_gmbi_traitees.add(ligne_similaire_GMBI[2])  # Ajouter la ligne de GMBI à celles déjà traitées

                                else:
                                    # Gérer le cas où la date d'arrivée ou l'occupation est incorrecte
                                    nouvelle_ligne = ligne_similaire_GMBI[:]
                                    nouvelle_ligne[1] = "abandon"
                                    nouvelle_ligne[64] = f"Abandon nom de rue G2GAI : {adresse_abandon}"
                                    ecrire_ligne_csv(nouveau_fichier, nouvelle_ligne)
                                    # nouvelle_ligne[0] = "abandonERREUR"
                                    # nouvelle_ligne[1] = ""
                                    # nouvelle_ligne[33:61] = [""] * 28
                                    # nouvelle_ligne[32] = "3"
                                    # nouvelle_ligne[33] = ""
                                    # nouvelle_ligne[45] = date_arrivee 
                                    # nouvelle_ligne[64] = f"Abandon nom de rue G2GAI : {adresse_abandon} numéro UI : {code_ui_abandon}"
                                    # ecrire_ligne_csv(nouveau_fichier, nouvelle_ligne)
                                    valeurs_gmbi_traitees.add(ligne_similaire_GMBI[2])  # Ajouter la ligne de GMBI à celles déjà traitées
                                
                        # Marquer toutes les lignes Abandon avec le même libellé d'adresse comme traitées
                        valeurs_abandon_traitees.update([x[0] for x in donnees_fichierAbandon if x[3] == adresse_abandon])

    similarite_minimum -= 5
# En cours d'abandon G2GAI

# Correspondance adresse
# Traitement des lignes où il n'y à personne en N-1 ou qui n'ont pas été traitées
similarite_minimum = 100
while similarite_minimum >= 80:
    print(f"{similarite_minimum} total")
    # Parcourir les lignes du fichier G2GAI
    for ligne_G2GAI in donnees_fichierG2GAI:

        # Si le logement est Domaniale et n'a pas été traité
        if ligne_G2GAI[16] == "D" and ligne_G2GAI[12] not in valeurs_g2gai_traitees:

            # Appel à la fonction pour initialisation des variables adresse
            (departement_logement_G2GAI, numero_logement_G2GAI, nigend_courant, nom_courant_G2GAI, prenom_courant_G2GAI, premier_prenom_courant_G2GAI, date_naissance_courante, adresse_G2GAI, adresse_G2GAI_caracteres, adresse_G2GAI_chiffres, etage, surface_G2GAI, ecart_maximal_surface, nbr_pieces_G2GAI, ecart_maximal_piece) = initialiser_variables_adresse(ligne_G2GAI)

            # Extraire les valeurs de l'adresse de la colonne J de GMBI
            adresse_GMBI = [ligne[9] for ligne in donnees_fichierGMBI
                                if ligne[4] == departement_logement_G2GAI
                                    and (fuzz.partial_token_sort_ratio(ligne[6], ligne_G2GAI[10] ) >= 85 or fuzz.token_set_ratio(ligne[6], ligne_G2GAI[10] ) >= 85)
                                    and ligne[2] not in valeurs_gmbi_traitees
                                    and ligne[3] == ""
                                    and "partie" in ligne[18].lower()
                                    and ligne[7] == adresse_G2GAI_chiffres
                                    and int(ligne[21]) - ecart_maximal_surface <= int(surface_G2GAI) <= int(ligne[21]) + ecart_maximal_surface
                                    and int(ligne[20]) - ecart_maximal_piece <= int(nbr_pieces_G2GAI) <= int(ligne[20]) + ecart_maximal_piece]

            if adresse_GMBI:
                traiter_correspondance_adresse(adresse_G2GAI_caracteres, adresse_GMBI, valeurs_g2gai_traitees, valeurs_gmbi_traitees, donnees_fichierG2GAI, donnees_fichierGMBI, nouveau_fichier, date_depart, date_arrivee)

    similarite_minimum -= 5

similarite_minimum = 100
while similarite_minimum >= 80:
    print(f"{similarite_minimum} sans numéro de rue")
    # Parcourir les lignes du fichier G2GAI
    for ligne_G2GAI in donnees_fichierG2GAI:

        # Si le logement est Domaniale et n'a pas été traité
        if ligne_G2GAI[16] == "D" and ligne_G2GAI[12] not in valeurs_g2gai_traitees:

            # Appel à la fonction pour initialisation des variables adresse
            (departement_logement_G2GAI, numero_logement_G2GAI, nigend_courant, nom_courant_G2GAI, prenom_courant_G2GAI, premier_prenom_courant_G2GAI, date_naissance_courante, adresse_G2GAI, adresse_G2GAI_caracteres, adresse_G2GAI_chiffres, etage, surface_G2GAI, ecart_maximal_surface, nbr_pieces_G2GAI, ecart_maximal_piece) = initialiser_variables_adresse(ligne_G2GAI)

            # Extraire les valeurs de l'adresse de la colonne J de GMBI
            adresse_GMBI = [ligne[9] for ligne in donnees_fichierGMBI
                                if ligne[4] == departement_logement_G2GAI
                                    and (fuzz.partial_token_sort_ratio(ligne[6], ligne_G2GAI[10] ) >= 85 or fuzz.token_set_ratio(ligne[6], ligne_G2GAI[10] ) >= 85)
                                    and ligne[2] not in valeurs_gmbi_traitees
                                    and ligne[3] == ""
                                    and "partie" in ligne[18].lower()
                                    and int(ligne[21]) - ecart_maximal_surface <= int(surface_G2GAI) <= int(ligne[21]) + ecart_maximal_surface
                                    and int(ligne[20]) - ecart_maximal_piece <= int(nbr_pieces_G2GAI) <= int(ligne[20]) + ecart_maximal_piece]

            if adresse_GMBI:
                traiter_correspondance_adresse(adresse_G2GAI_caracteres, adresse_GMBI, valeurs_g2gai_traitees, valeurs_gmbi_traitees, donnees_fichierG2GAI, donnees_fichierGMBI, nouveau_fichier, date_depart, date_arrivee)

    similarite_minimum -= 5

similarite_minimum = 100
while similarite_minimum >= 80:
    print(f"{similarite_minimum} sans le nombre de pièce")
    # Parcourir les lignes du fichier G2GAI
    for ligne_G2GAI in donnees_fichierG2GAI:

        # Si le logement est Domaniale et n'a pas été traité
        if ligne_G2GAI[16] == "D" and ligne_G2GAI[12] not in valeurs_g2gai_traitees:

            # Appel à la fonction pour initialisation des variables adresse
            (departement_logement_G2GAI, numero_logement_G2GAI, nigend_courant, nom_courant_G2GAI, prenom_courant_G2GAI, premier_prenom_courant_G2GAI, date_naissance_courante, adresse_G2GAI, adresse_G2GAI_caracteres, adresse_G2GAI_chiffres, etage, surface_G2GAI, ecart_maximal_surface, nbr_pieces_G2GAI, ecart_maximal_piece) = initialiser_variables_adresse(ligne_G2GAI)

            # Extraire les valeurs de l'adresse de la colonne J de GMBI
            adresse_GMBI = [ligne[9] for ligne in donnees_fichierGMBI
                                if ligne[4] == departement_logement_G2GAI
                                    and (fuzz.partial_token_sort_ratio(ligne[6], ligne_G2GAI[10] ) >= 85 or fuzz.token_set_ratio(ligne[6], ligne_G2GAI[10] ) >= 85)
                                    and ligne[2] not in valeurs_gmbi_traitees
                                    and ligne[3] == ""
                                    and "partie" in ligne[18].lower()
                                    and int(ligne[21]) - ecart_maximal_surface <= int(surface_G2GAI) <= int(ligne[21]) + ecart_maximal_surface]
            
            if adresse_GMBI:
                traiter_correspondance_adresse(adresse_G2GAI_caracteres, adresse_GMBI, valeurs_g2gai_traitees, valeurs_gmbi_traitees, donnees_fichierG2GAI, donnees_fichierGMBI, nouveau_fichier, date_depart, date_arrivee)

    similarite_minimum -= 5

similarite_minimum = 100
while similarite_minimum >= 80:
    print(f"{similarite_minimum} sans la taille")
    # Parcourir les lignes du fichier G2GAI
    for ligne_G2GAI in donnees_fichierG2GAI:

        # Si le logement est Domaniale et n'a pas été traité
        if ligne_G2GAI[16] == "D" and ligne_G2GAI[12] not in valeurs_g2gai_traitees:

            # Appel à la fonction pour initialisation des variables adresse
            (departement_logement_G2GAI, numero_logement_G2GAI, nigend_courant, nom_courant_G2GAI, prenom_courant_G2GAI, premier_prenom_courant_G2GAI, date_naissance_courante, adresse_G2GAI, adresse_G2GAI_caracteres, adresse_G2GAI_chiffres, etage, surface_G2GAI, ecart_maximal_surface, nbr_pieces_G2GAI, ecart_maximal_piece) = initialiser_variables_adresse(ligne_G2GAI)

            # Extraire les valeurs de l'adresse de la colonne J de GMBI
            adresse_GMBI = [ligne[9] for ligne in donnees_fichierGMBI
                                if ligne[4] == departement_logement_G2GAI
                                    and (fuzz.partial_token_sort_ratio(ligne[6], ligne_G2GAI[10] ) >= 85 or fuzz.token_set_ratio(ligne[6], ligne_G2GAI[10] ) >= 85)
                                    and ligne[2] not in valeurs_gmbi_traitees
                                    and ligne[3] == ""
                                    and "partie" in ligne[18].lower()]

            if adresse_GMBI:
                traiter_correspondance_adresse(adresse_G2GAI_caracteres, adresse_GMBI, valeurs_g2gai_traitees, valeurs_gmbi_traitees, donnees_fichierG2GAI, donnees_fichierGMBI, nouveau_fichier, date_depart, date_arrivee)

    similarite_minimum -= 5

similarite_minimum = 80
while similarite_minimum >= 60:
    print(f"{similarite_minimum} Reste à vérifier")
    # Parcourir les lignes du fichier G2GAI
    for ligne_G2GAI in donnees_fichierG2GAI:

        # Si le logement est Domaniale et n'a pas été traité
        if ligne_G2GAI[16] == "D" and ligne_G2GAI[12] not in valeurs_g2gai_traitees:

            # Appel à la fonction pour initialisation des variables adresse
            (departement_logement_G2GAI, numero_logement_G2GAI, nigend_courant, nom_courant_G2GAI, prenom_courant_G2GAI, premier_prenom_courant_G2GAI, date_naissance_courante, adresse_G2GAI, adresse_G2GAI_caracteres, adresse_G2GAI_chiffres, etage, surface_G2GAI, ecart_maximal_surface, nbr_pieces_G2GAI, ecart_maximal_piece) = initialiser_variables_adresse(ligne_G2GAI)

            # Extraire les valeurs de l'adresse de la colonne J de GMBI
            adresse_GMBI = [ligne[9] for ligne in donnees_fichierGMBI
                                if ligne[4] == departement_logement_G2GAI
                                    and (fuzz.partial_token_sort_ratio(ligne[6], ligne_G2GAI[10] ) >= 85 or fuzz.token_set_ratio(ligne[6], ligne_G2GAI[10] ) >= 85)
                                    and ligne[2] not in valeurs_gmbi_traitees
                                    and ligne[3] == ""
                                    and "partie" in ligne[18].lower()]

            if adresse_GMBI:
                traiter_correspondance_adresse(adresse_G2GAI_caracteres, adresse_GMBI, valeurs_g2gai_traitees, valeurs_gmbi_traitees, donnees_fichierG2GAI, donnees_fichierGMBI, nouveau_fichier, date_depart, date_arrivee)

    similarite_minimum -= 5
# Correspondance adresse

# Écrire les lignes GMBI non traitées dans le nouveau fichier
# Parcourir les lignes du fichier GMBI
for ligne_GMBI in donnees_fichierGMBI:
    # Vérifier si le numéro de logement de la ligne GMBI n'a pas été traité
    if ligne_GMBI[2] not in valeurs_gmbi_traitees:
        # Appeler la fonction pour écrire la ligne dans le fichier GMBI_non_trouve
        ecrire_ligne_csv(GMBI_non_trouve, ligne_GMBI)
        # ecrire_ligne_csv(nouveau_fichier, ligne_GMBI)

# Écrire les lignes G2GAI non traitées dans le fichier de sortie
# Parcourir les lignes du fichier G2GAI
for ligne_G2GAI in donnees_fichierG2GAI:
    # Vérifier si le numéro de logement de la ligne G2GAI n'a pas été traité
    if ligne_G2GAI[12] not in valeurs_g2gai_traitees:
        # Appeler la fonction pour écrire la ligne dans le fichier G2GAI_non_trouve
        ecrire_ligne_csv(G2GAI_non_trouve, ligne_G2GAI)

# Écrire les lignes PARTIE non traitées dans le fichier de sortie
# Parcourir les lignes du fichier G2GAI
for ligne_abandon in donnees_fichierAbandon: 
    # Vérifier si le numéro de logement de la ligne G2GAI n'a pas été traité
    if ligne_abandon[0] not in valeurs_abandon_traitees:
        # Appeler la fonction pour écrire la ligne dans le fichier G2GAI_non_trouve
        ecrire_ligne_csv(nom_abandon_non_trouve, ligne_abandon)

# Temps exécution programme
end = time.time()
execution_time = end - start
hours, remainder = divmod(execution_time, 3600)
minutes, seconds = divmod(remainder, 60)
print("Temps d'exécution total : {:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds))

# Ouvre le fichier CSV avec l'application par défaut
os.startfile(nouveau_fichier)
os.startfile(G2GAI_non_trouve)
os.startfile(GMBI_non_trouve)
