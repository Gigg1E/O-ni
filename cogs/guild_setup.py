from discord.ext import commands
import logging
from utils.guild_db import create_guild_db

logger = logging.getLogger(__name__)

class GuildSetupCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        create_guild_db(guild.id)
        logger.info(f"Created DB for guild {guild.name} ({guild.id}) on join.")
        
        # Optionally, send a welcome message
        if guild.system_channel:
            try:
                await guild.system_channel.send(
                    "Hello! I've set up my data storage for this server. Ready to roll! 🎉"
                )
            except Exception as e:
                logger.error(f"Failed to send welcome message in guild {guild.id}: {e}")

async def setup(bot):
    await bot.add_cog(GuildSetupCog(bot))
    print("[DEBUG] GuildSetupCog loaded successfully.")