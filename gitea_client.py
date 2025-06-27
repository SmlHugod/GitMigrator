"""
Gitea API client for repository operations
"""
import requests
import json
from typing import List, Dict, Optional

class GiteaClient:
    """Client for interacting with Gitea API"""
    
    def __init__(self, base_url: str, token: str, username: str):
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.username = username
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'token {token}',
            'Content-Type': 'application/json'
        })
    
    def get_user_repos(self) -> List[Dict]:
        """Get all repositories owned by the user"""
        url = f"{self.base_url}/api/v1/user/repos"
        params = {
            'limit': 100,  # Adjust as needed
            'page': 1
        }
        
        all_repos = []
        
        while True:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            repos = response.json()
            if not repos:
                break
                
            all_repos.extend(repos)
            params['page'] += 1
            
            # Break if we got less than the limit (last page)
            if len(repos) < params.get('limit', 100):
                break
        
        return all_repos
    
    def get_repo_info(self, owner: str, repo_name: str) -> Optional[Dict]:
        """Get information about a specific repository"""
        url = f"{self.base_url}/api/v1/repos/{owner}/{repo_name}"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return None
    
    def get_repo_clone_url(self, owner: str, repo_name: str) -> str:
        """Get the clone URL for a repository with authentication"""
        return f"{self.base_url}/{owner}/{repo_name}.git"
    
    def list_accessible_repos(self) -> List[Dict]:
        """List all repositories the user has access to (including organizations)"""
        url = f"{self.base_url}/api/v1/user/repos"
        params = {
            'limit': 100,
            'page': 1
        }
        
        all_repos = []
        
        while True:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            repos = response.json()
            if not repos:
                break
                
            all_repos.extend(repos)
            params['page'] += 1
            
            if len(repos) < params.get('limit', 100):
                break
        
        return all_repos 