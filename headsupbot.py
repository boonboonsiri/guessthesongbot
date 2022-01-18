
# Heads up bot: Boon Boonsiri
# To add, speed up time, play 10 seconds at a time


import discord
import json
client = discord.Client()
guild = discord.Guild

import discord
from discord.ext import commands, tasks
import random
import asyncio
from multiprocessing import Process
from urllib.parse import quote  

import youtube_dl
import os
from datetime import datetime, timedelta

client = discord.Client()
guild = discord.Guild
botToken = ''

authorLoop = "";

channelID = 789712854647308303
channelIDHide = 836619856870506516
voiceChannelID = 789712854647308304
bot = commands.Bot(command_prefix='!')
bot.remove_command('help')

# Hard code stuff because lazy
correctSongs = [];
incorrectSongs = [];
songs = [];
points = 0;
curMessage = None
curMessageHidden = []
gameAuthor = None
timeLeft = 90
addTime = True


import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
cid = '3e0bc985d4104ebb96c0870500823a06'
secret = '6e9bd2db093a4d5d97e9c5d6aa37921a'
client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

s = sp.search("Hello Adele",  type='track')

playlist_id = '6KeA7y2gKeFFSU9CSJSrnF'
username = 'tny0jipjihvy3x62dpaddrxf7'

url1 = None
url2 = None
path1 = "song1.mp3"
path2 = "song2.mp3"
index = 0 
urls = []
curUrl = None
curSong = None
pointsDict = None
guessSongs = []
downloadFlag = None
topScore = 200
spotifyGameOn = True
bonusOn = True 
bonusTime = None 
curCorrectGuesses = []


curCycle = 0
team1Score = 0
team2Score = 0

async def cycle1():
	global curCycle

	await sendMessage("Next Song! Cycle 1")

	await play()
	await asyncio.sleep(4.5)
	await pause()
	curCycle = 2

	await sendMessage("Pausing")

async def cycle2():
	global curCycle
	curCycle = 3
	await sendMessage("Cycle 2 Resume!")
	await resume()
	await asyncio.sleep(7)
	await pause()
	await sendMessage("Pausing!")

async def teamSkip():
	global curSong
	curUrl = None 
	await sendMessage("Skipping")
	await sendMessage(str(curSong))
	curSong = None
	await sendMessage("-------------------------")
	await sendMessage("Next Song Up")
	await cycle1()

async def teamGuess(message):
	global pointsDict, curSong, curUrl, topScore, curCycle, team1Score, team2Score

	searches = youtubeSearch(str(message.content[2:len(message.content)]) + " lyrics")

	guessCorrect = False
	try:
		for i in range(5):
			if searches[i] == curUrl:
				guessCorrect = True
				break
	except:
		return

	if guessCorrect:
		curUrl = None # Important 

		await sendMessage(str(curSong))
		await message.add_reaction('✅')
		if message.author.id == 664295404703318016: # Winnie
			await message.add_reaction('🧸')
		curCycle = 1
		if message.content.startswith('t1'):
			team1Score += 1
			await sendMessage("Team 1 point!")

		else:
			team2Score += 1 
			await sendMessage("Team 2 point!")

		await sendMessage("Team 1: " + str(team1Score))
		await sendMessage("Team 2: " + str(team2Score))

	
	if team1Score == topScore:
		await sendMessage("Team 1 wins!")
		await endTeamGame()
	elif team2Score == topScore:
		await sendMessage("Team 2 wins!")
		await endTeamGame()

	if curCycle == 1:
		await cycle1()
	elif curCycle == 2:
		await cycle2()

	elif curCycle == 3:
		curCycle = 4
		await sendMessage("Cycle 3 Resume!")
		await resume()


async def startTeamGame():
	global pointsDict, curSong, curUrl, topScore, curCycle, team1Score, team2Score
	team1Score = 0
	team2Score = 0
	curSong = None
	curUrl = None
	
	f = open('dict.txt', 'w')
	f.write("")

	await sendMessage("----------------------------------")
	await sendMessage("Starting Team Guessing Game")

	await cycle1()

