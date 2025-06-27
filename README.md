# 🚀 Gitea to GitHub Migration Tool

Ce projet fournit un outil pratique et modulable pour migrer vos repositories de Gitea vers GitHub automatiquement.

## ✨ Fonctionnalités

- **Migration automatique** : Migre tous vos repositories Gitea vers GitHub en une seule commande
- **🎯 Mode interactif par défaut** : Interface élégante pour sélectionner/déselectionner les repos à migrer
- **Vision complète** : Voit tous les repositories accessibles (vos repos + ceux d'organisations)
- **Sélection intelligente** : Vos repositories sont pré-sélectionnés, les autres sont désélectionnés par défaut
- **Migration sélective** : Choisissez spécifiquement quels repositories migrer en ligne de commande
- **Interface en ligne de commande** : Interface colorée et intuitive avec navigation au clavier
- **Logging complet** : Suivi détaillé des opérations avec fichier de log
- **Gestion des erreurs** : Robuste avec gestion gracieuse des erreurs

## 🛠 Installation

1. **Clonez le repository** :
```bash
git clone https://github.com/votre-username/GiteaToGithubMigrator.git
cd GiteaToGithubMigrator
```

2. **Configuration automatique** :
```bash
./run.sh --setup
```

Le script va automatiquement :
- Créer un environnement virtuel Python
- Installer toutes les dépendances
- Créer le fichier de configuration `.env`

Cela créera un fichier `.env` que vous devrez remplir avec vos informations :

```env
# Gitea Configuration
GITEA_URL=https://votre-instance-gitea.com
GITEA_TOKEN=votre_token_gitea
GITEA_USERNAME=votre_nom_utilisateur_gitea

# GitHub Configuration
GITHUB_TOKEN=votre_token_github
GITHUB_USERNAME=votre_nom_utilisateur_github
```

## 🔑 Configuration des tokens

### Token Gitea
1. Allez dans **Settings** → **Applications** → **Generate New Token**
2. Donnez un nom au token et sélectionnez les permissions :
   - `repo` (accès complet aux repositories)
   - `user` (accès aux informations utilisateur)

### Token GitHub
1. Allez dans **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
2. Cliquez sur **Generate new token (classic)**
3. Sélectionnez les permissions :
   - `repo` (accès complet aux repositories privés)
   - `public_repo` (accès aux repositories publics)

## 🚀 Utilisation

Après avoir configuré vos tokens dans le fichier `.env`, utilisez le script de lancement :

### Migration interactive (par défaut)
```bash
./run.sh
```

### Migration automatique de tous vos repos
```bash
./run.sh --no-interactive
```

### Migration de repositories spécifiques
```bash
./run.sh --repos mon-repo autre-repo
```

### Migration de repositories d'autres propriétaires
```bash
./run.sh --repos proprietaire/repo-name
```

### Lister les repositories disponibles
```bash
./run.sh --list
```

### Mode verbose (plus de détails)
```bash
./run.sh --verbose
```

> **💡 Alternative** : Vous pouvez aussi utiliser directement `python migrate.py` si vous avez activé l'environnement virtuel (`source venv/bin/activate`)

## 🎯 Mode Interactif

Le mode interactif (activé par défaut) offre une **interface utilisateur élégante** pour sélectionner précisément quels repositories migrer :

```bash
./run.sh  # Mode interactif par défaut
```

### Contrôles dans l'interface interactive :
- **↑↓** : Naviguer entre les repositories
- **←→** : Changer de page (si beaucoup de repos)
- **ESPACE** : Cocher/décocher un repository
- **A** : Sélectionner tous les repositories
- **N** : Désélectionner tous les repositories
- **ENTRÉE** : Confirmer la sélection et lancer la migration
- **Q** : Quitter sans migrer

### Fonctionnalités :
- ✅ **Checkboxes visuelles** avec émojis
- 👤 **Distinction propriétaire** : Vos repos vs repos d'autres utilisateurs
- 🎯 **Sélection intelligente** : Vos repos pré-sélectionnés par défaut
- 📄 **Pagination automatique** (15 repos par page)
- 🎨 **Interface colorée** avec mise en surbrillance
- 📊 **Compteur en temps réel** des repos sélectionnés
- 🔒 **Indicateurs visuels** (privé/public)
- 📝 **Descriptions tronquées** pour un affichage propre

## 📋 Exemples d'utilisation

### Exemple 1 : Migration interactive (défaut)
```bash
# Interface interactive pour sélectionner les repos
./run.sh
```

### Exemple 2 : Migration automatique
```bash
# Migre tous vos repositories automatiquement
./run.sh --no-interactive
```

### Exemple 3 : Migration sélective
```bash
# Migre seulement les repositories spécifiés
./run.sh --repos projet-web api-backend
```

### Exemple 4 : Migration depuis une organisation
```bash
# Migre un repository d'une organisation
./run.sh --repos mon-org/projet-important
```

### Exemple 5 : Premier lancement (configuration)
```bash
# 1. Setup initial
./run.sh --setup

# 2. Éditez le fichier .env avec vos credentials
nano .env

# 3. Listez vos repositories disponibles
./run.sh --list

# 4. Lancez la migration
./run.sh
```

## 📊 Résultats

L'outil affiche un résumé détaillé à la fin :
- ✅ Nombre de migrations réussies
- ❌ Nombre de migrations échouées
- 📝 Détail par repository

Tous les logs sont également sauvegardés dans `migration.log`.

## 🔧 Structure du projet

```
GiteaToGithubMigrator/
├── migrate.py          # Script principal
├── config.py           # Gestion de la configuration
├── gitea_client.py     # Client API Gitea
├── github_client.py    # Client API GitHub
├── migration_tool.py   # Logique de migration
├── requirements.txt    # Dépendances Python
├── .env               # Configuration (à créer)
└── README.md          # Documentation
```

## ⚠️ Prérequis

- Python 3.7+
- Git installé sur votre système
- Accès aux APIs Gitea et GitHub
- Tokens d'authentification valides

## 🛡 Sécurité

- Les tokens sont stockés dans un fichier `.env` (ajoutez-le à `.gitignore`)
- Les URLs d'authentification ne sont jamais loggées
- Nettoyage automatique des repositories temporaires

## 🐛 Résolution de problèmes

### Erreur d'authentification
- Vérifiez que vos tokens sont valides et ont les bonnes permissions
- Assurez-vous que les noms d'utilisateur correspondent

### Erreur de clonage
- Vérifiez votre connexion internet
- Assurez-vous que Git est installé et accessible

### Repository déjà existant
- L'outil vérifie automatiquement l'existence sur GitHub
- Les repositories existants sont ignorés avec un avertissement

## 📝 Logs

Tous les détails d'exécution sont sauvegardés dans `migration.log` :
- Timestamps des opérations
- Détails des erreurs
- Statistiques de migration

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
- Signaler des bugs
- Proposer des améliorations
- Soumettre des pull requests

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.