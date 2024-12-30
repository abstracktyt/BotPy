import discord
from discord import app_commands
from discord.ext import commands, tasks
from utils.style import Style
import datetime

class SlashStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.style = Style()
        self.update_stats.start()

    def cog_unload(self):
        self.update_stats.cancel()

    @tasks.loop(minutes=5.0)
    async def update_stats(self):
        for guild in self.bot.guilds:
            stats_category = discord.utils.get(guild.categories, name='Статистика')
            if stats_category:
                total_members = guild.member_count
                online_members = len([m for m in guild.members if m.status != discord.Status.offline])
                
                for channel in stats_category.channels:
                    try:
                        if channel.name.startswith('Участников:'):
                            await channel.edit(name=f'Участников: {total_members}')
                        elif channel.name.startswith('Онлайн:'):
                            await channel.edit(name=f'Онлайн: {online_members}')
                    except Exception as e:
                        continue

    @app_commands.command(name="stats", description="Показать статистику сервера")
    async def stats(self, interaction: discord.Interaction):
        guild = interaction.guild
        
        total_members = guild.member_count
        online_members = len([m for m in guild.members if m.status != discord.Status.offline])
        bots = len([m for m in guild.members if m.bot])
        humans = total_members - bots
        
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        categories = len(guild.categories)
        
        embed = self.style.info_embed(
            "Статистика сервера",
            f"Сервер: {guild.name}"
        )
        
        embed.add_field(
            name="Участники",
            value=f"Всего: {total_members}\n"
                  f"Людей: {humans}\n"
                  f"Ботов: {bots}\n"
                  f"Онлайн: {online_members}",
            inline=True
        )
        
        embed.add_field(
            name="Каналы",
            value=f"Текстовых: {text_channels}\n"
                  f"Голосовых: {voice_channels}\n"
                  f"Категорий: {categories}",
            inline=True
        )
        
        embed.add_field(
            name="Роли",
            value=f"Всего: {len(guild.roles)}\n"
                  f"Интеграций: {len([r for r in guild.roles if r.is_integration()])}",
            inline=True
        )
        
        embed.add_field(
            name="Сервер создан",
            value=guild.created_at.strftime("%d.%m.%Y"),
            inline=False
        )
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
            
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="setup_stats", description="Настроить каналы статистики")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_stats(self, interaction: discord.Interaction):
        guild = interaction.guild
        
        # Создаем или находим категорию
        category = discord.utils.get(guild.categories, name='Статистика')
        if not category:
            category = await guild.create_category('Статистика')
        
        # Создаем каналы статистики
        channels_to_create = [
            (f'Участников: {guild.member_count}', '👥'),
            (f'Онлайн: {len([m for m in guild.members if m.status != discord.Status.offline])}', '🟢')
        ]
        
        created_channels = []
        for name, emoji in channels_to_create:
            channel = discord.utils.get(category.channels, name=name.split(':')[0])
            if not channel:
                channel = await guild.create_voice_channel(
                    name=name,
                    category=category,
                    overwrites={
                        guild.default_role: discord.PermissionOverwrite(connect=False)
                    }
                )
                created_channels.append(channel.mention)
        
        if created_channels:
            embed = self.style.success_embed(
                "Статистика настроена",
                f"Созданы каналы:\n" + "\n".join(created_channels)
            )
        else:
            embed = self.style.info_embed(
                "Статистика",
                "Каналы статистики уже настроены"
            )
            
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(SlashStats(bot)) 