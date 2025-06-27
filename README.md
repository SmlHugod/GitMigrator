# 🚀 Multi-Provider Git Migration Tool

This project provides a practical and modular tool to automatically migrate your repositories between different Git providers.

## ✨ Features

- **Multi-provider migration**: Supports multiple source and destination providers
- **Supported providers**:
  - **Sources**: Gitea, GitLab
  - **Destinations**: GitHub, GitLab
- **Interactive mode by default**: Elegant interface to select/deselect repositories to migrate
- **Complete vision**: See all accessible repositories (your repos + those from organizations)
- **Smart selection**: Your repositories are pre-selected, others are deselected by default
- **Smart renaming**: Ability to rename repositories during migration
- **Selective migration**: Choose specifically which repositories to migrate via command line
- **Command line interface**: Colorful and intuitive interface with keyboard navigation
- **Complete logging**: Detailed operation tracking with log file
- **Error handling**: Robust with graceful error management
- **Extensible architecture**: Easily extensible to add new providers

## 🛠 Installation

1. **Clone the repository**:
```bash
git clone https://github.com/your-username/GitMigrator.git
cd GitMigrator
```

2. **Automatic configuration**:
```bash
./run.sh --setup
```

The script will automatically:
- Create a Python virtual environment
- Install all dependencies
- Create the `.env` configuration file

This will create a `.env` file that you will need to fill with your information according to the chosen providers.

## 🔧 Configuration

### Configuration with multi-instance support
```env
# Gitea Source Configuration
GITEA_SOURCE_URL=https://your-gitea-source-instance.com
GITEA_SOURCE_TOKEN=your_gitea_source_token
GITEA_SOURCE_USERNAME=your_gitea_source_username

# Gitea Destination Configuration  
GITEA_DEST_URL=https://your-gitea-dest-instance.com
GITEA_DEST_TOKEN=your_gitea_dest_token
GITEA_DEST_USERNAME=your_gitea_dest_username

# GitLab Source Configuration
GITLAB_SOURCE_URL=https://gitlab-source.com
GITLAB_SOURCE_TOKEN=your_gitlab_source_token
GITLAB_SOURCE_USERNAME=your_gitlab_source_username

# GitLab Destination Configuration
GITLAB_DEST_URL=https://gitlab-dest.com
GITLAB_DEST_TOKEN=your_gitlab_dest_token
GITLAB_DEST_USERNAME=your_gitlab_dest_username

# GitHub Configuration (same for source and destination - only one instance)
GITHUB_TOKEN=your_github_token
GITHUB_USERNAME=your_github_username
```

**📝 Instructions:**
1. **Multi-instances**: You can configure different instances of the same provider
2. **Same instance**: Use the same credentials for source and destination if it's the same instance
3. **Flexible migration**: Supports GitLab → GitLab, Gitea → Gitea, etc. between different instances
4. **Minimal configuration**: Configure only the source/destination providers that you use
5. The tool will interactively ask which provider to use as source and destination

## 🔑 Token Configuration

### Gitea Token
1. Go to **Settings** → **Applications** → **Generate New Token**
2. Give the token a name and select permissions:
   - `repo` (full access to repositories)
   - `user` (access to user information)

### GitLab Token
1. Go to **Settings** → **Access Tokens** or **User Settings** → **Access Tokens**
2. Create a **Personal Access Token** with permissions:
   - `read_api` (read API information)
   - `read_repository` (read repositories)
   - `write_repository` (write repositories - for destination)

### GitHub Token
1. Go to **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
2. Click on **Generate new token (classic)**
3. Select permissions:
   - `repo` (full access to private repositories)
   - `public_repo` (access to public repositories)

## 🚀 Usage

After configuring your tokens in the `.env` file, use the launch script:

### Interactive migration (default)
```bash
./run.sh
```

### Automatic migration of all your repos
```bash
./run.sh --no-interactive
```

### Migration of specific repositories
```bash
./run.sh --repos my-repo another-repo
```

### List available repositories
```bash
./run.sh --list
```

### Verbose mode (more details)
```bash
./run.sh --verbose
```

> **💡 Alternative**: You can also use `python main.py` directly if you have activated the virtual environment (`source venv/bin/activate`)

## 🎯 Interactive Mode

Interactive mode (enabled by default) offers an **elegant user interface** to precisely select which repositories to migrate:

```bash
./run.sh  # Interactive mode by default
```

### Controls in the interactive interface:
- **↑↓**: Navigate between repositories
- **←→**: Change page (if many repos)
- **SPACE**: Check/uncheck a repository
- **A**: Select all repositories
- **N**: Deselect all repositories
- **ENTER**: Confirm selection and proceed to renaming (optional)
- **Q**: Quit without migrating

### Renaming interface:
After selection, the tool offers to rename repositories:
- **Y**: Open renaming interface
- **N/ENTER**: Keep current names
- **Automatic validation** of repository names for the destination provider

