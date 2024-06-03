import discord

successEmoji = "<:success:1244217628046921735>"
infoEmoji = "<:info:1244217625635192883>"
failEmoji = "<:fail:1244217624276238398>"


def errorEmbed(ticket: str) -> discord.Embed:
	title = "Une erreur est survenue..."
	description = f"""Mais pas de panique ! Les développeurs ont été informés en détail et répareront ça en un rien de temps ! Si ils tardent, mentionne-les avec cet identifiant:\n
	```
	{ticket}```"""
	color = discord.Colour.brand_red()

	return discord.Embed(title = title, description = description, color = color)

def noPermEmbed() -> discord.Embed:
	title = "Hop hop hop !"
	description = f"Tu n'as pas la permission d'effectuer cette commande, que je ne t'y reprenne pas !"
	color = discord.Colour.brand_red()

	return discord.Embed(title = title, description = description, color = color)

class MatchEmbeds:
	# -------------------- SUCCÈS --------------------

	def gameCreated(self) -> discord.Embed:
		title = f"{infoEmoji} Bienvenue dans cette partie de World War III !"
		description = f"""
		Vous avez 36 pays à votre disposition. La première équipe a en coloniser 20 gagne la partie (la Russie vous donne accès à toutes ses colonies)\n
		
		## Nouveautés cette année\n
		Cette année, chaque pays apporte des ressources supplémentaires, et c'est ainsi que les **avions** et les **missiles** entrent en scène !\n
		**Avions:** Récoltables dans les pays B et C, les avions vous permettent de vous déplacer entre deux pays même s'ils ne sont pas limitrophes\n
		**Missiles:** Récupérables de la même façon que les avions, les bombes permettent de réduire le nombre de soldats dans un pays, et de vous le récupérer si il reste moins de 10 soldats\n

		## Comment ça marche\n
		Chaque pays apporte des ressources plus ou moins différentes, celles-ci sont classées en trois catégories:\n
		- **Catégorie A:** 20% :busts_in_silhouette:\*\n
		- **Catégorie B:** 50% :busts_in_silhouette:, 2 :airplane:, 0~1 :bomb:\n
		- **Catégorie C:** 80% :busts_in_silhouette:, 3~6 :airplane:, 1~3 :bomb:\n\n
		\* _Après une victoire face à 10 soldats, 2 soldats vous seront offerts sur le territoire attaqué._\n

		La Russie est classée C, à vous de découvrir les 4 catégorisés B\n
		Bonne chance !
		""".replace('\t', '')
		color = discord.Colour.dark_red()

		return discord.Embed(title = title, description = description, colour = color)
	
class TeamEmbeds:
	# -------------------- ERREURS --------------------

	def teamNotFound(self, teamName: str) -> discord.Embed:
		title = f"{failEmoji} Cette équipe n'existe pas"
		description = f"Impossible de trouver une équipe nommée « {teamName} » - Réessayez."
		color = discord.Colour.brand_red()

		return discord.Embed(title = title, description = description, colour = color)

	def alreadyInTeam(self, teamName: str) -> discord.Embed:
		title = f"{failEmoji} Vous devez quitter votre équipe"
		description = f"Il vous faut quitter l'équipe _{teamName}_ pour en rejoindre ou en créer une autre."
		color = discord.Colour.brand_red()

		return discord.Embed(title = title, description = description, colour = color)
	
	def alreadyExistingName(self, teamName: str) -> discord.Embed:
		title = f"{failEmoji} L'équipe _{teamName}_ existe déjà"
		description = f"Choisissez un autre nom ou arrangez-vous avec le chef de l'autre équipe pour la rejoindre."
		color = discord.Colour.brand_red()

		return discord.Embed(title = title, description = description, colour = color)
	
	def alreadyExistingColor(self, color: str) -> discord.Embed:
		title = f"{failEmoji} Impossible de prendre cette couleur"
		description = f"Votre couleur se rapproche trop de celle d'une équipe déjà existante."
		color = discord.Colour(int(color, 16))

		return discord.Embed(title = title, description = description, colour = color)
	
	def invalidName(self, name: str) -> discord.Embed:
		title = f"{failEmoji} Impossible de prendre ce nom"
		description = f"Le nom de votre équipe doit comprendre moins de 32 caractères."
		color = discord.Colour.brand_red()

		return discord.Embed(title = title, description = description, colour = color)
	
	def invalidColor(self, color: str) -> discord.Embed:
		title = f"{failEmoji} Impossible de prendre cette couleur"
		description = f"Votre couleur `{color}` est invalide car elle ne correspond pas au format hexadécimal: `0xABCDEF` ou `#ABCDEF`"
		color = discord.Colour.brand_red()

		return discord.Embed(title = title, description = description, colour = color)
	
	def notInvited(self, author: int) -> discord.Embed:
		title = f"{failEmoji} Vous n'êtes pas invité(e) dans cette équipe"
		description = f"Demandez à <@{author}> de vous inviter dans son équipe pour pouvoir la rejoindre."
		color = discord.Colour.dark_red()

		return discord.Embed(title = title, description = description, colour = color)
	
	# -------------------- SUCCÈS --------------------

	def teamCreated(self, name: str, color: str, author: int) -> discord.Embed:
		title = f"{successEmoji} Équipe créée avec succès !"
		description = f"""
		**Nom de l'équipe:** {name}\n
		**Couleur:** `{color}`\n
		**Chef:** <@{author}>
		"""
		color = discord.Colour.brand_green()

		return discord.Embed(title = title, description = description, colour = color)
	
	def teamJoined(self, name: str, author: int, membercount: int) -> discord.Embed:
		title = f"{successEmoji} Équipe créée avec succès !"
		description = f"""
		**Nom de l'équipe:** {name}\n
		**Chef:** <@{author}>\n
		**Membres:** {membercount}
		"""
		color = discord.Colour.brand_green()

		return discord.Embed(title = title, description = description, colour = color)


mm = MatchEmbeds()
tm = TeamEmbeds()