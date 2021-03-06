# Poly Bridge 2 Leaderboards Bot
[![](https://cdn.discordapp.com/app-assets/720364938908008568/758752385244987423.png)](https://store.steampowered.com/app/1062160/Poly_Bridge_2/)
[<img src="https://raw.githubusercontent.com/github/explore/80688e429a7d4ef2fca1e82350fe8e3517d3494d/topics/python/python.png" alt="Made with Python 3" width=128 height=128>](https://python.org)
- The PB2 Leaderboards bot is a project with the goal of creating a discord bot to view and analyse the PB2 leaderboards.

# Documentation
The doucmentation can be found [here](https://docs.google.com/document/d/1T3ucE2cbWTnCvEDN-aoGBPuXNbEpj3B7rnKfnCS0hdI/edit?usp=sharing)

# Requirements

Requires python 3.8 to run *(3.3 - 3.6 might work)*

[Python 3.8 via Python Website](https://www.python.org/downloads/release/python-383/)

[Python 3.8 via Microsoft Store](https://www.microsoft.com/en-us/p/python-38/9mssztt1n39l)

For the code to run properly you will be required to create a file called `.env`. This file will need to contain:

```conf
DISCORD_TOKEN=YOUR_TOKEN
```

Where `YOUR_TOKEN` is a Discord Bot token. [Creating a Discord Bot](https://discord.com/developers/docs/intro#bots-and-apps)

## Recommended Installation Method:

Install venv, then enable it in the project:

```sh
python3 -m venv env
```

Then to enter the Virtual Envirornment:

```sh
source env/bin/activate
```
On Windows:
```
.\env\Scripts\activate
```
[How to set up venv](https://docs.python.org/3/tutorial/venv.html#creating-virtual-environments)

To install required dependencies, use the below in the (env):

```sh
pip install -r requirements.txt
```

----------

Dependencies:
|Name               |Version            |
|-------------------|-------------------|
| aiohttp           | 3.6.2             |
| async-timeout     | 3.0.1             |
| asyncio           | 3.4.3             |
| attrs             | 19.3.0            |
| certifi           | 2020.6.20         |
| chardet           | 3.0.4             |
| DateTime          | 4.3               |
| discord-ext-menus | 1.0.0a26+g84caae8 |
| discord-flags     | 2.1.1             |
| discord.py        | 1.4.1             |
| dotenv-python     | 0.0.1             |
| idna              | 2.10              |
| multidict         | 4.7.6             |
| python-dotenv     | 0.14.0            |
| pytz              | 2020.1            |
| requests          | 2.24.0            |
| urllib3           | 1.25.10           |
| yarl              | 1.5.1             |
| zope.interface    | 5.1.0             |


# Development
Want to contribute? Great!

The Poly Bridge 2 Leaderboards Discord Bot has the aim of presenting the data from the PB2 Leaderboards in a format that is accessible to everyone. The inspiration for this project was partially taken from Bolt986's Leaderboard Fun Spreadsheet and my interest in the game's leaderboard data. 

I am open to feedback regarding the Discord Bot and feature suggestions will be considered. I am also open to contributions to this project.

**Please note** that I made this bot in my spare time so please be patient regarding a response or feature addition.
# License
See LICENSE.md

# Future Plans
Feature plans / additions will be noted here or on a projects board in this repository.

# Credits

Code Written by [Conqu3red](https://github.com/Conqu3red)
