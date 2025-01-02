import discord
from sizzlestools import sizzles
import yaml
import os
import json
from datetime import datetime, timedelta
import asyncio
import hashlib
import requests

try:
    with open("config.yaml", "r", encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file)
except UnicodeDecodeError as e:
    print(f"{sizzles.prefix.error} Error decoding config.yaml: {e}. Please ensure your config file uses UTF-8 encoding.")
    exit(1)


HASH_FILE = "DO_NOT_DELETE.txt"

def calculate_sha256(file_path):
    """Calculate the SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def write_hash_to_file(hash_value, signoff):
    """Write the SHA256 hash and INTERGRITY_SIGNOFF to the hash file."""
    with open(HASH_FILE, "w", encoding="utf-8") as hash_file:
        hash_file.write(f"{hash_value}{signoff}")

def read_hash_from_file():
    """Read the SHA256 hash from the hash file, removing the signoff."""
    if not os.path.exists(HASH_FILE):
        return None
    with open(HASH_FILE, "r", encoding="utf-8") as hash_file:
        content = hash_file.read()
    return content[:-len(config.get("INTERGRITY_SIGNOFF"))], content

def verify_data_integrity():
    """Verify if the hash of DATA_FILE matches the stored hash."""
    current_hash = calculate_sha256(DATA_FILE)
    stored_hash, _ = read_hash_from_file()
    if current_hash != stored_hash:
        print(f"{sizzles.prefix.warning} Integrity check failed! The data file has been tampered with.")

def save_data(data):
    """Save data and update the SHA256 hash."""
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)
    sha256 = calculate_sha256(DATA_FILE)
    write_hash_to_file(sha256, config.get("INTERGRITY_SIGNOFF"))

def load_data_sha():
    """Load data and verify its integrity."""
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump({}, file)
        sha256 = calculate_sha256(DATA_FILE)
        write_hash_to_file(sha256, config.get("INTERGRITY_SIGNOFF"))

    verify_data_integrity()
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


IMAGE_DIRECTORY = config.get("IMAGE_DIRECTORY")
DATA_FILE = config.get("DATA_FILE")
BLANK = config.get("EMBED_COLOR")



def allallowed():
    return [int(guild_id) for guild_id in config.get("ALLOWED_SERVER_IDS", [])]

intents = discord.Intents.all()
bot = discord.Bot(intents=intents, debug_guilds=allallowed())

def load_data():
    return load_data_sha() # 55

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

@bot.event
async def on_ready():
    print("""     _         _             _       _ 
 ___(_)_______| | ___  ___  | | ___ | |
