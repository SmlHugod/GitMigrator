# 🚀 Outil de Migration Git Multi-Providers

Cet projet fournit un outil pratique et modulable pour migrer automatiquement vos repositories entre différents providers Git.

## ✨ Fonctionnalités

- **Migration multi-providers** : Supporte plusieurs providers source et destination
- **Providers supportés** :
  - **Sources** : Gitea, GitLab
  - **Destinations** : GitHub, GitLab
- **Mode interactif par défaut** : Interface élégante pour sélectionner/déselectionner les repos à migrer
- **Vision complète** : Voit tous les repositories accessibles (vos repos + ceux d'organisations)
- **Sélection intelligente** : Vos repositories sont pré-sélectionnés, les autres sont désélectionnés par défaut
- **Renommage intelligent** : Possibilité de renommer les repositories lors de la migration
- **Migration sélective** : Choisissez spécifiquement quels repositories migrer en ligne de commande
- **Interface en ligne de commande** : Interface colorée et intuitive avec navigation au clavier
- **Logging complet** : Suivi détaillé des opérations avec fichier de log
- **Gestion des erreurs** : Robuste avec gestion gracieuse des erreurs
- **Architecture extensible** : Facilement extensible pour ajouter de nouveaux providers

## 🛠 Installation

1. **Clonez le repository** :
```bash
git clone https://github.com/votre-username/GitMigrator.git
cd GitMigrator
```

2. **Configuration automatique** :
```bash
./run.sh --setup
```

Le script va automatiquement :
- Créer un environnement virtuel Python
- Installer toutes les dépendances
- Créer le fichier de configuration `.env`

Cela créera un fichier `.env` que vous devrez remplir avec vos informations selon les providers choisis.

## 🔧 Configuration

### Configuration avec support multi-instances
```env
# Gitea Source Configuration
GITEA_SOURCE_URL=https://votre-instance-gitea-source.com
GITEA_SOURCE_TOKEN=votre_token_gitea_source
GITEA_SOURCE_USERNAME=votre_nom_utilisateur_gitea_source

# Gitea Destination Configuration  
GITEA_DEST_URL=https://votre-instance-gitea-dest.com
GITEA_DEST_TOKEN=votre_token_gitea_dest
GITEA_DEST_USERNAME=votre_nom_utilisateur_gitea_dest

# GitLab Source Configuration
GITLAB_SOURCE_URL=https://gitlab-source.com
GITLAB_SOURCE_TOKEN=votre_token_gitlab_source
GITLAB_SOURCE_USERNAME=votre_nom_utilisateur_gitlab_source

# GitLab Destination Configuration
GITLAB_DEST_URL=https://gitlab-dest.com
GITLAB_DEST_TOKEN=votre_token_gitlab_dest
GITLAB_DEST_USERNAME=votre_nom_utilisateur_gitlab_dest

# GitHub Configuration (same for source and destination - only one instance)
GITHUB_TOKEN=votre_token_github
GITHUB_USERNAME=votre_nom_utilisateur_github
```

**📝 Instructions :**
1. **Multi-instances** : Vous pouvez configurer différentes instances du même provider
2. **Même instance** : Utilisez les mêmes credentials pour source et destination si c'est la même instance
3. **Migration flexible** : Supports GitLab → GitLab, Gitea → Gitea, etc. entre différentes instances
4. **Configuration minimale** : Configurez seulement les providers source/destination que vous utilisez
5. L'outil vous demandera interactivement quel provider utiliser comme source et destination

## 🔑 Configuration des tokens

### Token Gitea
1. Allez dans **Settings** → **Applications** → **Generate New Token**
2. Donnez un nom au token et sélectionnez les permissions :
   - `repo` (accès complet aux repositories)
   - `user` (accès aux informations utilisateur)

### Token GitLab
1. Allez dans **Settings** → **Access Tokens** ou **User Settings** → **Access Tokens**
2. Créez un **Personal Access Token** avec les permissions :
   - `read_api` (lecture des informations API)
   - `read_repository` (lecture des repositories)
   - `write_repository` (écriture des repositories - pour destination)

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

### Lister les repositories disponibles
```bash
./run.sh --list
```

### Mode verbose (plus de détails)
```bash
./run.sh --verbose
```

> **💡 Alternative** : Vous pouvez aussi utiliser directement `python main.py` si vous avez activé l'environnement virtuel (`source venv/bin/activate`)

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
- **ENTRÉE** : Confirmer la sélection et passer au renommage (optionnel)
- **Q** : Quitter sans migrer

### Interface de renommage :
Après la sélection, l'outil propose de renommer les repositories :
- **Y** : Ouvrir l'interface de renommage
- **N/ENTRÉE** : Conserver les noms actuels
- **Validation automatique** des noms de repositories pour le provider de destination

### Fonctionnalités :
- ✅ **Checkboxes visuelles** avec émojis
- 👤 **Distinction propriétaire** : Vos repos vs repos d'autres utilisateurs
- 🎯 **Sélection intelligente** : Vos repos pré-sélectionnés par défaut
- 📋 **Tri intelligent** : Vos repos en premier, puis les autres, tous par ordre alphabétique
- ✏️ **Renommage optionnel** : Possibilité de renommer les repos sur le provider de destination
- 📄 **Pagination automatique** (15 repos par page)
- 🎨 **Interface colorée** avec mise en surbrillance et séparateurs visuels
- 📊 **Compteur en temps réel** des repos sélectionnés
- 🔒 **Indicateurs visuels** (privé/public)
- 📝 **Descriptions tronquées** pour un affichage propre

## 📋 Exemples d'utilisation

### Exemple 1 : Migration interactive (défaut)
```bash
# 1. Configurez vos providers dans .env
# 2. Lancez l'outil
./run.sh

# L'outil vous demandera :
# - Quel provider utiliser comme source
# - Quel provider utiliser comme destination
# - Puis vous pourrez sélectionner les repos à migrer
```

### Exemple 2 : Migration automatique
```bash
# Migre tous vos repositories automatiquement
# (après sélection interactive des providers)
./run.sh --no-interactive
```

### Exemple 3 : Migration sélective
```bash
# Migre seulement les repositories spécifiés
# (après sélection interactive des providers)
./run.sh --repos projet-web api-backend
```

### Exemple 4 : Migration depuis une organisation
```bash
# Migre un repository d'une organisation (fonctionne avec tous les providers)
./run.sh --repos mon-org/projet-important
```

### Exemple 5 : Premier lancement (configuration)
```bash
# 1. Setup initial - crée le fichier .env template
./run.sh --setup

# 2. Éditez le fichier .env avec vos credentials (au moins 2 providers)
nano .env

# 3. Lancez l'outil - il vous demandera quels providers utiliser
./run.sh

# 4. Pour lister les repos disponibles (après sélection du provider source)
./run.sh --list
```

### Exemple 6 : Migration avec renommage
```bash
# 1. Lancer le mode interactif
./run.sh

# 2. Sélectionner les providers source et destination
# 3. Sélectionner les repos à migrer
# 4. Choisir "Y" pour le renommage
# 5. Renommer les repos un par un
#    - Appuyer sur ENTRÉE pour garder le nom original
#    - Taper un nouveau nom pour renommer
# 6. Confirmer et lancer la migration
```

## 📊 Résultats

L'outil affiche un résumé détaillé à la fin :
- ✅ Nombre de migrations réussies
- ❌ Nombre de migrations échouées
- 📝 Détail par repository

Tous les logs sont également sauvegardés dans `migration.log`.

## 🔧 Structure du projet

```
GitMigrator/
├── main.py                     # Script principal
├── core/                       # Logique métier centrale
│   ├── config.py              # Gestion de la configuration multi-providers
│   └── migration_engine.py    # Moteur de migration
├── providers/                  # Providers pour différents services Git
│   ├── base.py                # Classes abstraites et modèles
│   ├── factory.py             # Factory pour créer les providers
│   ├── source/                # Providers source
│   │   ├── gitea.py          # Support Gitea
│   │   └── gitlab.py         # Support GitLab
│   └── destination/           # Providers destination
│       ├── github.py         # Support GitHub
│       └── gitlab.py         # Support GitLab
├── ui/                        # Interface utilisateur
│   └── interactive_selector.py
├── requirements.txt           # Dépendances Python
├── .env                      # Configuration (à créer)
└── README.md                 # Documentation
```

## 🌟 Providers supportés

### Providers Source
- **Gitea** : Instances Gitea (self-hosted ou cloud)
- **GitLab** : GitLab.com ou instances GitLab self-hosted

### Providers Destination
- **GitHub** : GitHub.com
- **GitLab** : GitLab.com ou instances GitLab self-hosted

### Combinaisons possibles
- Gitea → GitHub
- Gitea → GitLab
- GitLab → GitHub
- GitLab → GitLab (migration entre instances)

## ⚠️ Prérequis

- Python 3.7+
- Git installé sur votre système
- Accès aux APIs des providers source et destination
- Tokens d'authentification valides pour les providers

## 🛡 Sécurité

- Les tokens sont stockés dans un fichier `.env` (ajoutez-le à `.gitignore`)
- Les URLs d'authentification ne sont jamais loggées
- Nettoyage automatique des repositories temporaires

## 🐛 Résolution de problèmes

### Erreur d'authentification
- Vérifiez que vos tokens sont valides et ont les bonnes permissions
- Assurez-vous que les noms d'utilisateur correspondent
- Vérifiez que les URLs des providers sont correctes

### Erreur de clonage
- Vérifiez votre connexion internet
- Assurez-vous que Git est installé et accessible

### Repository déjà existant
- L'outil vérifie automatiquement l'existence sur le provider de destination
- Les repositories existants sont ignorés avec un avertissement

### Provider non supporté ou non configuré
- Vérifiez que vos providers sont bien configurés dans le fichier .env
- Assurez-vous d'avoir au moins 2 providers configurés
- Providers disponibles : gitea, gitlab, github
- L'outil vous indiquera quels providers sont configurés au démarrage

## 📝 Logs

Tous les détails d'exécution sont sauvegardés dans `migration.log` :
- Timestamps des opérations
- Sélection des providers source et destination
- Détails des erreurs
- Statistiques de migration
- Informations complètes sur le processus de migration

## 🚀 Extensibilité

L'architecture modulaire permet d'ajouter facilement de nouveaux providers :

1. **Créer un nouveau provider source** dans `providers/source/`
2. **Créer un nouveau provider destination** dans `providers/destination/`
3. **Enregistrer le provider** dans `providers/factory.py`
4. **Ajouter la configuration** dans `core/config.py`

Voir `ARCHITECTURE.md` pour plus de détails sur l'ajout de nouveaux providers.

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
- Signaler des bugs
- Proposer des améliorations
- Soumettre des pull requests
- Ajouter de nouveaux providers

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.