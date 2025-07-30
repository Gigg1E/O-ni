import os
import discord
import logging
from datetime import datetime
from discord.ext import commands
from dotenv import load_dotenv
from discord import Guild
from cogs.channel_control import load_allowed_channels
from cogs.admin import AdminCog
from core.session_manager import SessionManager

load_dotenv()

# ========== CONFIG ==========
LOG_DIR = "data/logs"
TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = "$"


# ========== LOGGING SETUP ==========
timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
log_filename = os.path.join(LOG_DIR, f"{timestamp}.log")

logger = logging.getLogger("O-ni")
logger.setLevel(logging.DEBUG)

log_format = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Console logging
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(log_format)
logger.addHandler(ch)

# File logging
fh = logging.FileHandler(log_filename, encoding='utf-8')
fh.setLevel(logging.DEBUG)
fh.setFormatter(log_format)
logger.addHandler(fh)

# ========== INTENTS / BOT ==========
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Needed for on_member_join

bot = commands.Bot(command_prefix=PREFIX, intents=intents)



# ========== EVENTS ==========
@bot.event
async def on_ready():
    logger.info(f"[O-ni] Logged in as {bot.user} ({bot.user.id})")
    await bot.tree.sync()
    for guild in bot.guilds:
        create_guild_db(guild.id)
    print("Checked and created DBs for all guilds.")
    logger.info("[O-ni] Ready to process prompts!")


@bot.check
async def global_channel_check(ctx):
    guild = ctx.guild
    if not guild:
        return True  # Allow DMs

    if ctx.command and ctx.command.name == "allowchannel":
        return True

    allowed = load_allowed_channels(guild.id)
    if not allowed or ctx.channel.id in allowed:
        return True
 

    try:
        await ctx.send("🚫 This channel is not authorized to use O-ni. Ask an admin to use `$allowchannel`.")
        logger.warning(f"[WARN] Unauthorized use in {ctx.channel.id} by {ctx.author.id} in guild {guild.id}")
    except discord.Forbidden:
        logger.warning(f"[WARN] Cannot warn in unauthorized channel {ctx.channel.id}")
    return False


@bot.event
async def on_guild_join(guild: Guild):
    guild_path = os.path.join("data", str(guild.id))
    sessions_path = os.path.join(guild_path, "sessions")
    channels_path = os.path.join(guild_path, "channels.json")

    # Create the required directories
    os.makedirs(sessions_path, exist_ok=True)

    # Optional: Create a default channels.json if missing
    if not os.path.exists(channels_path):
        with open(channels_path, "w") as f:
            json.dump({"welcome_channel_id": None}, f, indent=4)

    print(f"[INFO] Initialized folders for new guild: {guild.name} ({guild.id})")


# ========== COG LOADING ==========
async def load_extensions():
    logger.debug("[DEBUG] Loading cogs...")
    for cog in os.listdir("./cogs"):
        if cog.endswith(".py") and not cog.startswith("_"):
            ext = f"cogs.{cog[:-3]}"
            try:
                await bot.load_extension(ext)
                logger.debug(f"[DEBUG] Loaded cog: {ext}")
            except Exception as e:
                logger.error(f"[ERROR] Failed to load cog {ext}: {e}", exc_info=True)
    logger.debug("[DEBUG] Cogs loading complete.")

# ========== MAIN LOOP ==========
async def main():
    logger.info("[O-ni] Starting")
    try:
        async with bot:
            await load_extensions()
            await bot.start(TOKEN)
    finally:
        logger.info("[O-ni] Shutting down, flushing logs...")
        for handler in logger.handlers:
            handler.flush()
            handler.close()
        logger.handlers.clear()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())