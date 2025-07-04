import cairosvg
from io import BytesIO
import json
import math
import time

import discord

from game import models

def setenv(key: str, val: str) -> None:
	with open('.env', 'r') as buffer:
		lines = buffer.readlines()

	with open('.env', 'w') as buffer:
		for line in lines:
			if line.upper().startswith(key.upper() + "="):
				line = f"{key.upper()}={val}\n"

			buffer.write(line)

COLORS = {
	"white": 0xffffff,
	"gray": 0xe5e9f3,
	"grey": 0xbbbbbb,
	"black": 0x000000,
	"brown": 0x663300,
	"communism": 0xbb0022,
	"red": 0xee0022,
	"orange": 0xff551a,
	"amber": 0xffaa22,
	"yellow": 0xffdd22,
	"lime": 0xaaff22,
	"lightgreen": 0x22ff11,
	"green": 0x22cc22,
	"turquoise": 0x00bb99,
	"lightblue": 0x22bbff,
	"blue": 0x2255ff,
	"darkblue": 0x2222ee,
	"indigo": 0x4433ff,
	"purple": 0x9900ff,
	"magenta": 0xbb00ff,
}

def load_game(id: int) -> models.Game:
	game = models.Game(id)
	game.load()
	return game

def checkName(name: str) -> bool:
	if len(name) > 24:
		return False

	for char in name:
		if char not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789éèàâêçÉôûîÎëÔ'- ":
			return False

	return True

def rgbDistance(clr1: str | int, clr2: str | int) -> bool:
	tolerance = 40

	r1, g1, b1 = (clr1 >> 16) & 0xFF, (clr1 >> 8) & 0xFF, clr1 & 0xFF
	r2, g2, b2 = (clr2 >> 16) & 0xFF, (clr2 >> 8) & 0xFF, clr2 & 0xFF

	distance = math.sqrt((r2 - r1) ** 2 + (g2 - g1) ** 2 + (b2 - b1) ** 2)
	return distance < tolerance

def fillCountry(content: str, color: str, id: int):
	items = content.split('\n')

	newItems = []

	for item in items:
		if f'id="c{id}"' in item:
			newItems.append(item.replace('fill="#6CAF54"', f'fill="#{color.zfill(6)}"'))
		else:
			newItems.append(item)

	return '\n'.join(newItems)

def editCount(content: str, text: str, id: int):
	items = content.split('\n')

	newItems = []

	for item in items:
		if item.startswith(f'<text id="n{id}"'):
			newItems.append(item.replace(f'>{id}<', f'>{text}<'))
		else:
			newItems.append(item)

	return '\n'.join(newItems)

def svg_png(path: str) -> discord.File:
	tag = round(time.time())
	cairosvg.svg2png(url = path, write_to = f'.local/cache/output_{tag}.png', dpi = 300)

	with open(f'.local/cache/output_{tag}.png', 'rb') as _buffer:
		pngdata = BytesIO(_buffer.read())

	return discord.File(pngdata, filename = f'map.png')

class GuildConfig:
	def __init__(self, id: int):
		self.id: str = hex(id)[2:].upper()

		self.topSoloMessage: int = 0 # Message correspondant au leaderboard solo
		self.topTeamMessage: int = 0 # Message correspondant au leaderboard collectif
		self.topChannel: int = 0 # Salon où les messages ci-dessus doivent être envoyés

	def _load(self, _data: dict = {}):
		self.topSoloMessage: int = int(_data.get('topMessage', {}).get('solo', 0))
		self.topTeamMessage: int = int(_data.get('topMessage', {}).get('team', 0))
		self.topChannel: int = int(_data.get('topChannel', 0))

	def _to_dict(self):
		config = {
			'topMessage': {
				'solo': self.topSoloMessage,
				'team': self.topTeamMessage
			},
			'topChannel': self.topChannel
		}

		return config

	def load(self):
		try:
			with open(f'.local/data/config/{self.id}.json') as _file:
				data = json.load(_file)
		except FileNotFoundError:
			with open('assets/initial_config.json') as _file:
				data = json.load(_file)

		self._load(data)

	def save(self):
		with open(f'.local/data/config/{self.id}.json', 'w') as _file:
			json.dump(self._to_dict(), _file, indent = 4)

def load_config(id: int) -> GuildConfig:
	config = GuildConfig(id)
	config.load()
	return config