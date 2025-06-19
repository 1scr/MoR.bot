import io

import discord
from discord.ext import commands

from bot.utils import *
from bot import embeds
from game import models

class MiniMap(commands.Cog):
	def __init__(self, bot: discord.Bot):
		self.bot = bot

	minimap = discord.SlashCommandGroup('map', 'Commandes pour afficher la map')
	countries = discord.SlashCommandGroup('country', 'Commandes pour gérer les pays')

	async def reply(self, ctx: discord.ApplicationContext | discord.Message, **kwargs):
		if isinstance(ctx, discord.ApplicationContext):
			await ctx.send_response(**kwargs)
		elif isinstance(ctx, discord.Message):
			await ctx.reply(**kwargs)
		else:
			try:
				ctx.reply("Erreur lors de la réponse du bot.")
			except:
				pass

			print(f"Asked for Message, got {type(ctx)}")

	async def display_fastmap(self, ctx: discord.Message):
		game: models.Game = load_game(ctx.guild.id)

		with open('assets/map.svg') as _buffer:
			_map = _buffer.read()

		for ctr in game.countries.values():
			if ctr.team:
				_map = fillCountry(_map, hex(game.get_team(ctr.team).color).replace('0x', ''), ctr.id)

			_map = editCount(_map, "{} - {}/{}".format(str(ctr.id).zfill(2), ctr.get_units(1), ctr.get_units(0)), ctr.id)

		with open(f'.local/_map_cache/{ctx.author.id}.svg', 'w', encoding = 'UTF-8') as _buffer:
			_buffer.write(_map)

		_result = svg_png(f'.local/_map_cache/{ctx.author.id}.svg')

		game.save() # Refresh si besoin

		await ctx.reply(file = _result)

	@minimap.command(name = 'display')
	async def display_map(self, ctx: discord.ApplicationContext):
		await ctx.defer()

		game: models.Game = load_game(ctx.guild.id)

		with open('assets/map.svg') as _buffer:
			_map = _buffer.read()

		for ctr in game.countries.values():
			if ctr.team:
				_map = fillCountry(_map, hex(game.get_team(ctr.team).color).replace('0x', ''), ctr.id)

			_map = editCount(_map, "{} - {}".format(str(ctr.id).zfill(2), ctr.name), ctr.id)

		with open(f'.local/_map_cache/{ctx.author.id}.svg', 'w', encoding = 'UTF-8') as _buffer:
			_buffer.write(_map)

		_result = svg_png(f'.local/_map_cache/{ctx.author.id}.svg')

		game.save() # Refresh si besoin

		await ctx.send_followup(file = _result)


	@minimap.command(name = 'units')
	async def display_map_units(self, ctx: discord.ApplicationContext):
		await ctx.defer()

		game: models.Game = load_game(ctx.guild.id)

		with open('assets/map.svg') as _buffer:
			_map = _buffer.read()

		for ctr in game.countries.values():
			if ctr.team:
				_map = fillCountry(_map, hex(game.get_team(ctr.team).color).replace('0x', ''), ctr.id)

			_map = editCount(_map, "{}/{}".format(ctr.get_units(1), ctr.get_units(0)), ctr.id)

		with open(f'.local/_map_cache/{ctx.author.id}.svg', 'w', encoding = 'UTF-8') as _buffer:
			_buffer.write(_map)

		_result = svg_png(f'.local/_map_cache/{ctx.author.id}.svg')

		game.save() # Refresh si besoin

		await ctx.send_followup(file = _result)


	@minimap.command(name = 'ids')
	async def display_map_ids(self, ctx: discord.ApplicationContext):
		await ctx.defer()

		game: models.Game = load_game(ctx.guild.id)

		with open('assets/map.svg') as _buffer:
			_map = _buffer.read()

		for ctr in game.countries.values():
			if ctr.team:
				_map = fillCountry(_map, hex(game.get_team(ctr.team).color).replace('0x', ''), ctr.id)

		with open(f'.local/_map_cache/{ctx.author.id}.svg', 'w', encoding = 'UTF-8') as _buffer:
			_buffer.write(_map)

		_result = svg_png(f'.local/_map_cache/{ctx.author.id}.svg')

		game.save() # Refresh si besoin

		await ctx.send_followup(file = _result)


	@minimap.command(name = 'continents')
	async def display_map_continents(self, ctx: discord.ApplicationContext):
		await ctx.defer()

		with open('assets/map_continents.png', 'rb') as _buffer:
			_map = _buffer.read()

		data = io.BytesIO(_map)
		_file = discord.File(data, filename = 'map.png')

		game: models.Game = load_game(ctx.guild.id)
		game.save() # On provoque un refresh si besoin

		await ctx.send_followup(file = _file)


	# Commandes de gestion des pays

	@countries.command(name = 'rename')
	async def rename_country(self, ctx: discord.ApplicationContext, id: int, name: str):
		await ctx.defer()

		game: models.Game = load_game(ctx.guild.id)

		country = game.countries.get(str(id))

		if not country:
			await ctx.send_followup("Ce pays n'existe pas.")
			return

		player = game.fetch_player(ctx.author.id)

		if not player:
			await ctx.send_followup("Vous n'êtes pas dans la partie.")
			return

		if country.team != player.team:
			await ctx.send_followup(f"Le pays {country.name} ne vous appartient pas.")
			return

		if len(name) > 16:
			await ctx.send_followup("Le nom est trop long. 16 caractères maximum.")
			return

		for c in name:
			if c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789éèàâêçÉôûîÎëÔ'- ":
				await ctx.send_followup(f"Le nom {name} ne peut pas être accepté. Seules les lettres (accents autorisés), les chiffres, l'apostrophe, le trait d'union et les espaces sont autorisés.")
				return

		country.name = name

		game.save()

		await ctx.send_followup("Le pays a été renommé !")

	@countries.command(name = 'info')
	async def info_country(self, ctx: discord.ApplicationContext, id: int):
		game: models.Game = load_game(ctx.guild.id)

		country = game.countries.get(str(id))

		if not country:
			await ctx.send_response("Ce pays n'existe pas.")
			return

		embed = embeds.ig.country_info(country, game)

		game.save()

		await ctx.send_response(embed = embed)

def setup(bot):
	bot.add_cog(MiniMap(bot))