### Features:
- ✅ **Visual checkboxes** with emojis
- 👤 **Owner distinction**: Your repos vs other users' repos
- 🎯 **Smart selection**: Your repos pre-selected by default
- 📋 **Smart sorting**: Your repos first, then others, all alphabetically ordered
- ✏️ **Optional renaming**: Ability to rename repos on the destination provider
- 📄 **Automatic pagination** (15 repos per page)
- 🎨 **Colorful interface** with highlighting and visual separators
- 📊 **Real-time counter** of selected repos
- 🔒 **Visual indicators** (private/public)
- 📝 **Truncated descriptions** for clean display

## 📋 Usage Examples

### Example 1: Interactive migration (default)
```bash
# 1. Configure your providers in .env
# 2. Launch the tool
./run.sh

# The tool will ask you:
# - Which provider to use as source
# - Which provider to use as destination
# - Then you can select repos to migrate
```

### Example 2: Automatic migration
```bash
# Migrate all your repositories automatically
# (after interactive provider selection)
./run.sh --no-interactive
```

### Example 3: Selective migration
```bash
# Migrate only specified repositories
# (after interactive provider selection)
./run.sh --repos web-project api-backend
```

### Example 4: Migration from an organization
```bash
# Migrate a repository from an organization (works with all providers)
./run.sh --repos my-org/important-project
```

### Example 5: First launch (configuration)
```bash
# 1. Initial setup - creates .env template file
./run.sh --setup

# 2. Edit the .env file with your credentials (at least 2 providers)
nano .env

# 3. Launch the tool - it will ask which providers to use
./run.sh

# 4. To list available repos (after source provider selection)
./run.sh --list
```

### Example 6: Migration with renaming
```bash
# 1. Launch interactive mode
./run.sh

# 2. Select source and destination providers
# 3. Select repos to migrate
# 4. Choose "Y" for renaming
# 5. Rename repos one by one
#    - Press ENTER to keep original name
#    - Type new name to rename
# 6. Confirm and start migration
```

## 📊 Results

The tool displays a detailed summary at the end:
- ✅ Number of successful migrations
- ❌ Number of failed migrations
- 📝 Detail per repository

All logs are also saved in `migration.log`.

## 🔧 Project Structure

```
GitMigrator/
├── main.py                     # Main script
├── core/                       # Core business logic
│   ├── config.py              # Multi-provider configuration management
│   └── migration_engine.py    # Migration engine
├── providers/                  # Providers for different Git services
│   ├── base.py                # Abstract classes and models
│   ├── factory.py             # Factory to create providers
│   ├── source/                # Source providers
│   │   ├── gitea.py          # Gitea support
│   │   └── gitlab.py         # GitLab support
│   └── destination/           # Destination providers
│       ├── github.py         # GitHub support
│       └── gitlab.py         # GitLab support
├── ui/                        # User interface
│   └── interactive_selector.py
├── requirements.txt           # Python dependencies
├── .env                      # Configuration (to create)
└── README.md                 # Documentation
```

## 🌟 Supported Providers

### Source Providers
- **Gitea**: Gitea instances (self-hosted or cloud)
- **GitLab**: GitLab.com or self-hosted GitLab instances

### Destination Providers
- **GitHub**: GitHub.com
- **GitLab**: GitLab.com or self-hosted GitLab instances

### Possible Combinations
- Gitea → GitHub
- Gitea → GitLab
- GitLab → GitHub
- GitLab → GitLab (migration between instances)

## ⚠️ Prerequisites

- Python 3.7+
- Git installed on your system
- Access to source and destination provider APIs
- Valid authentication tokens for providers

## 🛡 Security

- Tokens are stored in a `.env` file (add it to `.gitignore`)
- Authentication URLs are never logged
- Automatic cleanup of temporary repositories

## 🐛 Troubleshooting

### Authentication error
- Check that your tokens are valid and have the right permissions
- Make sure usernames match
- Verify that provider URLs are correct

### Clone error
- Check your internet connection
- Make sure Git is installed and accessible

### Repository already exists
- The tool automatically checks existence on the destination provider
- Existing repositories are ignored with a warning

### Unsupported or unconfigured provider
- Check that your providers are properly configured in the .env file
- Make sure you have at least 2 providers configured
- Available providers: gitea, gitlab, github
- The tool will indicate which providers are configured at startup

## 📝 Logs

All execution details are saved in `migration.log`:
- Operation timestamps
- Source and destination provider selection
- Error details
- Migration statistics
- Complete information about the migration process

## 🚀 Extensibility

The modular architecture allows easy addition of new providers:

1. **Create a new source provider** in `providers/source/`
2. **Create a new destination provider** in `providers/destination/`
3. **Register the provider** in `providers/factory.py`
4. **Add configuration** in `core/config.py`

See `ARCHITECTURE.md` for more details on adding new providers.

## 🤝 Contribution

Contributions are welcome! Feel free to:
- Report bugs
- Suggest improvements
- Submit pull requests
- Add new providers

## 📄 License

This project is under MIT license. See the LICENSE file for more details.