async def endTeamGame():
	global pointsDict, curSong, curUrl, topScore, curCycle, team1Score, team2Score
	await sendMessage("Team 1: " + str(team1Score))
	await sendMessage("Team 2: " + str(team2Score))

	team1Score = 0
	team2Score = 0
	curSong = None
	curUrl = None

def getSong():
	global songs, guessSongs
	while True:
		n = random.randint(0, len(songs)-1)	
		song = songs[n]['title'] + ' - ' + songs[n]['artists']
		if not song in guessSongs:
			guessSongs.append(song)
			break
	return song

# Download songs in the background because I hate my computer
def downloadSong():

	global urls, index
	print("here5")
	while True:
		#await asyncio.sleep(1)
		if len(urls) >= 200:
			break 
		if len(urls) > index + 5: 
			continue
		print(urls)
		song = getSong()
		newUrl = youtubeSearch(song)[0]

		song_there = os.path.isfile("song" + str(len(urls)) + ".mp3") # Use length as that's +1 already
		print(song_there)
		if song_there:
			print("song" + str(len(urls)) + ".mp3")
			os.remove("song" + str(len(urls)) + ".mp3")
			print(os.path.isfile("song" + str(len(urls)) + ".mp3"))

		ydl_opts = {
			'format': 'bestaudio/best',
			'postprocessors': [{
				'key': 'FFmpegExtractAudio',
				'preferredcodec': 'mp3',
				'preferredquality': '192',
			}],
		}

		with youtube_dl.YoutubeDL(ydl_opts) as ydl:
			#await asyncio.create_task(asyncio.coroutine(ydl.download([newUrl])))
			print("test")
			ydl.download([newUrl])
			print("no")

		for file in os.listdir("./"):
			if file.endswith(".mp3") and not file.startswith('song'):
				os.rename(file, "song" + str(len(urls)) + ".mp3")
		urls.append(newUrl)
		

def youtubeSearch(search_keyword):
	import urllib.request
	import re

	#search_keyword="You should be sad - Halsey"
	search_keyword = re.sub("\s+", "+", search_keyword.strip())
	html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + quote(search_keyword))
	video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
	#print("https://www.youtube.com/watch?v=" + video_ids[0])
	return video_ids

def getSpotifyPlaylist():
	results = sp.user_playlist(username, playlist_id)

	tracks = results['tracks']
	for i, item in enumerate(tracks['items']):
		track = item['track']

		artists = [];
		for a in track['artists']:
			artists.append(a['name'])
		url = track['external_urls']['spotify']
		title = track['name']
		spotifyDict = {
			'artists': ', '.join(artists), 
			'title': title, 
			'url': url,
		}
		songs.append(spotifyDict)

async def endSpotify(winner):
	global index, curUrl, curSong, spotifyGameOn
	await sendMessage("WINNER IS: " + str(winner))
	await printScores()
	curUrl = None # Should already be but just in case you know
	spotifyGameOn = False

	index += 1 # Shouldn't have to restart in theory



async def skip():
	global curSong
	curUrl = None
	await sendMessage("Skipping")
	await sendMessage(str(curSong))
	curSong = None
	await sendMessage("-------------------------")
	await sendMessage("Next Song Up")
	await play()

async def printScores():
	global pointsDict
	for s in pointsDict:
		await sendMessage(str(s) +": " + str(pointsDict[s]))

