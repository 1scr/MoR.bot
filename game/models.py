import json
import math
import random
import time

class Gamerules:
	def __init__(self, _data: dict = {}):
		# Typage forcé des règles

		self.countriesToWin: int = 30 # Nombre de pays pour gagner (30 par défaut)
		self.delayAfterMove: int = 3600 # Temps autorisé entre chaque mouvements (1h par défaut)
		self.isBoostEnabled: bool = True # Prendre en compte les boosts (activés par défaut)
		self.isBoostReversed: bool = True # Inverser l'influence des boosts (désactivé par défaut)
		self.matchmakingWhilePlaying: bool = False # Autoriser la création d'équipes une fois la partie commencée (interdit par défaut)
		self.refreshAmountPerCountry: int = 1 # Nombre moyen d'unités ajoutées à chaque pays lors d'un refresh (0~2 unités par défaut)
		self.refreshRate: int = 1800 # Temps autorisé (en secondes) entre chaque refresh (30min par défaut)

	def _load(self, _data: dict = {}):
		# Typage forcé des règles

		self.countriesToWin: int = int(_data.get('countriesToWin', 30))
		self.delayAfterMove: int = int(_data.get('delayAfterMove', 3600))
		self.isBoostEnabled: bool = bool(_data.get('boosts', {'enabled': True}).get('enabled', True))
		self.isBoostReversed: bool = bool(_data.get('boosts', {'reversed': True}).get('reversed', True))
		self.matchmakingWhilePlaying: bool = bool(_data.get('matchmakingWhilePlaying', False))
		self.refreshAmountPerCountry: int = int(_data.get('refresh', {'amountPerCountry': 1}).get('amountPerCountry', 1))
		self.refreshRate: int = int(_data.get('refresh', {'rate': 1800}).get('rate', 1800))

	def _to_dict(self):
		rules = {
			"boosts": {
				"enabled": self.isBoostEnabled,
				"reversed": self.isBoostReversed
			},
			"countriesToWin": self.countriesToWin,
			"delayAfterMove": self.delayAfterMove,
			"matchmakingWhilePlaying": self.matchmakingWhilePlaying,
			"refresh": {
				"amountPerCountry": self.refreshAmountPerCountry,
				"rate": self.refreshRate
			}
		}

		return rules

class Soldier:
	def __init__(self, id: int):
		self.id = id
		self.chief: bool = False
		self.stats: dict = {
			"moves": 0,
			"attacks": 0,
			"score": 0,
			"continents": 0,
			"continent_theft": 0
		}
		self.team: str = None

	def _load(self, data: dict):
		self.chief = data.get('chief', self.chief)
		self.stats = data.get('stats', self.stats)
		self.team = data.get('team', self.team)

	def _convert(self) -> dict:
		return {
			"chief": self.chief,
			"stats": self.stats
		} # On ne sauvegarde pas le nom de l'équipe dans la db

class Team:
	def __init__(self):
		self.name: str = f"Équipe {random.randint(10000, 99999)}"
		self.color: int = 0x000000
		self.countries: list[int] = []
		self.members: dict[str, Soldier] = {}
		self.invites: list[int] = []
		self.base: int = 1

	def _load(self, data: dict):
		self.name = data.get('name', self.name)
		self.color = data.get('color', self.color)
		self.countries = data.get('countries', self.countries)
		self.invites = data.get('invites', self.invites)
		self.base = int(data.get('base', self.base))

		if 'members' in data.keys():
			for key, member in data['members'].items():
				_m = Soldier(int(key, 16))
				_m._load(member)
				_m.team = self.name

				self.members[key] = _m

	def _convert(self) -> dict:
		return {
			'name': self.name,
			'color': self.color,
			'countries': self.countries,
			'members': { hex(member.id)[2:].upper() : member._convert() for member in self.members.values() },
			'invites': self.invites,
			'base': self.base
		}

	def get_chief(self) -> Soldier | None:
		for member in self.members.values():
			if member.chief:
				return member

