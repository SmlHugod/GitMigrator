"""
Configuration module for Gitea to GitHub migration tool
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for migration settings"""
    
    def __init__(self):
        self.gitea_url = os.getenv('GITEA_URL', 'https://codefirst.iut.uca.fr/git')
        self.gitea_token = os.getenv('GITEA_TOKEN')
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.github_username = os.getenv('GITHUB_USERNAME')
        self.gitea_username = os.getenv('GITEA_USERNAME')
        
        # Validate required configuration
        self._validate_config()
    
    def _validate_config(self):
        """Validate that all required configuration is present"""
        missing = []
        
        if not self.gitea_token:
            missing.append('GITEA_TOKEN')
        if not self.github_token:
            missing.append('GITHUB_TOKEN')
        if not self.github_username:
            missing.append('GITHUB_USERNAME')
        if not self.gitea_username:
            missing.append('GITEA_USERNAME')
            
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
    
    def is_valid(self):
        """Check if configuration is valid"""
        try:
            self._validate_config()
            return True
        except ValueError:
            return False 