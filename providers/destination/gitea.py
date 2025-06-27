"""
Gitea destination provider implementation
"""
import logging
import requests
from typing import Dict
from ..base import DestinationProvider, Repository, ProviderError, ConfigurationError

logger = logging.getLogger(__name__)


class GiteaDestinationProvider(DestinationProvider):
    """Gitea destination provider implementation"""
    
    def _validate_config(self) -> None:
        """Validate Gitea-specific configuration"""
        required_keys = ['url', 'token', 'username']
        missing = [key for key in required_keys if not self.config.get(key)]
        
        if missing:
            raise ConfigurationError(f"Missing Gitea configuration: {', '.join(missing)}")
        
        self.base_url = self.config['url'].rstrip('/')
        self.token = self.config['token']
        self.username = self.config['username']
        
        # Setup HTTP session
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'token {self.token}',
            'Content-Type': 'application/json'
        })
        
        # Verify authentication
        try:
            response = self.session.get(f"{self.base_url}/api/v1/user")
            response.raise_for_status()
        except requests.RequestException as e:
            raise ConfigurationError(f"Failed to authenticate with Gitea: {e}")
    
    def create_repository(self, repository: Repository, target_name: str) -> bool:
        """Create a new repository on Gitea"""
        response = None
        try:
            # Check if repository already exists
            if self.repository_exists(target_name):
                logger.warning(f"Repository {target_name} already exists on Gitea")
                return True
            
            repo_data = {
                'name': target_name,
                'description': repository.description or '',
                'private': repository.private,
                'auto_init': False  # Don't auto-init since we'll push existing content
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/user/repos",
                json=repo_data
            )
            response.raise_for_status()
            
            logger.info(f"Created repository: {target_name}")
            return True
            
        except requests.RequestException as e:
            logger.error(f"Failed to create repository {target_name}: {e}")
            if response and response.status_code == 409:
                # Conflict - repository already exists
                logger.warning(f"Repository {target_name} already exists (conflict)")
                return True
            elif response and response.status_code == 422:
                # Unprocessable Entity - might already exist or name is invalid
                logger.warning(f"Repository creation failed, possibly already exists: {target_name}")
                return self.repository_exists(target_name)
            raise ProviderError(f"Failed to create Gitea repository: {e}")
        except Exception as e:
            logger.error(f"Unexpected error creating repository {target_name}: {e}")
            return False
    
    def repository_exists(self, name: str) -> bool:
        """Check if a repository exists"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/repos/{self.username}/{name}")
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def get_authenticated_push_url(self, name: str) -> str:
        """Get authenticated URL for pushing to repository"""
        base_url = self.base_url.replace('https://', '').replace('http://', '')
        return f"https://{self.username}:{self.token}@{base_url}/{self.username}/{name}.git" 