import os
import dotenv

from deta import Deta
import discord

dotenv.load_dotenv()

# On initialise le bot
bot = discord.Bot()

# Groupes de commandes
mng = bot.create_group('war', 'Commandes pour gérer la partie')
fml = bot.create_group('family', 'Commandes pour gérer votre clan')

# Bases
deta = Deta(os.getenv('DBKEY'))
games = deta.Base('games')
ldb = deta.Base('leaderboard')

@bot.event
async def on_ready():
    print(f'\033[32mConnecté en tant que \033[1m{bot.user.display_name}\033[0m')

@mng.command(name = 'init')
@discord.default_permissions(manage_events=True)
async def init(ctx):
    pass

bot.run(os.getenv('TOKEN'))