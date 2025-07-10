import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from keep_alive import keep_alive

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

client = commands.Bot(command_prefix="!", intents=intents)
tree = app_commands.CommandTree(client)

SETTINGS_FILE = "settings.json"

if not os.path.exists(SETTINGS_FILE):
    with open(SETTINGS_FILE, "w") as f:
        json.dump({}, f)

def load_settings():
    with open(SETTINGS_FILE, "r") as f:
        return json.load(f)

def save_settings(data):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(data, f, indent=4)

@client.event
async def on_ready():
    await tree.sync()
    await client.change_presence(activity=discord.Game(name="verification bot by Dpax"))
    print(f"Logged in as {client.user}")

def is_admin(interaction):
    return interaction.user.guild_permissions.administrator

@tree.command(name="enable-verification", description="Enable verification system")
async def enable_verification(interaction: discord.Interaction):
    if not is_admin(interaction):
        return await interaction.response.send_message("You must be an admin to use this.", ephemeral=True)

    settings = load_settings()
    gid = str(interaction.guild_id)
    settings[gid] = settings.get(gid, {})
    settings[gid]["enabled"] = True
    save_settings(settings)
    await interaction.response.send_message("✅ Verification enabled.")

@tree.command(name="disable-verification", description="Disable verification system")
async def disable_verification(interaction: discord.Interaction):
    if not is_admin(interaction):
        return await interaction.response.send_message("You must be an admin to use this.", ephemeral=True)

    settings = load_settings()
    gid = str(interaction.guild_id)
    settings[gid] = settings.get(gid, {})
    settings[gid]["enabled"] = False
    save_settings(settings)
    await interaction.response.send_message("❌ Verification disabled.")

@tree.command(name="verification-channel", description="Set the verification channel")
@app_commands.describe(channel="The channel to use for verification")
async def verification_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    if not is_admin(interaction):
        return await interaction.response.send_message("You must be an admin to use this.", ephemeral=True)

    settings = load_settings()
    gid = str(interaction.guild_id)
    settings[gid] = settings.get(gid, {})
    settings[gid]["channel"] = channel.id
    save_settings(settings)
    await interaction.response.send_message(f"📢 Verification channel set to {channel.mention}.")

@tree.command(name="verification-role", description="Set the verification role")
@app_commands.describe(role="The role to give to verified users")
async def verification_role(interaction: discord.Interaction, role: discord.Role):
    if not is_admin(interaction):
        return await interaction.response.send_message("You must be an admin to use this.", ephemeral=True)

    settings = load_settings()
    gid = str(interaction.guild_id)
    settings[gid] = settings.get(gid, {})
    settings[gid]["role"] = role.id
    save_settings(settings)
    await interaction.response.send_message(f"🎭 Verification role set to {role.mention}.")

@tree.command(name="verification-reset", description="Reset all verification settings")
async def verification_reset(interaction: discord.Interaction):
    if not is_admin(interaction):
        return await interaction.response.send_message("You must be an admin to use this.", ephemeral=True)

    settings = load_settings()
    gid = str(interaction.guild_id)
    if gid in settings:
        del settings[gid]
        save_settings(settings)
    await interaction.response.send_message("🔁 Verification settings reset.")

@client.event
async def on_message(message):
    if message.author.bot:
        return

    settings = load_settings()
    gid = str(message.guild.id)
    if gid not in settings:
        return

    conf = settings[gid]
    if not conf.get("enabled"):
        return

    if message.channel.id != conf.get("channel"):
        return

    desired_nick = message.content.strip()
    for member in message.guild.members:
        if member.nick == desired_nick or member.name == desired_nick:
            await message.add_reaction("❌")
            return

    try:
        await message.author.edit(nick=desired_nick)
        role = message.guild.get_role(conf.get("role"))
        if role:
            await message.author.add_roles(role)
        await message.add_reaction("✅")
    except:
        await message.add_reaction("❌")

keep_alive()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
client.run(TOKEN)