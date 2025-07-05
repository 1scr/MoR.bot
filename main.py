import os
import dotenv

import discord

dotenv.load_dotenv(override = True)

from bot.cogs.matchmaking import Matchmaking
from bot.cogs.minimap import MiniMap
from bot.cogs.teams import Teams
from bot.cogs.units import Units

# On initialise le bot
intents = discord.Intents.all()
bot = discord.Bot(intents = intents)

# On charge les cogs
bot.add_cog(Matchmaking(bot))
bot.add_cog(MiniMap(bot))
bot.add_cog(Teams(bot))
bot.add_cog(Units(bot))

# Et c'est parti
@bot.event
async def on_ready():
	print(f"\033[32mConnecté en tant que \033[1m{bot.user.display_name}\033[0m", flush = True)

@bot.event
async def on_message(message: discord.Message) -> None:
	if message.author.bot:
		return

	if ' ' in message.content:
		cmd = message.content.split(' ')
	else:
		cmd = [ message.content ]

	if cmd[0] in ('move', 'mv') and len(cmd) == 4:
		try:
			cmd[1:] = map(int, cmd[1:])

			await Units(bot).move_units(message, cmd[1], cmd[2], cmd[3])
		except TypeError:
			await message.reply("Mauvais arguments passés.")
	elif cmd[0] in ('fmap',):
		await MiniMap(bot).display_fastmap(message)

bot.run(os.getenv('TOKEN'))