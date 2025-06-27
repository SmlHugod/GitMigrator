"""
Configuration management for migration tool
"""
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from providers.base import ConfigurationError


class MigrationConfig:
    """Configuration manager for migration settings"""
    
    def __init__(self):
        # Reload environment variables from .env file each time
        load_dotenv(override=True)
        
        # Load all provider configurations (source and destination)
        self.gitea_source_config = self._load_gitea_source_config()
        self.gitea_dest_config = self._load_gitea_dest_config()
        self.gitlab_source_config = self._load_gitlab_source_config()
        self.gitlab_dest_config = self._load_gitlab_dest_config()
        self.github_config = self._load_github_config()  # Single config for GitHub
    
    def _load_gitea_source_config(self) -> Dict[str, Any]:
        """Load Gitea source configuration"""
        return {
            'url': os.getenv('GITEA_SOURCE_URL', 'https://codefirst.iut.uca.fr/git'),
            'token': os.getenv('GITEA_SOURCE_TOKEN'),
            'username': os.getenv('GITEA_SOURCE_USERNAME')
        }
    
    def _load_gitea_dest_config(self) -> Dict[str, Any]:
        """Load Gitea destination configuration"""
        return {
            'url': os.getenv('GITEA_DEST_URL', 'https://codefirst.iut.uca.fr/git'),
            'token': os.getenv('GITEA_DEST_TOKEN'),
            'username': os.getenv('GITEA_DEST_USERNAME')
        }
    
    def _load_gitlab_source_config(self) -> Dict[str, Any]:
        """Load GitLab source configuration"""
        return {
            'url': os.getenv('GITLAB_SOURCE_URL', 'https://gitlab.com'),
            'token': os.getenv('GITLAB_SOURCE_TOKEN'),
            'username': os.getenv('GITLAB_SOURCE_USERNAME')
        }
    
    def _load_gitlab_dest_config(self) -> Dict[str, Any]:
        """Load GitLab destination configuration"""
        return {
            'url': os.getenv('GITLAB_DEST_URL', 'https://gitlab.com'),
            'token': os.getenv('GITLAB_DEST_TOKEN'),
            'username': os.getenv('GITLAB_DEST_USERNAME')
        }
    
    def _load_github_config(self) -> Dict[str, Any]:
        """Load GitHub configuration"""
        return {
            'token': os.getenv('GITHUB_TOKEN'),
            'username': os.getenv('GITHUB_USERNAME')
        }
    
    def get_source_provider_config(self, provider_type: str) -> Dict[str, Any]:
        """Get source configuration for a specific provider"""
        if provider_type == 'gitea':
            return self.gitea_source_config
        elif provider_type == 'gitlab':
            return self.gitlab_source_config
        elif provider_type == 'github':
            return self.github_config  # Same config for source and dest
        else:
            raise ConfigurationError(f"Unknown source provider type: {provider_type}")
    
    def get_destination_provider_config(self, provider_type: str) -> Dict[str, Any]:
        """Get destination configuration for a specific provider"""
        if provider_type == 'gitea':
            return self.gitea_dest_config
        elif provider_type == 'gitlab':
            return self.gitlab_dest_config
        elif provider_type == 'github':
            return self.github_config  # Same config for source and dest
        else:
            raise ConfigurationError(f"Unknown destination provider type: {provider_type}")
    
    def is_source_provider_configured(self, provider_type: str) -> bool:
        """Check if a source provider is configured (has all required fields)"""
        try:
            config = self.get_source_provider_config(provider_type)
            return all(value for value in config.values())
        except ConfigurationError:
            return False
    
    def is_destination_provider_configured(self, provider_type: str) -> bool:
        """Check if a destination provider is configured (has all required fields)"""
        try:
            config = self.get_destination_provider_config(provider_type)
            return all(value for value in config.values())
        except ConfigurationError:
            return False
    
    def get_available_source_providers(self) -> Dict[str, bool]:
        """Get list of source providers and their configuration status"""
        return {
            'gitea': self.is_source_provider_configured('gitea'),
            'gitlab': self.is_source_provider_configured('gitlab'),
            'github': self.is_source_provider_configured('github')
        }
    
    def get_available_destination_providers(self) -> Dict[str, bool]:
        """Get list of destination providers and their configuration status"""
        return {
            'gitea': self.is_destination_provider_configured('gitea'),
            'gitlab': self.is_destination_provider_configured('gitlab'),
            'github': self.is_destination_provider_configured('github')
        }
    
    def validate_source_provider_config(self, provider_type: str) -> None:
        """Validate source configuration for a specific provider"""
        config = self.get_source_provider_config(provider_type)
        missing = [key for key, value in config.items() if not value]
        
        if missing:
            raise ConfigurationError(f"Missing {provider_type} source configuration: {', '.join(missing)}")
    
    def validate_destination_provider_config(self, provider_type: str) -> None:
        """Validate destination configuration for a specific provider"""
        config = self.get_destination_provider_config(provider_type)
        missing = [key for key, value in config.items() if not value]
        
        if missing:
            raise ConfigurationError(f"Missing {provider_type} destination configuration: {', '.join(missing)}")
    
    def is_valid(self) -> bool:
        """Check if at least one source and one destination provider are configured"""
        source_configured = any(self.get_available_source_providers().values())
        dest_configured = any(self.get_available_destination_providers().values())
        return source_configured and dest_configured

    # Deprecated methods for compatibility (if ever used elsewhere)
    def get_provider_config(self, provider_type: str) -> Dict[str, Any]:
        """DEPRECATED: Use get_source_provider_config or get_destination_provider_config"""
        return self.get_source_provider_config(provider_type)
    
    def is_provider_configured(self, provider_type: str) -> bool:
        """DEPRECATED: Use is_source_provider_configured or is_destination_provider_configured"""
        return self.is_source_provider_configured(provider_type)
    
    def get_available_providers(self) -> Dict[str, bool]:
        """DEPRECATED: Use get_available_source_providers or get_available_destination_providers"""
        return self.get_available_source_providers() 