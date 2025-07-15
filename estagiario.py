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

    
    
    ###  PLAY SONG COMMANDS  ###

    # #Play next song
    # async def play_next(ctx):
        
    #     if queues[ctx.guild.id] != []:
    #         link = queues[ctx.guild.id].pop(0)
            
    #         playing[ctx.guild.id] = False
    #         guild_music_players[ctx.guild.id].current_playing = False
    #         await play(ctx, link=link)
    #     else:  
    #         guild_music_players[ctx.guild.id].current_playing = False
    #         playing[ctx.guild.id] = False
     
    # #Play a song
    # @client.command(name="play")
    # async def play(ctx, *, link):
        
    #     try:
    #         # Alteracao para usar classes
    #         if ctx.guild.id not in guild_music_players:
    #             guild_music_players[ctx.guild.id] = GuildMusicPlayer(ctx.guild.id)

    #         guild_music_players[ctx.guild.id].voice_client = await ctx.author.voice.channel.connect()
    #         #voice_client = await ctx.author.voice.channel.connect()     #Connect to the channel
    #         #voice_clients[voice_client.guild.id] = voice_client
    #     except Exception as e:
    #         print(e)

    #     try:
    #         # If the message is not a link, it tries to search on youtube
    #         if youtube_base_url not in link:
    #             query_string = urllib.parse.urlencode({
    #                 'search_query': link
    #             })

    #             content = urllib.request.urlopen(
    #                 youtube_results_url + query_string
    #             )

    #             search_results = re.findall(r'/watch\?v=(.{11})', content.read().decode())

    #             link = youtube_watch_url + search_results[0]

    #         loop = asyncio.get_event_loop()
    #         data = await loop.run_in_executor(None, lambda: ytdl.extract_info(link, download=False))

    #         song = data['url']
            
    #         try:
    #             player = discord.FFmpegOpusAudio(song, **ffmpeg_options)
    #         except Exception as ex:
    #             print("Mensagem de erro: ", ex)

    #         # Creates the queue for the guild
    #         if ctx.guild.id not in queues:
    #             queues[ctx.guild.id] = []

            
    #         # if it is not playing yet
    #         # if not playing.get(ctx.guild.id, False):
    #         if not guild_music_players[ctx.guild.id].current_playing:
    #             guild_music_players[ctx.guild.id].current_playing = True
    #             playing[ctx.guild.id] = True
                
    #             #Song message
    #             await ctx.channel.send(f"Tocando {link}")  #data["fulltitle"] to use the title
                
    #             guild_music_players[ctx.guild.id].voice_client.play(player, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), client.loop))

    #             #voice_clients[ctx.guild.id].play(player, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), client.loop))
    #         else:
    #             queues[ctx.guild.id].append(link)
    #             # Adds the song to the queue
    #             guild_music_players[ctx.guild.id].queue.append(link)

    #             await ctx.send(f"{link} Adicionado a fila!")
                
    #     except Exception as e:
    #         print(e)
            
    # #Pause the song
    # @client.command(name="pause")
    # async def pause(ctx):
    #     try:
    #         guild_music_players[ctx.guild.id].voice_client.pause()
    #         #voice_clients[ctx.guild.id].pause()
    #         await ctx.channel.send("Musica pausada")
    #     except Exception as e:
    #         print(e)
        
    # #Resume song      
    # @client.command(name="resume")
    # async def resume(ctx):
    #     try:
    #         guild_music_players[ctx.guild.id].voice_client.resume()
    #         #voice_clients[ctx.guild.id].resume()
    #         await ctx.channel.send("Tocando...")
    #     except Exception as e:
    #         print(e)
            
    # #Stop playing
    # @client.command(name="stop")
    # async def stop(ctx):
    #     try:
    #         guild_music_players[ctx.guild.id].queue = []
    #         #queues[ctx.guild.id] = []
    #         guild_music_players[ctx.guild.id].voice_client.stop()
    #         #voice_clients[ctx.guild.id].stop()
    #         guild_music_players[ctx.guild.id].voice_client.disconnect()
    #         #await voice_clients[ctx.guild.id].disconnect()
    #         await ctx.channel.send("Parei!")     
    #     except Exception as e:
    #         print(e)
    
    # #Skip song
    # @client.command(name="skip")
    # async def skip(ctx):
    #     try:
    #         guild_music_players[ctx.guild.id].voice_client.stop()
    #         #voice_clients[ctx.guild.id].stop()
    #     except Exception as e:
    #         print(e)
            
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