# 🏗 Migration Tool Architecture

## Overview

The Migration Tool has been designed according to the following development principles:

- **Single Responsibility Principle (SRP)**: Each class has a unique responsibility
- **Open/Closed Principle**: Open to extension, closed to modification
- **Dependency Inversion**: Dependency on abstractions, not implementations
- **Extensibility**: Ease of adding new providers

## Project Structure

```
GitMigrator/
├── providers/                   # Providers for different Git services
│   ├── __init__.py
│   ├── base.py                 # Abstract classes and models
│   ├── factory.py              # Factory to create providers
│   ├── source/                 # Source providers (Gitea, GitLab, etc.)
│   │   ├── __init__.py
│   │   ├── gitea.py
│   │   └── gitlab.py
│   └── destination/            # Destination providers (GitHub, GitLab, etc.)
│       ├── __init__.py
│       ├── github.py
│       └── gitlab.py
├── core/                       # Core business logic
│   ├── __init__.py
│   ├── config.py              # Configuration management
│   └── migration_engine.py    # Migration engine
├── ui/                        # User interface
│   ├── __init__.py
│   └── interactive_selector.py
├── main.py                    # Main entry point
└── run.sh                     # Launch script
```

## Module Responsibilities

### 🔧 Providers (providers/)

#### Base (`providers/base.py`)
- **Repository**: Unified data model for all providers
- **SourceProvider**: Abstract interface for source providers
- **DestinationProvider**: Abstract interface for destination providers
- **Exceptions**: Specialized exceptions for error handling

#### Factory (`providers/factory.py`)
- Dynamic creation of provider instances
- Registration of new providers
- Validation of available provider types

#### Source Providers (`providers/source/`)
- **Gitea**: Implementation for Gitea
- **GitLab**: Implementation for GitLab (extensibility example)

#### Destination Providers (`providers/destination/`)
- **GitHub**: Implementation for GitHub
- **GitLab**: Implementation for GitLab (extensibility example)

### ⚙ Core (`core/`)

#### Configuration (`core/config.py`)
- Centralized configuration management
- Multi-provider support via environment variables
- Configuration parameter validation

#### Migration Engine (`core/migration_engine.py`)
- Migration process orchestration
- Temporary repository management
- Git command execution
- Logging and progress reporting

### 🎨 UI (`ui/`)

#### Interactive Selector (`ui/interactive_selector.py`)
- Interactive interface for repository selection
- Keyboard navigation
- Renaming system
- Paginated display

## Extensibility

### Adding a new source provider

1. **Create the file**: `providers/source/my_provider.py`

```python
from typing import List, Optional
from ..base import SourceProvider, Repository, ProviderError, ConfigurationError

class MyProviderSourceProvider(SourceProvider):
    def _validate_config(self) -> None:
        # Validate specific configuration
        pass
    
    def get_user_repositories(self) -> List[Repository]:
        # Retrieve user repositories
        pass
    
    def get_accessible_repositories(self) -> List[Repository]:
        # Retrieve all accessible repositories
        pass
    
    def get_repository_info(self, owner: str, name: str) -> Optional[Repository]:
        # Retrieve specific repository information
        pass
    
    def get_authenticated_clone_url(self, repository: Repository) -> str:
        # Generate authenticated clone URL
        pass
```

2. **Register the provider** in `providers/factory.py`:

```python
from .source.my_provider import MyProviderSourceProvider

class ProviderFactory:
    _source_providers: Dict[str, Type[SourceProvider]] = {
        'gitea': GiteaSourceProvider,
        'gitlab': GitLabSourceProvider,
        'my_provider': MyProviderSourceProvider,  # New provider
    }
```

3. **Add configuration** in `core/config.py`:

```python
def _load_source_config(self) -> Dict[str, Any]:
    if self.source_provider == 'my_provider':
        return {
            'url': os.getenv('MY_PROVIDER_URL'),
            'token': os.getenv('MY_PROVIDER_TOKEN'),
            'username': os.getenv('MY_PROVIDER_USERNAME')
        }
    # ... other providers
```

### Adding a new destination provider

The process is identical, but in `providers/destination/`.

## Design Patterns Used

### 1. Abstract Factory Pattern
- `ProviderFactory` creates provider instances
- Allows adding new providers without modifying existing code

### 2. Strategy Pattern
- Providers implement different strategies to access APIs
- Migration engine uses these strategies transparently

### 3. Template Method Pattern
- `SourceProvider` and `DestinationProvider` define operation skeletons
- Concrete implementations fill in specific details

### 4. Dependency Injection
- Providers are injected into `MigrationEngine`
- Facilitates testing and flexibility

## Configuration

### Environment Variables

```bash
# Source provider
SOURCE_PROVIDER=gitea|gitlab
GITEA_URL=https://gitea.example.com
GITEA_TOKEN=your_token
GITEA_USERNAME=your_username

# Destination provider
DESTINATION_PROVIDER=github|gitlab
GITHUB_TOKEN=your_token
GITHUB_USERNAME=your_username
```

### Configuration Extensibility

To add a new provider, simply add corresponding variables and modify `MigrationConfig`.

## Tests

### Recommended Structure

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

### Test Examples

```python
# Provider test
def test_gitea_provider_validates_config():
    config = {'url': 'https://gitea.com', 'token': 'token', 'username': 'user'}
    provider = GiteaSourceProvider(config)
    assert provider.base_url == 'https://gitea.com'

# Migration engine test
def test_migration_engine_handles_errors():
    source = Mock(spec=SourceProvider)
    dest = Mock(spec=DestinationProvider)
    engine = MigrationEngine(source, dest)
    # Test error handling...
```

## Best Practices

### 1. Error Handling
- Specialized exceptions for each error type
- Appropriate logging at each level
- Graceful failure handling

### 2. Documentation
- Docstrings for all public methods
- Type hints for code clarity
- README and architecture documentation

### 3. Security
- Tokens never logged
- Temporary repository cleanup
- User input validation

### 4. Performance
- Pagination for repository lists
- Possible migration parallelization
- Efficient memory management

## Future Evolutions

### Potential Features
- Incremental migration (changes only)
- Webhook support
- Web interface
- REST API
- Metadata migration (issues, pull requests)

### New Providers
- Bitbucket
- Azure DevOps
- Sourcehut
- Codeberg

The current architecture allows easy addition of these features without major restructuring. 