from discord.ext import commands
import discord
import asyncio
import yt_dlp
import urllib.parse, urllib.request, re
import os
from utils.GuildMusicPlayer import GuildMusicPlayer

class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild_music_players = {}
        self.players = {}

        self.ytdl_opts = {
        "format": "bestaudio/best"
        }

        self.ytdl = yt_dlp.YoutubeDL(self.ytdl_opts)
        self.youtube_base_url = "https://youtube.com/"
        self.youtube_results_url = self.youtube_base_url + "results?"
        self.youtube_watch_url = self.youtube_base_url + "watch?v="

        self.ffmpeg_opts = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn -filter:a "volume=0.25"'}

    # play command
    @commands.command(name="play")
    async def play(self, ctx, *, link):

        # Checks if the user is in a voice channel
        if ctx.author.voice is None:
            await ctx.send("Você precisa estar em um canal de voz.")
            return

        # Alteracao para usar classes
        if ctx.guild.id not in self.guild_music_players:
            self.guild_music_players[ctx.guild.id] = GuildMusicPlayer(ctx.guild.id)

        player = self.guild_music_players[ctx.guild.id]

        if player.voice_client is None or not player.voice_client.is_connected():
            try:
                player.voice_client = await ctx.author.voice.channel.connect()
            except Exception as e:
                print("Erro ao conectar: ", e)
                return
        #voice_client = await ctx.author.voice.channel.connect()     #Connect to the channel
        #voice_clients[voice_client.guild.id] = voice_client

        # If the message is not a link, it tries to search on youtube
        if self.youtube_base_url not in link:
            query_string = urllib.parse.urlencode({
                'search_query': link
            })

            content = urllib.request.urlopen(
                self.youtube_results_url + query_string
            )

            search_results = re.findall(r'/watch\?v=(.{11})', content.read().decode())

            link = self.youtube_watch_url + search_results[0]

        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(link, download=False))

        song = data['url']
        
        audio = discord.FFmpegOpusAudio(song, **self.ffmpeg_opts)
    
        # if it is not playing yet
        if not player.current_playing:
            player.current_playing = True
            
            #Song message
            await ctx.channel.send(f"Tocando {link}")  #data["fulltitle"] to use the title
            player.voice_client.play(audio, after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.bot.loop))
        else:
            #queues[ctx.guild.id].append(link)
            # Adds the song to the queue
            player.queue.append(link)

            await ctx.send(f"{link} Adicionado a fila!")

    #Play next song
    async def play_next(self, ctx):
        player = self.guild_music_players[ctx.guild.id]

        if player.queue != []:
            link = player.queue.pop(0)
            player.current_playing = False
            await self.play(ctx, link=link)
        else:  
            player.current_playing = False

    #Pause the song
    @commands.command(name="pause")
    async def pause(self, ctx):
        player = self.guild_music_players[ctx.guild.id]

        try:
            player.voice_client.pause()
            await ctx.channel.send("Musica pausada")
        except Exception as e:
            print(e)


    #Resume song      
    @commands.command(name="resume")
    async def resume(self, ctx):
        player = self.guild_music_players[ctx.guild.id]

        try:
            player.voice_client.resume()
            await ctx.channel.send("Tocando...")
        except Exception as e:
            print(e)

    #Stop playing
    @commands.command(name="stop")
    async def stop(self, ctx):
        player = self.guild_music_players[ctx.guild.id]

        try:
            player.queue = []
            player.voice_client.stop()
            player.voice_client.disconnect()

            await ctx.channel.send("Parei!")     
        except Exception as e:
            print(e)

    #Skip song
    @commands.command(name="skip")
    async def skip(self, ctx):
        player = self.guild_music_players[ctx.guild.id]

        try:
            player.voice_client.stop()
        except Exception as e:
            print(e)

async def setup(bot):
    await bot.add_cog(MusicCog(bot))