# aBot Security Audit & Hardening Report

**Audit Date:** October 28, 2026  
**Target:** `aBot` Telegram Bot / Userbot Framework ([GitHub Repository](https://github.com/GabryDX/abot))  
**Target Branch:** `dev`  
**Engine:** `wzgram>=1.0.0` (MTProto with Rust-backed `warpcrypto`)  
**Python Support:** `>=3.11` (Python 3.11, 3.12, 3.13)  
**Status:** All Identified Implementation Vulnerabilities Remediated & Verified  

---

## 1. Executive Summary

A comprehensive security audit of `aBot` was conducted covering the core framework (`src/abot/`), utilities, patch layers, core plugins (`plugins/core.py`), deployment configuration (`Dockerfile`, `default.ini`), and CI/CD pipelines.

The audit analyzed attack vectors including path traversal, Git CLI argument injection, process table data exposure, file permission weaknesses on Telegram session databases, exception log data leakage, and dispatcher stability. All identified implementation vulnerabilities have been systematically remediated and verified through automated test suites in continuous integration.

### Vulnerability & Remediation Status Matrix

| ID | Category | Title | Severity | Status | Remediation Commit |
|:---|:---|:---|:---:|:---:|:---:|
| **SEC-01** | Path Traversal | Directory traversal via `-d` and `remove_plugin` | **High** | **Resolved** | [`097ca79`](https://github.com/GabryDX/abot/commit/097ca79), [`868a201`](https://github.com/GabryDX/abot/commit/868a201) |
| **SEC-02** | Command Injection | Git submodule CLI option / flag injection | **Medium** | **Resolved** | [`9356ff0`](https://github.com/GabryDX/abot/commit/9356ff0) |
| **SEC-03** | Supply Chain / RCE | Code execution via dynamic third-party submodules | **High** | **Architectural** | Design Constraint / Admin Scoped |
| **SEC-04** | Auth Theft | Insecure default umask on `.session` databases | **Medium** | **Resolved** | [`fd91726`](https://github.com/GabryDX/abot/commit/fd91726) |
| **SEC-05** | Credential Leak | Plaintext session string visible in `/proc/<pid>/cmdline` | **Medium** | **Resolved** | [`5c8b925`](https://github.com/GabryDX/abot/commit/5c8b925) |
| **SEC-06** | Auth Confusion | Sudo ambiguity with channel `sender_chat` IDs | **Low** | **Documented** | Admin Best Practice |
| **SEC-07** | Information Leak | Plaintext HTTP credentials stored in `.gitmodules` | **Low** | **Resolved** | [`5c8b925`](https://github.com/GabryDX/abot/commit/5c8b925) |
| **SEC-08** | Information Leak | Sensitive command inputs dumped to exception logs | **Low** | **Resolved** | [`fc573e7`](https://github.com/GabryDX/abot/commit/fc573e7) |

---

## 2. Threat Model & Trust Boundaries

```mermaid
flowchart TD
    subgraph Telegram Cloud
        TG[Telegram MTProto Server]
    end

    subgraph User Roles
        PublicUser["Public / Untrusted Users"]
        SudoUser["Sudoers / Bot Owner (Privileged)"]
    end

    subgraph aBot Process Boundary
        Filter["Pyrogram Filter & Authenticator"]
        Core["Core Dispatcher & Plugins"]
        Storage["aiosqlite Session & Doc Storage (0600)"]
        Git["Subprocess: git / pip (-- options separator)"]
    end

    subgraph Host System
        Disk["Restricted Filesystem (umask 077, data/ 0700)"]
        Env["Host Environment / Container (UID 1000)"]
    end

    PublicUser -->|Public Commands: /help, /ping| TG
    SudoUser -->|Admin Commands: /install, /update| TG
    TG -->|Encrypted MTProto| Filter
    Filter -->|is_allowed| Core
    Core --> Storage
    Core -->|Install / Uninstall| Git
    Storage --> Disk
    Git --> Disk
    Git --> Env
```

### Trust Zones
1. **Public Telegram Users (Untrusted)**:
   - Evaluated by `is_allowed`. When `public = True`, non-sudo commands (e.g. `.help`, `.ping`) are accessible.
   - All administrative, process management, and submodule commands are strictly gated behind `sudo`.
2. **Sudoers (Privileged Administrators)**:
   - Evaluated by `sudo` (`update.from_user.is_self` or `id in client.sudoers`).
   - Sudoers possess execution authority over plugin installation, process restarting, and bot updates.
3. **Plugin Supply Chain (External / Untrusted)**:
   - External Git repositories cloned into `plugins/`.
   - Plugin dependencies installed via `pip install -r requirements.txt`.

---

## 3. Detailed Audit Findings & Implemented Fixes

### [SEC-01] Path Traversal in Plugin Directory Parameter & Cleanup
* **Severity:** High
* **Affected Areas:** [`plugins/core.py`](plugins/core.py), [`src/abot/util/plugins.py`](src/abot/util/plugins.py)
* **Risk:**
  - In `plugin_add_cmd`, the custom destination directory option (`-d` / `--dir`) was passed to `f"plugins/{folder}"` without boundary checking, allowing submodules to be checked out outside the `plugins/` directory.
  - In `remove_plugin`, passing a path containing `..` could cause `shutil.rmtree` to target `.git/modules` or parent project directories.
* **Remediation Implemented:**
  - Added strict regex validation `^[a-zA-Z0-9_.-]+$` on all folder and plugin names in `plugins/core.py`.
  - Added filesystem boundary enforcement via `Path(path).resolve().relative_to(plugins_root)` in `install_plugin`.
  - Added pre-normalization checks rejecting any input containing `..` across `remove_plugin`, `install_dependancies`, and `remove_dependancies`.
  - Verified with automated tests in [`tests/test_plugins.py`](tests/test_plugins.py).

---

### [SEC-02] Git CLI Option Injection in Submodule Operations
* **Severity:** Medium
* **Affected Areas:** [`src/abot/util/plugins.py`](src/abot/util/plugins.py)
* **Risk:**
  - Branch names or plugin URLs beginning with `-` (e.g., `--upload-pack`, `--config`) were passed directly to `git submodule add` and `git ls-remote`, potentially causing Git to interpret user input as command-line options.
* **Remediation Implemented:**
  - Added rejection logic for any branch or plugin input beginning with a dash (`-`).
  - Inserted the standard `--` argument delimiter before positional repository arguments in `git submodule add` and `git ls-remote`.
  - Verified with automated tests in [`tests/test_plugins.py`](tests/test_plugins.py).

---

### [SEC-03] Arbitrary Code Execution via Untrusted Submodules
* **Severity:** High (Architectural)
* **Affected Areas:** Dynamic plugin loading mechanism
* **Risk:**
  - Installing a plugin clones an external Git repository and executes `pip install -r requirements.txt`, followed by importing the Python package on restart (`os.execv`). A compromised repository could execute arbitrary code within the bot's process context.
* **Remediation & Mitigation:**
  - The feature is disabled by default (`allowPlugins = False` in config).
  - Restricted strictly to `sudo` users.
  - Recommended running within an unprivileged container with drop-all capabilities and read-only root filesystem.

---

### [SEC-04] Insecure Default File Permissions on Session Storage
* **Severity:** Medium
* **Affected Areas:** [`src/abot/__main__.py`](src/abot/__main__.py), [`src/abot/patches/storage.py`](src/abot/patches/storage.py), [`src/abot/util/permission.py`](src/abot/util/permission.py)
* **Risk:**
  - Telegram MTProto session files (`data/<name>.session`) store 2048-bit AES authorization keys in plaintext SQLite databases. Under standard Linux umasks (`0022`), session databases were created world-readable (`0644`), permitting any local user on the host to copy the auth key and achieve full Telegram account takeover.
* **Remediation Implemented:**
  - Enforced `os.umask(0o077)` at the CLI entrypoint in `src/abot/__main__.py`.
  - Set `0o700` directory permissions on `data/`.
  - Added `_lock_permissions()` in `DocumentFileStorage` ensuring the `.session` database file is chmodded to `0o600`.
  - Enforced `0o600` permissions upon saving `perms.json` in `JsonDriver.serialize()`.

---

### [SEC-05] Plaintext Credential Exposure via Process Table
* **Severity:** Medium
* **Affected Areas:** [`src/abot/__main__.py`](src/abot/__main__.py)
* **Risk:**
  - Providing credentials via `--session="..."` command-line argument exposed the plaintext Telegram auth token in `/proc/<pid>/cmdline` and `ps aux` to all users on the host system.
* **Remediation Implemented:**
  - Added native support for reading the session string from the `SESSION_STRING` environment variable.
  - Added an explicit security warning when `--session` is passed on the command line.

---

### [SEC-06] Sudo Ambiguity with Channel IDs
* **Severity:** Low
* **Affected Areas:** [`src/abot/util/permission.py`](src/abot/util/permission.py)
* **Risk:**
  - The `sudo` filter checks `update.sender_chat.id in client.sudoers`. If a channel ID is added to `sudoers`, anyone authorized to post on behalf of that channel inherits `sudo` execution privileges.
* **Operational Guidance:**
  - `sudoers` should only contain user IDs (positive integers), never channel or group IDs, unless all channel publishers are trusted system administrators.

---

### [SEC-07] Plaintext Git Token Exposure in `.gitmodules`
* **Severity:** Low
* **Affected Areas:** [`src/abot/util/plugins.py`](src/abot/util/plugins.py)
* **Risk:**
  - Supplying URLs in `https://username:password@github.com/...` format caused Git to write HTTP Basic Auth credentials in plaintext to the tracked `.gitmodules` file.
* **Remediation Implemented:**
  - Implemented automatic stripping of embedded HTTP credentials in `normalize_plugin_url` (`re.sub(r"^(https?://)[^/@]+@", r"\1", input_str)`).
  - Verified with automated tests in [`tests/test_plugins.py`](tests/test_plugins.py).

---

### [SEC-08] Sensitive Data Exposure in Exception Logging
* **Severity:** Low
* **Affected Areas:** [`src/abot/util/decorators.py`](src/abot/util/decorators.py)
* **Risk:**
  - The `report_error` decorator wrote raw incoming message text to `data/<name>.log` upon unhandled exceptions. If a command failed while handling sensitive inputs (passwords, tokens), the credentials were saved to disk.
* **Remediation Implemented:**
  - Added `_sanitize_msg_for_log()`, collapsing whitespace and truncating message inputs to a safe maximum length of 80 characters.

---

## 4. Production Hardening Guide

### Recommended Docker Deployment

To achieve defense-in-depth, run the containerized bot with maximum isolation:

```bash
docker run -d \
  --name abot \
  --restart unless-stopped \
  --read-only \
  --cap-drop=ALL \
  --security-opt=no-new-privileges \
  --user 1000:1000 \
  -e SESSION_STRING="<your_session_string>" \
  -v $(pwd)/data:/app/data:rw \
  -v $(pwd)/log:/app/log:rw \
  abot:latest
```

### Security Checklist for Operators
- [x] Run under Python 3.11+ on a dedicated service user or non-root container.
- [x] Keep `allowPlugins = False` unless plugin installation is actively needed.
- [x] Pass session tokens via environment variables (`SESSION_STRING`), never CLI arguments.
- [x] Ensure only trusted personal user IDs are listed in `sudoers`.
- [x] Protect repository `.ini` files with `chmod 0600` (they contain `api_hash`).