class Country:
	def __init__(self, id: int, name: str):
		self.id = id
		self.name: str = name
		self.team: str | None = None
		self.units: list[list[int]] = [] # Une liste de sous-listes avec chacune le nombre d'unités ajoutées et la date de l'action
		self.boost = 1
		self.frontiers: list[int] = []

		self.__rules: Gamerules = Gamerules()

	def _load(self, data: dict, gamerules: Gamerules):
		self.name = data.get('name', self.name)
		self.team = data.get('team', self.team)
		self.units = data.get('units', self.units)
		self.boost = data.get('boost', self.boost)
		self.frontiers = data.get('frontiers', self.frontiers)

		self.__rules = gamerules

	def _convert(self) -> dict:
		return {
			'name': self.name,
			'team': self.team,
			'units': self.units,
			'boost': self.boost,
			'frontiers': self.frontiers
		}

	def get_units(self, mode: int = 0) -> int:
		"""
		Mode
		- 0: total (toutes les unités)
		- 1: attack (seulement les unités reposées)
		- 2: defense (unités reposées et la moitié des unités non reposées)
		"""

		delay = self.__rules.delayAfterMove

		units = 0

		for unit in self.units:
			if mode == 0 or unit[0] <= 0:
				units += unit[0]
			elif mode == 1 and unit[1] + delay <= round(time.time()):
				units += unit[0]
			elif mode == 2:
				if unit[1] + delay <= round(time.time()):
					units += unit[0]
				else:
					units += .75 * unit[0]

		return round(units) if units >= 0 else 0

	def get_continent(self) -> str:
		if 0 < self.id <= 9: return "Amérique du Nord"
		elif 10 <= self.id <= 13: return "Amérique du Sud"
		elif 14 <= self.id <= 20: return "Europe"
		elif 21 <= self.id <= 32: return "Asie"
		elif 32 <= self.id <= 38: return "Afrique"
		elif 38 <= self.id <= 42: return "Océanie"

