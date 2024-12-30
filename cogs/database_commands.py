import discord
from discord import app_commands
from discord.ext import commands
from utils.style import Style

class DatabaseCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.style = Style()

    @app_commands.command(name="settings", description="Показать настройки сервера")
    @app_commands.checks.has_permissions(administrator=True)
    async def show_settings(self, interaction: discord.Interaction):
        settings = await self.bot.db.get_guild_settings(interaction.guild.id)
        
        if not settings:
            await interaction.response.send_message(
                embed=self.style.info_embed(
                    "Настройки",
                    "Для этого сервера ещё нет настроек"
                )
            )
            return
            
        # Форматируем настройки для отображения
        settings_text = "\n".join(f"**{k}**: {v}" for k, v in settings.items())
        
        await interaction.response.send_message(
            embed=self.style.info_embed(
                "Настройки сервера",
                settings_text
            )
        )

    @app_commands.command(name="reset_settings", description="Сбросить настройки сервера")
    @app_commands.checks.has_permissions(administrator=True)
    async def reset_settings(self, interaction: discord.Interaction):
        await self.bot.db.update_guild_setting(interaction.guild.id, {})
        
        await interaction.response.send_message(
            embed=self.style.success_embed(
                "Настройки сброшены",
                "Все настройки сервера были сброшены"
            )
        )

async def setup(bot):
    await bot.add_cog(DatabaseCommands(bot)) 