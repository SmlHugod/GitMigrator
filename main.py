#!/usr/bin/env python3
"""
Repository Migration Tool

A flexible tool for migrating repositories between different Git hosting providers.
Currently supports:
- Source providers: Gitea, GitLab
- Destination providers: GitHub, GitLab

Future providers can be easily added through the extensible provider system.
"""

import argparse
import logging
import sys
from pathlib import Path
from colorama import init, Fore, Style

from core.config import MigrationConfig
from core.migration_engine import MigrationEngine
from providers.factory import ProviderFactory
from providers.base import ConfigurationError, ProviderError, MigrationError
from ui.interactive_selector import select_repositories_interactive
from ui.provider_selector import select_providers

# Initialize colorama for cross-platform colored output
init()

def setup_logging(verbose: bool = False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    format_str = '%(asctime)s - %(levelname)s - %(message)s'
    
    logging.basicConfig(
        level=level,
        format=format_str,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('migration.log')
        ]
    )

def print_banner():
    """Print application banner"""
    print(f"{Fore.MAGENTA}{'='*60}")
    print(f"{'🚀 GIT MIGRATION TOOL':^60}")
    print(f"{'Multi-Provider Repository Migration':^60}")
    print(f"{'='*60}{Style.RESET_ALL}")

def print_success_summary(results: dict):
    """Print migration results summary"""
    total = len(results)
    successful = sum(1 for success in results.values() if success)
    
    print(f"\n{Fore.GREEN}{'='*60}")
    print(f"                MIGRATION SUMMARY")
    print(f"{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}✅ Successful migrations: {successful}/{total}{Style.RESET_ALL}")
    
    if successful < total:
        print(f"{Fore.RED}❌ Failed migrations: {total - successful}/{total}{Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}Detailed results:{Style.RESET_ALL}")
    for repo, success in results.items():
        status = f"{Fore.GREEN}✅ SUCCESS" if success else f"{Fore.RED}❌ FAILED"
        print(f"  {repo}: {status}{Style.RESET_ALL}")

def create_env_template():
    """Create a .env template file if it doesn't exist"""
    env_file = Path('.env')
    
    if not env_file.exists():
        template = """# Gitea Source Configuration
GITEA_SOURCE_URL=https://codefirst.iut.uca.fr/git
GITEA_SOURCE_TOKEN=your_gitea_source_personal_access_token
GITEA_SOURCE_USERNAME=your_gitea_source_username

# Gitea Destination Configuration
GITEA_DEST_URL=https://codefirst.iut.uca.fr/git
GITEA_DEST_TOKEN=your_gitea_dest_personal_access_token
GITEA_DEST_USERNAME=your_gitea_dest_username

# GitLab Source Configuration
GITLAB_SOURCE_URL=https://gitlab.com
GITLAB_SOURCE_TOKEN=your_gitlab_source_token
GITLAB_SOURCE_USERNAME=your_gitlab_source_username

# GitLab Destination Configuration
GITLAB_DEST_URL=https://gitlab.com
GITLAB_DEST_TOKEN=your_gitlab_dest_token
GITLAB_DEST_USERNAME=your_gitlab_dest_username

# GitHub Configuration (same for source and destination - only one instance)
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_USERNAME=your_github_username

# Instructions:
# 1. Fill in the credentials for the providers you want to use as source or destination
# 2. You can use the same credentials for source and dest if it's the same instance
# 3. For migrations between different instances of the same provider, use different credentials
# 4. GitHub only has one instance (github.com), so GitHub→GitHub migrations are not supported
# 5. The tool will ask you which provider to use as source and destination
"""
        env_file.write_text(template)
        print(f"{Fore.YELLOW}📝 Created .env template file. Please fill it with your credentials.{Style.RESET_ALL}")
        return False
    
    return True

