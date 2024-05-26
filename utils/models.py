import math
import random
import time

def startctr() -> list[dict]:
    data = []

    with open('./utils/ctrdata/attributes.txt') as _data:
        for ctr in _data.read().split('\n'):
            data.append(dict(zip(['difficulty', 'startnb'], [ int(ctr.split(' ')[0]), int(ctr.split(' ')[1]) ])))
        
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
        self.chief: int = 0
    
    def _convert(self) -> dict:
        data = self.__dict__
        data['chief'] = str(self.chief)
        data['members'] = [ str(id) for id in self.members ]

        return data

class Country:
    def __init__(self, name: str):
        self.name: str = name
        self.team: str = 'Neutre'
        self.chief: int = 0
        self.units: list[int] = random.randint(5, 10) * [ 0 ]
        self.missiles: int = 0
        self.boost = 1

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

    def _convert(self) -> dict:
        data = self.__dict__

        return data
    
class Game:
    def __init__(self, id: int):
        self.id: int = id
        self.countries: list[Country] = []
        self.teams: list[Team] = []
        self.lastrefresh: int = 0

        tm = Team()
        tm.name = 'Neutre'
        tm.color = '#6CAF54'

        i = 0
        for ctr in ctrinfo:
            country = Country(ctr['name'])
            country.units = ctr['startnb'] * [ 0 ]
            country.boost = ctr['difficulty']

            self.countries.append(country)
            tm.countries.append(i)
            
            i += 1
        
        self.teams.append(tm)

    class ConquestResponse:
        def __init__(self):
            self.oldchief = 0
            self.losses = 0
            self.score = 0
            self.won = False

    def conquest(self, _from: Country, target: Country, attackers: int) -> ConquestResponse:
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
            _from.units += math.ceil(base / 5) * [ 0 ] # On offre 20% de soldats tous neufs à l'attaquant

            cqr.won = True
        else:
            target.units = defenders * [ 0 ] # Une attaque leur permet d'être prêts au combat (à revoir)
        
        return cqr
    
    def refresh(self):
        for country in ctrinfo:
            add = 0
            ctr = self.fetch_country(country['name'])
            if len(ctr.units) > (1000 * country['difficulty']) / 7:
                add = country['difficulty'] ** 2

            ctr.units += add * [ 0 ] 
            ctr.missiles += country['difficulty'] // 5

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
    
    def _convert(self) -> dict:
        data = {}

        data['id'] = str(self.id)
        data['teams'] = [ team._convert() for team in self.teams ]
        data['countries'] = [ country._convert() for country in self.countries ]

        return data