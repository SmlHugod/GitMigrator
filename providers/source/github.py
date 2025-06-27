"""
GitHub source provider implementation
"""
import logging
from github import Github
from github.GithubException import GithubException
from typing import List, Dict, Optional
from ..base import SourceProvider, Repository, ProviderError, ConfigurationError

logger = logging.getLogger(__name__)


class GitHubSourceProvider(SourceProvider):
    """GitHub source provider implementation"""
    
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
    
    def get_user_repositories(self) -> List[Repository]:
        """Get repositories owned by the authenticated user"""
        repositories = self.get_accessible_repositories()
        return [repo for repo in repositories if repo.owner == self.username]
    
    def get_accessible_repositories(self) -> List[Repository]:
        """Get all repositories accessible to the authenticated user"""
        all_repos = []
        
        try:
            # Get user's own repositories
            user_repos = self.user.get_repos()
            all_repos.extend([self._parse_repository(repo) for repo in user_repos])
            
            # Get repositories from organizations the user belongs to
            for org in self.user.get_orgs():
                try:
                    org_repos = org.get_repos()
                    all_repos.extend([self._parse_repository(repo) for repo in org_repos])
                except GithubException as e:
                    logger.warning(f"Could not fetch repositories from organization {org.login}: {e}")
                    continue
                    
        except GithubException as e:
            raise ProviderError(f"Failed to fetch repositories from GitHub: {e}")
        
        return all_repos
    
    def get_repository_info(self, owner: str, name: str) -> Optional[Repository]:
        """Get information about a specific repository"""
        try:
            repo = self.github.get_repo(f"{owner}/{name}")
            return self._parse_repository(repo)
        except GithubException:
            return None
    
    def get_authenticated_clone_url(self, repository: Repository) -> str:
        """Get authenticated clone URL for a repository"""
        return f"https://{self.token}@github.com/{repository.owner}/{repository.name}.git"
    
    def _parse_repository(self, repo) -> Repository:
        """Parse repository data from GitHub API response"""
        return Repository(
            name=repo.name,
            owner=repo.owner.login,
            description=repo.description or '',
            private=repo.private,
            clone_url=repo.clone_url,
            ssh_url=repo.ssh_url,
            web_url=repo.html_url,
            default_branch=repo.default_branch or 'main'
        ) 