def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(
        description="Migrate repositories between Git hosting providers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Interactive mode (default): select repositories
  %(prog)s --no-interactive          # Migrate all your repositories automatically
  %(prog)s --repos repo1 repo2       # Migrate specific repositories
  %(prog)s --repos owner/repo1       # Migrate repositories from other owners
  %(prog)s --list                    # List available repositories
  %(prog)s --verbose                 # Enable verbose logging
  
Supported providers:
  Source: """ + ", ".join(ProviderFactory.get_available_source_providers()) + """
  Destination: """ + ", ".join(ProviderFactory.get_available_destination_providers()) + """
        """
    )
    
    parser.add_argument(
        '--repos', 
        nargs='+', 
        help='Specific repositories to migrate (format: repo_name or owner/repo_name)'
    )
    
    parser.add_argument(
        '--list', 
        action='store_true', 
        help='List all available repositories and exit'
    )
    
    parser.add_argument(
        '--verbose', '-v', 
        action='store_true', 
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--setup', 
        action='store_true', 
        help='Create .env template file'
    )
    
    parser.add_argument(
        '--no-interactive',
        action='store_true',
        help='Skip interactive mode: migrate all your repositories automatically'
    )
    
    args = parser.parse_args()
    
    print_banner()
    setup_logging(args.verbose)
    
    # Handle setup command
    if args.setup:
        create_env_template()
        return
    
    # Check if .env file exists
    if not create_env_template():
        return
    
    try:
        # Initialize configuration
        config = MigrationConfig()
        
        # Select providers interactively
        source_provider_type, destination_provider_type = select_providers()
        
        # Create providers
        source_provider = ProviderFactory.create_source_provider(
            source_provider_type, 
            config.get_source_provider_config(source_provider_type)
        )
        destination_provider = ProviderFactory.create_destination_provider(
            destination_provider_type, 
            config.get_destination_provider_config(destination_provider_type)
        )
        
        # Initialize migration engine
        migration_engine = MigrationEngine(source_provider, destination_provider)
        
        # Handle list command
        if args.list:
            print(f"{Fore.CYAN}📋 Available repositories from {source_provider_type}:{Style.RESET_ALL}")
            repos = source_provider.get_accessible_repositories()
            
            for repo in repos:
                private = "🔒 Private" if repo.private else "🌐 Public"
                description = repo.description or 'No description'
                
                print(f"  {Fore.BLUE}{repo.owner}/{repo.name}{Style.RESET_ALL} - {private}")
                if description:
                    print(f"    📝 {description}")
            
            print(f"\n{Fore.GREEN}Total repositories: {len(repos)}{Style.RESET_ALL}")
            return
        
        # Perform migration
        if args.repos:
            print(f"{Fore.CYAN}🎯 Migrating specific repositories: {', '.join(args.repos)}{Style.RESET_ALL}")
            repositories = []
            for repo_spec in args.repos:
                if '/' in repo_spec:
                    owner, repo_name = repo_spec.split('/', 1)
                else:
                    owner = config.get_source_provider_config(source_provider_type)['username']
                    repo_name = repo_spec
                
                repo = source_provider.get_repository_info(owner, repo_name)
                if repo:
                    repositories.append(repo)
                else:
                    print(f"{Fore.RED}⚠️  Repository {owner}/{repo_name} not found or not accessible{Style.RESET_ALL}")
            
            results = migration_engine.migrate_repositories(repositories)
        else:
            # Get all accessible repositories
            all_repos = source_provider.get_accessible_repositories()
            
            if args.no_interactive:
                print(f"{Fore.CYAN}🚀 Migrating all your repositories automatically...{Style.RESET_ALL}")
                # Filter to only user's repositories
                user_repos = source_provider.get_user_repositories()
                results = migration_engine.migrate_repositories(user_repos)
            else:
                print(f"{Fore.CYAN}🎯 Interactive mode - select repositories to migrate{Style.RESET_ALL}")
                username = config.get_source_provider_config(source_provider_type)['username']
                selected_repos = select_repositories_interactive(all_repos, username)
                results = migration_engine.migrate_repositories(selected_repos)
        
        # Print results
        if results:
            print_success_summary(results)
        else:
            print(f"{Fore.YELLOW}⚠️  No repositories found to migrate.{Style.RESET_ALL}")
            
    except ConfigurationError as e:
        print(f"{Fore.RED}❌ Configuration error: {e}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}💡 Run '{sys.argv[0]} --setup' to create a configuration template.{Style.RESET_ALL}")
        sys.exit(1)
        
    except (ProviderError, MigrationError) as e:
        print(f"{Fore.RED}❌ Migration error: {e}{Style.RESET_ALL}")
        sys.exit(1)
        
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        print(f"{Fore.RED}❌ An unexpected error occurred. Check migration.log for details.{Style.RESET_ALL}")
        sys.exit(1)

if __name__ == '__main__':
    main() 