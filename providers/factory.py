"""
Factory for creating provider instances
"""
from typing import Dict, Type
from .base import SourceProvider, DestinationProvider, ConfigurationError
from .source.gitea import GiteaSourceProvider
from .source.gitlab import GitLabSourceProvider
from .destination.github import GitHubDestinationProvider
from .destination.gitlab import GitLabDestinationProvider


class ProviderFactory:
    """Factory for creating provider instances"""
    
    _source_providers: Dict[str, Type[SourceProvider]] = {
        'gitea': GiteaSourceProvider,
        'gitlab': GitLabSourceProvider,
    }
    
    _destination_providers: Dict[str, Type[DestinationProvider]] = {
        'github': GitHubDestinationProvider,
        'gitlab': GitLabDestinationProvider,
    }
    
    @classmethod
    def create_source_provider(cls, provider_type: str, config: Dict) -> SourceProvider:
        """Create a source provider instance"""
        if provider_type not in cls._source_providers:
            available = ', '.join(cls._source_providers.keys())
            raise ConfigurationError(f"Unknown source provider '{provider_type}'. Available: {available}")
        
        provider_class = cls._source_providers[provider_type]
        return provider_class(config)
    
    @classmethod
    def create_destination_provider(cls, provider_type: str, config: Dict) -> DestinationProvider:
        """Create a destination provider instance"""
        if provider_type not in cls._destination_providers:
            available = ', '.join(cls._destination_providers.keys())
            raise ConfigurationError(f"Unknown destination provider '{provider_type}'. Available: {available}")
        
        provider_class = cls._destination_providers[provider_type]
        return provider_class(config)
    
    @classmethod
    def register_source_provider(cls, name: str, provider_class: Type[SourceProvider]) -> None:
        """Register a new source provider"""
        cls._source_providers[name] = provider_class
    
    @classmethod
    def register_destination_provider(cls, name: str, provider_class: Type[DestinationProvider]) -> None:
        """Register a new destination provider"""
        cls._destination_providers[name] = provider_class
    
    @classmethod
    def get_available_source_providers(cls) -> list:
        """Get list of available source providers"""
        return list(cls._source_providers.keys())
    
    @classmethod
    def get_available_destination_providers(cls) -> list:
        """Get list of available destination providers"""
        return list(cls._destination_providers.keys()) 