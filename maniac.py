import os
from dotenv import load_dotenv
import asyncio
import yt_dlp
import discord 
from discord.ext import commands
import urllib.parse, urllib.request, re
def run_bot():
    #STEP 0: LOAD THE DOTENV
    load_dotenv()
    TOKEN = os.getenv("DISCORD_TOKEN")
    
    #STEP 1: BOT SETUP  
    intents = discord.Intents.default()
    intents.message_content = True
    client = commands.Bot(command_prefix=".", intents = intents)

    queues = {}           #The music queue

    voice_clients = {}
    
    #Youtube settings
    yt_dl_options = {"format": "bestaudio/best"}
    ytdl = yt_dlp.YoutubeDL(yt_dl_options)
    youtube_base_url = "https://youtube.com/"
    youtube_results_url = youtube_base_url + "results?"
    youtube_watch_url = youtube_base_url + "watch?v="
    
    #ffmpeg settings
    ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn -filter:a "volume=0.25"'}
    
    @client.event
    async def on_ready():
        print(f"{client.user} is now On!")
    
    async def play_next(ctx):
        if queues[ctx.guild.id] != []:
            link = queues[ctx.guild.id].pop(0)
            await play(ctx, link=link)
     
    @client.command(name="play")
    async def play(ctx, *, link):
        try:
            voice_client = await ctx.author.voice.channel.connect()     #Connect to the channel
            voice_clients[voice_client.guild.id] = voice_client
        except Exception as e:
            print(e)

        try:

            if youtube_base_url not in link:
                query_string = urllib.parse.urlencode({
                    'search_query': link
                })

                content = urllib.request.urlopen(
                    youtube_results_url + query_string
                )

                search_results = re.findall(r'/watch\?v=(.{11})', content.read().decode())

                link = youtube_watch_url + search_results[0]

            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(link, download=False))

            song = data['url']
            player = discord.FFmpegOpusAudio(song, **ffmpeg_options)

            voice_clients[ctx.guild.id].play(player, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), client.loop))
        except Exception as e:
            print(e)
            
        #Queue command
        @client.command(name="queue")
        async def queue(ctz, url):
            if ctx.guild.id not in queues:
                queues[ctx.guild.id] = []
            queues[ctx.guild.id].append(url)
            await ctx.send("Video adicionado a fila!")
            
        #Pause function
        @client.command(name="pause")
        async def pause(ctx):
            try:
                voice_clients[ctx.guild.id].pause()
                await ctx.channel.send("Musica pausada")
            except Exception as e:
                print(e)
          
        #Resume Function      
        @client.command(name="resume")
        async def resume(ctx):
            try:
                voice_clients[ctx.guild.id].resume()
                await ctx.channel.send("Tocando...")
            except Exception as e:
                print(e)
                
        @client.command(name="stop")
        async def stop(ctx):
            try:
                voice_clients[ctx.guild.id].stop()
                await voice_clients[ctx.guild.id].disconnect()
                await ctx.channel.send("Parei!")
            except Exception as e:
                print(e)
                
########################################################################################################
    # @client.event
    # async def on_message(message):         #When someone sends a message
    #     channel = message.channel          #Channel that the message was sent
        
        # if message.content.startswith("?p"):
        #     try:
        #         voice_client = await message.author.voice.channel.connect()
        #         voice_clients[voice_client.guild.id] = voice_client
        #     except Exception as e:
        #         print(e)
        #     try:
        #         url = message.content.split()[1]
                
        #         loop = asyncio.get_event_loop()
        #         data = await loop.run_in_executor(None, lambda:ytdl.extract_info(url, download=False))
        #         song = data["url"]
                
        #         queue.append(song)
        #         await play_song(channel, url, message)
        #     except Exception as e:
        #         print(e)
            
        
        #Play the song(?play)
        # if message.content.startswith("?play"): 
        #     try:
        #         #tries to connect the channel
        #         voice_client = await message.author.voice.channel.connect()
        #         voice_clients[voice_client.guild.id] = voice_client
                
        #         await channel.send("Entrando...")
        #     except Exception as e:
        #         print(e)
        #     try:
        #         url = message.content.split()[1]

        #         loop = asyncio.get_event_loop()
        #         data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
                
        #         song = data["url"]
        #         player = discord.FFmpegOpusAudio(song, **ffmpeg_options)
                
                
        #         await channel.send(f"Tocando {url}")
                
        #         voice_clients[message.guild.id].play(player)
        #     except Exception as e:
        #         print(e)
                
        #Pausing the music
        # if message.content.startswith("?pause"):
        #     try:
        #         voice_clients[message.guild.id].pause()
        #         await channel.send("Musica pausada")
        #     except Exception as e:
        #         print(e)
                
        #Resume the music
        # if message.content.startswith("?resume"):
        #     try:
        #         voice_clients[message.guild.id].resume()
        #         await channel.send("Tocando...")
        #     except Exception as e:
        #         print(e)
                
        #stop the music
        # if message.content.startswith("?stop"):
        #     try:
        #         voice_clients[message.guild.id].stop()
        #         await voice_clients[message.guild.id].disconnect()
        #         await channel.send("Parei!")
        #     except Exception as e:
        #         print(e)
                
    # async def play_song(channel, url, message):
    #     if len(queue) > 0:
    #         player = discord.FFmpegOpusAudio(queue[0], **ffmpeg_options)   
    #         queue.pop(0)
               
    #         await channel.send(f"Tocando {url}")
        
    #         await voice_clients[message.guild.id].play(player)
    #     else:
    #         print("A Fila Acabou...")
            
    client.run(TOKEN)