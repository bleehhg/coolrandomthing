import discord
import os
import aiohttp
from discord.ext import commands, tasks
from discord.ext.commands import context
from multidict import CIMultiDictProxy

# Set up your bot token
TOKEN = 'MTIxMzY3MDE4NjI3MjQzMjE2OQ.GImyhp.7a8DTRheeDxQqlMOYO9tVL7qAAII1QQ5BQAnnM'

# Set the URL to check
GEAR_JSON_URL = 'https://splatoon3.ink/data/gear.json'

# Store the selected gear channel ID
selected_gear_channel = None

# Initialize an empty set to store processed gear IDs
processed_gear_ids = set()

# Create a bot instance with intents
intents = discord.Intents.all()  # You can customize this based on your needs
bot = commands.Bot(command_prefix='/', intents=intents)


@bot.event
async def on_ready():
  print("Bot is working.")
  check_gear_json.start(
      bot.get_channel(1213649475554246717))  # Start the background task


@bot.command()
async def test(ctx):
  await ctx.send("success")


@bot.command()
async def gearchannel(ctx, channel: discord.TextChannel):
  global selected_gear_channel
  selected_gear_channel = channel
  await ctx.send(f"Gear updates will now be posted in {channel.mention}.")


@tasks.loop(minutes=1)
async def check_gear_json(ctx):

  channel = bot.get_channel(1213649475554246717)
  async with aiohttp.ClientSession() as session:
    async with session.get(GEAR_JSON_URL) as response:
      if response.status == 200:
        gear_data = await response.json()

        #process daily drop gear
        brand_gears = gear_data.get('data',
                                    {}).get('gesotown',
                                            {}).get('pickupBrand',
                                                    {}).get('brandGears', [])
        for gear_entry in brand_gears:
          gear_id = gear_entry.get('id')
          if gear_id not in processed_gear_ids:
            # New gear ID found, process its data
            gear_name = gear_entry.get('gear', {}).get('name')
            gear_type = gear_entry.get('gear', {}).get('__typename')
            primary_gear_power = gear_entry.get('gear', {}).get(
                'primaryGearPower', {}).get('name')
            gear_image_url = gear_entry.get('gear', {}).get('image',
                                                            {}).get('url')
            gear_slots = len(
                gear_entry.get('gear', {}).get('additionalGearPowers', []))
            gear_brand = gear_entry.get('gear',
                                        {}).get('brand',
                                                {}).get('usualGearPower',
                                                        {}).get('name')

            if gear_name and gear_type and primary_gear_power and gear_image_url:

              # get role name
              role_name = f"{primary_gear_power} {gear_type}"
              role = discord.utils.get(ctx.guild.roles, name=role_name)

              print(role)
              # Create an embedded message
              embed = discord.Embed(title=f"New gear: {gear_name}",
                                    color=discord.Color.blue())
              embed.add_field(name='Ability: ',
                              value=f"{primary_gear_power}",
                              inline=False)
              embed.add_field(name='Slots: ',
                              value=f"{gear_slots}",
                              inline=False)
              embed.add_field(name='Brand Ability: ',
                              value=f"{gear_brand}",
                              inline=False)
              embed.set_image(url=gear_image_url)

              await ctx.send(role.mention, embed=embed)
            else:
              await ctx.send("Incomplete gear data found.")

            # Add the processed gear ID to the set
            processed_gear_ids.add(gear_id)

        #process other gear
        other_gears = gear_data.get('data',
                                    {}).get('gesotown',
                                            {}).get('limitedGears', [])
        for gear_entry in other_gears:
          gear_id = gear_entry.get('id')
          if gear_id not in processed_gear_ids:
            # New gear ID found, process its data
            gear_name = gear_entry.get('gear', {}).get('name')
            gear_type = gear_entry.get('gear', {}).get('__typename')
            primary_gear_power = gear_entry.get('gear', {}).get(
                'primaryGearPower', {}).get('name')
            gear_image_url = gear_entry.get('gear', {}).get('image',
                                                            {}).get('url')
            gear_slots = len(
                gear_entry.get('gear', {}).get('additionalGearPowers', []))
            gear_brand = gear_entry.get('gear',
                                        {}).get('brand',
                                                {}).get('usualGearPower',
                                                        {}).get('name')

            if gear_name and gear_type and primary_gear_power and gear_image_url:

              # get role name
              role_name = f"{primary_gear_power} {gear_type}"
              role = discord.utils.get(ctx.guild.roles, name=role_name)

              print(role)
              # Create an embedded message
              embed = discord.Embed(title=f"New gear: {gear_name}",
                                    color=discord.Color.blue())
              embed.add_field(name='Ability: ',
                              value=f"{primary_gear_power}",
                              inline=False)
              embed.add_field(name='Slots: ',
                              value=f"{gear_slots}",
                              inline=False)
              embed.add_field(name='Brand Ability: ',
                              value=f"{gear_brand}",
                              inline=False)
              embed.set_image(url=gear_image_url)

              await ctx.send(role.mention, embed=embed)
            else:
              await ctx.send("Incomplete gear data found.")

            # Add the processed gear ID to the set
            processed_gear_ids.add(gear_id)


# Background task to check for new content
#@tasks.loop(minutes=1)  # Adjust the interval as needed

# Run the bot
bot.run(TOKEN)
