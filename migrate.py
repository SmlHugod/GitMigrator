#!/usr/bin/env python3
"""
Gitea to GitHub Migration Tool

This script migrates repositories from Gitea to GitHub.
It can migrate all user repositories or specific ones.
"""

import argparse
import logging
import sys
from colorama import init, Fore, Style
from pathlib import Path

from config import Config
from migration_tool import MigrationTool

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
    banner = f"""
{Fore.CYAN}╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║            🚀 Gitea to GitHub Migration Tool 🚀              ║
║                                                               ║
║  Migrates your repositories from Gitea to GitHub seamlessly  ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(banner)

def print_success_summary(results: dict):
    """Print migration results summary"""
    successful = sum(1 for success in results.values() if success)
    total = len(results)
    
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
        template = """# Gitea Configuration
GITEA_URL=https://your-gitea-instance.com
GITEA_TOKEN=your_gitea_personal_access_token
GITEA_USERNAME=your_gitea_username

# GitHub Configuration
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_USERNAME=your_github_username
"""
        env_file.write_text(template)
        print(f"{Fore.YELLOW}📝 Created .env template file. Please fill it with your credentials.{Style.RESET_ALL}")
        return False
    
    return True

def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(
        description="Migrate repositories from Gitea to GitHub",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Migrate all your repositories
  %(prog)s --repos repo1 repo2       # Migrate specific repositories
  %(prog)s --repos owner/repo1       # Migrate repositories from other owners
  %(prog)s --list                    # List available repositories
  %(prog)s --verbose                 # Enable verbose logging
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
        config = Config()
        
        # Initialize migration tool
        migration_tool = MigrationTool(config)
        
        # Handle list command
        if args.list:
            print(f"{Fore.CYAN}📋 Available repositories:{Style.RESET_ALL}")
            repos = migration_tool.list_available_repos()
            
            for repo in repos:
                owner = repo['owner']['login']
                name = repo['name']
                private = "🔒 Private" if repo.get('private', False) else "🌐 Public"
                description = repo.get('description', 'No description')
                
                print(f"  {Fore.BLUE}{owner}/{name}{Style.RESET_ALL} - {private}")
                if description:
                    print(f"    📝 {description}")
            
            print(f"\n{Fore.GREEN}Total repositories: {len(repos)}{Style.RESET_ALL}")
            return
        
        # Perform migration
        if args.repos:
            print(f"{Fore.CYAN}🎯 Migrating specific repositories: {', '.join(args.repos)}{Style.RESET_ALL}")
            results = migration_tool.migrate_specific_repos(args.repos)
        else:
            print(f"{Fore.CYAN}🚀 Migrating all your repositories...{Style.RESET_ALL}")
            results = migration_tool.migrate_all_user_repos()
        
        # Print results
        if results:
            print_success_summary(results)
        else:
            print(f"{Fore.YELLOW}⚠️  No repositories found to migrate.{Style.RESET_ALL}")
            
    except ValueError as e:
        print(f"{Fore.RED}❌ Configuration error: {e}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}💡 Run '{sys.argv[0]} --setup' to create a configuration template.{Style.RESET_ALL}")
        sys.exit(1)
        
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        print(f"{Fore.RED}❌ An unexpected error occurred. Check migration.log for details.{Style.RESET_ALL}")
        sys.exit(1)

if __name__ == '__main__':
    main() 