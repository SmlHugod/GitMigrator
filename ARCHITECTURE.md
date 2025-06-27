# 🏗 Architecture du Migration Tool

## Vue d'ensemble

Le Migration Tool a été conçu selon les principes de développement suivants :

- **Single Responsibility Principle (SRP)** : Chaque classe a une responsabilité unique
- **Open/Closed Principle** : Ouvert à l'extension, fermé à la modification
- **Dependency Inversion** : Dépendance sur des abstractions, pas des implémentations
- **Extensibilité** : Facilité d'ajout de nouveaux providers

## Structure du projet

```
GiteaToGithubMigrator/
├── providers/                   # Providers pour différents services Git
│   ├── __init__.py
│   ├── base.py                 # Classes abstraites et modèles
│   ├── factory.py              # Factory pour créer les providers
│   ├── source/                 # Providers source (Gitea, GitLab, etc.)
│   │   ├── __init__.py
│   │   ├── gitea.py
│   │   └── gitlab.py
│   └── destination/            # Providers destination (GitHub, GitLab, etc.)
│       ├── __init__.py
│       ├── github.py
│       └── gitlab.py
├── core/                       # Logique métier centrale
│   ├── __init__.py
│   ├── config.py              # Gestion de la configuration
│   └── migration_engine.py    # Moteur de migration
├── ui/                        # Interface utilisateur
│   ├── __init__.py
│   └── interactive_selector.py
├── main.py                    # Point d'entrée principal
└── run.sh                     # Script de lancement
```

## Responsabilités des modules

### 🔧 Providers (providers/)

#### Base (`providers/base.py`)
- **Repository** : Modèle de données unifié pour tous les providers
- **SourceProvider** : Interface abstraite pour les providers source
- **DestinationProvider** : Interface abstraite pour les providers destination
- **Exceptions** : Exceptions spécialisées pour la gestion d'erreurs

#### Factory (`providers/factory.py`)
- Création dynamique des instances de providers
- Enregistrement de nouveaux providers
- Validation des types de providers disponibles

