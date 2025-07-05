import random
import time

import discord
from discord.ext import commands

from bot.utils import *
from bot import embeds
from game import models

class Matchmaking(commands.Cog):
	def __init__(self, bot: discord.Bot):
		self.bot = bot

	matchmaking = discord.SlashCommandGroup('game', 'Commandes pour gérer le jeu')
	leaderboard = discord.SlashCommandGroup('leaderboard', 'Commandes du leaderboard')
	gamerules = discord.SlashCommandGroup('gamerules', 'Commandes permettant de modifier les règles')

	@matchmaking.command(name = 'new')
	@discord.default_permissions(manage_events = True)
	async def prepare_game(self, ctx: discord.ApplicationContext, info_channel: discord.TextChannel):
		if ctx.author.guild_permissions.manage_events:
			game: models.Game = models.Game(ctx.guild.id)
			game.load(new = True)

			game.lastRefresh = round(time.time())
			game.save()

			config: GuildConfig = GuildConfig(ctx.guild.id)
			config.topChannel = info_channel.id
			config.save()

			await ctx.send_response(embed = embeds.mm.gameCreated(game.rules))
		else:
			await ctx.send_response(embed = embeds.noPermEmbed())

	@matchmaking.command(name = "start")
	@discord.default_permissions(manage_events = True)
	async def start_game(self, ctx: discord.ApplicationContext):
		if ctx.author.guild_permissions.manage_events:
			game: models.Game = load_game(ctx.guild.id)

			if game.has_started():
				await ctx.send_response(embed = embeds.mm.gameAlreadyStarted())
				return

			game.startDate = round(time.time())
			game.lastRefresh = 0
			game.open = True

			for team in game.teams:
				ctr = str(random.randint(1, 44))
				while game.countries[ctr].team:
					ctr = str(random.randint(1, 44))

				country = game.countries[ctr]

				country.team = team.name
				country.units.append([ 5, round(time.time()) - game.rules.delayAfterMove ]) # 5 unités gratuites pour pas se retrouver coincé par les no mans land

				team.base = country.id
				team.countries.append(country.id)

			game.save()

			await ctx.send_response(embed = embeds.mm.gameStarted(game.rules))
		else:
			await ctx.send_response(embed = embeds.noPermEmbed())

	@matchmaking.command(name = 'switch')
	@discord.default_permissions(manage_events = True)
	async def switch_state(self, ctx: discord.ApplicationContext, pause: bool | None = None):
		game: models.Game = load_game(ctx.guild.id)

		if pause is None:
			game.open = bool(1 - game.open)
		else:
			game.open = pause

		game.save()

		if game.open:
			await ctx.send_response("La partie a repris.")
		else:
			await ctx.send_response("La partie est temporairement suspendue.")

	@leaderboard.command(name = "update")
	async def update_leaderboard(self, ctx: discord.ApplicationContext):
		await self.top_solo(ctx)
		await self.top_team(ctx)

		await ctx.send_response("Le classement a bien été mis à jour.", ephemeral = True)

	async def top_solo(self, ctx: discord.ApplicationContext):
		# Pas de réponse ni de defer() car la commande est censée avoir reçu une réponse antérieurement

		game: models.Game = load_game(ctx.guild.id)
		config: GuildConfig = load_config(ctx.guild.id)

		calc_score = lambda stats: (.5 * stats['moves']) + (1.5 * stats['attacks']) + (2 * stats['score']) + (15 * stats['continents'])
		top = sorted(game.list_players(), key = lambda p: calc_score(p.stats))

		# Embed
		title = ":trophy: Classement individuel"
		body = [
			f"_Mis à jour <t:{round(time.time())}:R>_",
			""
		]
		color = discord.Color(0x123456)

		for i, soldier in enumerate(top):
			emoji = ':first_place:' if i == 0 else\
					':second_place:' if i == 1 else\
					':third_place:' if i == 2 else\
					(i + 1) + '-'

			body.append(f"{emoji} <@{soldier.id}> ({calc_score(soldier.stats)}pts)")

		embed = discord.Embed(title = title, description = '\n'.join(body), color = color)

		# Envoi du message
		if config.topSoloMessage == 0:
			if config.topChannel == 0:
				print("No top channel defined.")
				return

			channel: discord.TextChannel = self.bot.get_channel(config.topChannel)

			if not channel:
				print("Channel not found.")
				return

			message = await channel.send(embed = embed)

			config.topSoloMessage = message.id
			config.save()
		else:
			message = self.bot.get_message(config.topSoloMessage)

			if not message:
				print("Message not found.")
				return

			await message.edit(embed = embed)

	async def top_team(self, ctx: discord.ApplicationContext):
		# Pas de réponse ni de defer() car la commande est censée avoir reçu une réponse antérieurement

		game: models.Game = load_game(ctx.guild.id)
		config: GuildConfig = load_config(ctx.guild.id)

		top = sorted(game.teams, key = lambda t: len(t.countries))

		# Embed
		title = ":trophy: Classement collectif"
		body = [
			f"_Mis à jour <t:{round(time.time())}:R>_",
			""
		]
		color = discord.Color(0x123456)

		for i, team in enumerate(top):
			emoji = ':first_place:' if i == 0 else\
					':second_place:' if i == 1 else\
					':third_place:' if i == 2 else\
					(i + 1) + '-'

			body.append(f"{emoji} **{team.name}** ({len(team.countries)} pays)")

		embed = discord.Embed(title = title, description = '\n'.join(body), color = color)

		# Envoi du message
		if config.topTeamMessage == 0:
			if config.topChannel == 0:
				print("No top channel defined.")
				return

			channel: discord.TextChannel = self.bot.get_channel(config.topChannel)

			if not channel:
				print("Channel not found.")
				return

			message = await channel.send(embed = embed)

			config.topTeamMessage = message.id
			config.save()
		else:
			message = self.bot.get_message(config.topTeamMessage)

			if not message:
				print("Message not found.")
				return

			await message.edit(embed = embed)

def setup(bot):
	bot.add_cog(Matchmaking(bot))