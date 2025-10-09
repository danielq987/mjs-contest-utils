import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from read_csv import get_teams, get_schedule, get_individuals
# Load environment variables from .env
load_dotenv()

# Bot setup
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

print(intents)
bot = discord.Client(intents=intents)

individuals = get_individuals()
if not individuals: raise ValueError("No individuals found in CSV.")
print(individuals)
teams, team_names = get_teams()
print(teams)
if not teams: raise ValueError("No teams found in CSV.")
schedule = get_schedule()
if not schedule: raise ValueError("No schedule found in CSV.")

maj_to_disc_lookup = {player[1]: player[0] for player in individuals}

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

    guild = bot.get_guild(1153518265742667869)
    print(guild)

    for team in teams:
        players = teams[team]
        role = discord.utils.get(guild.roles, name=team)
        if not role:
            print("Role doesn't exist", team)

        
        for player in players:
            discord_name = maj_to_disc_lookup.get(player)
            if not discord_name:
                print("Discord name not found for player", player)
                continue

            member = discord.utils.get(guild.members, name=discord_name)
            if not member:
                print("Member doesn't exist", discord_name)
            elif role not in member.roles:
                await member.add_roles(role)
                print(f"Added role {role} to {member}")
            else:
                print(f"{member} already has role {role}")




    

token = os.getenv('DISCORD_BOT_TOKEN')
if not token:
    raise RuntimeError('DISCORD_BOT_TOKEN is not set. Add it to your .env file.')

bot.run(token)