#### Source Providers (`providers/source/`)
- **Gitea** : Implémentation pour Gitea
- **GitLab** : Implémentation pour GitLab (exemple d'extensibilité)

#### Destination Providers (`providers/destination/`)
- **GitHub** : Implémentation pour GitHub
- **GitLab** : Implémentation pour GitLab (exemple d'extensibilité)

### ⚙ Core (`core/`)

#### Configuration (`core/config.py`)
- Gestion centralisée de la configuration
- Support multi-providers via variables d'environnement
- Validation des paramètres de configuration

#### Migration Engine (`core/migration_engine.py`)
- Orchestration du processus de migration
- Gestion des repositories temporaires
- Exécution des commandes Git
- Logging et rapport de progression

### 🎨 UI (`ui/`)

#### Interactive Selector (`ui/interactive_selector.py`)
- Interface interactive pour la sélection de repositories
- Navigation au clavier
- Système de renommage
- Affichage paginated

## Extensibilité

### Ajouter un nouveau provider source

1. **Créer le fichier** : `providers/source/mon_provider.py`

```python
from typing import List, Optional
from ..base import SourceProvider, Repository, ProviderError, ConfigurationError

class MonProviderSourceProvider(SourceProvider):
    def _validate_config(self) -> None:
        # Valider la configuration spécifique
        pass
    
    def get_user_repositories(self) -> List[Repository]:
        # Récupérer les repos de l'utilisateur
        pass
    
    def get_accessible_repositories(self) -> List[Repository]:
        # Récupérer tous les repos accessibles
        pass
    
    def get_repository_info(self, owner: str, name: str) -> Optional[Repository]:
        # Récupérer les infos d'un repo spécifique
        pass
    
    def get_authenticated_clone_url(self, repository: Repository) -> str:
        # Générer l'URL de clone authentifiée
        pass
```

2. **Enregistrer le provider** dans `providers/factory.py` :

```python
from .source.mon_provider import MonProviderSourceProvider

class ProviderFactory:
    _source_providers: Dict[str, Type[SourceProvider]] = {
        'gitea': GiteaSourceProvider,
        'gitlab': GitLabSourceProvider,
        'mon_provider': MonProviderSourceProvider,  # Nouveau provider
    }
```

3. **Ajouter la configuration** dans `core/config.py` :

```python
def _load_source_config(self) -> Dict[str, Any]:
    if self.source_provider == 'mon_provider':
        return {
            'url': os.getenv('MON_PROVIDER_URL'),
            'token': os.getenv('MON_PROVIDER_TOKEN'),
            'username': os.getenv('MON_PROVIDER_USERNAME')
        }
    # ... autres providers
```

### Ajouter un nouveau provider destination

Le processus est identique, mais dans `providers/destination/`.

## Patterns utilisés

### 1. Abstract Factory Pattern
- `ProviderFactory` crée des instances de providers
- Permet d'ajouter de nouveaux providers sans modifier le code existant

### 2. Strategy Pattern
- Les providers implémentent des stratégies différentes pour accéder aux APIs
- Le moteur de migration utilise ces stratégies de manière transparente

### 3. Template Method Pattern
- `SourceProvider` et `DestinationProvider` définissent le squelette des opérations
- Les implémentations concrètes remplissent les détails spécifiques

### 4. Dependency Injection
- Les providers sont injectés dans `MigrationEngine`
- Facilite les tests et la flexibilité

## Configuration

### Variables d'environnement

```bash
# Provider source
SOURCE_PROVIDER=gitea|gitlab
GITEA_URL=https://gitea.example.com
GITEA_TOKEN=your_token
GITEA_USERNAME=your_username

# Provider destination
DESTINATION_PROVIDER=github|gitlab
GITHUB_TOKEN=your_token
GITHUB_USERNAME=your_username
```

### Extensibilité de la configuration

Pour ajouter un nouveau provider, il suffit d'ajouter les variables correspondantes et de modifier `MigrationConfig`.

## Tests

### Structure recommandée

```
tests/
├── unit/
│   ├── providers/
│   │   ├── test_gitea_provider.py
│   │   └── test_github_provider.py
│   ├── core/
│   │   └── test_migration_engine.py
│   └── ui/
│       └── test_interactive_selector.py
├── integration/
│   └── test_full_migration.py
└── fixtures/
    └── sample_repositories.json
```

### Exemples de tests

```python
# Test d'un provider
def test_gitea_provider_validates_config():
    config = {'url': 'https://gitea.com', 'token': 'token', 'username': 'user'}
    provider = GiteaSourceProvider(config)
    assert provider.base_url == 'https://gitea.com'

# Test du moteur de migration
def test_migration_engine_handles_errors():
    source = Mock(spec=SourceProvider)
    dest = Mock(spec=DestinationProvider)
    engine = MigrationEngine(source, dest)
    # Test error handling...
```

## Bonnes pratiques

### 1. Gestion d'erreurs
- Exceptions spécialisées pour chaque type d'erreur
- Logging approprié à chaque niveau
- Gestion gracieuse des échecs

### 2. Documentation
- Docstrings pour toutes les méthodes publiques
- Type hints pour la clarté du code
- README et documentation d'architecture

### 3. Sécurité
- Tokens jamais loggés
- Nettoyage des repositories temporaires
- Validation des entrées utilisateur

### 4. Performance
- Pagination pour les listes de repositories
- Parallélisation possible des migrations
- Gestion efficace de la mémoire

## Évolutions futures

### Fonctionnalités potentielles
- Migration incrémentale (seulement les changements)
- Support des webhooks
- Interface web
- API REST
- Migration de métadonnées (issues, pull requests)

### Nouveaux providers
- Bitbucket
- Azure DevOps
- Sourcehut
- Codeberg

L'architecture actuelle permet d'ajouter facilement ces fonctionnalités sans restructuration majeure. 