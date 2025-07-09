import discord
from discord.ext import commands
import wavelink
import os
from keep_alive import keep_alive

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await wavelink.NodePool.create_node(
        bot=bot,
        host="lavalink.darrennathanael.com",  # public Lavalink node
        port=443,
        password="youshallnotpass",
        https=True
    )
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} global commands.")
    except Exception as e:
        print("Failed to sync commands:", e)

@bot.tree.command(name="join", description="Join your voice channel")
async def join(interaction: discord.Interaction):
    if not interaction.user.voice:
        await interaction.response.send_message("You're not in a voice channel!", ephemeral=True)
        return
    vc = interaction.user.voice.channel
    await vc.connect(cls=wavelink.Player)
    await interaction.response.send_message(f"Joined {vc.name}!")

@bot.tree.command(name="play", description="Play a YouTube song")
async def play(interaction: discord.Interaction, query: str):
    if not interaction.guild.voice_client:
        await join(interaction)
    player: wavelink.Player = interaction.guild.voice_client
    track = await wavelink.YouTubeTrack.search(query, return_first=True)
    await player.play(track)
    await interaction.response.send_message(f"Now playing: {track.title}")

@bot.tree.command(name="pause", description="Pause music")
async def pause(interaction: discord.Interaction):
    await interaction.guild.voice_client.pause()
    await interaction.response.send_message("Paused.")

@bot.tree.command(name="resume", description="Resume music")
async def resume(interaction: discord.Interaction):
    await interaction.guild.voice_client.resume()
    await interaction.response.send_message("Resumed.")

@bot.tree.command(name="skip", description="Skip current song")
async def skip(interaction: discord.Interaction):
    await interaction.guild.voice_client.stop()
    await interaction.response.send_message("Skipped.")

@bot.tree.command(name="leave", description="Leave the voice channel")
async def leave(interaction: discord.Interaction):
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("Disconnected.")
    else:
        await interaction.response.send_message("I'm not in a voice channel.")

keep_alive()  # Start Flask server for uptime
bot.run(TOKEN)