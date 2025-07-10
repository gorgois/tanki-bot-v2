import discord
from discord.ext import commands
from discord import app_commands
import os
import json
from keep_alive import keep_alive

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

client = commands.Bot(command_prefix="!", intents=intents)
tree = client.tree

# Load or initialize settings
if os.path.exists("verification_settings.json"):
    with open("verification_settings.json", "r") as f:
        settings = json.load(f)
else:
    settings = {}

def save_settings():
    with open("verification_settings.json", "w") as f:
        json.dump(settings, f, indent=4)

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    await client.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="verification bot by Dpax"
        )
    )
    await tree.sync()

@tree.command(name="enable-verification", description="Enable verification system")
@app_commands.checks.has_permissions(administrator=True)
async def enable_verification(interaction: discord.Interaction):
    guild_id = str(interaction.guild_id)
    settings[guild_id] = settings.get(guild_id, {})
    settings[guild_id]["enabled"] = True
    save_settings()
    await interaction.response.send_message("✅ Verification enabled.", ephemeral=True)

@tree.command(name="disable-verification", description="Disable verification system")
@app_commands.checks.has_permissions(administrator=True)
async def disable_verification(interaction: discord.Interaction):
    guild_id = str(interaction.guild_id)
    if guild_id in settings:
        settings[guild_id]["enabled"] = False
        save_settings()
        await interaction.response.send_message("❌ Verification disabled.", ephemeral=True)
    else:
        await interaction.response.send_message("⚠️ Verification was not set up yet.", ephemeral=True)

@tree.command(name="verification-channel", description="Set the verification channel")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(channel="Select a channel for verification")
async def verification_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    guild_id = str(interaction.guild_id)
    settings[guild_id] = settings.get(guild_id, {})
    settings[guild_id]["channel"] = channel.id
    save_settings()
    await interaction.response.send_message(f"📢 Verification channel set to {channel.mention}.", ephemeral=True)

@tree.command(name="verification-role", description="Set the role to give on verification")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(role="Select a role to give when users verify")
async def verification_role(interaction: discord.Interaction, role: discord.Role):
    guild_id = str(interaction.guild_id)
    settings[guild_id] = settings.get(guild_id, {})
    settings[guild_id]["role"] = role.id
    save_settings()
    await interaction.response.send_message(f"🎭 Verification role set to {role.name}.", ephemeral=True)

@tree.command(name="verification-reset", description="Reset all verification settings")
@app_commands.checks.has_permissions(administrator=True)
async def verification_reset(interaction: discord.Interaction):
    guild_id = str(interaction.guild_id)
    if guild_id in settings:
        del settings[guild_id]
        save_settings()
        await interaction.response.send_message("🔄 Verification settings reset.", ephemeral=True)
    else:
        await interaction.response.send_message("⚠️ Nothing to reset.", ephemeral=True)

@client.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return

    guild_id = str(message.guild.id)
    config = settings.get(guild_id)

    if not config or not config.get("enabled"):
        return

    if message.channel.id != config.get("channel"):
        return

    nickname = message.content.strip()
    if any(member.nick == nickname for member in message.guild.members if member.nick):
        await message.add_reaction("❌")
        return

    try:
        await message.author.edit(nick=nickname)
        role = message.guild.get_role(config.get("role"))
        if role:
            await message.author.add_roles(role)
        await message.add_reaction("✅")
    except discord.Forbidden:
        await message.channel.send("⚠️ I don't have permission to change nicknames or assign roles.")

# Start the keep-alive server and run the bot
keep_alive()
client.run(os.getenv("DISCORD_BOT_TOKEN"))