async def guess(message):
	global pointsDict, curSong, curUrl, topScore, bonusTime, curCorrectGuesses, bonusOn
	searches = youtubeSearch(str(message.content[1:len(message.content)]) + " lyrics")

	guessCorrect = False
	try:
		for i in range(5):
			if searches[i] == curUrl:
				guessCorrect = True
				break
	except:
		return

	if guessCorrect and bonusTime and bonusOn:
		now = datetime.now()

		if now < bonusTime:
			if len(curCorrectGuesses) < 5 and not(message.author in curCorrectGuesses):
				curCorrectGuesses.append(message.author)
				await message.add_reaction('🅱️')
				
				if not(message.author in pointsDict):
					pointsDict[message.author] = 0
				pointsDict[message.author] += 0.5
				if pointsDict[message.author] == topScore:
					await endSpotify(message.author)
		return # Return to not do extra stuff

	
	if guessCorrect:
		bonusTime = datetime.now() + timedelta(0,2)
		curCorrectGuesses = [message.author]

		if not(bonusOn):
			curUrl = None # Important, doesn't allow second guesses
		await message.add_reaction('✅')

		if message.author.id == 664295404703318016: # Winnie
			await message.add_reaction('🧸')

		if not(message.author in pointsDict):
			pointsDict[message.author] = 0
		
		pointsDict[message.author] += 1

		await sendMessage(str(curSong))
		await sendMessage(str(message.author) + " point!")
		curSong = None # Doesn't need to be but whatever
		await printScores()
	
		if pointsDict[message.author] == topScore:
			await endSpotify(message.author)
		else:
			await sendMessage("-------------------------")
			await sendMessage("Next Song Up")
			await play()


async def play():

	global urls, index, curUrl, curSong, bonusTime, curCorrectGuesses
	await stop()
	await asyncio.sleep(0.1)

	voiceChannel = client.get_channel(voiceChannelID)
	
	if not(client.voice_clients):
		await voiceChannel.connect()

	voice = client.voice_clients[0]

	while index >= len(urls):
		await asyncio.sleep(1)
		print("hello")
		try:
			f = open("dict.txt", "r")
			jsonDict = f.read()
			print(jsonDict)
			urls = json.loads(jsonDict)
		except:
			continue

	curUrl = urls[index]['url']
	curSong = urls[index]['name']
	voice.play(discord.FFmpegPCMAudio("song" + str(index) + ".mp3"))
	try:
		os.remove('song' + str(index-1) + '.mp3')
	except:
		pass
	index += 1
	bonusTime = None
	curCorrectGuesses = []
	
	# Write new index
	f = open('index.txt', 'w')
	f.write(str(index))


def worker():
    import time
    while(True):
        time.sleep(1)
        print("i")

async def startSpotifyGame():
	global urls, pointsDict, index, curUrl, guessSongs, curSong, spotifyGameOn, bonusTime, curCorrectGuesses
	curCorrectGuesses = []
	bonusTime = None
	guessSongs = []
	urls = []
	pointsDict = {}
	#index = 0 shouldn't need this in theory
	curMessage = None
	curSong = None
	spotifyGameOn = True
	# Write new index
	f = open('dict.txt', 'w')
	f.write("")


	await sendMessage("----------------------------------")
	await sendMessage("Starting Guessing Game")

	#loop = asyncio.new_event_loop()
	#asyncio.create_task(downloadSong()) // Works but slow
	#loop.run_forever()

	#p1 = Process(target = worker)
	#p1.start()
	#p1.join()
	#print("here3")
	#asyncio.create_task(timer())
	await play()

async def leave():
	voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
	if voice.is_connected():
		await voice.disconnect()
	else:
		pass

async def pause():
	voice = client.voice_clients[0]
	if voice.is_playing():
		voice.pause()
	else:
		pass

async def resume():
	voice = client.voice_clients[0]
	if voice.is_paused():
		voice.resume()
	else:
		pass

async def stop():
	if client.voice_clients:
		voice = client.voice_clients[0]
		voice.stop()

async def sendNewSong():
	global gameAuthor, points, correctSongs, incorrectSongs, curMessage, curMessageHidden, songs

	while True:
		n = random.randint(0, len(songs)-1)	
		song = songs[n]['title'] + ' - ' + songs[n]['artists']

		if (not song in correctSongs) and (not song in incorrectSongs):
			break

	if curMessageHidden:
		await sendMessage(curMessageHidden.content)
		# Get the message
		channel = client.get_channel(channelID) # Change this to hide eventually 
		async for m in channel.history():
			if m.author == client.user: # Get the most recent bot message
				curMessage = m
				break

	await sendMessageHide(song)
	
	# Get the message
	channel = client.get_channel(channelIDHide) # Change this to hide eventually 
	async for m in channel.history():
		if m.author == client.user: # Get the most recent bot message
			curMessageHidden = m
			break

	
	
