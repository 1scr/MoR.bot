import math
import os
import random
import time

from deta import Deta

deta = Deta(os.getenv('DBKEY'))
games = deta.Base('games')
ldb = deta.Base('leaderboard')

def startctr() -> list[dict]:
	"""
	Génération des pays dans leur état premier (défini dans /utils/ctrdata)
	"""
	data = []

	with open('./utils/ctrdata/attributes.txt') as _data:
		for ctr in _data.read().split('\n'):
			data.append(dict(zip(['difficulty', 'startnb', 'isSpawner'], [ int(ctr.split(' ')[0]), int(ctr.split(' ')[1]), bool(int(ctr.split(' ')[2])) ])))
		
	with open('./utils/ctrdata/names.txt', encoding = 'UTF-8') as _file:
		names = _file.read().split('\n')

		for i in range(len(data)):
			data[i]['name'] = names[i]

	with open('./utils/ctrdata/frontiers.txt') as _file:
		frontiers = _file.read().split('\n')

		for i in range(len(data)):
			data[i]['frontiers'] = frontiers[i].split(' ')
	
	return data

ctrinfo = startctr()

class Team:
	def __init__(self):
		self.name: str = f"Équipe {random.randint(10000, 99999)}"
		self.color: str = "#000000"
		self.countries: list[int] = []
		self.members: list[int] = [ 0 ]
		self.invites: list[int] = []
		self.chief: int = 0
	
	def _load(self, data: dict):
		self.name = data.get('name', self.name)
		self.color = data.get('color', self.color)
		self.countries = data.get('countries', self.countries)
		self.members = [ int(id) for id in data.get('members', self.members) ]
		self.invites = [ int(id) for id in data.get('invites', self.invites) ]
		self.chief = int(data.get('chief', self.chief))
	
	def _convert(self) -> dict:
		data = self.__dict__
		data['chief'] = str(self.chief)
		data['members'] = [ str(id) for id in self.members ]
		data['invites'] = [ str(id) for id in self.invites ]

		return data

class Country:
	def __init__(self, name: str):
		self.name: str = name
		self.team: str = 'Neutre'
		self.chief: int = 0
		self.units: list[int] = random.randint(5, 10) * [ 0 ]
		self.missiles: int = 0
		self.boost = 1
		self.isSpawner = False

	def get_id(self) -> int:
		i = 0
		for ctr in ctrinfo:
			if ctr['name'] == self.name:
				return i
			
			i += 1

	def nuke(self, author: Team) -> int:
		losses = random.randint(60, 90) / 100
		for u in range(math.ceil(len(self.units) * losses)):
			self.units.pop(0)
		
		if len(self.units) < 10:
			self.team = author.name
		
		return losses

	def _load(self, data: dict):
		self.name = data.get('name', self.name)
		self.team = data.get('team', self.team)
		self.chief = int(data.get('chief', self.chief))
		self.units = [ int(id) for id in data.get('units', self.units) ]
		self.missiles = data.get('missiles', self.missiles)
		self.boost = data.get('boost', self.boost)
		self.isSpawner = data.get('isSpawner', self.isSpawner)

	def _convert(self) -> dict:
		data = self.__dict__

		data['units'] = [ str(unit) for unit in data ('units') ]

		return data
	
class Game:
	def __init__(self, id: int):
		self.id: int = id
		self.countries: list[Country] = []
		self.teams: list[Team] = []
		self.lastrefresh: int = 0
		self.privacy = False

		tm = Team()
		tm.name = 'Neutre'
		tm.color = '0x6CAF54'

		i = 0
		for ctr in ctrinfo:
			country = Country(ctr['name'])
			country.units = ctr['startnb'] * [ 0 ]
			country.boost = ctr['difficulty']
			country.isSpawner = ctr['isSpawner']

			self.countries.append(country)
			tm.countries.append(i)
			
			i += 1
		
		self.teams.append(tm)

	class Player:
		def __init__(self, id: int):
			self.id = id
			self.team: Team | None = None
			self.score = 0 # À venir

	class ConquestResponse:
		def __init__(self):
			self.oldchief = 0
			self.losses = 0
			self.score = 0
			self.won = False
			self.rewards: dict = {'planes': 0, 'missiles': 0}

	def conquest(self, _from: Country, target: Country, attackers: int) -> ConquestResponse:
		"""
		Fonction de conquête d'un pays. 40% de chances pour une victoire, 30% pour une défaite, 30% de match nul (à soldats égaux)
		"""
		cqr = self.ConquestResponse()
		cqr.oldchief = target.chief
		author = self.fetch_team(_from.team)

		defenders = len(target.units)
		base = defenders

		while attackers > 0 and defenders > base / 10:
			if random.randint(0, 100) > 30:
				defenders -= 1
				cqr.score += 1

			if random.randint(0, 100) > 40:
				attackers -= 1
				cqr.losses += 1

		if attackers != 0:
			self.fetch_team(target.team).countries.remove(target.get_id())
			author.countries.append(target.get_id())

			target.team = author.name
			target.chief = author.chief
			target.units =  attackers * [ round(time.time()) ]
			_from.units += math.ceil(base / (5 if target.boost == 1 else 2 if target.boost == 2 else 1.25)) * [ 0 ] # On offre un pourcentage de soldats tous neufs à l'attaquant
			
			if target.boost == 2:
				cqr.rewards['planes'] += random.randint(0, 2)
				cqr.rewards['missilers'] += random.randint(0, 1)
			elif target.boost == 3:
				cqr.rewards['planes'] += random.randint(3, 6)
				cqr.rewards['missiles'] += random.randint(1, 3)

			cqr.won = True
		else:
			target.units = defenders * [ 0 ] # Une attaque leur permet d'être prêts au combat (à revoir)
		
		return cqr
	
	def refresh(self):
		for country in ctrinfo:
			add = 0
			ctr = self.fetch_country(country['name'])
			if len(ctr.units) < (1000 * country['difficulty']) / 7:
				add = country['difficulty'] ** 2

			ctr.units += add * [ 0 ] 

	def fetch_team(self, name: str = '', color: str = '', chief: int = 0) -> Team | None:
		for team in self.teams:
			if team.name == name or team.color == color or team.chief == chief:
				return team
		
		return None
	
	def fetch_country(self, name: str = '') -> Country | None:
		for country in self.countries:
			if country.name == name:
				return country
		
		return None
	
	def fetch_player(self, id: int) -> Player | None:
		pl = self.Player(id)

		for team in self.teams:
			if id in team.members:
				pl.team = team
				break
		else:
			pl = None
		
		return pl
	
	def _load(self, data: dict):
		self.id = data.get('key', self.id)
		self.lastrefresh = data.get('lastRefresh', self.lastrefresh)
		self.privacy = data.get('privacy', self.privacy)

		if data.get('teams', None) is not None:
			for team in data['teams']:
				tm = Team()
				tm._load(team)

				self.teams.append(tm)
		
		if data.get('countries', None) is not None:
			for country in data['countries']:
				ctr = Country(country['name'])
				ctr._load(country)

				self.countries.append(ctr)

	def _convert(self) -> dict:
		data = {}

		data = self.__dict__
		del data['id']
		data['teams'] = [ team._convert() for team in self.teams ]
		data['countries'] = [ country._convert() for country in self.countries ]

		return data

	def save(self) -> None:
		games.put(key = str(self.id), data = self._convert())