"""
Provider selection interface
"""
from colorama import Fore, Style
from providers.factory import ProviderFactory
from core.config import MigrationConfig


def select_providers() -> tuple[str, str]:
    """
    Interactive provider selection for source and destination
    Returns tuple (source_provider, destination_provider)
    """
    config = MigrationConfig()
    
    # Get available providers from factory
    available_source_providers = ProviderFactory.get_available_source_providers()
    available_destination_providers = ProviderFactory.get_available_destination_providers()
    
    print(f"\n{Fore.CYAN}🔧 Provider Configuration{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Available providers by type:{Style.RESET_ALL}")
    print(f"  📥 Source: {', '.join(available_source_providers).upper()}")
    print(f"  📤 Destination: {', '.join(available_destination_providers).upper()}")
    
    # Check configured providers
    source_provider_configs = config.get_available_source_providers()
    dest_provider_configs = config.get_available_destination_providers()
    
    print(f"\n{Fore.YELLOW}Source provider configuration status:{Style.RESET_ALL}")
    configured_source_providers = []
    for provider, is_configured in source_provider_configs.items():
        if provider in available_source_providers:
            status = f"{Fore.GREEN}✅ Configured" if is_configured else f"{Fore.RED}❌ Not configured"
            print(f"  {provider.upper()}: {status}{Style.RESET_ALL}")
            if is_configured:
                configured_source_providers.append(provider)
    
    print(f"\n{Fore.YELLOW}Destination provider configuration status:{Style.RESET_ALL}")
    configured_destination_providers = []
    for provider, is_configured in dest_provider_configs.items():
        if provider in available_destination_providers:
            status = f"{Fore.GREEN}✅ Configured" if is_configured else f"{Fore.RED}❌ Not configured"
            print(f"  {provider.upper()}: {status}{Style.RESET_ALL}")
            if is_configured:
                configured_destination_providers.append(provider)
    
    # Validate we have at least one configured source and destination
    if not configured_source_providers:
        print(f"\n{Fore.RED}❌ No source providers configured!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}💡 Please configure at least one source provider in .env:{Style.RESET_ALL}")
        for provider in available_source_providers:
            if provider == 'gitea':
                print(f"   GITEA_SOURCE_URL, GITEA_SOURCE_TOKEN, GITEA_SOURCE_USERNAME")
            elif provider == 'gitlab':
                print(f"   GITLAB_SOURCE_URL, GITLAB_SOURCE_TOKEN, GITLAB_SOURCE_USERNAME")
            elif provider == 'github':
                print(f"   GITHUB_TOKEN, GITHUB_USERNAME")
        exit(1)
    
    if not configured_destination_providers:
        print(f"\n{Fore.RED}❌ No destination providers configured!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}💡 Please configure at least one destination provider in .env:{Style.RESET_ALL}")
        for provider in available_destination_providers:
            if provider == 'gitea':
                print(f"   GITEA_DEST_URL, GITEA_DEST_TOKEN, GITEA_DEST_USERNAME")
            elif provider == 'github':
                print(f"   GITHUB_TOKEN, GITHUB_USERNAME")
            elif provider == 'gitlab':
                print(f"   GITLAB_DEST_URL, GITLAB_DEST_TOKEN, GITLAB_DEST_USERNAME")
        exit(1)
    
    # Select source provider
    print(f"\n{Fore.CYAN}📥 Select SOURCE provider:{Style.RESET_ALL}")
    source_provider = _select_provider(configured_source_providers, "source")
    
    # Select destination provider (exclude GitHub → GitHub)
    available_destinations = configured_destination_providers.copy()
    if source_provider == 'github' and 'github' in available_destinations:
        available_destinations.remove('github')
        print(f"\n{Fore.YELLOW}ℹ️  GitHub → GitHub migration not supported (same instance){Style.RESET_ALL}")
    
    if not available_destinations:
        print(f"\n{Fore.RED}❌ No valid destination providers available!{Style.RESET_ALL}")
        if source_provider == 'github':
            print(f"{Fore.YELLOW}GitHub can only migrate TO other providers, not to itself.{Style.RESET_ALL}")
        exit(1)
    
    # Select destination provider
    print(f"\n{Fore.CYAN}📤 Select DESTINATION provider:{Style.RESET_ALL}")
    destination_provider = _select_provider(available_destinations, "destination")
    
    print(f"\n{Fore.GREEN}✅ Migration will be: {source_provider.upper()} → {destination_provider.upper()}{Style.RESET_ALL}")
    
    return source_provider, destination_provider


def _select_provider(providers: list, provider_type: str) -> str:
    """
    Select a provider from the available list
    """
    if len(providers) == 1:
        print(f"{Fore.GREEN}✅ Only one {provider_type} provider available: {providers[0].upper()}{Style.RESET_ALL}")
        return providers[0]
    
    while True:
        print(f"\n{Fore.YELLOW}Available {provider_type} providers:{Style.RESET_ALL}")
        for i, provider in enumerate(providers, 1):
            print(f"  {i}. {provider.upper()}")
        
        try:
            choice = input(f"\nEnter your choice (1-{len(providers)}): ").strip()
            
            if choice.isdigit():
                index = int(choice) - 1
                if 0 <= index < len(providers):
                    selected = providers[index]
                    print(f"{Fore.GREEN}✅ Selected {provider_type}: {selected.upper()}{Style.RESET_ALL}")
                    return selected
            
            print(f"{Fore.RED}❌ Invalid choice. Please enter a number between 1 and {len(providers)}.{Style.RESET_ALL}")
            
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}🛑 Migration cancelled.{Style.RESET_ALL}")
            exit(0)
        except EOFError:
            print(f"\n{Fore.YELLOW}🛑 Migration cancelled.{Style.RESET_ALL}")
            exit(0) 