"""
Interactive repository selector for migration tool
"""
import sys
import termios
import tty
from typing import List, Dict, Set
from colorama import Fore, Style, init

init()

class InteractiveSelector:
    """Interactive repository selector with keyboard navigation"""
    
    def __init__(self, repositories: List[Dict], username: str):
        self.username = username
        # Sort repositories: user's repos first, then others, both alphabetically
        self.repositories = self._sort_repositories(repositories, username)
        # Only select user's own repositories by default
        self.selected = set(i for i, repo in enumerate(self.repositories) 
                          if repo['owner']['login'] == username)
        self.current_index = 0
        self.page_size = 15  # Number of repos to show per page
        self.current_page = 0
        
    def get_key(self):
        """Get a single keypress from stdin"""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            key = sys.stdin.read(1)
            # Handle arrow keys and special keys
            if key == '\x1b':  # ESC sequence
                key += sys.stdin.read(2)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return key
    
    def display_page(self):
        """Display current page of repositories"""
        # Clear screen
        print('\033[2J\033[H', end='')
        
        # Header
        print(f"{Fore.CYAN}╔═══════════════════════════════════════════════════════════════╗")
        print(f"║                  📋 SELECT REPOSITORIES                      ║")
        print(f"║                                                               ║")
        print(f"║  👤 = Your repos (selected by default)  👥 = Others' repos   ║")
        print(f"║  ↑↓ navigate, SPACE toggle, A all, N none, ENTER confirm     ║")
        print(f"╚═══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
        print()
        
        # Calculate pagination
        start_idx = self.current_page * self.page_size
        end_idx = min(start_idx + self.page_size, len(self.repositories))
        
        # Show page info
        total_pages = (len(self.repositories) + self.page_size - 1) // self.page_size
        selected_count = len(self.selected)
        total_count = len(self.repositories)
        
        print(f"{Fore.YELLOW}📊 Page {self.current_page + 1}/{total_pages} | "
              f"Selected: {selected_count}/{total_count} repositories{Style.RESET_ALL}")
        print()
        
        # Display repositories for current page
        last_owner_type = None  # Track if we're switching from user repos to others
        
        for i in range(start_idx, end_idx):
            repo = self.repositories[i]
            is_selected = i in self.selected
            is_current = i == self.current_index
            
            # Check if we need to add a separator
            owner = repo['owner']['login']
            is_own_repo = owner == self.username
            current_owner_type = "own" if is_own_repo else "others"
            
            # Add separator when transitioning from own repos to others
            if last_owner_type == "own" and current_owner_type == "others":
                print(f"  {Fore.LIGHTBLACK_EX}{'─' * 50} Autres repositories {'─' * 10}{Style.RESET_ALL}")
            
            last_owner_type = current_owner_type
            
            # Checkbox
            checkbox = "☑️ " if is_selected else "☐ "
            
            # Repository info
            name = repo['name']
            private = "🔒" if repo.get('private', False) else "🌐"
            ownership_indicator = "👤" if is_own_repo else "👥"
            description = repo.get('description', 'No description')[:45]
            if len(repo.get('description', '')) > 45:
                description += "..."
            
            # Highlight current selection
            if is_current:
                line = f"{Fore.BLACK}{Style.BRIGHT}> {checkbox}{ownership_indicator} {Fore.BLUE}{owner}/{name}{Style.RESET_ALL}"
                line += f"{Fore.BLACK}{Style.BRIGHT} {private} - {description}{Style.RESET_ALL}"
            else:
                if is_own_repo:
                    color = Fore.GREEN if is_selected else Fore.WHITE
                else:
                    color = Fore.YELLOW if is_selected else Fore.LIGHTBLACK_EX
                line = f"  {checkbox}{ownership_indicator} {color}{owner}/{name}{Style.RESET_ALL}"
                line += f" {private} - {Fore.LIGHTBLACK_EX}{description}{Style.RESET_ALL}"
            
            print(line)
        
        # Navigation help at bottom
        print()
        nav_help = []
        if self.current_page > 0:
            nav_help.append("← PREV PAGE")
        if self.current_page < total_pages - 1:
            nav_help.append("→ NEXT PAGE")
        
        if nav_help:
            print(f"{Fore.CYAN}Navigation: {' | '.join(nav_help)}{Style.RESET_ALL}")
        
        print(f"\n{Fore.GREEN}Press ENTER to continue with selected repositories{Style.RESET_ALL}")
        print(f"{Fore.RED}Press Q to quit{Style.RESET_ALL}")
    
    def move_up(self):
        """Move selection up"""
        if self.current_index > 0:
            self.current_index -= 1
            # Check if we need to go to previous page
            if self.current_index < self.current_page * self.page_size:
                self.current_page = max(0, self.current_page - 1)
    
    def move_down(self):
        """Move selection down"""
        if self.current_index < len(self.repositories) - 1:
            self.current_index += 1
            # Check if we need to go to next page
            total_pages = (len(self.repositories) + self.page_size - 1) // self.page_size
            if self.current_index >= (self.current_page + 1) * self.page_size:
                self.current_page = min(total_pages - 1, self.current_page + 1)
    
    def toggle_current(self):
        """Toggle selection of current repository"""
        if self.current_index in self.selected:
            self.selected.remove(self.current_index)
        else:
            self.selected.add(self.current_index)
    
    def select_all(self):
        """Select all repositories"""
        self.selected = set(range(len(self.repositories)))
    
    def select_none(self):
        """Deselect all repositories"""
        self.selected.clear()
    
    def prev_page(self):
        """Go to previous page"""
        if self.current_page > 0:
            self.current_page -= 1
            self.current_index = self.current_page * self.page_size
    
    def next_page(self):
        """Go to next page"""
        total_pages = (len(self.repositories) + self.page_size - 1) // self.page_size
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self.current_index = self.current_page * self.page_size
    
    def _rename_repositories_interface(self, selected_repos: List[Dict]) -> List[Dict]:
        """Interface for renaming selected repositories"""
        print('\033[2J\033[H', end='')  # Clear screen
        
        print(f"{Fore.CYAN}╔═══════════════════════════════════════════════════════════════╗")
        print(f"║                  ✏️  RENAME REPOSITORIES                     ║")
        print(f"║                                                               ║")
        print(f"║  Press ENTER to keep current name, or type new name          ║")
        print(f"║  Repository names should be valid GitHub repo names          ║")
        print(f"╚═══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
        print()
        
        renamed_repos = []
        
        for i, repo in enumerate(selected_repos, 1):
            owner = repo['owner']['login']
            original_name = repo['name']
            private = "🔒" if repo.get('private', False) else "🌐"
            
            print(f"{Fore.YELLOW}📦 Repository {i}/{len(selected_repos)}:{Style.RESET_ALL}")
            print(f"   Source: {Fore.BLUE}{owner}/{original_name}{Style.RESET_ALL} {private}")
            
            # Get new name from user
            new_name = input(f"   GitHub name [{Fore.GREEN}{original_name}{Style.RESET_ALL}]: ").strip()
            
            # Validate and use new name
            if new_name:
                # Basic validation
                if not self._is_valid_repo_name(new_name):
                    print(f"   {Fore.RED}⚠️  Invalid repository name. Using original name: {original_name}{Style.RESET_ALL}")
                    new_name = original_name
                else:
                    print(f"   {Fore.GREEN}✅ Will rename to: {new_name}{Style.RESET_ALL}")
            else:
                new_name = original_name
                print(f"   {Fore.CYAN}ℹ️  Keeping original name: {original_name}{Style.RESET_ALL}")
            
            # Create new repo dict with updated name
            renamed_repo = repo.copy()
            renamed_repo['github_name'] = new_name  # Add field for GitHub name
            renamed_repos.append(renamed_repo)
            print()
        
        # Summary
        print(f"{Fore.GREEN}✅ Repository renaming complete!{Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}📋 Migration summary:{Style.RESET_ALL}")
        
        for repo in renamed_repos:
            owner = repo['owner']['login']
            original_name = repo['name']
            github_name = repo['github_name']
            private = "🔒" if repo.get('private', False) else "🌐"
            
            if original_name != github_name:
                print(f"  • {Fore.BLUE}{owner}/{original_name}{Style.RESET_ALL} → {Fore.GREEN}{github_name}{Style.RESET_ALL} {private}")
            else:
                print(f"  • {Fore.BLUE}{owner}/{original_name}{Style.RESET_ALL} {private}")
        
        input(f"\n{Fore.YELLOW}Press ENTER to continue...{Style.RESET_ALL}")
        return renamed_repos
    
    def _sort_repositories(self, repositories: List[Dict], username: str) -> List[Dict]:
        """Sort repositories: user's repos first, then others, both alphabetically"""
        def sort_key(repo):
            owner = repo['owner']['login']
            name = repo['name'].lower()  # Case-insensitive sorting
            is_user_repo = owner == username
            
            # Return tuple: (is_not_user_repo, owner.lower(), name)
            # This will sort user repos first (False < True), then alphabetically
            return (not is_user_repo, owner.lower(), name)
        
        return sorted(repositories, key=sort_key)
    
    def _is_valid_repo_name(self, name: str) -> bool:
        """Validate GitHub repository name"""
        if not name:
            return False
        
        # GitHub repo name rules (simplified)
        if len(name) > 100:
            return False
        
        # Should not start or end with special characters
        if name.startswith('.') or name.startswith('-') or name.endswith('.'):
            return False
        
        # Should contain only alphanumeric, hyphens, underscores, and dots
        import re
        return bool(re.match(r'^[a-zA-Z0-9._-]+$', name))
    
    def run(self) -> List[Dict]:
        """Run interactive selection and return selected repositories"""
        if not self.repositories:
            print(f"{Fore.YELLOW}⚠️  No repositories found.{Style.RESET_ALL}")
            return []
        
        try:
            while True:
                self.display_page()
                key = self.get_key()
                
                if key == '\x1b[A':  # Up arrow
                    self.move_up()
                elif key == '\x1b[B':  # Down arrow
                    self.move_down()
                elif key == '\x1b[D':  # Left arrow (previous page)
                    self.prev_page()
                elif key == '\x1b[C':  # Right arrow (next page)
                    self.next_page()
                elif key == ' ':  # Space - toggle selection
                    self.toggle_current()
                elif key.lower() == 'a':  # Select all
                    self.select_all()
                elif key.lower() == 'n':  # Select none
                    self.select_none()
                elif key == '\r' or key == '\n':  # Enter - confirm
                    break
                elif key.lower() == 'q':  # Quit
                    print(f"\n{Fore.YELLOW}🚪 Migration cancelled by user.{Style.RESET_ALL}")
                    sys.exit(0)
        
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}🚪 Migration cancelled by user.{Style.RESET_ALL}")
            sys.exit(0)
        
        # Return selected repositories
        selected_repos = [self.repositories[i] for i in sorted(self.selected)]
        
        # Clear screen and show summary
        print('\033[2J\033[H', end='')
        print(f"{Fore.GREEN}✅ Selected {len(selected_repos)} repositories for migration:{Style.RESET_ALL}\n")
        
        for repo in selected_repos:
            owner = repo['owner']['login']
            name = repo['name']
            private = "🔒" if repo.get('private', False) else "🌐"
            print(f"  • {Fore.BLUE}{owner}/{name}{Style.RESET_ALL} {private}")
        
        # Ask if user wants to rename repositories
        print(f"\n{Fore.YELLOW}📝 Voulez-vous changer le nom de certains repos sur GitHub ?{Style.RESET_ALL}")
        print(f"{Fore.CYAN}[Y/y] Oui - Interface de renommage{Style.RESET_ALL}")
        print(f"{Fore.CYAN}[N/n ou ENTER] Non - Conserver les noms actuels{Style.RESET_ALL}")
        
        choice = input(f"\n{Fore.YELLOW}Votre choix: {Style.RESET_ALL}").strip().lower()
        
        if choice == 'y' or choice == 'yes' or choice == 'oui':
            selected_repos = self._rename_repositories_interface(selected_repos)
        
        print(f"\n{Fore.CYAN}🚀 Starting migration...{Style.RESET_ALL}\n")
        
        return selected_repos


def select_repositories_interactive(repositories: List[Dict], username: str) -> List[Dict]:
    """
    Interactive repository selection interface
    
    Args:
        repositories: List of repository dictionaries from Gitea API
        username: Current user's username to distinguish own repos
        
    Returns:
        List of selected repositories
    """
    selector = InteractiveSelector(repositories, username)
    return selector.run() 