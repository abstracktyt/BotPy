import discord
from discord.ext import commands, tasks
import datetime
from utils.style import Style

class Statistics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.style = Style()
        self.update_stats.start()

    def cog_unload(self):
        self.update_stats.cancel()

    @tasks.loop(minutes=5.0)
    async def update_stats(self):
        """Обновление статистики серверов"""
        for guild in self.bot.guilds:
            # Подсчет статистики
            total_members = guild.member_count
            online_members = len([m for m in guild.members if m.status != discord.Status.offline])
            total_channels = len(guild.channels)
            text_channels = len(guild.text_channels)
            voice_channels = len(guild.voice_channels)
            
            # Обновление каналов статистики
            stats_category = discord.utils.get(guild.categories, name='Статистика')
            if stats_category:
                for channel in stats_category.channels:
                    if channel.name.startswith('Участников:'):
                        await channel.edit(name=f'Участников: {total_members}')
                    elif channel.name.startswith('Онлайн:'):
                        await channel.edit(name=f'Онлайн: {online_members}')

    @commands.command()
    async def stats(self, ctx):
        """Показать статистику сервера"""
        guild = ctx.guild
        
        # Подсчет статистики
        total_members = guild.member_count
        online_members = len([m for m in guild.members if m.status != discord.Status.offline])
        bots = len([m for m in guild.members if m.bot])
        humans = total_members - bots
        
        channels_info = (
            f"Всего: {len(guild.channels)}\n"
            f"Текстовых: {len(guild.text_channels)}\n"
            f"Голосовых: {len(guild.voice_channels)}"
        )
        
        roles_info = (
            f"Всего: {len(guild.roles)}\n"
            f"Управляющих: {len([r for r in guild.roles if r.permissions.administrator])}"
        )

        embed = self.style.info_embed(
            "Статистика сервера",
            f"Сервер: {guild.name}"
        )
        
        # Участники
        embed.add_field(
            name="Участники",
            value=f"Всего: {total_members}\n"
                  f"Людей: {humans}\n"
                  f"Ботов: {bots}\n"
                  f"Онлайн: {online_members}",
            inline=True
        )
        
        # Каналы
        embed.add_field(
            name="Каналы",
            value=channels_info,
            inline=True
        )
        
        # Роли
        embed.add_field(
            name="Роли",
            value=roles_info,
            inline=True
        )

        # Дополнительная информация
        embed.add_field(
            name="Информация о сервере",
            value=f"Создан: {guild.created_at.strftime('%d.%m.%Y')}\n"
                  f"Регион: {guild.region if hasattr(guild, 'region') else 'Не указан'}\n"
                  f"Владелец: {guild.owner.mention if guild.owner else 'Не найден'}",
            inline=False
        )

        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        embed.set_footer(text=f"ID: {guild.id}")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Statistics(bot)) 