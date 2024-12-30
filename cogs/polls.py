import discord
from discord.ext import commands
from utils.style import Style

class Polls(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.style = Style()
        self.emoji_numbers = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

    @commands.command()
    async def poll(self, ctx, question, *options):
        """
        📊 Создать голосование
        
        Использование:
        !poll "Вопрос" "Вариант 1" "Вариант 2" ...
        """
        if len(options) < 2:
            await ctx.send(embed=self.style.error_embed(
                "Ошибка",
                "Нужно указать минимум 2 варианта ответа!"
            ))
            return
            
        if len(options) > 10:
            await ctx.send(embed=self.style.error_embed(
                "Ошибка",
                "Максимум 10 вариантов ответа!"
            ))
            return

        embed = self.style.info_embed(
            "📊 Голосование",
            f"**{question}**\n\n" + 
            "\n".join(f"{self.emoji_numbers[idx]} {option}" for idx, option in enumerate(options))
        )
        embed.set_footer(text=f"Создал: {ctx.author.name}")
        
        poll_message = await ctx.send(embed=embed)
        for idx in range(len(options)):
            await poll_message.add_reaction(self.emoji_numbers[idx])

async def setup(bot):
    await bot.add_cog(Polls(bot)) 