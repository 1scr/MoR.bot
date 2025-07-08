import random

import discord
from discord.ext import commands

from bot.utils import *
from bot import embeds
from game import models

class Teams(commands.Cog):
	def __init__(self, bot: discord.Bot):
		self.bot = bot

	teams = discord.SlashCommandGroup('team', 'Commandes pour gérer votre clan')

	@teams.command(name = 'create')
	async def create_team(self, ctx: discord.ApplicationContext, name: str, color: str):
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

		# On commence à chercher la partie
		game: models.Game = load_game(ctx.guild.id)

		if game.open and not game.rules.matchmakingWhilePlaying:
			await ctx.send_response(embed = embeds.tm.gameStarted())
			return

		if len(game.teams) >= 10:
			await ctx.send_response(embeds.tm.tooMuchTeams(10))

		# On vérifie déjà si la couleur est bien hexadécimale (on sait jamais avec eux)
		try:
			if color.startswith("#"):
				color: int = int(color[1:], 16)
			elif color in COLORS.keys():
				color: int = COLORS[color]
			else:
				raise Exception()
		except:
			await ctx.send_response(embed = embeds.tm.invalidColor(color))
			return

		# On vérifie que la longueur du nom soit inférieure à 24 caractères
		if not checkName(name):
			await ctx.send_response(embed = embeds.tm.invalidName(name))
			return

		# On vérifie que le nom et la couleur ne soient pas similaires à ceux d'une autre équipe
		for team in game.teams:
			if name.replace(' ', '') == team.name.replace(' ', ''): # On évitera plusieurs noms d'équipe qui diffèrent d'un ou plusieurs espaces seulement
				await ctx.send_response(embed = embeds.tm.alreadyExistingName(name))
				return
			elif rgbDistance(color, team.color):
				await ctx.send_response(embed = embeds.tm.alreadyExistingColor(color))
				return

		# Vérification de l'appartenance à une autre équipe
		player = game.fetch_player(ctx.author.id)
		if player is not None:
			await ctx.send_response(embed = embeds.tm.alreadyInTeam(player.team))
			return

		# Profil du soldat
		hex_id = hex(ctx.author.id)[2:].upper()

		soldier = models.Soldier(ctx.author.id)
		soldier.chief = True
		soldier.team = name

		# Création de l'équipe
		team: models.Team = models.Team()

		team.name = name
		team.color = color
		team.members[hex_id] = soldier

		game.teams.append(team)

		if not game.rules.waitForStartToSpawn:
			ctr = str(random.randint(1, 42))
			while game.countries[ctr].team:
				ctr = str(random.randint(1, 42))

			country = game.countries[ctr]

			country.team = team.name
			country.units.append([ 5, 0 ]) # 5 unités gratuites pour pas se retrouver coincé par les no mans land

			team.base = country.id
			team.countries.append(country.id)

		game.save()

		await ctx.send_response(embed = embeds.tm.teamCreated(name, color, ctx.author.id))

	@teams.command(name = 'edit')
	async def edit_team(self, ctx: discord.ApplicationContext, name: str | None = None, color: str | None = None):
		game: models.Game = load_game(ctx.guild.id)

		if game.open and not game.rules.matchmakingWhilePlaying:
			await ctx.send_response(embed = embeds.tm.gameStarted())
			return

		player = game.fetch_player(ctx.author.id)
		if player is None:
			await ctx.send_response(embed = embeds.tm.notInAnyTeam())
			return

		if not player.chief:
			await ctx.send_response("Vous n'êtes pas le chef de votre équipe.")
			return

		team = game.get_team(player.team)

		if name:
			if not checkName(name):
				await ctx.send_response(embed = embeds.tm.invalidName(name))
				return

			for _team in game.teams:
				if name.replace(' ', '') == _team.name.replace(' ', ''):
					await ctx.send_response(embed = embeds.tm.alreadyExistingName(name))
					return

			old_name = team.name
			team.name = name

			for country in game.countries.values():
				if country.team == old_name: country.team = name

		if color:
			try:
				if color.startswith("#"):
					color: int = int(color[1:], 16)
				elif color in COLORS.keys():
					color: int = COLORS[color]
				else:
					raise Exception()
			except:
				await ctx.send_response(embed = embeds.tm.invalidColor(color))
				return

			for _team in game.teams:
				if rgbDistance(color, _team.color):
					await ctx.send_response(embed = embeds.tm.alreadyExistingColor(color))
					return

			team.color = color

		game.save()

		await ctx.send_response("L'équipe a bien été modifiée.")


	@teams.command(name = 'list')
	async def list_teams(self, ctx: discord.ApplicationContext):
		game: models.Game = load_game(ctx.guild.id)

		desc = []

		_teams = sorted(game.teams, key = lambda t: len(t.countries))

		for team in _teams:
			chief = team.get_chief()

			desc += [ f"**{team.name}** par <@{chief.id}> ({len(team.members)} membres)" ]

		await ctx.send_response(embed = discord.Embed(
			title = f"Liste des équipes pour le serveur {ctx.guild.name}",
			description = '\n'.join(desc) if desc else "Il n'y a aucune équipe dans cette partie.",
			color = discord.Colour.blurple()
		))

	@teams.command(name = 'info')
	async def team_info(self, ctx: discord.ApplicationContext, name: str):
		game: models.Game = load_game(ctx.guild.id)

		team = game.get_team(name)
		if not team:
			await ctx.send_response(embed = embeds.tm.teamNotFound(name))
			return

		await ctx.send_response(embed = embeds.tm.teamInfos(
			team,
			[ ctr for _, ctr in game.countries.items() if ctr.team == team.name ],
			game.rules
		))

	@teams.command(name = 'join')
	async def join_team(self, ctx: discord.ApplicationContext, name: str):
		"""
		Commande permettant de rejoindre une équipe. Elle fonctionne si ces conditions sont remplies:
			- Le joueur n'est présent dans aucune autre équipe
			- Il y est invité
		"""

		game: models.Game = load_game(ctx.guild.id)

		# Vérification de l'appartenance à une autre équipe
		player = game.fetch_player(ctx.author.id)
		if player is not None: # Le fetch renvoie None si le joueur n'est présent dans aucune équipe.
			await ctx.send_response(embed = embeds.tm.alreadyInTeam(player.team))
			return 

		# On vérifie si l'équipe existe
		team = game.get_team(name)
		if team is None:
			await ctx.send_response(embed = embeds.tm.teamNotFound(name))
			return

		if len(team.countries) > 15:
			await ctx.send_response(embed = embeds.tm.gameReallyReallyStarted())
			return

		# On vérifie s'il est invité sinon c'est ciao
		if ctx.author.id not in team.invites:
			await ctx.send_response(embed = embeds.tm.notInvited(team.get_chief()))
		else:
			if ctx.author.id not in team.members: # Normalement condition toujours vraie car sinon "alreadyInTeam"
				team.members[ctx.author.id] = models.Soldier(ctx.author.id)

			team.invites.remove(ctx.author.id) # On supprime son invitation -> il peut pas revenir si il se fait kick
			game.save()

			await ctx.send_response(embed = embeds.tm.teamJoined(team.name, team.get_chief().id, len(team.members)))

	@teams.command(name = 'leave')
	async def leave_team(self, ctx: discord.ApplicationContext):
		"""
		Commande permettant de quitter une équipe.
		"""

		game: models.Game = load_game(ctx.guild.id)

		# Vérification de l'appartenance à une équipe
		player = game.fetch_player(ctx.author.id)
		if player is None: # Le fetch renvoie None si le joueur n'est présent dans aucune équipe.
			await ctx.send_response(embed = embeds.tm.notInAnyTeam())
			return

		if game.open and not game.rules.matchmakingWhilePlaying :
			await ctx.send_response(embed = embeds.tm.gameStarted())
			return

		team = game.get_team(player.team)

		if len(team.countries) > 15:
			await ctx.send_response(embed = embeds.tm.gameReallyReallyStarted())
			return

		if player.chief:
			for ctr in team.countries:
				game.countries[str(ctr)].team = None

			game.delete_team(team.name)

			await ctx.send_response(embed = embeds.tm.teamDeleted(team.color))
		else:
			del team.members[ctx.author.id]
			await ctx.send_response(embed = embeds.tm.teamLeft(team.name, team.color, len(team.members)))

		game.save()

	@teams.command(name = 'kick')
	async def kick_from_team(self, ctx: discord.ApplicationContext, member: discord.Member):
		"""
		Commande permettant de virer un joueur d'une équipe.
		"""

		game: models.Game = load_game(ctx.guild.id)

		if game.open and not game.rules.matchmakingWhilePlaying:
			await ctx.send_response(embed = embeds.tm.gameStarted())
			return

		# Author
		author = game.fetch_player(ctx.author.id)
		if author is None:
			author = models.Soldier(ctx.author.id)

		if not (author.chief or ctx.author.guild_permissions.manage_events):
			await ctx.send_response(embed = embeds.noPermEmbed())
			return

		# Vérification de l'appartenance à une équipe
		player = game.fetch_player(member.id)
		if player is None:
			await ctx.send_response(embed = embeds.tm.notInAnyTeam(member.display_name))
			return 

		team = game.get_team(player.team)

		if len(team.countries) > 15 and not ctx.author.guild_permissions.manage_events:
			await ctx.send_response(embed = embeds.tm.gameReallyReallyStarted())
			return

		if player.chief:
			for ctr in team.countries:
				game.countries[str(ctr)].team = None

			game.delete_team(team.name)

			await ctx.send_response(embed = embeds.tm.teamDeleted(team.color))
		else:
			_id = hex(ctx.author.id)[2:].upper()

			if _id in team.members.keys():
				del team.members[_id]

			await ctx.send_response(embed = embeds.tm.teamLeft(team.name, team.color, len(team.members)))

		game.save()


	@teams.command(name = 'invite')
	async def invite(self, ctx: discord.ApplicationContext, member: discord.User):
		"""
		Commande permettant au chef d'une équipe d'y inviter un membre
		"""

		game: models.Game = load_game(ctx.guild.id)

		# On vérifie s'il est chef d'équipe
		player = game.fetch_player(ctx.author.id)
		if player is None or game.get_team(player.team).get_chief().id != player.id: # Le fetch renvoie None si le joueur n'est présent dans aucune équipe.
			await ctx.send_response(embed = embeds.tm.notInAnyTeam())
			return

		team = game.get_team(player.team)

		if len(team.countries) > 15 and not ctx.author.guild_permissions.manage_events:
			await ctx.send_response(embed = embeds.tm.gameReallyReallyStarted())
			return

		# On envoie l'invitation si elle n'est pas déjà envoyée
		sent = False # Elle nous servira à savoir si l'invit a été envoyée par DM

		if member.id not in team.invites:
			team.invites.append(member.id)

			try:
				if member.can_send():
					await member.send(embed = embeds.info.invite(team.name, team.get_chief().id, len(team.members), ctx.guild.name))
					sent = True
			except:
				pass

		game.save()

		# On répond poliement
		await ctx.send_response(embed = embeds.tm.memberInvited(member.name), ephemeral = True)

		if not sent:
			await ctx.channel.send(member.mention, embed = embeds.info.invite(team.name, team.get_chief().id, len(team.members), ctx.guild.name))

def setup(bot):
	bot.add_cog(Teams(bot))