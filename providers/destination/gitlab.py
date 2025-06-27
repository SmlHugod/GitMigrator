"""
GitLab destination provider implementation (Example for extensibility)
"""
import logging
import requests
from typing import Dict
from ..base import DestinationProvider, Repository, ProviderError, ConfigurationError

logger = logging.getLogger(__name__)


class GitLabDestinationProvider(DestinationProvider):
    """GitLab destination provider implementation"""
    
    def _validate_config(self) -> None:
        """Validate GitLab-specific configuration"""
        required_keys = ['url', 'token', 'username']
        missing = [key for key in required_keys if not self.config.get(key)]
        
        if missing:
            raise ConfigurationError(f"Missing GitLab configuration: {', '.join(missing)}")
        
        self.base_url = self.config['url'].rstrip('/')
        self.token = self.config['token']
        self.username = self.config['username']
        
        # Setup HTTP session
        self.session = requests.Session()
        # GitLab uses different token formats - try Private-Token first
        if self.token.startswith('glpat-'):
            # Personal Access Token
            self.session.headers.update({
                'Private-Token': self.token,
                'Content-Type': 'application/json'
            })
        else:
            # OAuth token or other format
            self.session.headers.update({
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            })
        
        # Verify authentication
        try:
            response = self.session.get(f"{self.base_url}/api/v4/user")
            response.raise_for_status()
            self.user_id = response.json()['id']
        except requests.RequestException as e:
            raise ConfigurationError(f"Failed to authenticate with GitLab: {e}")
    
    def create_repository(self, repository: Repository, target_name: str) -> bool:
        """Create a new repository on GitLab"""
        response = None
        try:
            # Check if repository already exists
            if self.repository_exists(target_name):
                logger.warning(f"Repository {target_name} already exists on GitLab")
                return True
            
            project_data = {
                'name': target_name,
                'description': repository.description or '',
                'visibility': 'private' if repository.private else 'public',
                'initialize_with_readme': False
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v4/projects",
                json=project_data
            )
            response.raise_for_status()
            
            logger.info(f"Created repository: {target_name}")
            return True
            
        except requests.RequestException as e:
            logger.error(f"Failed to create repository {target_name}: {e}")
            if response and response.status_code == 400:
                # Repository might already exist or name is invalid
                logger.warning(f"Repository creation failed, possibly already exists: {target_name}")
                return self.repository_exists(target_name)
            elif response and response.status_code == 409:
                # Conflict - repository already exists
                logger.warning(f"Repository {target_name} already exists (conflict)")
                return True
            raise ProviderError(f"Failed to create GitLab repository: {e}")
        except Exception as e:
            logger.error(f"Unexpected error creating repository {target_name}: {e}")
            return False
    
    def repository_exists(self, name: str) -> bool:
        """Check if a repository exists"""
        project_path = f"{self.username}/{name}"
        url = f"{self.base_url}/api/v4/projects/{requests.utils.quote(project_path, safe='')}"
        
        try:
            response = self.session.get(url)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def get_authenticated_push_url(self, name: str) -> str:
        """Get authenticated URL for pushing to repository"""
        base_url = self.base_url.replace('https://', '').replace('http://', '')
        return f"https://oauth2:{self.token}@{base_url}/{self.username}/{name}.git" 