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
	async def prepare_game(self, ctx: discord.ApplicationContext):
		if ctx.author.guild_permissions.manage_events:
			game: models.Game = models.Game(ctx.guild.id)
			game.load(new = True)

			game.lastRefresh = round(time.time())
			game.save()

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

	@leaderboard.command(name = "solo")
	async def top_solo(self, ctx: discord.ApplicationContext):
		game: models.Game = load_game(ctx.guild.id)

		calc_score = lambda stats: (.5 * stats['moves']) + (1.5 * stats['attacks']) + (2 * stats['score']) + (15 * stats['continents'] + (2.5 * stats['continent_theft']))
		top = sorted(game.list_players(), key = lambda p: calc_score(p.stats), reverse = True)

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
					str(i + 1) + '-'

			body.append(f"{emoji} <@{soldier.id}> ({calc_score(soldier.stats)}pts)")

		embed = discord.Embed(title = title, description = '\n'.join(body), color = color)

		await ctx.send_response(embed = embed)

	@leaderboard.command(name = "global")
	async def top_team(self, ctx: discord.ApplicationContext):
		game: models.Game = load_game(ctx.guild.id)

		top = sorted(game.teams, key = lambda t: len(t.countries), reverse = True)

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
					str(i + 1) + '-'

			body.append(f"{emoji} **{team.name}** ({len(team.countries)} pays)")

		embed = discord.Embed(title = title, description = '\n'.join(body), color = color)

		await ctx.send_response(embed = embed)