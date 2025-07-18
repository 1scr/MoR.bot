import random
import time

import discord
from discord.ext import commands

from bot.utils import *
from bot.cogs import matchmaking
from bot import embeds
from game import models

class Units(commands.Cog):
	def __init__(self, bot: discord.Bot):
		self.bot = bot

	async def reply(self, ctx: discord.ApplicationContext | discord.Message, content: str = None, **kwargs):
		if isinstance(ctx, discord.ApplicationContext):
			await ctx.send_followup(content, **kwargs)
		elif isinstance(ctx, discord.Message):
			await ctx.reply(content, **kwargs)
		else:
			try:
				await ctx.reply(content, "Erreur lors de la réponse du bot.")
			except:
				pass

			print(f"Asked for ApplicationContext or Message, got {type(ctx)}")

	@discord.slash_command(name = 'move')
	async def move_units(self, ctx: discord.ApplicationContext, base: int, destination: int, quantity: int | None = None):
		if isinstance(ctx, discord.ApplicationContext): await ctx.defer()

		game: models.Game = load_game(ctx.guild.id)

		if not game.open:
			await self.reply(ctx, embed = embeds.ig.gameNotStarted())
			return

		ctr1 = game.countries.get(str(base))
		ctr2 = game.countries.get(str(destination))

		if not ctr1:
			await self.reply(ctx, embed = embeds.ig.wrong_country(base))
			return

		if not ctr2:
			await self.reply(ctx, embed = embeds.ig.wrong_country(destination))
			return

		player = game.fetch_player(ctx.author.id)

		if player is None:
			await self.reply(ctx, "Vous n'appartenez à aucune équipe.")
			return

		if ctr1.team != player.team:
			await self.reply(ctx, embed = embeds.ig.not_your_country(ctr1))
			return

		if ctr2.id not in ctr1.frontiers:
			await self.reply(ctx, embed = embeds.ig.no_frontier(ctr1, ctr2))
			return

		if (not quantity) or quantity > ctr1.get_units(1): # Pas la peine de déclencher une erreur
			quantity = ctr1.get_units(1)

		initial_team = game.get_team(ctr2.team) # Utils pour la suite

		cqr = game.conquest(ctr1, ctr2, quantity, hex(ctx.author.id)[2:].upper())

		refreshed = 0
		if random.randint(1, 10) == 1:
			game.refresh()
			refreshed = 1
		elif random.randint(1, 50) == 1:
			game.refresh(2)
			refreshed = 2
		elif random.randint(1, 100) == 1:
			game.refresh(5)
			refreshed = 5
		elif random.randint(1, 500) == 1:
			game.refresh(10)
			refreshed = 10

		game.save()

		with open('assets/map.svg') as _buffer:
			_map = _buffer.read()

		for ctr in game.countries.values():
			if ctr.team:
				_map = fillCountry(_map, hex(game.get_team(ctr.team).color).replace('0x', ''), ctr.id)

			_map = editCount(_map, "{} - {}/{}".format(ctr.id, ctr.get_units(1), ctr.get_units(0)), ctr.id)

		with open(f'.local/_map_cache/{ctx.author.id}.svg', 'w', encoding = 'UTF-8') as _buffer:
			_buffer.write(_map)

		_result = svg_png(f'.local/_map_cache/{ctx.author.id}.svg')

		if cqr.is_ally:
			await self.reply(ctx, f"Déplacement de **{quantity} unités** entre deux terres alliées, de **{ctr1.name}** ({ctr1.id}) à **{ctr2.name}** ({ctr2.id})", file = _result)
		else:
			await self.reply(ctx, embed = embeds.ig.conquest_response(cqr, ctr2, quantity), file = _result)

			if initial_team:
				for p in initial_team.members.values():
					member = self.bot.get_user(p.id)

					if (member and member.can_send()):
						await member.send(embed = embeds.info.defense_response(cqr, ctr2, quantity, ctr1.team))

		if refreshed == 1:
			embed = discord.Embed(
				title = "Pas mal",
				description = "Vous avez déclenché un refresh en attaquant. Chaque attaque offre 10% de chances de déclencher un refresh.",
				color = 0x123456
			)
		elif refreshed == 2:
			embed = discord.Embed(
				title = "Coup double !",
				description = "Vous avez déclenché un **double refresh** en attaquant. Chaque attaque offre 5% de chances de déclencher un double refresh.",
				color = 0x123456
			)
		elif refreshed == 5:
			embed = discord.Embed(
				title = "Il pleut des unités :military_helmet:",
				description = "Vous avez déclenché un __**mega refresh**__ (5 refresh) en attaquant. Chaque attaque offre 2% de chances de déclencher un mega refresh.",
				color = 0x123456
			)
		elif refreshed == 10:
			embed = discord.Embed(
				title = "DROP THE BOMB :lips:",
				description = "Vous avez déclenché un __**GIGA REFRESH**__ (10 refresh) en attaquant. Chaque attaque offre 1% de chances de déclencher un giga refresh.",
				color = 0x123456
			)

		team = game.get_team(player.team)

		if len(team.countries) == game.rules.countriesToWin:
			embed = discord.Embed(
				title = "Victoire !",
				description = f"Vous avez atteint {game.rules.countriesToWin}"
			)

		if refreshed != 0:
			await self.reply(ctx, embed = embed)

		if cqr.won or cqr.is_ally:
			save_map(game)

	@discord.slash_command(name = "next-refresh")
	async def refresh_info(self, ctx: discord.ApplicationContext):
		game: models.Game = load_game(ctx.guild.id)

		last = game.lastRefresh
		rate = game.rules.refreshRate
		next = last + rate
		amount = game.rules.refreshAmountPerCountry

		if next < round(time.time()):
			next = round(time.time())

		embed = discord.Embed(
			title = "Infos refresh",
			description = embeds.noTab(f"""
			**Prochain refresh:** <t:{next}:R>
			**Intervalle des refresh:** {rate // 60} minutes
			**Unités par pays\\*:** {amount} par refresh

			> Les unités par pays sont le nombre basique d'unités rajoutées. Celui-ci peut changer en fonction de différents paramètres (le pays concerné, les différents boosts ou nerfs liés aux équipes ou aux continents, etc.)

			> **Les infos ci-dessus ne prennent pas en compte les refresh dûs aux attaques (une attaque a 10% de chances de déclencher un refresh)**
			""")
		)

		await ctx.send_response(embed = embed)

def setup(bot):
	bot.add_cog(Units(bot))