import discord

successEmoji = "<:success:1244217628046921735>"
infoEmoji = "<:info:1244217625635192883>"
failEmoji = "<:fail:1244217624276238398>"

class TeamEmbeds:
    # -------------------- ERREURS --------------------

    def alreadyInTeam(teamName: str) -> discord.Embed:
        title = f"{failEmoji} Vous devez quitter votre équipe"
        description = f"Il vous faut quitter l'équipe _{teamName}_ pour en rejoindre ou en créer une autre."
        color = discord.Colour.dark_red()

        return discord.Embed(title = title, description = description, colour = color)
    
    def alreadyExistingName(teamName: str) -> discord.Embed:
        title = f"{failEmoji} L'équipe _{teamName}_ existe déjà"
        description = f"Choisissez un autre nom ou arrangez-vous avec le chef de l'autre équipe pour la rejoindre."
        color = discord.Colour.dark_red()

        return discord.Embed(title = title, description = description, colour = color)
    
    def alreadyExistingColor(color: str) -> discord.Embed:
        title = f"{failEmoji} Impossible de prendre cette couleur"
        description = f"Votre couleur se rapproche trop de celle d'une équipe déjà existante."
        color = discord.Colour(int(color, 16))

        return discord.Embed(title = title, description = description, colour = color)