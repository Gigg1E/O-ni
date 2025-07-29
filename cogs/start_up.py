import discord
from discord.ext import commands
import json
import os

# Define the base directory for server-specific data
BASE_SERVER_DATA_DIR = "data/servers" 

class StartupCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Event listener that triggers when the bot is ready.
        It loads allowed channel IDs from a guild-specific JSON file (data/servers/<guild_id>/channels.json)
        and sends a welcome message to those channels in each guild the bot is a part of.
        """
        print("[StartupCog] Bot is ready. Attempting to send welcome messages.")

        for guild in self.bot.guilds:
            guild_id_str = str(guild.id)
            # Construct the dynamic path for the current guild's allowed channels file
            allowed_channels_file_path = os.path.join(BASE_SERVER_DATA_DIR, guild_id_str, "channels.json") 
            
            allowed_channel_ids_for_guild = []
            
            try:
                # Ensure the directory exists before attempting to open the file
                # os.makedirs(os.path.dirname(allowed_channels_file_path), exist_ok=True) # Not needed if file exists
                with open(allowed_channels_file_path, "r") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        allowed_channel_ids_for_guild = data
                    elif isinstance(data, dict) and "allowed" in data:
                        allowed_channel_ids_for_guild = data.get("allowed", [])
                    else:
                        print(f"[StartupCog] Unexpected JSON structure in {allowed_channels_file_path}. Expected a list or a dict with 'allowed' key.")
                        continue
                        
            except FileNotFoundError:
                print(f"[StartupCog] No allowed channels file found for guild {guild.name} ({guild.id}) at {allowed_channels_file_path}. Skipping welcome message for this guild.")
                continue
            except json.JSONDecodeError:
                print(f"[StartupCog] Error decoding allowed channels JSON for guild {guild.name} ({guild.id}) from {allowed_channels_file_path}. Skipping welcome message for this guild.")
                continue
            except Exception as e:
                print(f"[StartupCog] An unexpected error occurred while loading channels for guild {guild.name} ({guild.id}): {e}")
                continue

            if not allowed_channel_ids_for_guild:
                print(f"[StartupCog] No allowed channels configured for guild: {guild.name} ({guild.id}) after loading {allowed_channels_file_path}.")
                continue

            print(f"[StartupCog] Found allowed channels for guild {guild.name} ({guild.id}): {allowed_channel_ids_for_guild}")
            for channel_id in allowed_channel_ids_for_guild:
                channel = guild.get_channel(channel_id)
                if channel and isinstance(channel, discord.TextChannel):
                    try:
                        await channel.send("👋 Hello! I'm online now!")
                        print(f"[StartupCog] Sent welcome message to {channel.name} ({channel.id}) in {guild.name}.")
                    except discord.Forbidden:
                        print(f"[StartupCog] Failed to send message to {channel.name} ({channel.id}) in {guild.name}: Missing permissions.")
                    except Exception as e:
                        print(f"[StartupCog] Failed to send message in {channel.name} ({channel.id}) in {guild.name}: {e}")
                else:
                    print(f"[StartupCog] Channel ID {channel_id} not found or is not a text channel in guild {guild.name}.")

        print("[StartupCog] Startup cog is ready and welcome messages processed.")

async def setup(bot):
    await bot.add_cog(StartupCog(bot))