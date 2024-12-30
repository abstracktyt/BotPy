import discord
from discord import app_commands
from discord.ext import commands
from utils.style import Style
import datetime
import random
import asyncio

class SlashCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.style = Style()

    @app_commands.command(name="ping", description="Проверить задержку бота")
    async def ping(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)
        await interaction.response.send_message(
            embed=self.style.info_embed(
                "Пинг",
                f"Задержка: {latency}мс"
            )
        )

    @app_commands.command(name="serverinfo", description="Подробная информация о сервере")
    async def serverinfo(self, interaction: discord.Interaction):
        guild = interaction.guild
        
        # Сбор информации о сервере
        total_members = guild.member_count
        online_members = len([m for m in guild.members if m.status != discord.Status.offline])
        bots = len([m for m in guild.members if m.bot])
        humans = total_members - bots
        
        embed = self.style.info_embed(
            f"Информация о сервере {guild.name}",
            f"Создан: {guild.created_at.strftime('%d.%m.%Y')}"
        )
        embed.add_field(name="Участники", value=f"Всего: {total_members}\nЛюдей: {humans}\nБотов: {bots}")
        embed.add_field(name="Каналы", value=f"Текстовых: {len(guild.text_channels)}\nГолосовых: {len(guild.voice_channels)}")
        embed.add_field(name="Роли", value=str(len(guild.roles)))
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="user", description="Информация о пользователе")
    async def userinfo(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        
        roles = [role.mention for role in member.roles[1:]]  # Исключаем @everyone
        joined_at = member.joined_at.strftime("%d.%m.%Y") if member.joined_at else "Неизвестно"
        created_at = member.created_at.strftime("%d.%m.%Y")
        
        embed = self.style.info_embed(
            f"Информация о {member.name}",
            f"ID: {member.id}"
        )
        embed.add_field(name="Присоединился", value=joined_at)
        embed.add_field(name="Аккаунт создан", value=created_at)
        if roles:
            embed.add_field(name=f"Роли ({len(roles)})", value=" ".join(roles), inline=False)
        embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="remind", description="Установить напоминание")
    @app_commands.describe(
        time="Время в минутах",
        reminder="Текст напоминания"
    )
    async def remind(self, interaction: discord.Interaction, time: int, reminder: str):
        if time < 1:
            await interaction.response.send_message(
                embed=self.style.error_embed("Ошибка", "Минимальное время - 1 минута")
            )
            return
            
        await interaction.response.send_message(
            embed=self.style.success_embed(
                "Напоминание установлено",
                f"Я напомню вам через {time} минут(ы)"
            )
        )
        
        await asyncio.sleep(time * 60)
        try:
            await interaction.user.send(
                embed=self.style.info_embed(
                    "Напоминание",
                    f"Вы просили напомнить: {reminder}"
                )
            )
        except:
            # Если личные сообщения закрыты
            channel = interaction.channel
            await channel.send(
                content=f"{interaction.user.mention}",
                embed=self.style.info_embed(
                    "Напоминание",
                    f"Вы просили напомнить: {reminder}"
                )
            )

    @app_commands.command(name="poll", description="Создать голосование")
    @app_commands.describe(
        question="Вопрос для голосования",
        option1="Первый вариант ответа",
        option2="Второй вариант ответа",
        option3="Третий вариант ответа (необязательно)",
        option4="Четвертый вариант ответа (необязательно)"
    )
    async def poll(self, interaction: discord.Interaction, question: str, option1: str, option2: str, 
                  option3: str = None, option4: str = None):
        options = [option1, option2]
        if option3:
            options.append(option3)
        if option4:
            options.append(option4)
            
        reactions = ['1️⃣', '2️⃣', '3️⃣', '4️⃣']
        
        description = f"**{question}**\n\n"
        for idx, option in enumerate(options):
            description += f"{reactions[idx]} {option}\n"
            
        embed = self.style.info_embed("Голосование", description)
        embed.set_footer(text=f"Создал: {interaction.user.name}")
        
        await interaction.response.send_message(embed=embed)
        message = await interaction.original_response()
        
        for idx in range(len(options)):
            await message.add_reaction(reactions[idx])

    @app_commands.command(name="random", description="Случайное число")
    @app_commands.describe(
        min="Минимальное число",
        max="Максимальное число"
    )
    async def random_number(self, interaction: discord.Interaction, min: int = 1, max: int = 100):
        if min >= max:
            await interaction.response.send_message(
                embed=self.style.error_embed(
                    "Ошибка",
                    "Минимальное число должно быть меньше максимального"
                )
            )
            return
            
        number = random.randint(min, max)
        await interaction.response.send_message(
            embed=self.style.success_embed(
                "Случайное число",
                f"Выпало число: **{number}**"
            )
        )

async def setup(bot):
    await bot.add_cog(SlashCommands(bot)) 