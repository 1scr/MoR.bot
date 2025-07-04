# IMPORTANT: Assurez-vous que ce fichier ne soit pas en train de s'éxécuter si vous avez
# effectué des changements non sauvegardés !

import dotenv
import os
import requests
import subprocess
import time

dotenv.load_dotenv(override = True)

repo_url = "https://raw.githubusercontent.com/1scr/MoR.bot"
file_paths = [
	"requirments.txt",
	"main.py",
	"bot/utils.py",
	"bot/embeds.py",
	"bot/cogs/matchmaking.py",
	"bot/cogs/minimap.py",
	"bot/cogs/teams.py",
	"bot/cogs/units.py",
	"game/models.py",
	"assets/initial_config.json",
	"assets/initial_game.json"
]

def update_bot(version: str):
	for file_path in file_paths:
		print(f"Mise à jour de {file_path} depuis {repo_url}/{version}/{file_path} ...")
		github_url = f"{repo_url}/{version}/{file_path}"

		response = requests.get(github_url, headers = { 'authorization': os.getenv('GITHUB_PAT') })

		if response.status_code == 200:
			content = response.text
			if os.path.basename(file_path) == "main.py":
				content = content.replace('TOKEN', 'TOKEN_DEV')

			with open(file_path, "w", encoding = "utf-8") as local_file:
				if os.path.basename(file_path) == "main.py":
					local_file.write('')
					time.sleep(3)

				local_file.write(content)
				print(f"- {file_path} mis à jour avec succès !")
		else:
			print(f"- Erreur {response.status_code} - Impossible de mettre à jour {file_path}")

def check_release() -> str | None:
	response = requests.get(f"https://api.github.com/repos/1scr/MoR.bot/releases", headers = { 'method': 'GET', 'authorization': os.getenv('GITHUB_PAT') })

	if response.status_code == 200:
		releases = response.json()

		if len(releases) == 0:
			return None

		release = releases[0]

		return release['tag_name']
	else:
		print(f"Erreur {response.status_code} - Impossible de vérifier la release")
		return None

botproc = None

def launch():
    global botproc

    botproc = subprocess.Popen(
        [".venv/Scripts/python", "main.py"],
        stdout = None,
        stderr = None
    )

def stop():
    global botproc

    if botproc and botproc.poll() is None:
        botproc.terminate()

        try:
            botproc.wait(timeout = 5)
        except subprocess.TimeoutExpired:
            botproc.kill()

if __name__ == "__main__":
	launch()

	while True:
		print("Recherche de mises à jour...")
		new_release = check_release()

		if new_release is not None and new_release != os.getenv('BOT_VERSION'):
			os.system('cls' if os.name == 'nt' else 'clear')

			print(f"Nouvelle mise à jour détectée: {new_release}")
			update_bot(new_release)

			os.environ['BOT_VERSION'] = new_release

			print("\n", "Installation des dépendances...", "\n", sep = '')
			subprocess.Popen([".venv/Scripts/pip", "install", "-r", "requirments.txt"])

			print("\n", "Redémarage en cours.", sep = '', end = '')
			stop()
			print(".\n")
			launch()
		else:
			print("L'application est à jour.")

		time.sleep(300)