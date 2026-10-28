# aBot
**Telegram bot/userbot framework**

This repo contains the root for abot:
* `core` plugin
* utils
* config file
* folders

### Features
* a centralized config file
* a command parsing system (UNIX-like) to implement sophisticated commands
* an help command which automatically extracts docstrings
* a 2 role permission system (user/root)
* a wrapper around SQLite db, for easy storage of persistent data
* some common commands (/update, /ping, /info)
* events for bot startup/shutdown
* some utility functions to handle most common tasks
* a plugin manager (with git submodules), allowing plugins to access all above features

aBot simplifies my bot development, by providing a standardized and solid baseline, with common features to all projects, which can focus on their specific functionalities.

# Some plugins
* `https://git.alemi.dev/abot/debugtool.git` very useful tools for debugging and interacting with server
* `https://git.alemi.dev/abot/tricks.git` my biggest collection of "trick command": fancy stuff to show off
* `https://git.alemi.dev/abot/moderation.git` a powerful purge command, to precisely delete messages, plus a small censor utility
* `https://git.alemi.dev/abot/statsbot.git` a powerful tracker bot to log your group stats or provide fun insights
* ... more to come, send me your plugins!

## Making custom plugins
To develop your own plugins for aBot, you should clone first this repository and work in a folder in the `plugins` directory.
Each plugin must be a repository itself which can be installed in the `plugins` folder as a submodule.

**One "catch":** your plugin should import its files as `import plugins.<yourplugin>.<...>`. This means that if you need to have custom classes, you cannot have dashes (`-`) in your plugin name. Thinking about solutions... On the flip side, you can always access utils.

---

## Installation & Deployment

You just need Python 3.11+ and a machine always on. It is strongly recommended to install on Linux / UNIX. If using Windows, [installing inside WSL](https://docs.microsoft.com/en-us/windows/wsl/install-win10) is recommended.

### Standard Setup (Virtualenv)

1. **Clone this repository**:
   ```bash
   git clone https://github.com/alemidev/abot.git abot
   cd abot
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install `abot`**:
   ```bash
   pip install .
   ```
   *(To install development and testing dependencies, use `pip install ".[dev]"`)*.

4. **Configure your instance**:
   Copy `default.ini` to a custom name (e.g. `my-bot.ini`):
   ```bash
   cp default.ini my-bot.ini
   ```
   Edit `my-bot.ini` and fill in your `api_id` and `api_hash` (obtain them from [my.telegram.org](https://my.telegram.org/)).

5. **Launch**:
   ```bash
   abot my-bot
   ```
   *(Alternatively: `python -m abot my-bot`)*.  
   On first launch in userbot mode, Telegram will request your phone number and verification code.

### Docker Deployment

You can also run `aBot` as a container:

1. **Build the image**:
   ```bash
   docker build -t abot .
   ```

2. **Run container**:
   ```bash
   docker run -d \
     --name abot \
     --restart unless-stopped \
     -v $(pwd)/data:/app/data \
     -v $(pwd)/log:/app/log \
     -v $(pwd)/my-bot.ini:/app/my-bot.ini \
     -e NAME="my-bot" \
     abot
   ```

---

## Configuration

Configuration is managed via INI files. The base template is `default.ini`:

```ini
[wzgram]                              # or [pyrogram]
api_id = 123456                       # Your Telegram API ID (from https://my.telegram.org/)
api_hash = 0123456789abcdef0123456789 # Your Telegram API Hash
# bot_token = 123456:ABC...           # Optional: uncomment if running as a Bot instead of Userbot

[perms]
sudo = 12345678                       # User IDs allowed to use owner commands (/update, /install). Separate with space
public = False                        # If True, non-sudo commands (/help, /ping) are available to everyone
allowPlugins = True                   # Allow superusers to install plugins dynamically

[customization]
prefixes = .!                         # Command prefixes (e.g. .ping or !ping)
useSsh = False                        # Use SSH instead of HTTPS to clone plugins
desc = A bot made with aBot           # Description displayed in /help

[plugins]
root = plugins                        # Plugins directory (default: plugins)
```

Multiple independent bot instances can run from a single installation: create distinct config files (e.g. `work.ini`, `personal.ini`) and launch them with `abot <config-name>`.

### CLI Options

The `abot` command line interface accepts several options:
```text
usage: abot [-h] [--config PATH] [--api-id API_ID] [--api-hash API_HASH]
            [--session STRING] [--install PLUGIN [PLUGIN ...]]
            [--prefix PREFIXES] [--sudo UID [UID ...]] [--allow-plugins]
            [--no-color] [--debug]
            name
```

### Running Tests

Run the unit test suite with:
```bash
pytest
```

# Security
For a comprehensive security assessment, threat model, and remediation report, see [SECURITY_AUDIT.md](SECURITY_AUDIT.md).

# Contacts
on [my site](https://alemi.dev) or [mail me](mailto:me@alemi.dev)
