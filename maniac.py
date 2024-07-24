import os
from dotenv import load_dotenv
import asyncio
import yt_dlp
import discord 
from responses import get_response

def run_bot():
    #STEP 0: LOAD THE DOTENV
    load_dotenv()
    TOKEN = os.getenv("DISCORD_TOKEN")
    
    #STEP 1: BOT SETUP  
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents = intents)

    voice_clients = {}
    yt_dl_options = {"format": "bestaudio/best"}
    ytdl = yt_dlp.YoutubeDL(yt_dl_options)
    
    ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn -filter:a "volume=0.25"'}
    
    @client.event
    async def on_ready():
        print(f"{client.user} is now On!")
        
    @client.event
    async def on_message(message):         #When someone sends a message
        channel = message.channel          #Channel that the message was sent
        
        #Play the song(?play)
        if message.content.startswith("?play"): 
            try:
                #tries to connect the channel
                voice_client = await message.author.voice.channel.connect()
                voice_clients[voice_client.guild.id] = voice_client
                
                await channel.send("Entrando...")
            except Exception as e:
                print(e)
            try:
                url = message.content.split()[1]

                loop = asyncio.get_event_loop()
                data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
                
                song = data["url"]
                player = discord.FFmpegPCMAudio(song, **ffmpeg_options)
                
                
                await channel.send(f"Tocando {url}")
                
                voice_clients[message.guild.id].play(player)
            except Exception as e:
                print(e)
                
        #Pausing the music
        if message.content.startswith("?pause"):
            try:
                voice_clients[message.guild.id].pause()
                await channel.send("Musica pausada")
            except Exception as e:
                print(e)
                
        #Resume the music
        if message.content.startswith("?resume"):
            try:
                voice_clients[message.guild.id].resume()
                await channel.send("Tocando...")
            except Exception as e:
                print(e)
                
        #stop the music
        if message.content.startswith("?stop"):
            try:
                voice_clients[message.guild.id].stop()
                await voice_clients[message.guild.id].disconnect()
                await channel.send("Parei!")
            except Exception as e:
                print(e)

    client.run(TOKEN)