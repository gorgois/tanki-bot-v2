import discord
from discord.ext import commands, tasks
import json
import random
import os

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents)

if not os.path.exists("users.json"):
    with open("users.json", "w") as f:
        json.dump({}, f)

with open("users.json", "r") as f:
    users = json.load(f)

ranks = [
    ("Recruit", 0), ("Private", 500), ("Gefreiter", 1200), ("Corporal", 2100),
    ("Master Corporal", 3200), ("Sergeant", 4500), ("Staff Sergeant", 6000),
    ("Master Sergeant", 7700), ("First Sergeant", 9600), ("Sergeant Major", 11700),
    ("Warrant Officer 1", 14000), ("Warrant Officer 2", 16500), ("Warrant Officer 3", 19200),
    ("Warrant Officer 4", 22100), ("Third Lieutenant", 25200), ("Second Lieutenant", 28500),
    ("First Lieutenant", 32000), ("Captain", 35700), ("Major", 39600), ("Lieutenant Colonel", 43700),
    ("Colonel", 48000), ("Brigadier", 52500), ("Major General", 57200), ("Lieutenant General", 62100),
    ("General", 67200), ("Marshal", 72500), ("Field Marshal", 78000), ("Commander", 83700),
    ("Generalissimo", 89600), ("Legend", 95600)
]

def get_rank(xp):
    for i in range(len(ranks)-1, -1, -1):
        if xp >= ranks[i][1]:
            return ranks[i][0], i
    return "Recruit", 0

def get_next_xp(current_xp):
    for rank, xp_needed in ranks:
        if current_xp < xp_needed:
            return xp_needed - current_xp
    return 0

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command()
async def battle(ctx):
    user_id = str(ctx.author.id)
    if user_id not in users:
        users[user_id] = {"xp": 0, "crystals": 0}

    earned_xp = random.randint(200, 500)
    earned_crystals = random.randint(100, 300)
    goldbox = random.random() < 0.05

    users[user_id]["xp"] += earned_xp
    users[user_id]["crystals"] += earned_crystals

    rank_name, _ = get_rank(users[user_id]["xp"])

    msg = f"🏆 You joined a battle!
You earned **{earned_xp} XP** and **💎 {earned_crystals} crystals**.
"
    if goldbox:
        msg += "🎉 You found a **GOLDBOX**! 🎁
"
        users[user_id]["crystals"] += 1000

    msg += f"Your current rank is **{rank_name}**."

    await ctx.send(msg)
    with open("users.json", "w") as f:
        json.dump(users, f)

@bot.command()
async def rank(ctx):
    user_id = str(ctx.author.id)
    if user_id not in users:
        await ctx.send("You haven't played yet. Use /battle to start!")
        return

    xp = users[user_id]["xp"]
    crystals = users[user_id]["crystals"]
    rank_name, i = get_rank(xp)
    if i + 1 < len(ranks):
        next_rank_name, next_xp_required = ranks[i+1]
        progress = int((xp - ranks[i][1]) / (next_xp_required - ranks[i][1]) * 20)
        bar = "[" + "■" * progress + "—" * (20 - progress) + "]"
        remaining = next_xp_required - xp
    else:
        bar = "[■■■■■■■■■■■■■■■■■■■■]"
        remaining = 0

    await ctx.send(f"📊 **{ctx.author.name}'s Rank:** {rank_name}
XP: {xp} | Crystals: 💎 {crystals}
Progress: {bar} {remaining} XP to next rank")

@bot.command()
async def shop(ctx):
    await ctx.send("🛒 **Shop:**
- XP Pass (+2x XP for 1 minute): 1000 💎
- XP Pass (+2x XP for 1 hour): 10000 💎")

@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello, {ctx.author.name}!")

@bot.command()
async def serverinfo(ctx):
    await ctx.send(f"Server Name: {ctx.guild.name}
Total Members: {ctx.guild.member_count}")

@bot.command()
async def avatar(ctx, member: discord.Member = None):
    member = member or ctx.author
    await ctx.send(member.avatar.url)

TOKEN = os.getenv("TOKEN")
bot.run(TOKEN)
