# cogs/ai.py

import discord
from discord.ext import commands
from discord import app_commands
import logging
import asyncio
import json
import requests
import os

from core.session_manager import SessionManager
from core.llm_client import LLMClient
from utils.config_loader import load_config
from utils.config_loader import get_allowed_channels

config = load_config()

# Logging tag formatter
LOG_LEVEL_TAGS = {
    logging.DEBUG: "[DEBUG]",
    logging.INFO: "[AI]",
    logging.WARNING: "[WARNING]",
    logging.ERROR: "[ERROR]",
    logging.CRITICAL: "[CRITICAL]",
}


class CustomFormatter(logging.Formatter):
    def format(self, record):
        tag = LOG_LEVEL_TAGS.get(record.levelno, f"[{record.levelname}]")
        if record.levelno == logging.INFO and record.getMessage().startswith("User"):
            tag = "[USER]"
        record.levelname = tag
        return super().format(record)


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if not logger.hasHandlers():
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(CustomFormatter('%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
    logger.addHandler(ch)


class AICog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        logger.debug("Initializing AICog...")

        self.sessions = SessionManager(
            db_path=os.path.join(config["bfl_root"], "sessions.db"),
            max_sessions=config["max_sessions_per_user"]
        )
        self.llm = LLMClient(default_model=config["default_model"])
        self.default_model = config["default_model"]
        self.system_prompt = config["default_system_prompt"]
        self.available_models = self.fetch_models()

        logger.debug(f"SessionManager initialized (root={config['bfl_root']})")
        logger.debug(f"LLMClient initialized (model={self.default_model})")

    def get_user_model(self, guild_id, user_id):
        # Placeholder for future customization
        logger.debug(f"Returning default model for guild {guild_id}, user {user_id}")
        return self.default_model

    def fetch_models(self):
        try:
            response = requests.get("http://localhost:11434/api/tags")
            response.raise_for_status()
            models = [m["name"] for m in response.json().get("models", [])]
            logger.info(f"Fetched {len(models)} models from Ollama.")
            return models
        except requests.RequestException as e:
            logger.error(f"Failed to fetch models: {e}", exc_info=True)
            return []

    @app_commands.command(name="talk", description="💬 Talk to the AI using your current session.")
    async def talk(self, interaction: discord.Interaction, prompt: str):
        logger.debug(f"[COMMAND] /talk invoked by user {interaction.user} ({interaction.user.id}) in guild {interaction.guild} ({interaction.guild.id}) with prompt: {prompt}")

        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        #await interaction.response.defer(thinking=True)

        # Load allowed channels for this guild
        allowed_channels = None
        try:
            allowed_channels = get_allowed_channels(guild_id)
            logger.debug(f"[COMMAND] Allowed channels for guild {guild_id}: {allowed_channels}")
        except Exception as e:
            logger.error(f"[COMMAND] Failed to load allowed channels for guild {guild_id}: {e}", exc_info=True)

        # Check if command is used in an allowed channel (if restrictions exist)
        if allowed_channels and interaction.channel.id not in allowed_channels:
            logger.debug(f"[COMMAND] Command blocked: channel {interaction.channel.id} not in allowed channels for guild {guild_id}")
            await interaction.response.send_message("⚠️ You cannot use this command in this channel.", ephemeral=True)
            return

        try:
            # Defer the interaction to show "thinking..." and buy time for processing
            await interaction.response.defer()

            # Get session cog and session name
            session_cog = self.bot.get_cog("SessionCog")
            if session_cog is None:
                logger.error("[COMMAND] SessionCog not found!")
                await interaction.followup.send("⚠️ Session manager is not available right now.", ephemeral=True)
                return

            session_name = session_cog.get_session_name(guild_id, user_id)
            logger.debug(f"[COMMAND] Session name for user {user_id} in guild {guild_id} is '{session_name}'")

            # Get the model for the user (customize as needed)
            model = self.get_user_model(guild_id, user_id)
            logger.debug(f"[COMMAND] Using model '{model}' for user {user_id} in guild {guild_id}")

            # Retrieve current chat history for this session
            history = self.sessions.get_current_session(guild_id, user_id, session_name)
            logger.debug(f"[COMMAND] Retrieved history with {len(history)} messages")

            # Build full prompt for LLM
            messages = self.llm.build_prompt(self.system_prompt, history, prompt)
            logger.debug(f"[COMMAND] Built prompt with {len(messages)} messages (including system prompt and user input)")

            # Call the LLM asynchronously in a thread to avoid blocking
            response = await asyncio.to_thread(self.llm.call_model, model, messages)
            logger.debug(f"[COMMAND] Received response from model, length {len(response)} characters")

            # Update session history
            updated_history = history + [
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": response}
            ]
            self.sessions.update_session(guild_id, user_id, session_name, updated_history)
            logger.debug(f"[COMMAND] Session updated with new messages; total messages now {len(updated_history)}")

            # Save session to temp storage or DB
            try:
                self.sessions.filter_and_sync_sessions()
                logger.debug("[COMMAND] Temporary sessions saved successfully.")
            except Exception as e:
                logger.error(f"[COMMAND] Failed to save temporary sessions: {e}", exc_info=True)

            # Send response in Discord message chunks of max 2000 characters
            # The first chunk must use followup.send (after defer), subsequent chunks also use followup.send
            first_chunk = True
            for i in range(0, len(response), 2000):
                chunk = response[i:i + 2000]
                if first_chunk:
                    await interaction.followup.send(chunk)
                    first_chunk = False
                else:
                    await interaction.followup.send(chunk)

            logger.debug("[COMMAND] Response sent successfully")

        except Exception as e:
            logger.error(f"[COMMAND] Error in /talk command: {e}", exc_info=True)
            # If the interaction has not been responded to yet, use response.send_message()
            # Otherwise use followup.send()
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message("⚠️ Something went wrong while processing your message.", ephemeral=True)
                else:
                    await interaction.followup.send("⚠️ Something went wrong while processing your message.", ephemeral=True)
            except Exception:
                pass


    @app_commands.command(name="setmodel", description="🛠 Set your preferred model.")
    @app_commands.describe(model_name="The model you want to use.")
    async def setmodel(self, interaction: discord.Interaction, model_name: str):
        await interaction.response.defer(thinking=True)
        user_id = str(interaction.user.id)
        logger.info(f"User {user_id} requested model change to {model_name}")

        if model_name not in self.available_models:
            await interaction.followup.send("❌ Model not available. Use `$modellist` to view options.", ephemeral=True)
            return

        self.default_model = model_name
        await interaction.followup.send(f"✅ Model switched to `{model_name}`", ephemeral=True)

    @app_commands.command(name="modellist", description="📄 View available LLM models.")
    async def modellist(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        logger.info(f"User {interaction.user.id} requested model list.")
        await interaction.followup.send("🧠 Available models:\n```\n" + "\n".join(self.available_models) + "\n```", ephemeral=True)


async def setup(bot: commands.Bot):
    logger.debug("Loading AICog...")
    await bot.add_cog(AICog(bot))
    logger.info("AICog loaded successfully.")