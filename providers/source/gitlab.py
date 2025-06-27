"""
GitLab source provider implementation (Example for extensibility)
"""
import requests
from typing import List, Dict, Optional
from ..base import SourceProvider, Repository, ProviderError, ConfigurationError


class GitLabSourceProvider(SourceProvider):
    """GitLab source provider implementation"""
    
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
    
    def get_user_repositories(self) -> List[Repository]:
        """Get repositories owned by the authenticated user"""
        repositories = self.get_accessible_repositories()
        return [repo for repo in repositories if repo.owner == self.username]
    
    def get_accessible_repositories(self) -> List[Repository]:
        """Get all repositories accessible to the authenticated user"""
        url = f"{self.base_url}/api/v4/projects"
        params = {
            'membership': 'true',
            'per_page': 100,
            'page': 1
        }
        
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
                
                # Check if there are more pages
                if 'X-Next-Page' not in response.headers:
                    break
                
                params['page'] += 1
                
            except requests.RequestException as e:
                raise ProviderError(f"Failed to fetch repositories from GitLab: {e}")
        
        return all_repos
    
    def get_repository_info(self, owner: str, name: str) -> Optional[Repository]:
        """Get information about a specific repository"""
        # GitLab uses project ID or namespace/project format
        project_path = f"{owner}/{name}"
        url = f"{self.base_url}/api/v4/projects/{requests.utils.quote(project_path, safe='')}"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return self._parse_repository(response.json())
        except requests.RequestException:
            return None
    
    def get_authenticated_clone_url(self, repository: Repository) -> str:
        """Get authenticated clone URL for a repository"""
        base_url = self.base_url.replace('https://', '').replace('http://', '')
        return f"https://oauth2:{self.token}@{base_url}/{repository.owner}/{repository.name}.git"
    
    def _parse_repository(self, repo_data: Dict) -> Repository:
        """Parse repository data from GitLab API response"""
        namespace = repo_data['namespace']
        owner = namespace['path'] if namespace['kind'] == 'user' else namespace['full_path']
        
        return Repository(
            name=repo_data['name'],
            owner=owner,
            description=repo_data.get('description', ''),
            private=repo_data.get('visibility') == 'private',
            clone_url=repo_data['http_url_to_repo'],
            ssh_url=repo_data.get('ssh_url_to_repo'),
            web_url=repo_data.get('web_url'),
            default_branch=repo_data.get('default_branch', 'main')
        ) 