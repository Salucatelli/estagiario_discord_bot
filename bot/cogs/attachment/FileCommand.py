from discord.ext import commands
import discord

class FileCommandCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        ## CONSEGUI FAZER ELE RECEBER UM ARQUIVO E BAIXAR, AGORA PRECISO DESCOBRIR COMO TORNAR ISSO ÚTIL, SEJA COM UM SISTEMA DE ÁUDIOS OU ALGUMA COISA COM FOTOS

    @commands.command(name="file")
    async def file(self, ctx):
        if(ctx.message.attachments != []):
            file = ctx.message.attachments[0]
            print("Veio um arquivo")

            # Teste para salvar um arquivo
            await file.save(file.filename)
        else:
            print("Não veio nenhum arquivo") 

        await ctx.send("recebido")

async def setup(bot):
    await bot.add_cog(FileCommandCog(bot))
