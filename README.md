⛽ GAS-MALI : Système de Gestion de Crise & Files d'Attente
Digitalisation et optimisation des flux de distribution de carburant en temps réel.

🚀 Version Démo : Ce dépôt contient une version hybride. Si les clés API (Supabase/Twilio) ne sont pas détectées, l'application bascule automatiquement en Mode Démo avec une simulation de file d'attente dynamique.

📋 Contexte du Projet
Lors des crises d'approvisionnement en carburant au Mali, les stations-service font face à des engorgements massifs, créant des problèmes de sécurité et d'équité. GAS-MALI résout ce problème en transformant les files d'attente physiques en files d'attente virtuelles gérées par SIG et SMS.

🛠 Stack Technique
Frontend : Python (Streamlit) avec injection CSS personnalisée pour une expérience Mobile-First.

Backend & Sécurité : Supabase (PostgreSQL) avec Row Level Security (RLS) pour l'isolation des données par station.

SIG (Système d'Information Géographique) : Cartographie interactive via Folium / Leaflet.

Communication : API Twilio pour l'envoi automatisé de notifications SMS internationales.

Algorithmique : Implémentation d'une "File glissante" (Automated FIFO Queue Management).

✨ Fonctionnalités Clés
📱 Espace Citoyen (Client)
Localisation SIG : Visualisation en temps réel des stations disposant de stock et état de la file d'attente.

Ticket Virtuel : Inscription via plaque d'immatriculation avec contrôle anti-fraude (règle des 48h).

Suivi Dynamique : Consultation en direct de sa position dans la file sans avoir à se déplacer.

🧑‍💼 Interface Pompiste (Gestionnaire)
Dashboard Opérationnel : Suivi des métriques (Stock restant, File physique vs File virtuelle).

Appel Massif : Fonction de convocation par SMS pour remplir la file physique à l'ouverture.

Service Automatisé : La file avance automatiquement ; chaque service déclenche l'appel du client suivant via SMS.

👑 Administration Centrale
Pilotage du Réseau : Vue d'ensemble des stocks nationaux et modification en temps réel des capacités de service.

Sécurité des Accès : Authentification robuste avec hachage de mots de passe (Bcrypt).

🏗 Architecture & Ingénierie
Pour garantir l'intégrité des données lors d'accès simultanés, la logique métier critique est déportée sur la base de données via des Procédures Stockées (RPC) :

Atomicité : Décrémentation du stock et mise à jour du statut de file en une seule transaction.

Performance : Calcul de position dynamique effectué côté serveur pour alléger l'application client.

📦 Installation & Démo Locale
Cloner le projet

Bash

git clone https://github.com/Ybaba86/Portfolio-GasMali.git
cd Portfolio-GasMali
Installer les dépendances

Bash

pip install -r requirements.txt
Lancer l'application (Mode Démo par défaut)

Bash

streamlit run app.py
Développé par Youssouf BOIRE Doctorant Ingénieur • Expert en Digitalisation de Processus
