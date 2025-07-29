# 🤖 O-ni - Your Personal Anime AI Discord Assistant

![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.10+-blue)
![Discord.py](https://img.shields.io/badge/discord.py-2.3.2-blue)
![Status](https://img.shields.io/badge/status-active-brightgreen)

O-ni is a customizable anime-themed AI assistant built for Discord. She blends personality and utility, combining traditional Discord bot features with local LLM integration, server tools, and immersive responses.

> **"O-ni is not just a bot... she's your server’s virtual companion."**

---

## ✨ Features

- 💬 **Personality Chat** - Converses with users using a local LLM (via [Ollama](https://ollama.com)).
- ⚙️ **Admin Tools** - Ban, warn, and manage users through rich moderation commands.
- 📂 **Session Memory** - Remembers conversations across sessions (optional).
- 🛠️ **Tasks & Automation** - Execute structured tasks through `$run`, `$task`, etc.
- 🎭 **Impersonation Tools** - Perform actions *as another user* for fun or testing.
- 📈 **Logs & Analytics** - Tracks interactions, sessions, and server data.
- 🌗 **Themed Responses** - Custom responses styled for both dark and light Discord themes.

---

## 📁 Project Structure

```bash
O-ni/
├── bot.py                   # Main entry point
├── cogs/                    # Bot feature modules
│   ├── admin.py
│   ├── chat.py
│   ├── tasks/
│   │   └── impersonate_task.py
├── core/                    # Core logic (LLM, session manager)
│   ├── llm_client.py
│   ├── session_manager.py
├── utils/                   # Utility helpers and config
│   ├── config_loader.py
├── data/
│   ├── servers/             # Per-server config/logs
│   ├── sessions.db          # SQLite database for session tracking
│   └── logs/
├── config.json              # Main bot config
├── requirements.txt
└── README.md
````

---

## ⚙️ Configuration

Create a `config.json` in the root directory:

```json
{
  "default_model": "llama3:latest",
  "max_response_length": 1999,
  "default_system_prompt": "You are O-ni, a helpful, smart, and cute anime girl AI assistant.",
  "max_sessions_per_user": 5,
  "session_db_path": "data/sessions.db",
  "temp_session_file": "data/temp",
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

### 3. Set Up Discord Bot Token

Create a `.env` file or use `os.environ` in `bot.py`:

```
DISCORD_TOKEN=your_bot_token_here
```

### 4. Run the Bot

```bash
python -m bot
```

---

## 💡 Example Commands

| Command     | Description                              |
| ----------- | ---------------------------------------- |
| `$help`     | Show all available commands              |
| `$talk`     | Talk to O-ni (personality chat with LLM) |
| `$run`      | Run a task like impersonation            |
| `$ban`      | Admin-only: ban a user                   |
| `$warn`     | Admin-only: warn a user                  |
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
* Impersonation requires privileged access to avoid abuse.

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

* Developed by [MqllpW](https://github.com/your-profile)
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