"""
Abstract base classes for source and destination providers
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class Repository:
    """Repository data model"""
    name: str
    owner: str
    description: str
    private: bool
    clone_url: str
    ssh_url: Optional[str] = None
    web_url: Optional[str] = None
    default_branch: Optional[str] = None
    github_name: Optional[str] = None  # For renaming during migration


class SourceProvider(ABC):
    """Abstract base class for source providers (Gitea, GitLab, etc.)"""
    
    def __init__(self, config: Dict):
        self.config = config
        self._validate_config()
    
    @abstractmethod
    def _validate_config(self) -> None:
        """Validate provider-specific configuration"""
        pass
    
    @abstractmethod
    def get_user_repositories(self) -> List[Repository]:
        """Get repositories owned by the authenticated user"""
        pass
    
    @abstractmethod
    def get_accessible_repositories(self) -> List[Repository]:
        """Get all repositories accessible to the authenticated user"""
        pass
    
    @abstractmethod
    def get_repository_info(self, owner: str, name: str) -> Optional[Repository]:
        """Get information about a specific repository"""
        pass
    
    @abstractmethod
    def get_authenticated_clone_url(self, repository: Repository) -> str:
        """Get authenticated clone URL for a repository"""
        pass


class DestinationProvider(ABC):
    """Abstract base class for destination providers (GitHub, GitLab, etc.)"""
    
    def __init__(self, config: Dict):
        self.config = config
        self._validate_config()
    
    @abstractmethod
    def _validate_config(self) -> None:
        """Validate provider-specific configuration"""
        pass
    
    @abstractmethod
    def create_repository(self, repository: Repository, target_name: str) -> bool:
        """Create a new repository in the destination provider"""
        pass
    
    @abstractmethod
    def repository_exists(self, name: str) -> bool:
        """Check if a repository exists"""
        pass
    
    @abstractmethod
    def get_authenticated_push_url(self, name: str) -> str:
        """Get authenticated URL for pushing to repository"""
        pass


class MigrationError(Exception):
    """Base exception for migration errors"""
    pass


class ProviderError(MigrationError):
    """Exception for provider-specific errors"""
    pass


class ConfigurationError(MigrationError):
    """Exception for configuration errors"""
    pass 