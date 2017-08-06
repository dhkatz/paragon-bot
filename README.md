Paragon-Discord-Bot
===================

[![Python3](https://img.shields.io/badge/python-3.6-blue.svg)](https://github.com/DoctorJew/Paragon-Discord-Bot)
[![GitHub license](https://img.shields.io/aur/license/yaourt.svg)](https://raw.githubusercontent.com/DoctorJew/Paragon-Discord-Bot/master/LICENSE)
[![Discord Server](https://img.shields.io/badge/Support-Discord%20Server-blue.svg)](https://discord.gg/kqSRzfU)

A Discord Bot built for use specifically in Paragon related Discord servers. Made with hate and [discord.py](https://github.com/Rapptz/discord.py).
This bot is not designed to be setup by anyone else, but it's design intention is easy to understand.

Tournament Creation
-------------------
Detailed steps on how to create a tournament.

To create a tournament, use the **.tournament create** command supplied by the bot.
You **must** include the following parameters in the **mentioned order**. Please read the **notes** column for important information!

Upon creating a tournament, the bot will reply with tournament details, including a tournament ID which players can use to signup with, which you then **must confirm**.

#### Parameter List ####

Parameter | Description | Possible Values | Notes
----------|-------------|-----------------|------
**type** : `str` | The type of tournament being created. | `ARAM`, `Standard`
**name** : `str` | Name of your tournament. | `"Best Tournament"` | Names with spaces should be surrounded with quotes!
**date** : `str` | Date and time of your tournament in UTC. (MM-DD-YYYY hh:mm) | `"12-31-2017 16:30"` | Ensure the date is surrounded by quotes! Dates MUST be in UTC!

Example Command Usage: `.tournament create ARAM "Paragon Subreddit ARAM 3" "8-19-2017 16:30"`

Signups will automatically be closed 48 hours before the tournament start time, to ensure proper preparation time.
Any users who signup after this time will be stored as substitutes, and will automatically fill spots vacated by players.

Commands List (WIP)
-------------------
**Info:** Currently each command is prefixed with a period (.)

### Agora ###

Command and Aliases | Description | Usage
----------------|--------------|-------
`.card` | Returns information on a card or multiple cards. | `.card "Quenching Scales"`, `.card quenching`
`.elo` | Returns a player's elo by name from Agora.gg | `.elo DoctorJew`
`.herodeck`, `.deck`, `.d` | Returns top three hero decks from Agora.gg | `.deck Serath`
`.heroguide`, `.guide`, `.g` | Returns top three hero guides from Agora.gg | `.guide Serath`
`.stats` | Returns a player's stats from Agora.gg | `.stats DoctorJew`
`.lpg` | Get a player's last played game stats from Agora.gg | `.lpg DoctorJew`
`.ign` | Tag your Paragon IGN to your Discord account. Surround names with spaces in quotes. Empty to see current. | `.ign DoctorJew`

### Fun ###

Command and Aliases | Description | Usage
----------------|--------------|-------
`.cat` | Get a random cat picture from random.cat | `.cat`

### Info ###

Command and Aliases | Description | Usage
----------------|--------------|-------
`.info avatar` | Returns information about the bot's avatar. | `.info avatar`

### Music ###

Command and Aliases | Description | Usage
----------------|--------------|-------
`.join` | Joins a voice channel. | `.join General`
`.pause` | Pauses the currently played song. | `.pause`
`.play` | Plays a song. | `.play https://youtu.be/dQw4w9WgXcQ`
`.playing` | Shows info about the currently played song. | `.playing`
`.resume` | Resumes the currently played song. | `.resume`
`.skip` | Vote to skip a song. The song requester can automatically skip. | `.skip`
`.stop` | Stops playing audio and leaves the voice channel. | `.stop`
`.summon` | Summons the bot to join your voice channel. | `.summon`
`.volume` | Sets the volume of the currently playing song. | `.volume 50`

### Pick ###

Command and Aliases | Description | Usage
----------------|--------------|-------
`.pick` | Pick a random hero. | `.pick`
`.pick10` | Pick 10 random heroes. | `.pick10`
`.pick5` | Pick 5 random heroes. | `.pick5`
`.pickcarry` | Pick a random ADC. | `.pickcarry`
`.pickjungle` | Pick a random jungler. | `.pickjungle`
`.pickmid` | Pick a random Midlaner. | `.pickmid`
`.pickoff` | Pick a random Offlaner | `.pickoff`
`.picksupport` | Pick a random Support | `.picksupport`

Requirements
------------

Please see the specific requirements listed for each of the packages listed below.

* Python 3.6+
* discord.py
