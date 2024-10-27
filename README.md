# Projet de Traitement des Déclarations de Biens Immobiliers de la Gendarmerie Nationale

## Description du Projet

Ce projet a pour objectif de développer une suite de programmes destinés à automatiser le traitement des déclarations de biens immobiliers de la Gendarmerie Nationale. En raison de la grande complexité et du volume des données, il est essentiel de rationaliser la gestion des informations en facilitant la recherche de correspondances entre divers fichiers et attributs (nom, adresse, localisation, typologie). 

## Objectifs

Les objectifs principaux sont de :
1. **Automatiser le traitement des correspondances** (nom, adresse, typologie) afin de réduire les erreurs et le temps de travail manuel.
2. **Assurer une identification précise** des biens en fonction de leur localisation et typologie, facilitant leur gestion et leur suivi.
3. **Préparer une infrastructure durable** pour une gestion simplifiée dans les années futures, avec l'intégration d'identifiants uniques dans les bases de données.

## Démarche et Méthodologie

Le projet se compose de trois programmes indépendants qui effectuent des traitements distincts sur les données de déclaration immobilière :

### Programme 1 : Recherche par Nom, Prénom et Adresse

- **Fonction** : Ce programme est chargé d’identifier des correspondances de biens en croisant les informations de nom, prénom et adresse.
- **Approche** : J’ai utilisé `thefuzz`, une bibliothèque de correspondance floue, pour analyser et comparer les chaînes de caractères. Cette approche permet d’identifier les enregistrements similaires, en tenant compte des différences mineures d’écriture, par exemple des fautes de frappe ou variations d’adresses.
- **Pourquoi sans `Pandas`** : Bien que `Pandas` aurait simplifié le traitement des grandes quantités de données et permis des manipulations plus rapides, l’installation n’était pas autorisée dans cet environnement. J’ai donc conçu ce programme en m'appuyant sur des structures de données natives de Python, comme les dictionnaires et les listes, pour parcourir et filtrer les informations.
- **Résultat** : Ce programme génère un fichier listant toutes les correspondances trouvées, facilitant l’identification des biens pour les équipes de la SDIL et réduisant les traitements manuels.

### Programme 2 : Recherche par Localisation et Typologie

- **Fonction** : Ce programme cherche les correspondances par localisation (ville, département) et typologie des biens (ex. appartement, maison), offrant un niveau de granularité supplémentaire.
- **Approche** : À partir des données issues des fichiers source, le programme compare les caractéristiques des biens pour chaque région, en se basant sur les attributs de localisation et de type de logement. L’objectif est de cibler les correspondances spécifiques pour une meilleure organisation et suivi des déclarations.
- **Résultat** : Ce programme fournit des correspondances précises pour chaque bien en fonction de sa localisation et typologie, facilitant ainsi le suivi des propriétés sur l’ensemble du territoire.

### Programme 3 : Automatisation pour les Années Futures

- **Fonction** : Conçu pour simplifier le traitement des données dans les années futures, ce programme tire parti des identifiants uniques nouvellement ajoutés aux bases de données, permettant une correspondance directe des biens.
- **Approche** : L’utilisation d’identifiants uniques réduit les étapes de traitement et garantit des correspondances précises, sans devoir croiser plusieurs champs de données. 
- **Résultat** : Ce programme offre une gestion simplifiée et plus rapide des bases de données pour les années à venir, avec des vérifications automatiques réduisant les interventions manuelles et améliorant la fiabilité des données.

## Résultats et Impacts

Ces programmes permettent une simplification et une accélération significative du traitement des déclarations de biens. En automatisant les étapes de correspondance, le projet diminue le risque d’erreurs humaines et garantit une base de données plus précise et à jour pour la Gendarmerie. De plus, l’utilisation des identifiants uniques assure une adaptabilité et une efficacité accrue pour les traitements futurs.

## Fonctionnement Global

Le flux de traitement des données s’effectue en plusieurs étapes :
1. **Chargement des Données** : Les fichiers CSV de l'année en cours sont chargés et traités par chaque programme.
2. **Recherche de Correspondances** : Les programmes 1 et 2 recherchent les correspondances selon les critères définis (nom, adresse, localisation, etc.).
3. **Automatisation pour les Années Futures (Programme 3)** : Lors des années futures, le programme 3 effectuera les traitements en utilisant directement les identifiants uniques pour une correspondance rapide.
4. **Sortie des Résultats** : Chaque programme génère un fichier de résultats répertoriant les correspondances, simplifiant ainsi la vérification et le suivi des biens.

---

Ce projet fournit une solution évolutive et fiable pour la gestion des déclarations immobilières de la Gendarmerie Nationale, avec des traitements optimisés pour répondre aux contraintes actuelles et futures du service immobilier de la Gendarmerie.