/ __| |_  /_  / |/ _ || __| | |/ _ -| |
|__ | |/ / / /| |  __/|__ |_| | (_) | |
|___/_/___/___|_||___||___(_)_|-___/|_|
""")
    print(f"{sizzles.prefix.heart} Booting up mainframe...")

    try:
        url = "https://raw.githubusercontent.com/spiritualnulll/sizzloutrecah/refs/heads/main/bot.py"
        latest_script = requests.get(url).text
        with open(__file__, "r", encoding="utf-8") as current_file:
            current_script = current_file.read()

        if latest_script != current_script:
            print(f"{sizzles.prefix.warn} The current script is outdated. Please update to the latest version.")
            if os.path.exists("upgrade.py"):
                try:
                    print(f"{sizzles.prefix.info} Attempting to upgrade the bot by running upgrade.py...")
                    exec(open("upgrade.py").read())
                    print(f"{sizzles.prefix.info} Upgrade script executed successfully.")
                    exit()
                except Exception as e:
                    print(f"{sizzles.prefix.error} Failed to execute upgrade script: {e}")
            else:
                print(f"{sizzles.prefix.warn} upgrade.py not found. Getting from https://github.com")
                try:
                    url = "https://raw.githubusercontent.com/spiritualnulll/sizzloutrecah/refs/heads/main/upgrade.py"
                    upgrade_script = requests.get(url).text
                    with open("upgrade.py", "w", encoding="utf-8") as upgrade_file:
                        upgrade_file.write(upgrade_script)
                    print(f"{sizzles.prefix.info} upgrade.py has been downloaded successfully.")
                    print(f"{sizzles.prefix.info} Attempting to upgrade the bot by running upgrade.py...")
                    exec(upgrade_script)
                    print(f"{sizzles.prefix.info} Upgrade script executed successfully.")
                    exit()
                except Exception as e:
                    print(f"{sizzles.prefix.error} Failed to download or execute upgrade script: {e}")
        else:
            print(f"{sizzles.prefix.info} The current bot is up-to-date.")
    except Exception as e:
        print(f"{sizzles.prefix.error} Failed to check the script against the latest version: {e}")

    print(f"{sizzles.prefix.info} Checking config.yaml's integrity...")

    owners_no = len(config.get("OWNER_IDS", []))
    dead_owners = 0
    for userid in config.get("OWNER_IDS", []):
        userobject = await bot.get_or_fetch_user(userid)
        if not userobject:
            print(f"{sizzles.prefix.error} No user found for ID {userid}.")
            dead_owners += 1

    if dead_owners >= owners_no:
        print(f"{sizzles.prefix.error} No valid owners found! Please check config.yaml.")
        await bot.close()
        exit()

    global data
    data = load_data()
    print(f"{sizzles.prefix.heart} The bot is ready as {bot.user.name} ({bot.user.id}).")

log = bot.create_group("log", "Log commands")


@log.command(name="add_outreach", guild_ids=allallowed())
async def log_add_outreach(ctx, number: int, image: discord.Attachment, image2: discord.Attachment = None, image3: discord.Attachment = None):
    """Logs an outreach for the user, along with images for proof."""
    if not data.get(str(ctx.author.id)):
        embed = discord.Embed(description="You are not registered as an outreacher. Use /outreacher_register first.", colour=BLANK)
        await ctx.respond(embed=embed, ephemeral=True)
        return

    images = [image, image2, image3]
    valid_images = []

    for img in images:
        if img:
            if not img.filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
                embed = discord.Embed(description="Please upload a valid image file. [INVALID_FILE_TYPE]", colour=BLANK)
                await ctx.respond(embed=embed, ephemeral=True)
                return

            image_data = await img.read()
            if len(image_data) > 50 * 1024 * 1024:
                embed = discord.Embed(description="The image is too large. Please upload a smaller image. [FILE_TOO_LARGE]", colour=BLANK)
                await ctx.respond(embed=embed, ephemeral=True)
                return

            file_path = os.path.join(IMAGE_DIRECTORY, f"image_{ctx.author.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{img.filename}")
            os.makedirs(IMAGE_DIRECTORY, exist_ok=True)
            with open(file_path, "wb") as file:
                file.write(image_data)
            valid_images.append(file_path)

    data[str(ctx.author.id)]["total_outreaches"] += number
    save_data(data)
    embed = discord.Embed(description=f"Outreach logged successfully with images: {', '.join([img.filename for img in valid_images])}", colour=0x00ff00)
    await ctx.respond(embed=embed, ephemeral=True)

    # Send to the specified channel
    channel = bot.get_channel(1324131385711005696)
    if channel:
        await channel.send(f"Outreach logged by {ctx.author.name} with {number} outreaches.")
        for img_path in valid_images:
            await channel.send(file=discord.File(img_path))

@log.command(name="outreach_closed_deal_add", guild_ids=allallowed())
async def log_outreach_closed_deal_add(ctx, number: int, image: discord.Attachment, image2: discord.Attachment = None, image3: discord.Attachment = None):
    """Adds a closed deal to the user’s record along with images for proof."""
    if not data.get(str(ctx.author.id)):
        embed = discord.Embed(description="You are not registered as an outreacher. Use /outreacher_register first.", colour=BLANK)
        await ctx.respond(embed=embed, ephemeral=True)
        return

    images = [image, image2, image3]
    valid_images = []

    for img in images:
        if img:
            if not img.filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
                embed = discord.Embed(description="Please upload a valid image file. [INVALID_FILE_TYPE]", colour=BLANK)
                await ctx.respond(embed=embed, ephemeral=True)
                return

            image_data = await img.read()
            if len(image_data) > 50 * 1024 * 1024:
                embed = discord.Embed(description="The image is too large. Please upload a smaller image. [FILE_TOO_LARGE]", colour=BLANK)
                await ctx.respond(embed=embed, ephemeral=True)
                return

            file_path = os.path.join(IMAGE_DIRECTORY, f"image_{ctx.author.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{img.filename}")
            os.makedirs(IMAGE_DIRECTORY, exist_ok=True)
            with open(file_path, "wb") as file:
                file.write(image_data)
            valid_images.append(file_path)

    data[str(ctx.author.id)]["closed_deals"] += number
    save_data(data)
    embed = discord.Embed(description=f"{number} closed deals have been added to your record with images: {', '.join([img.filename for img in valid_images])}", colour=0x00ff00)
    await ctx.respond(embed=embed, ephemeral=True)

    # Send to the specified channel
    channel = bot.get_channel(1324131385711005696)
    if channel:
        await channel.send(f"Closed deal logged by {ctx.author.name} with {number} deals.")
        for img_path in valid_images:
            await channel.send(file=discord.File(img_path))

@bot.slash_command(name="leaderboard", guild_ids=allallowed())
async def leaderboard(ctx):
    """Displays the top 10 outreachers on the leaderboard."""
    sorted_users = sorted(data.items(), key=lambda x: x[1]["total_outreaches"], reverse=True)[:10]
    embed = discord.Embed(title="🏆 Leaderboard", colour=0x00ff00)
    for i, (user_id, stats) in enumerate(sorted_users, start=1):
        user = await bot.get_or_fetch_user(int(user_id))
        embed.add_field(name=f"#{i} {user.name}", value=f"Outreaches: {stats['total_outreaches']}", inline=False)
    await ctx.respond(embed=embed)

@bot.slash_command(name="profile", guild_ids=allallowed())
async def profile(ctx, user: discord.Member):
    """Shows the user’s profile."""
    if not data.get(str(user.id)):
        embed = discord.Embed(description=f"{user.name} is not registered.", colour=BLANK)
        await ctx.respond(embed=embed, ephemeral=True)
        return

    stats = data[str(user.id)]
    embed = discord.Embed(title=f"{user.name}'s Profile", colour=0x00ff00)
    embed.add_field(name="Bio", value=stats.get("bio", "No bio set"), inline=False)
    embed.add_field(name="Monthly Goal", value=stats.get("goal", "Not set"), inline=False)
    embed.add_field(name="Total Outreaches", value=stats.get("total_outreaches", 0), inline=False)
    embed.add_field(name="Closed Deals", value=stats.get("closed_deals", 0), inline=False)
    await ctx.respond(embed=embed)

@bot.slash_command(name="outreacher_register", guild_ids=allallowed())
async def outreacher_register(ctx, user: discord.Member):
    """Registers a user as part of the outreach team."""
    if data.get(str(user.id)):
        embed = discord.Embed(description=f"{user.name} is already registered.", colour=BLANK)
        await ctx.respond(embed=embed, ephemeral=True)
        return

    data[str(user.id)] = {"bio": "", "goal": 0, "total_outreaches": 0, "closed_deals": 0}
    save_data(data)
    embed = discord.Embed(description=f"{user.name} has been registered successfully!", colour=0x00ff00)
    await ctx.respond(embed=embed)

@bot.slash_command(name="bio_add", guild_ids=allallowed())
async def bio_add(ctx, text: str):
    """Adds text to the user's bio."""
    if not data.get(str(ctx.author.id)):
        embed = discord.Embed(description="You are not registered as an outreacher. Use /outreacher_register first.", colour=BLANK)
        await ctx.respond(embed=embed, ephemeral=True)
        return

    data[str(ctx.author.id)]["bio"] = text
    save_data(data)
    embed = discord.Embed(description="Your bio has been updated successfully.", colour=0x00ff00)
    await ctx.respond(embed=embed)

