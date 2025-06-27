"""
GitHub API client for repository operations
"""
from github import Github
from github.GithubException import GithubException
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

class GitHubClient:
    """Client for interacting with GitHub API"""
    
    def __init__(self, token: str, username: str):
        self.github = Github(token)
        self.username = username
        self.user = self.github.get_user()
    
    def create_repository(self, repo_name: str, description: str = "", private: bool = False) -> bool:
        """Create a new repository on GitHub"""
        try:
            # Check if repository already exists
            if self.repository_exists(repo_name):
                logger.warning(f"Repository {repo_name} already exists on GitHub")
                return True
            
            self.user.create_repo(
                name=repo_name,
                description=description,
                private=private,
                auto_init=False  # Don't auto-init since we'll push existing content
            )
            logger.info(f"Created repository: {repo_name}")
            return True
            
        except GithubException as e:
            logger.error(f"Failed to create repository {repo_name}: {e}")
            return False
    
    def repository_exists(self, repo_name: str) -> bool:
        """Check if a repository exists"""
        try:
            self.user.get_repo(repo_name)
            return True
        except GithubException:
            return False
    
    def get_repo_clone_url(self, repo_name: str) -> str:
        """Get the clone URL for a GitHub repository"""
        return f"https://github.com/{self.username}/{repo_name}.git"
    
    def get_authenticated_clone_url(self, repo_name: str, token: str) -> str:
        """Get the authenticated clone URL for pushing"""
        return f"https://{token}@github.com/{self.username}/{repo_name}.git" 