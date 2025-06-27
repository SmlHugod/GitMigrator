"""
Configuration management for migration tool
"""
import os
from typing import Dict, Any
from dotenv import load_dotenv
from providers.base import ConfigurationError

# Load environment variables from .env file
load_dotenv()


class MigrationConfig:
    """Configuration manager for migration settings"""
    
    def __init__(self):
        self.source_provider = os.getenv('SOURCE_PROVIDER', 'gitea').lower()
        self.destination_provider = os.getenv('DESTINATION_PROVIDER', 'github').lower()
        
        self.source_config = self._load_source_config()
        self.destination_config = self._load_destination_config()
        
        self._validate_config()
    
    def _load_source_config(self) -> Dict[str, Any]:
        """Load source provider configuration"""
        if self.source_provider == 'gitea':
            return {
                'url': os.getenv('GITEA_URL', 'https://codefirst.iut.uca.fr/git'),
                'token': os.getenv('GITEA_TOKEN'),
                'username': os.getenv('GITEA_USERNAME')
            }
        elif self.source_provider == 'gitlab':
            return {
                'url': os.getenv('GITLAB_URL', 'https://gitlab.com'),
                'token': os.getenv('GITLAB_TOKEN'),
                'username': os.getenv('GITLAB_USERNAME')
            }
        else:
            raise ConfigurationError(f"Unsupported source provider: {self.source_provider}")
    
    def _load_destination_config(self) -> Dict[str, Any]:
        """Load destination provider configuration"""
        if self.destination_provider == 'github':
            return {
                'token': os.getenv('GITHUB_TOKEN'),
                'username': os.getenv('GITHUB_USERNAME')
            }
        elif self.destination_provider == 'gitlab':
            return {
                'url': os.getenv('GITLAB_DEST_URL', 'https://gitlab.com'),
                'token': os.getenv('GITLAB_DEST_TOKEN'),
                'username': os.getenv('GITLAB_DEST_USERNAME')
            }
        else:
            raise ConfigurationError(f"Unsupported destination provider: {self.destination_provider}")
    
    def _validate_config(self) -> None:
        """Validate configuration completeness"""
        # Check source config
        missing_source = [key for key, value in self.source_config.items() if not value]
        if missing_source:
            raise ConfigurationError(f"Missing {self.source_provider} source configuration: {', '.join(missing_source)}")
        
        # Check destination config
        missing_dest = [key for key, value in self.destination_config.items() if not value]
        if missing_dest:
            raise ConfigurationError(f"Missing {self.destination_provider} destination configuration: {', '.join(missing_dest)}")
    
    def is_valid(self) -> bool:
        """Check if configuration is valid"""
        try:
            self._validate_config()
            return True
        except ConfigurationError:
            return False 