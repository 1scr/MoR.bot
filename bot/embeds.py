import discord

from game import models

successEmoji = "<:success:1390798534022004806>"
infoEmoji = "<:info:1390798495627218974>"
failEmoji = "<:fail:1390798468141944992>"

def noTab(text: str) -> str:
	return text.replace('    ', '').replace('\t', '')

def errorEmbed(ticket: str) -> discord.Embed:
	title = "Une erreur est survenue..."
	description = f"""Mais pas de panique ! Les développeurs ont été informés en détail et répareront ça en un rien de temps ! Si ils tardent, mentionne-les avec cet identifiant:\n
	```{ticket}```"""
	color = discord.Color.brand_red()

	return discord.Embed(title = title, description = noTab(description), color = color)

def noPermEmbed() -> discord.Embed:
	title = "Hop hop hop !"
	description = f"Tu n'as pas la permission d'effectuer cette commande, que je ne t'y reprenne pas !"
	color = discord.Color.brand_red()

	return discord.Embed(title = title, description = description, color = color)

class MatchEmbeds:
	# -------------------- SUCCÈS --------------------

	def gameCreated(self, gamerules: models.Gamerules) -> discord.Embed:
		title = "Matchmaking en cours..."
		description = f"""
		Le matchmaking a commencé. Pendant cette phase, vous pouvez créer ou trouver une équipe. La carte est déjà visible mais ne faites pas trop de planifications: vous ne savez pas encore où vous allez apparaître.

		Les noms des équipes ne peuvent pas dépasser 24 lettres, et ceux des pays 16 lettres pour des raisons évidentes. Vous ne pouvez pas créer deux équipes avec le même nom ou des couleurs similaires.

		Une fois les équipes créées, vous pouvez demander à votre administrateur de taper la commande `/game start`, qui démarrera la partie et vous donnera vos deux points de spawn. Ils pourront mettre la partie sur pause et la faire reprendre via la commande `/game switch`.
		"""
		color = discord.Color.dark_red()

		return discord.Embed(title = title, description = noTab(description), color = color)

	def gameStarted(self, gamerules: models.Gamerules) -> discord.Embed:
		canMakeTeamWhilePlaying = ("Vous pouvez"  if gamerules.matchmakingWhilePlaying else "Vous ne pouvez pas") + " créer ou rejoindre une équipe pendant le match"

		title = f"{infoEmoji} Bienvenue dans cette partie de World War III !"
		description = f"""
		Vous avez 42 pays à votre disposition. La première équipe a en coloniser {gamerules.countriesToWin} gagne la partie.\n

		## Infos

		### Modalités
		- Lorsque vous déplacez des unités, celles-ci seront immobiles et défendront moins efficacement pendant {round(gamerules.delayAfterMove / 60)} minutes.
		- Toutes les {round(gamerules.refreshRate / 60)} minutes, environ {gamerules.refreshAmountPerCountry * 42} unités apparaissent aléatoirement sur la map.
		- {canMakeTeamWhilePlaying}
		- La partie ne démarrera pas si il n'y a qu'une seule équipe. Pour un jeu optimal, prévoyez 4 à 10 équipes d'au moins deux personnes.

		### Règles
		- Faites pas de vannes sur Hitler qui envahit la Pologne svp c'est drôle 2 minutes mais après c'est juste gênant sah
		- Les règles du serveur s'appliquent


		## Commandes

		### Équipes
		- `/team create <name> <color>`: Créer une équipe
		- `/team join <name>`: Rejoindre l'équipe <name> si on y est invité
		- `/team invite <member>`: Inviter le joueur <member> dans son équipe
		- `/team edit <name> <color>`: Modifier son équipe
		- `/team kick <member>`: Virer <member> de son équipe (ne fonctionne que pour les chefs d'équipe et administrateurs)

		### Guerre
		- `/move units <base (nombre)> <destination (nombre)> <quantity>`: Déplacer <quantity> unités de <base> à <destination>
		- `/country info <ID>`: Se renseigner sur le pays n°<ID>
		- `/country rename <ID> <name>`: Rebaptiser le pays n°<ID> avec le nom <name>

		> :light_bulb: Astuce: Tapez `fmap` pour voir la map rapidement, et `move XX XX XX` (dans le même ordre que la commande ci-dessus) pour déplacer des unités.

		Bonne chance !
		"""
		color = discord.Color.dark_red()

		return discord.Embed(title = title, description = noTab(description), color = color)

	# -------------------- ERREURS --------------------

	def gameAlreadyStarted(self):
		title = "La partie a déjà commencé"
		description = "Utilisez la commande `/game switch` si la partie est en pause et que vous voulez la reprendre. Utilisez `/game new` si vous voulez reprendre de zéro (irréversible)."
		color = discord.Color.brand_red()

		return discord.Embed(title = title, description = description, color = color)


