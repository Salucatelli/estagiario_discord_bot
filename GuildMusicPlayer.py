# For now it only allows you to use the bot in one channel per guild, but I am trying to fix if so you can use it in multiple channels

class GuildMusicPlayer:
    def __init__(self, guild_id):   
        self.guild_id = guild_id
        self.queue = []
        self.voice_client = None
        self.current_playing = False