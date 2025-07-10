import discord
from discord.ext import commands
from discord import app_commands
import json
import os

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = commands.Bot(command_prefix="!", intents=intents)
tree = client.tree  # ✅ Fixed: use built-in tree

# Load config
if os.path.exists("verification_config.json"):
    with open("verification_config.json", "r") as f:
        config = json.load(f)
else:
    config = {}

# Save config
def save_config():
    with open("verification_config.json", "w") as f:
        json.dump(config, f, indent=4)

# Bot presence
@client.event
async def on_ready():
    await tree.sync()
    await client.change_presence(activity=discord.ActivityType=watching,name="verification"))
    print(f"Logged in as {client.user}")

# /enable-verification
@tree.command(name="enable-verification", description="Enable verification system")
@app_commands.checks.has_permissions(administrator=True)
async def enable_verification(interaction: discord.Interaction):
    config[str(interaction.guild.id)] = config.get(str(interaction.guild.id), {})
    config[str(interaction.guild.id)]["enabled"] = True
    save_config()
    await interaction.response.send_message("✅ Verification enabled.")

# /disable-verification
@tree.command(name="disable-verification", description="Disable verification system")
@app_commands.checks.has_permissions(administrator=True)
async def disable_verification(interaction: discord.Interaction):
    if str(interaction.guild.id) in config:
        config[str(interaction.guild.id)]["enabled"] = False
        save_config()
        await interaction.response.send_message("❌ Verification disabled.")
    else:
        await interaction.response.send_message("Verification was not set up.")

# /verification-channel
@tree.command(name="verification-channel", description="Set the verification channel")
@app_commands.checks.has_permissions(administrator=True)
async def verification_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    config[str(interaction.guild.id)] = config.get(str(interaction.guild.id), {})
    config[str(interaction.guild.id)]["channel_id"] = channel.id
    save_config()
    await interaction.response.send_message(f"📢 Verification channel set to {channel.mention}.")

# /verification-role
@tree.command(name="verification-role", description="Set the role to give upon verification")
@app_commands.checks.has_permissions(administrator=True)
async def verification_role(interaction: discord.Interaction, role: discord.Role):
    config[str(interaction.guild.id)] = config.get(str(interaction.guild.id), {})
    config[str(interaction.guild.id)]["role_id"] = role.id
    save_config()
    await interaction.response.send_message(f"🎭 Verification role set to `{role.name}`.")

# /verification-reset
@tree.command(name="verification-reset", description="Reset the verification system")
@app_commands.checks.has_permissions(administrator=True)
async def verification_reset(interaction: discord.Interaction):
    if str(interaction.guild.id) in config:
        del config[str(interaction.guild.id)]
        save_config()
        await interaction.response.send_message("🔄 Verification settings reset.")
    else:
        await interaction.response.send_message("Verification is not set up.")

# /start
@tree.command(name="start", description="Check if the verification bot is running.")
@app_commands.checks.has_permissions(administrator=True)
async def start_command(interaction: discord.Interaction):
    await interaction.response.send_message("✅ I'm alive and ready to verify users!", ephemeral=True)

# Listen for messages in verification channel
@client.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return

    guild_id = str(message.guild.id)
    if guild_id not in config:
        return

    settings = config[guild_id]
    if not settings.get("enabled"):
        return

    if message.channel.id != settings.get("channel_id"):
        return

    nickname = message.content.strip()

    # Check for duplicate nickname
    for member in message.guild.members:
        if member.nick == nickname:
            await message.add_reaction("❌")
            return

    try:
        await message.author.edit(nick=nickname)
        role = message.guild.get_role(settings.get("role_id"))
        if role:
            await message.author.add_roles(role)
        await message.add_reaction("✅")
    except discord.Forbidden:
        await message.channel.send("❌ I don't have permission to change nicknames or roles.")
    except Exception as e:
        await message.channel.send(f"⚠️ An error occurred: {str(e)}")

# Run the bot
client.run(os.getenv("DISCORD_BOT_TOKEN"))