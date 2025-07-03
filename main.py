import discord
from discord.ext import commands
import json
import random
import time
import os
from ranks import ranks

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)

TOKEN = os.getenv("TOKEN")

# Load users data
if os.path.exists("users.json"):
    with open("users.json", "r") as f:
        users = json.load(f)
else:
    users = {}

# Load emojis
if os.path.exists("emojis.json"):
    with open("emojis.json", "r") as f:
        emojis = json.load(f)
else:
    emojis = {
        "xp": "🌟",
        "crystal": "💎",
        "battle": "⚔️",
        "rank": "🏅",
        "goldbox": "🎁"
    }

def save_users():
    with open("users.json", "w") as f:
        json.dump(users, f, indent=2)

def get_rank(xp):
    for rank_name, xp_req in reversed(ranks):
        if xp >= xp_req:
            return rank_name
    return ranks[0][0]

@bot.command()
async def loademojis(ctx):
    for name in emojis.keys():
        for emoji in ctx.guild.emojis:
            if emoji.name.lower() == name:
                emojis[name] = str(emoji)
    with open("emojis.json", "w") as f:
        json.dump(emojis, f, indent=2)
    await ctx.send("✅ Emojis loaded from this server!")

@bot.command()
async def battle(ctx):
    user_id = str(ctx.author.id)
    if user_id not in users:
        users[user_id] = {
            "nickname": ctx.author.name,
            "xp": 0,
            "crystals": 0,
            "pass_active": False,
            "pass_expires": 0
        }
    user = users[user_id]

    earned_xp = random.randint(200, 500)
    earned_crystals = random.randint(20, 50)

    # Check XP boost pass
    now = time.time()
    if user["pass_active"] and now < user["pass_expires"]:
        earned_xp *= 2
        earned_crystals *= 2
    else:
        user["pass_active"] = False

    user["xp"] += earned_xp
    user["crystals"] += earned_crystals

    # Chance for goldbox (5%)
    goldbox_msg = ""
    if random.random() < 0.05:
        user["crystals"] += 100  # bonus crystals for goldbox
        goldbox_msg = f"\n{emojis.get('goldbox', '🎁')} You found a Goldbox and got **100** bonus crystals!"

    save_users()

    msg = (
        f"{emojis.get('battle', '⚔️')} You joined a battle!\n"
        f"You earned {emojis.get('xp', '🌟')} **{earned_xp} XP** and {emojis.get('crystal', '💎')} **{earned_crystals} crystals**."
        + goldbox_msg
    )
    await ctx.send(msg)

@bot.command()
async def rank(ctx):
    user_id = str(ctx.author.id)
    if user_id not in users:
        await ctx.send("You haven't joined a battle yet! Use `/battle` first.")
        return

    user = users[user_id]
    current_rank = get_rank(user["xp"])

    # Calculate progress to next rank
    next_rank_xp = None
    for rank_name, xp_req in ranks:
        if xp_req > user["xp"]:
            next_rank_xp = xp_req
            break
    progress = 0
    if next_rank_xp:
        progress = (user["xp"] / next_rank_xp) * 100
    else:
        progress = 100  # max rank

    bar_length = 20
    filled_length = int(bar_length * progress // 100)
    bar = "█" * filled_length + "─" * (bar_length - filled_length)

    await ctx.send(
        f"{emojis.get('rank', '🏅')} {ctx.author.name}, your rank is **{current_rank}**\n"
        f"XP Progress: [{bar}] {progress:.1f}%\n"
        f"Crystals: {emojis.get('crystal', '💎')} **{user['crystals']}**"
    )

@bot.command()
async def shop(ctx):
    shop_text = (
        "**Battle Passes:**\n"
        "1. `/usepass 1` - 1 minute - 500 💎\n"
        "2. `/usepass 5` - 5 minutes - 2000 💎\n"
        "3. `/usepass 30` - 30 minutes - 8000 💎\n"
        "4. `/usepass 60` - 1 hour - 14000 💎"
    )
    await ctx.send(shop_text)

@bot.command()
async def usepass(ctx, duration: int):
    user_id = str(ctx.author.id)
    if user_id not in users:
        await ctx.send("You need to join a battle first using `/battle`!")
        return

    prices = {1: 500, 5: 2000, 30: 8000, 60: 14000}
    if duration not in prices:
        await ctx.send("Invalid pass duration. Use `/shop` to see options.")
        return

    user = users[user_id]
    cost = prices[duration]

    if user["crystals"] < cost:
        await ctx.send("You don't have enough crystals for this pass!")
        return

    user["crystals"] -= cost
    user["pass_active"] = True
    user["pass_expires"] = time.time() + duration * 60
    save_users()
    await ctx.send(f"Pass activated for {duration} minute(s)! You now earn double XP and crystals.")

bot.run(TOKEN)