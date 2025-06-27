"""
Main migration tool for transferring repositories from Gitea to GitHub
"""
import os
import subprocess
import tempfile
import shutil
import logging
from typing import List, Dict, Optional
from pathlib import Path

from config import Config
from gitea_client import GiteaClient
from github_client import GitHubClient

logger = logging.getLogger(__name__)

class MigrationTool:
    """Main tool for migrating repositories from Gitea to GitHub"""
    
    def __init__(self, config: Config):
        self.config = config
        self.gitea_client = GiteaClient(
            config.gitea_url, 
            config.gitea_token, 
            config.gitea_username
        )
        self.github_client = GitHubClient(
            config.github_token, 
            config.github_username
        )
    
    def migrate_all_user_repos(self) -> Dict[str, bool]:
        """Migrate all repositories owned by the user"""
        logger.info("Fetching user repositories from Gitea...")
        repos = self.gitea_client.get_user_repos()
        
        results = {}
        for repo in repos:
            if repo['owner']['login'] == self.config.gitea_username:
                repo_name = repo['name']
                logger.info(f"Migrating repository: {repo_name}")
                success = self.migrate_repository(repo)
                results[repo_name] = success
        
        return results
    
    def migrate_specific_repos(self, repo_specs: List[str]) -> Dict[str, bool]:
        """
        Migrate specific repositories
        repo_specs: List of repository specifications in format 'owner/repo' or just 'repo'
        """
        results = {}
        
        for repo_spec in repo_specs:
            if '/' in repo_spec:
                owner, repo_name = repo_spec.split('/', 1)
            else:
                owner = self.config.gitea_username
                repo_name = repo_spec
            
            logger.info(f"Migrating repository: {owner}/{repo_name}")
            repo_info = self.gitea_client.get_repo_info(owner, repo_name)
            
            if repo_info:
                success = self.migrate_repository(repo_info)
                results[f"{owner}/{repo_name}"] = success
            else:
                logger.error(f"Repository {owner}/{repo_name} not found or not accessible")
                results[f"{owner}/{repo_name}"] = False
        
        return results
    
    def migrate_repository(self, repo_info: Dict) -> bool:
        """Migrate a single repository"""
        repo_name = repo_info['name']
        repo_owner = repo_info['owner']['login']
        
        try:
            # Create GitHub repository
            success = self.github_client.create_repository(
                repo_name=repo_name,
                description=repo_info.get('description', ''),
                private=repo_info.get('private', False)
            )
            
            if not success:
                return False
            
            # Clone and push repository
            return self._clone_and_push_repo(repo_owner, repo_name)
            
        except Exception as e:
            logger.error(f"Failed to migrate repository {repo_name}: {e}")
            return False
    
    def _clone_and_push_repo(self, repo_owner: str, repo_name: str) -> bool:
        """Clone repository from Gitea and push to GitHub"""
        temp_dir = None
        
        try:
            # Create temporary directory
            temp_dir = tempfile.mkdtemp(prefix=f"migration_{repo_name}_")
            repo_path = Path(temp_dir) / repo_name
            
            # Clone from Gitea
            gitea_url = self._get_authenticated_gitea_url(repo_owner, repo_name)
            clone_cmd = ['git', 'clone', '--mirror', gitea_url, str(repo_path)]
            
            logger.info(f"Cloning repository from Gitea: {repo_owner}/{repo_name}")
            result = subprocess.run(clone_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Failed to clone repository: {result.stderr}")
                return False
            
            # Change to repository directory
            os.chdir(repo_path)
            
            # Add GitHub remote
            github_url = self.github_client.get_authenticated_clone_url(
                repo_name, 
                self.config.github_token
            )
            
            add_remote_cmd = ['git', 'remote', 'add', 'github', github_url]
            result = subprocess.run(add_remote_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Failed to add GitHub remote: {result.stderr}")
                return False
            
            # Push to GitHub
            logger.info(f"Pushing repository to GitHub: {repo_name}")
            push_cmd = ['git', 'push', '--mirror', 'github']
            result = subprocess.run(push_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Failed to push to GitHub: {result.stderr}")
                return False
            
            logger.info(f"Successfully migrated repository: {repo_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error during repository migration: {e}")
            return False
            
        finally:
            # Clean up temporary directory
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
    
    def _get_authenticated_gitea_url(self, owner: str, repo_name: str) -> str:
        """Get authenticated Gitea URL for cloning"""
        base_url = self.config.gitea_url.replace('https://', '').replace('http://', '')
        return f"https://{self.config.gitea_username}:{self.config.gitea_token}@{base_url}/{owner}/{repo_name}.git"
    
    def list_available_repos(self) -> List[Dict]:
        """List all repositories available for migration"""
        return self.gitea_client.list_accessible_repos() 