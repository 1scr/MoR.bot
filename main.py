import os
import dotenv
import time

from deta import Deta
import discord

import utils.models as models
import utils.embeds as embeds
import utils.models as models
import utils.models as models

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
crashes = deta.Base('crashes')

@bot.event
async def on_ready():
    print(f'\033[32mConnecté en tant que \033[1m{bot.user.display_name}\033[0m')

@mng.command(name = 'start')
@discord.default_permissions(manage_events=True)
async def start(ctx: discord.ApplicationContext, private: bool | None = False):
    try:
        if ctx.author.id == 1116248453127876618:
            game: models.Game = models.Game(ctx.guild.id)
            game.privacy = private
            game.lastrefresh = round(time.time())
            game.refresh()
            game.save()

            await ctx.send_response("Vous jouez en mode privé, vous êtes donc invisibles dans le classement et aucune de vos données (hormis les erreurs) ne seront collectées." if private else "Vous jouez publiquement, les équipes et leurs noms seront donc visibles depuis n'importe quel serveur.", ephemeral = True)
            await ctx.send_followup(embed = embeds.mm.gameCreatedEmbed())
        else:
            await ctx.send_response(embed = embeds.noPermEmbed())
    except Exception as e: 
        ticket = str(round(ctx.author.id / time.time()))
        crashes.put(key = ticket, data = {'author': ctx.author.display_name, 'command': 'send', 'data': str(e), 'args': {'private': private }})
        await ctx.send(embed = embeds.errorEmbed(ticket))

bot.run(os.getenv('DEVTOKEN'))