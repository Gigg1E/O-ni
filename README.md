# 🤖 O-ni - Your Personal Anime AI Discord Assistant

![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.10+-blue)
![Discord.py](https://img.shields.io/badge/discord.py-2.3.2-blue)
![Status](https://img.shields.io/badge/status-active-brightgreen)

* This is push one. Not all mentioned features or functions will be included and or 100% working. Any issues you see or features to add, post in issues and/or pull. Thank you. *

O-ni is a customizable anime-themed AI assistant built for Discord. She blends personality and utility, combining traditional Discord bot features with local LLM integration, server tools, and immersive responses.

> **"O-ni is not just a bot... she's your server’s virtual companion."**

---

## ✨ Features

- 💬 **Personality Chat** - Converses with users using a local LLM (via [Ollama](https://ollama.com)).
- ⚙️ **Admin Tools** - Ban, warn, and manage users through rich moderation commands. (inactive/Connected to $run/$task)
- 📂 **Session Memory** - Remembers conversations across sessions.
- 🛠️ **Tasks & Automation** - Execute structured tasks through `$run`, `$task`, etc. (inactive)
- 🎭 **Impersonation Tools** - Perform actions *as another user* for fun or testing. (inactive)
- 📈 **Logs & Analytics** - Tracks interactions, sessions, and server data. (Logs only really work in terminal while bot is active)
- 🌗 **Themed Responses** - Custom responses styled for both dark and light Discord themes.
- 🛡️ **Command Protection** - Only admins will know what '$' copmmands can be used (unless you run $help in a @everyone channel... Don't). '/' commands users can see.

---

## 📁 Project Structure

```bash
O-ni/
├── bot.py                   # Main entry point
├── cogs/                    # Bot feature modules
│   ├── admin.py
│   ├── ai.py
|   ├── channel_control.py
|   ├── guild_setup.py
|   ├── misc.py
|   ├── session.py
|   ├── start_up.py
│   ├── tasks/			  # Comming Soon
│   │   └── impersonate_task.py # More to add
├── core/                    # Core logic (LLM, session manager)
│   ├── llm_client.py
│   ├── session_manager.py 
├── utils/                   # Utility helpers and config
│   ├── config_loader.py
|   ├── guild_db.py
|   ├── permissions.py	  # Not used and will be removed soon
├── data/
│   ├── servers/             # Per-server config/logs
│   ├── sessions.db          # SQLite database for session tracking
│   └── logs/
├── config/ 
|   ├──  config.json              # Main bot config
├── requirements.txt
└── README.md
````

---

## ⚙️ Configuration

Edit the `config.json` in the config/ directory:

```json
{
  "default_model": "llama3:latest",
  "max_response_length": 1999,
  "default_system_prompt": "default prompt here",
  "max_sessions_per_user": 5,
  "session_db_path": "data/sessions.db",
  "temp_session_file": "data/temp.json",
  "bfl_root": "data/servers",
  "logs_root": "data/logs"
}
```

---

## 🧪 Installation

### 1. Clone the Repo

```bash
git clone https://github.com/your-username/O-ni.git
cd O-ni
```

### 2. Install Requirements

```bash
pip install -r requirements.txt
```

### 2.5. Install ollama and download models

1. Visit [Ollama](https://ollama.com/download) to dowload the API

2. Pull a model you want to use
```bash
ollama pull llama3:latest
```


### 3. Set Up Discord Bot Token

Create a `.env` file or use `os.environ` in `bot.py`:

```
DISCORD_TOKEN=YOUR_TOKEN
```

### 4. Run the Bot

```bash
python -m bot
```
> This is all included in run_bot.bat

---

## 💡 Example Commands

| Command     | Description                              |
| ----------- | ---------------------------------------- |
| `$help`     | Show all available commands              |
| `$info`     | Shows basic content about O-ni           |
| `$talk`     | Talk to O-ni (personality chat with LLM) |
| `$run`      | Run a task like impersonation (inactive) |
| `$ban`      | Admin-only: ban a user        (inactive) |
| `$warn`     | Admin-only: warn a user       (inactive) |
| `$shutdown` | Admin-only: gracefully shut down the bot |

---

## 🧠 Powered by Local AI

O-ni integrates with [Ollama](https://ollama.com) to run language models locally on your machine. You can swap out models like `llama3`, `gemma`, `mistral`, and more.

Make sure Ollama is running locally before using LLM features:

```bash
ollama run llama3
```

---

## 🛡️ Permissions & Security

* All admin commands are protected using Discord role checks.
* Session memory is stored per-user and per-guild (with limits).
* Impersonation requires privileged access to avoid abuse. (inactive)

---

## 🤝 Contributing

Pull requests are welcome! Here's how to get started:

1. Fork the repo
2. Create a new branch (`git checkout -b feature-xyz`)
3. Make your changes
4. Commit and push (`git commit -m "feat: added xyz"`)
5. Open a PR

---

## 📜 License

This project is licensed under the MIT License.

---

## 🎀 Credits

* Developed by [MqllpW](https://github.com/Gigg1E)
* Powered by `discord.py`, `Ollama`, and a passion for anime and AI.

---

## 🔮 Future Roadmap

* [ ] Voice input support
* [ ] Web dashboard for configuration
* [ ] Per-server fine-tuning
* [ ] Reaction-based prompts
* [ ] Auto-response triggers

---

*Thank you for using O-ni. She’s always listening... and always learning.* 🍡
