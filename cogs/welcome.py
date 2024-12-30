import discord
from discord.ext import commands
from utils.style import Style

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.style = Style()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Приветствие новых участников"""
        channel = discord.utils.get(member.guild.channels, name='приветствия')
        if channel:
            embed = self.style.info_embed(
                "Добро пожаловать!",
                f"{self.style.EMOJIS['members']} Привет, {member.mention}!\n"
                f"Добро пожаловать на сервер **{member.guild.name}**!"
            )
            embed.add_field(
                name="📜 Информация",
                value="Пожалуйста, ознакомьтесь с правилами сервера",
                inline=False
            )
            embed.add_field(
                name="🎭 Роли",
                value="Чтобы получить роли, посетите канал <#roles>",
                inline=False
            )
            embed.set_thumbnail(url=member.avatar.url)
            embed.set_footer(text=f"Участник #{len(member.guild.members)}")
            
            await channel.send(embed=embed)

            # Автовыдача роли
            role = discord.utils.get(member.guild.roles, name="Участник")
            if role:
                await member.add_roles(role)

async def setup(bot):
    await bot.add_cog(Welcome(bot)) 