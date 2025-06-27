"""
Main migration engine
"""
import os
import subprocess
import tempfile
import shutil
import logging
from typing import List, Dict
from pathlib import Path

from providers.base import SourceProvider, DestinationProvider, Repository, MigrationError
from .config import MigrationConfig

logger = logging.getLogger(__name__)


class MigrationEngine:
    """Main migration engine that orchestrates repository migrations"""
    
    def __init__(self, source_provider: SourceProvider, destination_provider: DestinationProvider):
        self.source_provider = source_provider
        self.destination_provider = destination_provider
    
    def migrate_repositories(self, repositories: List[Repository]) -> Dict[str, bool]:
        """Migrate a list of repositories"""
        if not repositories:
            logger.info("No repositories selected for migration")
            return {}
        
        results = {}
        for repository in repositories:
            target_name = repository.github_name or repository.name
            
            if repository.github_name and repository.github_name != repository.name:
                logger.info(f"Migrating repository: {repository.owner}/{repository.name} → {target_name}")
            else:
                logger.info(f"Migrating repository: {repository.owner}/{repository.name}")
            
            try:
                success = self._migrate_single_repository(repository, target_name)
                display_name = f"{repository.owner}/{repository.name}"
                if target_name != repository.name:
                    display_name += f" → {target_name}"
                results[display_name] = success
                
            except Exception as e:
                logger.error(f"Unexpected error migrating {repository.name}: {e}")
                display_name = f"{repository.owner}/{repository.name}"
                if target_name != repository.name:
                    display_name += f" → {target_name}"
                results[display_name] = False
        
        return results
    
    def _migrate_single_repository(self, repository: Repository, target_name: str) -> bool:
        """Migrate a single repository"""
        try:
            # Create destination repository
            logger.info(f"Creating destination repository: {target_name}")
            success = self.destination_provider.create_repository(repository, target_name)
            if not success:
                logger.error(f"Failed to create destination repository: {target_name}")
                return False
            
            # Clone and push repository
            logger.info(f"Starting clone and push for repository: {repository.name}")
            return self._clone_and_push_repository(repository, target_name)
            
        except MigrationError as e:
            logger.error(f"Migration error for repository {repository.name}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error migrating repository {repository.name}: {e}")
            logger.error(f"Exception type: {type(e).__name__}")
            logger.error(f"Exception args: {e.args}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return False
    
    def _clone_and_push_repository(self, repository: Repository, target_name: str) -> bool:
        """Clone repository from source and push to destination"""
        temp_dir = None
        original_cwd = os.getcwd()
        
        try:
            # Create temporary directory
            temp_dir = tempfile.mkdtemp(prefix=f"migration_{repository.name}_")
            repo_path = Path(temp_dir) / repository.name
            
            # Clone from source
            source_url = self.source_provider.get_authenticated_clone_url(repository)
            clone_cmd = ['git', 'clone', '--mirror', source_url, str(repo_path)]
            
            logger.info(f"Cloning repository from {self.source_provider.__class__.__name__}: {repository.owner}/{repository.name}")
            result = subprocess.run(clone_cmd, capture_output=True, text=True, cwd=temp_dir)
            
            if result.returncode != 0:
                logger.error(f"Failed to clone repository: {result.stderr}")
                return False
            
            # Verify repository was cloned successfully
            if not repo_path.exists():
                logger.error(f"Repository directory not found after cloning: {repo_path}")
                return False
            
            # Add destination remote
            dest_url = self.destination_provider.get_authenticated_push_url(target_name)
            add_remote_cmd = ['git', 'remote', 'add', 'destination', dest_url]
            result = subprocess.run(add_remote_cmd, capture_output=True, text=True, cwd=str(repo_path))
            
            if result.returncode != 0:
                logger.error(f"Failed to add destination remote: {result.stderr}")
                return False
            
            # Push to destination
            return self._push_to_destination(repository, target_name, repo_path)
            
        except Exception as e:
            logger.error(f"Error during repository migration: {e}")
            return False
            
        finally:
            # Restore original working directory
            try:
                os.chdir(original_cwd)
            except Exception as e:
                logger.warning(f"Failed to restore original working directory: {e}")
            
            # Clean up temporary directory
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir, ignore_errors=True)
                except Exception as e:
                    logger.warning(f"Failed to clean up temporary directory {temp_dir}: {e}")
    
    def _push_to_destination(self, repository: Repository, target_name: str, repo_path: Path) -> bool:
        """Push repository to destination provider"""
        if target_name != repository.name:
            logger.info(f"Pushing repository to destination: {repository.name} → {target_name}")
        else:
            logger.info(f"Pushing repository to destination: {repository.name}")
        
        # Push branches
        push_branches_cmd = ['git', 'push', '--all', 'destination']
        result = subprocess.run(push_branches_cmd, capture_output=True, text=True, cwd=str(repo_path))
        
        if result.returncode != 0:
            logger.error(f"Failed to push branches to destination: {result.stderr}")
            return False
        
        # Push tags (non-blocking)
        push_tags_cmd = ['git', 'push', '--tags', 'destination']
        result = subprocess.run(push_tags_cmd, capture_output=True, text=True, cwd=str(repo_path))
        
        if result.returncode != 0:
            logger.warning(f"Failed to push tags to destination (this is often normal): {result.stderr}")
        
        if target_name != repository.name:
            logger.info(f"Successfully migrated repository: {repository.name} → {target_name}")
        else:
            logger.info(f"Successfully migrated repository: {repository.name}")
        
        return True 