class TeamEmbeds:
	# -------------------- ERREURS --------------------

	def teamNotFound(self, teamName: str) -> discord.Embed:
		title = f"{failEmoji} Cette équipe n'existe pas"
		description = f"Impossible de trouver une équipe nommée « {teamName} » - Réessayez."
		color = discord.Color.brand_red()

		return discord.Embed(title = title, description = description, color = color)

	def notInAnyTeam(self, name: str = None) -> discord.Embed:
		title = f"{failEmoji} Impossible d'effectuer l'action"

		if name:
			description = f"{name} n'appartient à aucune équipe."
		else:
			description = "Vous n'appartenez à aucune équipe."

		color = discord.Color.brand_red()

		return discord.Embed(title = title, description = description, color = color)

	def alreadyInTeam(self, teamName: str) -> discord.Embed:
		title = f"{failEmoji} Vous devez quitter votre équipe"
		description = f"Il vous faut quitter l'équipe _{teamName}_ pour en rejoindre ou en créer une autre."
		color = discord.Color.brand_red()

		return discord.Embed(title = title, description = description, color = color)

	def alreadyExistingName(self, teamName: str) -> discord.Embed:
		title = f"{failEmoji} L'équipe _{teamName}_ existe déjà"
		description = "Choisissez un autre nom ou arrangez-vous avec le chef de l'autre équipe pour la rejoindre."
		color = discord.Color.brand_red()

		return discord.Embed(title = title, description = description, color = color)

	def alreadyExistingColor(self, color: int) -> discord.Embed:
		title = f"{failEmoji} Impossible de prendre cette couleur"
		description = "Votre couleur se rapproche trop de celle d'une équipe déjà existante."
		color = discord.Color(color)

		return discord.Embed(title = title, description = description, color = color)

	def invalidName(self, name: str) -> discord.Embed:
		title = f"{failEmoji} Impossible de prendre ce nom"
		description = f"""Le nom {name} Ne répond pas à l'un des critères suivant:
		- 32 caractères maximum,
		- Seulement les lettres alphanumériques et les espaces
		- Commencer par une majuscule, un peu de sérieux !"""
		color = discord.Color.brand_red()

		return discord.Embed(title = title, description = noTab(description), color = color)

	def invalidColor(self, color: str) -> discord.Embed:
		title = f"{failEmoji} Impossible de prendre cette couleur"
		description = f"Votre couleur `{color}` est invalide car elle ne correspond pas au format hexadécimal: `0xABCDEF` ou `#ABCDEF`"
		color = discord.Color.brand_red()

		return discord.Embed(title = title, description = description, color = color)

	def notInvited(self, author: int) -> discord.Embed:
		title = f"{failEmoji} Vous n'êtes pas invité(e) dans cette équipe"
		description = f"Demandez à <@{author}> de vous inviter dans son équipe pour pouvoir la rejoindre."
		color = discord.Color.brand_red()

		return discord.Embed(title = title, description = description, color = color)

	def gameStarted(self):
		title = "Le matchmaking est terminé !"
		description = "Les règles du jeu ne permettent pas la modification des équipes en match. Demandez à votre administrateur de mettre la partie en pause pour que vous puissiez en rejoindre ou créer une."
		color = discord.Color.brand_red()

		return discord.Embed(title = title, description = description, color = color)

	def gameReallyReallyStarted(self):
		title = "Impossible d'effectuer cette action."
		description = "Le jeu est à un stade où certaines équipes ne peuvent être modifiées afin d'éviter toute injustice."
		color = discord.Color.brand_red()

		return discord.Embed(title = title, description = description, color = color)

	# -------------------- SUCCÈS --------------------

	def teamCreated(self, name: str, color: int, author: int) -> discord.Embed:
		title = f"{successEmoji} Équipe créée avec succès !"
		description = f"""
		**Nom de l'équipe:** {name}
		**Couleur:** `#{hex(color)[2:].zfill(6)}`
		**Chef:** <@{author}>
		""".replace('\t', '')
		color = discord.Color(color)

		return discord.Embed(title = title, description = description, color = color)

	def teamDeleted(self, color: int) -> discord.Embed:
		title = f"{successEmoji} Équipe supprimée avec succès !"
		description = "Les membres peuvent désormais en rejoindre une autre."
		color = discord.Color(color)

		return discord.Embed(title = title, description = description, color = color)

	def teamJoined(self, name: str, author: int, membercount: int) -> discord.Embed:
		title = f"{successEmoji} Équipe rejointe avec succès !"
		description = f"""
		**Nom de l'équipe:** {name}
		**Chef:** <@{author}>
		**Membres:** {membercount}
		""".replace('\t', '')
		color = discord.Color.brand_green()

		return discord.Embed(title = title, description = description, color = color)

	def memberInvited(self, name: str) -> discord.Embed:
		title = f"{successEmoji} Joueur invité avec succès !"
		description = f"{name} vient de recevoir l'invitation dans ses DM, iel peut rejoindre l'équipe à tout moment."
		color = discord.Color.brand_green()

		return discord.Embed(title = title, description = description, color = color)

	# -------------------- INFOS --------------------

	def teamInfos(self, team: models.Team, countries: list[models.Country], gamerules: models.Gamerules) -> discord.Embed:
		_ctries = '\n'.join([ f"- {country.name}" for country in countries ])
		_members = '\n'.join([ f"- <@{int(id, 16)}>" for id in team.members.keys() ])

		title = team.name
		description = f"""
		**Chef:** <@{team.get_chief().id}>

		### Membres ({len(team.members)})
		{_members}

		### Pays ({len(countries)}/{gamerules.countriesToWin})
		{_ctries}
		""".replace('\t', '')
		color = discord.Color(team.color)

		return discord.Embed(title = title, description = description, color = color)

