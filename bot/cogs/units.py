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
	async def move_units(self, ctx: discord.ApplicationContext, base: int, destination: int, quantity: int):
		if isinstance(ctx, discord.ApplicationContext): await ctx.defer()

		game: models.Game = load_game(ctx.guild.id)

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

		if quantity > ctr1.get_units(1): # Pas la peine de déclencher une erreur
			quantity = ctr1.get_units(1)

		initial_team = game.get_team(ctr2.team) # Utils pour la suite

		cqr = game.conquest(ctr1, ctr2, quantity, hex(ctx.author.id)[2:].upper())
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
			await self.reply(ctx, f"Déplacement de **{quantity} unités** entre deux terres alliées (**{ctr1.id}** => **{ctr2.id}**)", file = _result)
		else:
			await self.reply(ctx, embed = embeds.ig.conquest_response(cqr, ctr2, quantity), file = _result)

			if initial_team:
				for p in initial_team.members.values():
					member = self.bot.get_user(p.id)

					if (member and member.can_send()):
						await member.send(embed = embeds.info.defense_response(cqr, ctr2, quantity, ctr1.team))

		await matchmaking.Matchmaking(self.bot).top_team(ctx)
		await matchmaking.Matchmaking(self.bot).top_solo(ctx)

def setup(bot):
	bot.add_cog(Units(bot))