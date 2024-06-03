import os
import dotenv
import time

from deta import Deta
import discord

import utils.models as models
import utils.embeds as embeds
import utils.methods as methods
import utils.exceptions as exc

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

def load_game(id: int) -> models.Game:
	game = models.Game(id)
	load = games.get(str(id))

	if load is None:
		game._load({})
	else:
		game._load(load)

	return game


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
			await ctx.send_followup(embed = embeds.mm.gameCreated())
		else:
			await ctx.send_response(embed = embeds.noPermEmbed())
	except Exception as e: 
		ticket = str(round(ctx.author.id / time.time()))
		crashes.put(key = ticket, data = {'author': ctx.author.display_name, 'command': 'send', 'data': str(e), 'args': {'private': private }, 'traceback': e.with_traceback(None)})
		await ctx.send(embed = embeds.errorEmbed(ticket))

@fml.command(name = 'create')
async def create(ctx: discord.ApplicationContext, name: str, color: str):
	"""
	Commande permettant de créer une équipe. Celle-ci fonctionne si ces 3 conditions sont remplies:
		- L'auteur ne fait partie d'aucune équipe
		- La couleur de l'équipe est au format hexadécimal
		- Le nom et la couleur ne sont pas similaires à ceux d'une autre équipe

	Args:
		- name (str): Le nom de l'équipe, utilisé durant toute la partie
		- color (str): Couleur de l'équipe, utilisée durant toute la partie

	Returns:
		- discord.Embed: Embed de confirmation si les conditions sont remplies, sinon embed d'erreur
	"""

	try:
		# On vérifie déjà si la couleur est bien hexadécimale (on sait jamais avec eux)
		try:
			color: str = color.replace('#', '0x')
		except:
			await ctx.send_response(embed = embeds.tm.invalidColor(color))
			return
		
		# On vérifie que la longueur du nom soit inférieure à 32 caractères
		if len(name) > 32:
			await ctx.send_response(embed = embeds.tm.invalidName(name))
			return
		
		# On commence à chercher la partie
		game: models.Game = load_game(ctx.guild.id)

		# On vérifie que le nom et la couleur ne soient pas similaires à ceux d'une autre équipe
		for team in game.teams:
			if name.replace(' ', '') == team.name.replace(' ', ''): # On évitera plusieurs noms d'équipe qui diffèrent d'un ou plusieurs espaces seulement
				await ctx.send_response(embed = embeds.tm.alreadyExistingName(name))
				return
			elif methods.rgbDistance(color, team.color) <= 128:
				await ctx.send_response(embed = embeds.tm.alreadyExistingColor(color))
				return
		
		# Vérification de l'appartenance à une autre équipe
		player = game.fetch_player(ctx.author.id)
		if player is not None:
			await ctx.send_response(embed = embeds.tm.alreadyInTeam(player.team.name))
			return
		
		# Création de l'équipe
		team: models.Team = models.Team()

		team.name = name
		team.color = color
		team.chief = ctx.author.id
		team.members = [ ctx.author.id ]
		team.invites = []
		
		game.teams.append(team)
		game.save()

		await ctx.send_response(embed = embeds.tm.teamCreated(name, color, ctx.author.id))
	except Exception as e:
		ticket = str(round(ctx.author.id / time.time()))
		crashes.put(key = ticket, data = {'author': ctx.author.display_name, 'command': 'team create', 'data': str(e), 'args': {'name': name, 'color': color }, 'traceback': e.with_traceback(None)})
		await ctx.send(embed = embeds.errorEmbed(ticket))

@fml.command(name = 'join')
async def join(ctx: discord.ApplicationContext, name: str):
	"""
	Commande permettant de rejoindre une équipe. Elle fonction si ces conditions sont remplies:
		- Le joueur n'est présent dans aucune autre équipe
		- Il y est invité
	"""

	try:
		game: models.Game = load_game(ctx.guild.id)

		# Vérification de l'appartenance à une autre équipe
		player = game.fetch_player(ctx.author.id)
		if player is not None: # Le fetch renvoie None si le joueur n'est présent dans aucune équipe.
			await ctx.send_response(embed = embeds.tm.alreadyInTeam(player.team.name))
			return
		
		# On vérifie si l'équipe existe
		team = game.fetch_team(name)
		if team is None:
			await ctx.send_response(embed = embeds.tm.teamNotFound(name))
			return
		
		# On vérifie s'il est invité sinon c'est ciao
		if ctx.author.id not in team.invites:
			await ctx.send_response(embed = embeds.tm.notInvited(team.chief))
		else:
			if ctx.author.id not in team.members: # Normalement condition toujours vraie car sinon "alreadyInTeam"
				team.members.append(ctx.author.id)

			team.invites.remove(ctx.author.id) # On supprime son invitation -> il peut pas revenir si il se fait kick
			game.save()

			await ctx.send_response(embed = embeds.tm.teamJoined(team.name, team.chief, len(team.members)))
	except Exception as e:
		ticket = str(round(ctx.author.id / time.time()))
		crashes.put(key = ticket, data = {'author': ctx.author.display_name, 'command': 'team join', 'data': str(e), 'args': {'name': name }, 'traceback': e.with_traceback(None)})
		await ctx.send(embed = embeds.errorEmbed(ticket))

bot.run(os.getenv('TOKEN'))