async def charadesSuccess():
	global gameAuthor, correctSongs, incorrectSongs, curMessage, curMessageHidden, timeLeft

	correctSongs.append(curMessageHidden.content)
	if addTime:
		timeLeft += 3
	
	await curMessageHidden.add_reaction('✅')

	await sendNewSong()
	if curMessage:
		await curMessage.add_reaction('✅')


async def charadesFailure():
	global gameAuthor, points, correctSongs, incorrectSongs, curMessage, curMessageHidden, timeLeft
	incorrectSongs.append(curMessageHidden.content)

	await curMessageHidden.add_reaction('❌')

	await sendNewSong()
	if curMessage:
		await curMessage.add_reaction('❌')

async def startGame(author):
	global gameAuthor, points, correctSongs, incorrectSongs, curMessage, curMessageHidden, timeLeft
	points = 0
	correctSongs = []
	incorrectSongs = []
	curMessage = None
	curMessageHidden = None
	gameAuthor = author
	timeLeft = 90

	if author.id == 836769058883633212:
		author = "Stupid Bear"
	await sendMessage("----------------------------------")
	await sendMessage("Starting Game with " + str(author))
	await sendMessageHide('--------------------------------')
	await sendMessageHide("Starting Game with " + str(author))
	await sendNewSong()
	asyncio.create_task(timer())

async def endGame():
	global gameAuthor, points, correctSongs, incorrectSongs, curMessage, curMessageHidden, timeLeft

	await sendMessage("Correct Songs: " + str(len(correctSongs)) + "\n" + str(correctSongs))
	await sendMessage("Incorrect Songs: " + str(len(incorrectSongs)) + "\n" + str(incorrectSongs))
	await sendMessage("---------------------------------------------------")

	await sendMessageHide("Correct Songs: " + str(len(correctSongs)) + "\n" + str(correctSongs))
	await sendMessageHide("Incorrect Songs: " + str(len(incorrectSongs)) + "\n" + str(incorrectSongs))
	await sendMessageHide("---------------------------------------------------")

	gameAuthor = None
	correctSongs = []
	incorrectSongs = []
	
async def sendMessage(message):
	channel =  client.get_channel(channelID)
	await channel.send(message);

async def sendMessageHide(message):
	channel =  client.get_channel(channelIDHide)
	await channel.send(message);

async def timer():
	global timeLeft

	while timeLeft > 0:
		if timeLeft % 5 == 0 or timeLeft <= 5:
			await sendMessage(timeLeft)
			await sendMessageHide(timeLeft)
		await asyncio.sleep(1)
		timeLeft -= 1
	await endGame()

@client.event
async def on_ready():
	# Load the songs
	#f = open("songs.txt", "r")
	#songsString = f.read()

	#for line in songsString.splitlines():
	#	if line != "":
	#		if line not in songs:
	#			songs.append(line); 
	getSpotifyPlaylist()
	channel = client.get_channel(voiceChannelID)
	await channel.connect()
	

@client.event
async def on_message(message):
	
	if message.author == client.user: # in case of discord bot
		return
	if message.author == gameAuthor:
		if message.content.lower() == 'y' or message.content.lower() == 'yes':
			await charadesSuccess()

		elif message.content.lower() == 'n' or message.content.lower() == 'no':
			await charadesFailure()
	if message.content.lower() == "!charades start": # You can use commands but man are they not working for me
		await startGame(message.author)	
	
	if message.content.lower() == "!start spotify game":
		await startSpotifyGame()

	if message.content.lower() == "playnext":
		print(urls)
		await play()
	if message.content.lower() == "?skip" and spotifyGameOn:
		await skip()
		return
	if message.content.startswith("?") and spotifyGameOn:
		await guess(message)

	if message.content.lower() == "!start team game":
		await startTeamGame()

	if message.content.lower() == "?teamskip":
		await teamSkip()
	if message.content.startswith("t1") or message.content.startswith("t2"):
		await teamGuess(message)


client.run(botToken);
