"""
GitHub destination provider implementation
"""
import logging
from github import Github
from github.GithubException import GithubException
from typing import Dict
from ..base import DestinationProvider, Repository, ProviderError, ConfigurationError

logger = logging.getLogger(__name__)


class GitHubDestinationProvider(DestinationProvider):
    """GitHub destination provider implementation"""
    
    def _validate_config(self) -> None:
        """Validate GitHub-specific configuration"""
        required_keys = ['token', 'username']
        missing = [key for key in required_keys if not self.config.get(key)]
        
        if missing:
            raise ConfigurationError(f"Missing GitHub configuration: {', '.join(missing)}")
        
        self.token = self.config['token']
        self.username = self.config['username']
        
        try:
            self.github = Github(self.token)
            self.user = self.github.get_user()
        except GithubException as e:
            raise ConfigurationError(f"Failed to authenticate with GitHub: {e}")
    
    def create_repository(self, repository: Repository, target_name: str) -> bool:
        """Create a new repository on GitHub"""
        try:
            # Check if repository already exists
            if self.repository_exists(target_name):
                logger.warning(f"Repository {target_name} already exists on GitHub")
                return True
            
            logger.info(f"Creating GitHub repository: {target_name}")
            self.user.create_repo(
                name=target_name,
                description=repository.description or '',
                private=repository.private,
                auto_init=False  # Don't auto-init since we'll push existing content
            )
            logger.info(f"Successfully created repository: {target_name}")
            return True
            
        except GithubException as e:
            logger.error(f"GitHub API error creating repository {target_name}: {e}")
            logger.error(f"GitHub error status: {e.status}")
            logger.error(f"GitHub error data: {e.data}")
            
            # Handle specific GitHub errors
            if e.status == 422 and 'already exists' in str(e.data).lower():
                logger.warning(f"Repository {target_name} already exists (422 error)")
                return True
            
            raise ProviderError(f"Failed to create GitHub repository: {e}")
        except Exception as e:
            logger.error(f"Unexpected error creating GitHub repository {target_name}: {e}")
            logger.error(f"Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            raise ProviderError(f"Unexpected error creating GitHub repository: {e}")
    
    def repository_exists(self, name: str) -> bool:
        """Check if a repository exists"""
        try:
            repo = self.user.get_repo(name)
            logger.debug(f"Repository {name} exists: {repo.full_name}")
            return True
        except GithubException as e:
            if e.status == 404:
                logger.debug(f"Repository {name} does not exist (404)")
                return False
            else:
                logger.warning(f"Error checking if repository {name} exists: {e}")
                return False
        except Exception as e:
            logger.error(f"Unexpected error checking repository existence {name}: {e}")
            return False
    
    def get_authenticated_push_url(self, name: str) -> str:
        """Get authenticated URL for pushing to repository"""
        return f"https://{self.token}@github.com/{self.username}/{name}.git" 