class Game:
	def __init__(self, id: int):
		self.id: str = hex(id)[2:].upper()
		self.countries: dict[str, Country] = {}
		self.teams: list[Team] = []

		self.startDate: int = 0 # Date de démarrage du jeu
		self.update: int = 0 # Dernière activité
		self.lastRefresh: int = 0 # Dernier refresh des unités
		self.open: bool = False # En pause ou non

		self.rules = Gamerules()

	def __generate_json(self):
		countries = {}
		teams = []

		countries = { key: country._convert() for key, country in self.countries.items() }
		teams = [ team._convert() for team in self.teams ]

		return {
			'started': self.startDate,
			'updated': self.update,
			'refreshed': self.lastRefresh,
			'open': self.open,
			'rules': self.rules._to_dict(),
			'teams': teams,
			'countries': countries
		}

	def __is_registered(self) -> bool:
		try:
			with open(f'.local/data/games/{self.id}.json'):
				return True
		except FileNotFoundError:
			return False

	def __get_data(self, new: bool = False) -> dict:
		if self.__is_registered() and not new:
			with open(f'.local/data/games/{self.id}.json', encoding = 'UTF-8') as _data:
				return json.loads(_data.read())
		else:
			with open('assets/initial_game.json', encoding = 'UTF-8') as _data:
				return json.loads(_data.read())

	class ConquestResponse:
		def __init__(self):
			self.losses = 0
			self.score = 0
			self.won = False
			self.is_ally = False
			self.stole_continent = False

	def conquest(self, _from: Country, target: Country, attackers: int, author_id: str) -> ConquestResponse:
		cqr = self.ConquestResponse()
		author = self.get_team(_from.team)
		victim = self.get_team(target.team)

		defenders = target.get_units(2)
		base = defenders
		base_owner = self.get_continent_owner(target.get_continent())

		soldier = author.members[author_id]

		if target.get_units(0) == 0 or target.team == author.name:
			if target.team == author.name:
				cqr.is_ally = True
				soldier.stats['moves'] += 1
			else:
				soldier.stats['attacks'] += 1
				soldier.stats['score'] += 1

			if base_owner != self.get_continent_owner(target.get_continent()):
				if base_owner:
					cqr.continent_action = 'stolen'
					soldier.stats['continent_theft'] += 1
				else:
					cqr.continent_action = 'conquested'
					soldier.stats['continents'] += 1

			cqr.won = True

			target.team = author.name

			_from.units.append([ -attackers, round(time.time()) ])
			target.units.append([ attackers, round(time.time()) ]) # Comptabilisation des gains
		else:
			soldier.stats['attacks'] += 1

			_from.units.append([ -attackers, round(time.time()) ])

			while attackers > 0 and defenders > base / 10:
				if random.randint(0, 100) > 30:
					defenders -= 1
					cqr.score += 1

				if random.randint(0, 100) > 40:
					attackers -= 1
					cqr.losses += 1

			target.units.append([ -(base - defenders), round(time.time()) ]) # Comptabilisation des pertes

			if defenders <= base / 10:
				target.team = author.name
				author.countries.append(target.id)
				if victim: victim.countries.remove(target.id)

				target.units.append([ attackers, round(time.time()) ]) # Comptabilisation des gains

				if base_owner != self.get_continent_owner(target.get_continent()):
					if base_owner:
						cqr.continent_action = 'stolen'
						soldier.stats['continent_theft'] += 1
					else:
						cqr.continent_action = 'conquested'
						soldier.stats['continents'] += 1

				soldier.stats['score'] += 1
				cqr.won = True

		if random.randint(0, 9) == 0:
			self.refresh() # Refresh au hasard

		self.save()

		return cqr

	def get_continent_countries(self, name: str) -> list[str]:
		if name == "Afrique": # +5
			return list(map(str, range(33, 39)))
		elif name == "Amérique du Nord": # +3
			return list(map(str, range(1, 10)))
		elif name == "Amérique du Sud": # +3
			return list(map(str, range(10, 14)))
		elif name == "Asie": # +7
			return list(map(str, range(21, 33)))
		elif name == "Europe": # +5
			return list(map(str, range(14, 21)))
		elif name == "Océanie": # +2
			return list(map(str, range(39, 43)))
		elif name == "Eurasie": # +6 (+20 au total)
			return list(map(str, range(14, 33)))
		elif name == "Amérique": # +4 (+10 au total)
			return list(map(str, range(1, 14)))
		else:
			return []

	def get_continent_owner(self, name: str) -> str:
		countries = self.get_continent_countries(name)

		old_name = None

		for ctr in countries:
			country = self.countries[ctr]

			if country.team != old_name:
				if old_name:
					return
				else:
					old_name = country.team
			elif not country.team:
				return
			else:
				continue

		return old_name

	def list_players(self) -> list[Soldier]:
		players = []

		for team in self.teams:
			for player in team.members.values():
				players.append(player)

		return players

	def get_team(self, name: str = None, color: str = None) -> Team | None:
		for team in self.teams:
			if team.name == name or team.color == color:
				return team

	def delete_team(self, name: str = None, color: str = None):
		team = self.get_team(name, color)

		if not team:
			return

		new_teams: list[Team] = []

		for _team in self.teams:
			if _team.name != team.name:
				new_teams.append(_team)

		self.teams = new_teams.copy()

	def fetch_player(self, id: int) -> Soldier | None:
		_id = hex(id)[2:].upper()
		for team in self.teams:
			if _id in team.members.keys():
				return team.members[_id]

	def has_started(self) -> bool:
		return self.startDate != 0 # Si la date a été modifiée c'est que le jeu a commencé

	def refresh(self, times: int = 1) -> None:
		_boosts = {
			"Afrique": 5,
			"Amérique du Nord": 4,
			"Amérique du Sud": 3,
			"Asie": 7,
			"Europe": 5,
			"Océanie": 2,
			"Eurasie": 6,
			"Amériques": 4
		}

		for country in self.countries.values():
			rules = self.rules

			if rules.isBoostEnabled:
				if rules.isBoostReversed:
					boost = 1 / country.boost
				else:
					boost = country.boost
			elif country.team or country.get_units() == 0:
				boost = 1
			else:
				boost = 0

			amount = math.ceil(random.randint(0, rules.refreshAmountPerCountry) * boost) * times


			# Boosts par continents

			continent = country.get_continent()

			if self.get_continent_owner(continent) and _boosts[continent] > 0:
				amount += 1
				_boosts[continent] -= 1

			# Boosts par double continent

			if continent in ("Europe", "Asie") and self.get_continent_owner("Eurasie") and _boosts["Eurasie"] > 0:
				amount += 1
				_boosts["Eurasie"] -= 1

			if continent in ("Amérique du Nord", "Amérique du Sud") and self.get_continent_owner("Amériques") and _boosts["Amériques"] > 0:
				amount += 1
				_boosts["Amériques"] -= 1

			country.units.append([ amount, 0 ])

	def save(self) -> None:
		if self.open and self.update != 0:
			# Partie non commencée => Pas de refresh

			refreshes_missed = math.floor((time.time() - self.lastRefresh) / self.rules.refreshRate)

			if refreshes_missed > 0:
				self.refresh(times = 1) # On se contera de faire les refreshes un par un
				self.lastRefresh = round(time.time())

		self.update = round(time.time())

		with open(f'.local/data/games/{self.id}.json', 'w', encoding = 'utf-8') as f:
			json.dump(self.__generate_json(), f, indent = 4, ensure_ascii = False)

	def load(self, new: bool = False) -> None:
		data = self.__get_data(new)

		self.startDate = data.get('started', self.startDate)
		self.update = data.get('updated', self.update)
		self.lastRefresh = data.get('refreshed', self.lastRefresh)
		self.open = data.get('open', self.open)

		try:
			self.rules._load(data.get('rules'))
		except:
			print(f"Error loading game {data.get('id')}: Game rules not properly defined. Some rules may stay in default config.")
			pass

		teams = data.get('teams', [ team._convert() for team in self.teams ])
		countries = data.get('countries', { key: country._convert() for key, country in self.countries.items() })

		self.teams, self.countries = [], {}

		for team in teams:
			model = Team()
			model._load(team)

			self.teams.append(model)

		for key, country in countries.items():
			model = Country(int(key), country['name'])
			model._load(country, self.rules)

			self.countries[key] = model