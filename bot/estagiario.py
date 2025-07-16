import os
from dotenv import load_dotenv
import asyncio
import yt_dlp
import discord 
from discord.ext import commands
import urllib.parse, urllib.request, re

from utils.GuildMusicPlayer import GuildMusicPlayer


def run_bot():
    #STEP 0: LOAD THE DOTENV
    load_dotenv()
    TOKEN = os.getenv("BOT_TOKEN")
    
    #STEP 1: BOT SETUP  
    intents = discord.Intents.default()
    intents.message_content = True
    client = commands.Bot(command_prefix=".", intents = intents)

    #The music queue
    queues = {}     

    voice_clients = {}

    #A dictionary that has the guild_id as key, and tells if the bot is playing
    playing = {}

    # This dictionary contains the players pf each guild
    guild_music_players = {}
    
    #Youtube settings
    yt_dl_options = {
        "format": "bestaudio/best"
    }
    ytdl = yt_dlp.YoutubeDL(yt_dl_options)
    youtube_base_url = "https://youtube.com/"
    youtube_results_url = youtube_base_url + "results?"
    youtube_watch_url = youtube_base_url + "watch?v="
    
    #ffmpeg settings
    ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn -filter:a "volume=0.25"'}
    
    # Carrega os cogs
    async def load_extensions():
        await client.load_extension("music.music_cog")

    @client.event
    async def on_ready():
        print(f"{client.user} is now On!")
        # Load the cogs
        await load_extensions()
            
    #Queue Commands----------------------------------------------------        
    
    #Clean queue
    @client.command(name="clean_queue")
    async def clean_queue(ctx):
        try:
            queues = {}
            await ctx.channel.send("Lista apagada com sucesso!")
        except Exception as e:
            print(e)
            
    #Show queue
    @client.command(name="show_queue")
    async def show_queue(ctx):
        try:     
            if queues[ctx.guild.id] != []:
                loop = asyncio.get_event_loop()
                songs = ""
                n = 1
            
                for song in queues[ctx.guild.id]: 
                    data = await loop.run_in_executor(None, lambda: ytdl.extract_info((song), download=False))
                    # songs.append(data["fulltitle"])
                    songs += f"{n} - {data['fulltitle']}\n"
                    n += 1
                await ctx.channel.send(songs)
            else:
                await ctx.channel.send("Nada na fila")
        except Exception as e:
            print(e)
    
    @client.command(name="remove")
    async def remove(ctx, link):
        try:
            if queues[ctx.guild.id][int(link)-1]:
                print(queues[ctx.guild.id])
                queues[ctx.guild.id].remove(queues[ctx.guild.id][int(link)-1])
                print(queues[ctx.guild.id])
                await ctx.channel.send("Música removinda com sucesso!")
            else:
                await ctx.channel.send("Música não encontrada")
        except Exception as e:
            print(e)


                  
    client.run(TOKEN)