@bot.slash_command(name="outreacher_goal", guild_ids=allallowed())
async def outreacher_goal(ctx, number: int):
    """Sets an outreach goal for the user."""
    if not data.get(str(ctx.author.id)):
        embed = discord.Embed(description="You are not registered as an outreacher. Use /outreacher_register first.", colour=BLANK)
        await ctx.respond(embed=embed, ephemeral=True)
        return

    data[str(ctx.author.id)]["goal"] = number
    save_data(data)
    embed = discord.Embed(description=f"Your outreach goal has been set to {number}.", colour=0x00ff00)
    await ctx.respond(embed=embed)

@log.command(name="outreacher_closed_deal_add", guild_ids=allallowed())
async def outreacher_closed_deal_add(ctx, number: int):
    """Adds a closed deal to the user’s record."""
    if not data.get(str(ctx.author.id)):
        embed = discord.Embed(description="You are not registered as an outreacher. Use /outreacher_register first.", colour=BLANK)
        await ctx.respond(embed=embed, ephemeral=True)
        return

    data[str(ctx.author.id)]["closed_deals"] += number
    save_data(data)
    embed = discord.Embed(description=f"{number} closed deals have been added to your record.", colour=0x00ff00)
    await ctx.respond(embed=embed)

@bot.slash_command(name="dashboard", guild_ids=allallowed())
async def dashboard(ctx):
    """Shows your own personal dashboard."""
    if not data.get(str(ctx.author.id)):
        embed = discord.Embed(description="**You are not registered as an outreacher.** Use /outreacher_register first.", colour=BLANK)
        await ctx.respond(embed=embed, ephemeral=True)
        return

    stats = data[str(ctx.author.id)]
    embed = discord.Embed(title=f"{ctx.author.name}'s Dashboard", colour=0x00ff00)
    embed.add_field(name="Bio", value=stats.get("bio", "No bio set"), inline=False)
    embed.add_field(name="Monthly Goal", value=stats.get("goal", "Not set"), inline=False)
    embed.add_field(name="Total Outreaches", value=stats.get("total_outreaches", 0), inline=False)
    embed.add_field(name="Closed Deals", value=stats.get("closed_deals", 0), inline=False)
    await ctx.respond(embed=embed)

async def monthly_top_outreachers():
    """Sends a message each month showcasing the top 3 outreachers."""
    await bot.wait_until_ready()
    while not bot.is_closed():
        now = datetime.now()
        next_month = (now.replace(day=1) + timedelta(days=31)).replace(day=1)
        wait_time = (next_month - now).total_seconds()
        await asyncio.sleep(wait_time)

        sorted_users = sorted(data.items(), key=lambda x: x[1]["total_outreaches"], reverse=True)[:3]
        channel = bot.get_channel(config.get("TOP_OUTREACHERS_CHANNEL_ID"))
        if channel:
            embed = discord.Embed(title="🌟 Monthly Top Outreachers", colour=0x00ff00)
            for i, (user_id, stats) in enumerate(sorted_users, start=1):
                user = await bot.get_or_fetch_user(int(user_id))
                embed.add_field(name=f"#{i} {user.name}", value=f"Outreaches: {stats['total_outreaches']}", inline=False)
            await channel.send(embed=embed)

bot.loop.create_task(monthly_top_outreachers())


bot.run(config.get("DISCORD_TOKEN"))
