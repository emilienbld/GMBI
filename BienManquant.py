import csv
import re

bien_manquant = "C:/Users/internet/Documents/Domaniale/Liste des biens gendarmerie absents de GMBi.csv"
fichier_G2GAI = "C:/Users/internet/Documents/Domaniale/Traitement Rendu/G2GAI Reste.csv"
nouveau_fichier = "C:/Users/internet/Documents/Domaniale/Traitement Rendu/bien manquant GMBI reste.csv"

# Fonction pour ouvrir les fichiers et écrire les premières lignes dans les fichiers correspondants
def charger_ecrire_fichier(input_file, output_file):
    # Ouvrir le fichier d'entrée en mode lecture
    with open(input_file, 'r', newline='', encoding='utf-8') as fichier_entree:
        lecteur_fichier_entree = csv.reader(fichier_entree, delimiter=';')
        premiere_ligne_fichier_entree = next(lecteur_fichier_entree)  # Lire la première ligne du fichier d'entrée

        # Ouvrir le fichier de sortie en mode écriture
        with open(output_file, 'w', newline='', encoding='utf-8') as fichier_sortie:
            writer = csv.writer(fichier_sortie, delimiter=';')
            writer.writerow(premiere_ligne_fichier_entree)  # Écrire la première ligne dans le fichier de sortie

        donnees_fichier_entree = list(lecteur_fichier_entree)  # Lire toutes les données du fichier d'entrée et les stocker dans une liste
    
    # Retourner la première ligne et les données du fichier d'entrée
    return premiere_ligne_fichier_entree, donnees_fichier_entree

# Fonction pour écrire dans un fichier CSV
def ecrire_ligne_csv(fichier, ligne):
    with open(fichier, 'a', newline='', encoding='utf-8') as fichier_csv:
        writer = csv.writer(fichier_csv, delimiter=';')
        writer.writerow(ligne)

# Charger les données du fichier Liste des biens gendarmerie absents de GMBi
premiere_ligne_adresse_fausse, donnees_bien_manquant = charger_ecrire_fichier(bien_manquant, nouveau_fichier)
# Charger les données du fichier G2GAI
premiere_ligne_G2GAI, donnees_fichierG2GAI = charger_ecrire_fichier(fichier_G2GAI, nouveau_fichier)

for ligne_bien_manquant in donnees_bien_manquant:
    if ligne_bien_manquant[1].strip() != '':
        departement_G2GAI = ligne_bien_manquant[0]
        adresse_G2GAI = ligne_bien_manquant[1]
        commune_G2GAI = ligne_bien_manquant[2]
        nombre_logement_G2GAI = ligne_bien_manquant[4]


        for ligne_G2GAI in donnees_fichierG2GAI:
            if adresse_G2GAI in ligne_G2GAI:
                print(adresse_G2GAI)
                nouvelle_ligne = ligne_G2GAI[:]
                ecrire_ligne_csv(nouveau_fichier, nouvelle_ligne)