class InGameEmbeds:
	def gameNotStarted(self):
		title = "La partie n'a pas commencé"
		description = "Impossible de bouger des unités pour le moment. Profitez-en pour revoir vos préparatifs."
		color = discord.Color.brand_red()

		return discord.Embed(title = title, description = description, color = color)

	def conquest_response(self, cqr: models.Game.ConquestResponse, ctr: models.Country, amount: int) -> discord.Embed:
		title = f"{successEmoji} Victoire !" if cqr.won else f"{failEmoji} Défaite"
		description = f"""
		Unités envoyées: {amount}
		Score: {cqr.score}
		Pertes: {cqr.losses}

		Il reste {ctr.get_units(0)} unités dans le pays attaqué, {ctr.get_units(1)} d'entre elles peuvent attaquer en retour.
		""".replace('\t', '')
		color = discord.Color.brand_green() if cqr.won else discord.Color.brand_red()

		return discord.Embed(title = title, description = description, color = color)

	def move_response(self, amount: int, ctr1: models.Country, ctr2: models.Country) -> discord.Embed:
		amount = f"{amount:,}".replace(',', ' ')

		title = f"{infoEmoji} Déplacement"
		description = f"""
		**{amount} unités** ont été déplacées de **{ctr1.name}** vers **{ctr2.name}**.
		""".replace('\t', '')
		color = discord.Color.blurple()

		return discord.Embed(title = title, description = description, color = color)

	def country_info(self, ctr: models.Country, game: models.Game) -> discord.Embed:
		_team: models.Team = game.get_team(ctr.team)
		_frontiers: list[models.Country] = [ c for c in game.countries.values() if c.id in ctr.frontiers ]

		if _frontiers:
			frontiers = "- " + '\n- '.join([ f"{f.id} - {f.name}" for f in _frontiers ])
		else:
			frontiers = "_Aucun pays voisin._"

		title = f"{infoEmoji} {ctr.name}"
		description = f"""
		**Continent:** {ctr.get_continent()}
		**Unités:** {ctr.get_units(1)}/{ctr.get_units(0)}

		**Pays voisins:**
		{frontiers}
		""".replace('\t', '')
		color = discord.Color(_team.color)

		return discord.Embed(title = title, description = description, color = color)

	def wrong_country(self, ctr: int) -> discord.Embed:
		title = f"{failEmoji} Ce pays n'existe pas !"
		description = f"""
		Il n'y a aucun pays avec l'ID {ctr}. Corrigez votre commande et vérifiez la carte si nécessaire.
		""".replace('\t', '')
		color = discord.Color.brand_red()

		return discord.Embed(title = title, description = description, color = color)

	def lack_of_units(self, available: int, total: int) -> discord.Embed:
		title = f"{infoEmoji} Vous n'avez pas ce nombre d'unités !"
		description = f"""
		Seulement **{available}** unités ont pu être envoyées sur un total de **{total}** unités.
		""".replace('\t', '')
		color = discord.Color.brand_red()

		return discord.Embed(title = title, description = description, color = color)

	def not_your_country(self, ctr: models.Country) -> discord.Embed:
		title = f"{failEmoji} Ce pays ne vous appartient pas"
		description = f"""
		Le pays {ctr.name} appartient à l'équipe {ctr.team}.
		""".replace('\t', '')
		color = discord.Color.brand_red()

		return discord.Embed(title = title, description = description, color = color)

	def no_frontier(self, ctr1: models.Country, ctr2: models.Country) -> discord.Embed:
		title = f"{failEmoji} Impossible de déplacer des troupes !"
		description = f"""
		Les pays {ctr1.name} et {ctr2.name} ne partagent aucune frontière.
		""".replace('\t', '')
		color = discord.Color.brand_red()

		return discord.Embed(title = title, description = description, color = color)

	def not_in_any_team(self) -> discord.Embed:
		title = f"{failEmoji} Impossible d'effectuer l'action"
		description = f"""
		Vous n'êtes dans aucune équipe.
		""".replace('\t', '')
		color = discord.Color.brand_red()

		return discord.Embed(title = title, description = description, color = color)

class InfoEmbeds:
	def invite(self, name: str, author: int, membercount: int, servername: str) -> discord.Embed:
		title = f"{infoEmoji} Vous avez été invité dans une équipe sur {servername}"
		description = f"""
		**Nom de l'équipe:** {name}\n
		**Chef:** <@{author}>\n
		**Membres:** {membercount}
		""".replace('\t', '')
		color = discord.Color.blurple()

		return discord.Embed(title = title, description = description, color = color)

	def defense_response(self, cqr: models.Game.ConquestResponse, ctr: models.Country, amount: int, author: str) -> discord.Embed:
		title = f"{failEmoji} Défaite" if cqr.won else f"{successEmoji} Victoire !"

		description = f"""
		Votre pays {ctr.name} vient d'être attaqué par l'équipe {author}.

		Unités envoyées: {amount}
		Pertes: {cqr.score}
		Score: {cqr.losses}
		""".replace('\t', '')
		color = discord.Color.brand_red() if cqr.won else discord.Color.brand_green()

		return discord.Embed(title = title, description = description, color = color)


mm = MatchEmbeds()
tm = TeamEmbeds()
ig = InGameEmbeds()
info = InfoEmbeds()