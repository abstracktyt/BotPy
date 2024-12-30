import discord
from discord import app_commands
from discord.ext import commands
from utils.style import Style

class SlashWelcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.style = Style()

    @app_commands.command(
        name="welcome_setup",
        description="Настроить систему приветствий"
    )
    @app_commands.describe(
        channel="Канал для приветствий",
        message="Сообщение приветствия (используйте {user} для упоминания)",
        role="Роль для автовыдачи"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def welcome_setup(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        message: str = None,
        role: discord.Role = None
    ):
        try:
            # Сохраняем настройки в базу данных
            await self.bot.db.update_guild_setting(
                interaction.guild.id,
                'welcome_channel',
                channel.id
            )
            
            if message:
                await self.bot.db.update_guild_setting(
                    interaction.guild.id,
                    'welcome_message',
                    message
                )
                
            if role:
                await self.bot.db.update_guild_setting(
                    interaction.guild.id,
                    'autorole',
                    role.id
                )
            
            embed = self.style.success_embed(
                "Настройки приветствий",
                f"Канал приветствий: {channel.mention}\n" +
                (f"Сообщение: {message}\n" if message else "") +
                (f"Автороль: {role.mention}" if role else "")
            )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(
                embed=self.style.error_embed("Ошибка", str(e))
            )

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # Получаем настройки из базы данных
        settings = await self.bot.db.get_guild_settings(member.guild.id)
        if not settings:
            return
            
        # Отправляем приветствие
        channel_id = settings.get('welcome_channel')
        if channel_id:
            channel = member.guild.get_channel(channel_id)
            if channel:
                message = settings.get('welcome_message', 'Добро пожаловать, {user}!')
                message = message.replace('{user}', member.mention)
                
                embed = self.style.info_embed(
                    "Новый участник",
                    message
                )
                embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
                await channel.send(embed=embed)
        
        # Выдаем автороль
        role_id = settings.get('autorole')
        if role_id:
            role = member.guild.get_role(role_id)
            if role:
                try:
                    await member.add_roles(role)
                except Exception:
                    pass

async def setup(bot):
    await bot.add_cog(SlashWelcome(bot)) 