"""
Gitea source provider implementation
"""
import requests
from typing import List, Dict, Optional
from ..base import SourceProvider, Repository, ProviderError, ConfigurationError


class GiteaSourceProvider(SourceProvider):
    """Gitea source provider implementation"""
    
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
    
    def get_user_repositories(self) -> List[Repository]:
        """Get repositories owned by the authenticated user"""
        repositories = self.get_accessible_repositories()
        return [repo for repo in repositories if repo.owner == self.username]
    
    def get_accessible_repositories(self) -> List[Repository]:
        """Get all repositories accessible to the authenticated user"""
        url = f"{self.base_url}/api/v1/user/repos"
        params = {'limit': 100, 'page': 1}
        
        all_repos = []
        
        while True:
            try:
                response = self.session.get(url, params=params)
                response.raise_for_status()
                repos_data = response.json()
                
                if not repos_data:
                    break
                
                repos = [self._parse_repository(repo_data) for repo_data in repos_data]
                all_repos.extend(repos)
                
                params['page'] += 1
                
                if len(repos_data) < params['limit']:
                    break
                    
            except requests.RequestException as e:
                raise ProviderError(f"Failed to fetch repositories from Gitea: {e}")
        
        return all_repos
    
    def get_repository_info(self, owner: str, name: str) -> Optional[Repository]:
        """Get information about a specific repository"""
        url = f"{self.base_url}/api/v1/repos/{owner}/{name}"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return self._parse_repository(response.json())
        except requests.RequestException:
            return None
    
    def get_authenticated_clone_url(self, repository: Repository) -> str:
        """Get authenticated clone URL for a repository"""
        base_url = self.base_url.replace('https://', '').replace('http://', '')
        return f"https://{self.username}:{self.token}@{base_url}/{repository.owner}/{repository.name}.git"
    
    def _parse_repository(self, repo_data: Dict) -> Repository:
        """Parse repository data from Gitea API response"""
        return Repository(
            name=repo_data['name'],
            owner=repo_data['owner']['login'],
            description=repo_data.get('description', ''),
            private=repo_data.get('private', False),
            clone_url=repo_data['clone_url'],
            ssh_url=repo_data.get('ssh_url'),
            web_url=repo_data.get('html_url'),
            default_branch=repo_data.get('default_branch', 'main')
        ) 