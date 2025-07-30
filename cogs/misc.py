import discord
from discord.ext import commands
from discord import app_commands
import logging

logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

class Misc(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="help", description="Get help with bot commands.")
    async def help_command(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📘 O-ni Slash Command Help",
            description="Here's a categorized list of available commands:",
            color=discord.Color.blue()
        )

        # ─── AI LLM Commands ───
        embed.add_field(name="‎", value="━━━━━━━━━━━━━━━━", inline=False)
        embed.add_field(name="**🤖 AI / LLM Commands**", value="\u200b", inline=False)
        embed.add_field(name="/talk", value="💬 Talk to the AI using your current session.", inline=False)
        embed.add_field(name="/modellist", value="📄 View available LLM models.", inline=False)
        embed.add_field(name="/setmodel", value="🛠 Change your default LLM model.", inline=False)

        # ─── Session Management ───
        embed.add_field(name="‎", value="━━━━━━━━━━━━━━━━", inline=False)
        embed.add_field(name="**📂 Session Management**", value="\u200b", inline=False)
        embed.add_field(name="/listcurrentsession", value="📌 Show your current session name.", inline=False)
        embed.add_field(name="/createsession", value="🆕 Create a new temporary session.", inline=False)
        embed.add_field(name="/switchsession", value="🔄 Switch to a different session.", inline=False)
        embed.add_field(name="/savesession", value="💾 Save your current session.", inline=False)
        embed.add_field(name="/deletesession", value="🗑️ Delete a saved session.", inline=False)
        embed.add_field(name="/clearsession", value="🧹 Clear all messages in the current session.", inline=False)
        embed.add_field(name="/export", value="📦 Export your session to a file.", inline=False)

        # ─── Server & Misc ───
        embed.add_field(name="‎", value="━━━━━━━━━━━━━━━━", inline=False)
        embed.add_field(name="**⚙️ Server & Miscellaneous**", value="\u200b", inline=False)
        embed.add_field(name="/listallowed", value="📄 List allowed channels in this server.", inline=False)
        embed.add_field(name="/help", value="💡 Displays this help message.", inline=False)
        embed.add_field(name="/info", value="ℹ️ Get information about the bot.", inline=False)

        embed.set_footer(
            text="Use these commands to interact with O-ni. For more details, try /info.",
            icon_url=self.bot.user.display_avatar.url
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="info", description="Learn more about the bot.")
    async def info(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🤖 Meet O-ni!",
            description="Hey there! I'm **O-ni**, your cute AI-powered assistant here on Discord. I’m built to be smart, helpful, and just a little bit playful.\n\nHere's a bit more about me:",
            color=discord.Color.blurple()
        )
        embed.set_thumbnail(url=self.bot.user.avatar.url if self.bot.user.avatar else discord.Embed.Empty)
        embed.set_footer(text="Use /help to see everything I can do!", icon_url=self.bot.user.display_avatar.url)

        embed.add_field(
            name="🧠 Powered by AI",
            value="I'm backed by a powerful local LLM to give meaningful responses, help with tasks, or even chat like a real person. My brain runs locally – no cloud spying!",
            inline=False
        )

        embed.add_field(
            name="📚 Useful Commands",
            value="From managing your server to answering questions, I've got tools to help. Use `/help` to see them all neatly organized.",
            inline=False
        )

        embed.add_field(
            name="🔒 Privacy First",
            value="Nothing you say is ever shared. Everything runs locally or in a private, secure environment just between you and me ❤️ (Others in the server CAN see your chats with me, though!)\nYou can shoot me a DM to chat privately. Only you and I will see those messages.",
            inline=False
        )

        embed.add_field(
            name="🔧 Under Active Development",
            value="I'm constantly learning and gaining new features. If you see something weird or have a feature request, tell my creator!",
            inline=False
        )

        embed.add_field(
            name="💌 Created With Care",
            value="Made by someone who believes bots should be helpful *and* have personality. Expect me to get better with time. 💖",
            inline=False
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @commands.command(name="help_legacy", help="Legacy help command using traditional prefix.")
    async def help_legacy(self, ctx: commands.Context):
        embed = discord.Embed(
            title="📘 O-ni Help Guide (Legacy)",
            description="Hi! I'm **O-ni**, your friendly AI assistant. Here’s everything I can do in command form:\n\nUse `/help` if you're using slash commands instead!",
            color=discord.Color.white()
        )

        embed.set_thumbnail(url=self.bot.user.avatar.url if self.bot.user.avatar else discord.Embed.Empty)
        embed.set_footer(
            text="Use these commands to interact with O-ni. For more details, try !info_legacy or /info.",
            icon_url=self.bot.user.display_avatar.url
        )

        # ─── AI / LLM Commands ───
        embed.add_field(name="‎", value="━━━━━━━━━━━━━━━━", inline=False)
        embed.add_field(name="**🤖 AI / LLM Commands**", value="\u200b", inline=False)
        embed.add_field(name="/talk", value="💬 Talk to the AI using your current session.", inline=False)
        embed.add_field(name="/modellist", value="📄 View available LLM models.", inline=False)
        embed.add_field(name="/setmodel", value="🛠 Change your default LLM model.", inline=False)

        # ─── Session Management ───
        embed.add_field(name="‎", value="━━━━━━━━━━━━━━━━", inline=False)
        embed.add_field(name="**📂 Session Management**", value="\u200b", inline=False)
        embed.add_field(name="/listcurrentsession", value="📌 Show your current session name.", inline=False)
        embed.add_field(name="/createsession", value="🆕 Create a new temporary session.", inline=False)
        embed.add_field(name="/switchsession", value="🔄 Switch to a different session.", inline=False)
        embed.add_field(name="/savesession", value="💾 Save your current session.", inline=False)
        embed.add_field(name="/deletesession", value="🗑️ Delete a saved session.", inline=False)
        embed.add_field(name="/clearsession", value="🧹 Clear all messages in the current session.", inline=False)

        # ─── Server & Miscellaneous ───
        embed.add_field(name="‎", value="━━━━━━━━━━━━━━━━", inline=False)
        embed.add_field(name="**⚙️ Server & Miscellaneous**", value="\u200b", inline=False)
        embed.add_field(name="/listallowed", value="📄 List allowed channels in this server.", inline=False)
        embed.add_field(name="/info", value="ℹ️ Learn more about the bot.", inline=False)
        embed.add_field(name="/help", value="💡 Displays this help message.", inline=False)

        # Ending message
        embed.add_field(name="‎", value="━━━━━━━━━━━━━━━━", inline=False)
        embed.add_field(
            name="💬 Need Help?",
            value="If something’s unclear or broken, just let my creator know! I’m learning and improving all the time. ❤️",
            inline=False
        )

        await ctx.send(embed=embed)



    @commands.command(name="info_legacy", help="Legacy version of the info command for non-slash use.")
    async def info_legacy(self, ctx: commands.Context):
        embed = discord.Embed(
            title="🤖 Meet O-ni!",
            description="Hey there! I'm **O-ni**, your cute AI-powered assistant here on Discord. I'm built to be smart, helpful, and just a little bit playful.\n\nHere's a bit more about me:",
            color=discord.Color.white()
        )
        embed.set_thumbnail(url=self.bot.user.avatar.url if self.bot.user.avatar else discord.Embed.Empty)
        embed.set_footer(text="Use /help to see everything I can do!", icon_url=self.bot.user.display_avatar.url)

        embed.add_field(
            name="🤖 What I Can Do",
            value=(
                "• Respond to questions using AI models like `llama3` or `gemma3`\n"
                "• Manage sessions and chats with built-in memory\n"
                "• Help with moderation, automation, and other server tasks\n"
                "• Learn more with `/help`"
            ),
            inline=False
        )

        embed.add_field(
            name="🧠 Powered by AI",
            value="I'm backed by a powerful local LLM to give meaningful responses, help with tasks, or even chat like a real person. My brain runs locally – no cloud spying!",
            inline=False
        )

        embed.add_field(
            name="📚 Useful Commands",
            value="From managing your server to answering questions, I've got tools to help. Use `/help` to see them all neatly organized.",
            inline=False
        )

        embed.add_field(
            name="🔒 Privacy First",
            value="Nothing you say is ever shared. Everything runs locally or in a private, secure environment just between you and me ❤️ (Others in the server CAN see your chats with me, though!)\nYou can shoot me a DM to chat privately. Only you and I will see those messages.",
            inline=False
        )

        embed.add_field(
            name="🔧 Under Active Development",
            value="I'm constantly learning and gaining new features. If you see something weird or have a feature request, tell my creator!",
            inline=False
        )

        embed.add_field(
            name="💌 Created With Care",
            value="Made by someone who believes bots should be helpful *and* have personality. Expect me to get better with time. 💖",
            inline=False
        )

        await ctx.send(embed=embed)

async def setup(bot):
    logger.debug("[DEBUG] Loading HelpSlashCog...")
    await bot.add_cog(Misc(bot))
    logger.info("[AI] HelpSlashCog Loaded successfully.")
