#import youtube_dl
import yt_dlp
import os
import random

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from urllib.parse import quote  
#from pydub import AudioSegment
from mutagen.mp3 import MP3

cid = '3e0bc985d4104ebb96c0870500823a06'
secret = ''
client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

s = sp.search("Hello Adele",  type='track')

playlist_id_pop = '6KeA7y2gKeFFSU9CSJSrnF'
playlist_id_pop2 = '3LxozhI1inYIea6wvCRkvi'
playlist_id_kpop = '51h8UAK7qU0p17n7o8i81L'
playlist_id_taylor = '3EtrSk2q5jGu6vLZZo8QCu'
playlist_id_test = '0H3iNJE1iXzVUlPbqKqWT4'
playlist_id_christmas = '4cKWxTBzqVT8MYA0aFH53v'

playlist_id_kpop2 = '3gYSvFS0lC6qPdGkxX4mDX'
username = 'tny0jipjihvy3x62dpaddrxf7'

url1 = None
url2 = None
path1 = "song1.mp3"
path2 = "song2.mp3"
index = 0 
urls = []
curUrl = None
pointsDict = None
guessSongs = []
downloadFlag = None
randomTime = False
isTitleOnly = True

songs = []
def youtubeSearch(search_keyword):
	import urllib.request
	import re

	#search_keyword="You should be sad - Halsey"
	search_keyword = re.sub("\s+", "+", search_keyword.strip())
	html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + quote(search_keyword))
	video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
	#print("https://www.youtube.com/watch?v=" + video_ids[0])
	return video_ids

def getSong():
	global songs, guessSongs
	print(len(songs))
	while True:
		n = random.randint(0, len(songs)-1)	
		print(n)

		song = None
		if isTitleOnly:
			song = songs[n]['title']
		else:
			song = songs[n]['title'] + ' - ' + songs[n]['artists']
		if not song in guessSongs:
			guessSongs.append(song)
			break
	return song

def printSongs():
	global songs
	for song in songs:
		print(song['title'] + ' - ' + song['artists'])

def getSpotifyPlaylist():
	#playlist_ids = [playlist_id_pop,playlist_id_pop2]
	playlist_ids = [playlist_id_christmas]

	for playlist_id in playlist_ids:
		results = sp.user_playlist(username, playlist_id)
		#results = sp.user_playlist_tracks(username, playlist_id, limit = 1000)
		tracks = results['tracks']
		while True:
			for i, item in enumerate(tracks['items']):
				track = item['track']
				print(len(tracks['items']))

				artists = [];
				for a in track['artists']:
					artists.append(a['name'])
				try:
					url = track['external_urls']['spotify']
				except:
					pass
				title = track['name']
				spotifyDict = {
					'artists': ', '.join(artists), 
					'title': title, 
					'url': url,
				}
				songs.append(spotifyDict)
			if tracks['next']:
				tracks = sp.next(tracks)
			else:
				break

def checkDuplicates():
	seen = {}
	dupes = []

	for s in songs:
		x= s['title'] + ' - ' + s['artists']
		if x not in seen:
			seen[x] = 1
		else:
			if seen[x] == 1:
				dupes.append(x)
			seen[x] += 1
	print(dupes)


songDict = {
	"Rolling in the Deep - Adele": "Rolling in the Deep",
	"Gangnam Style (강남스타일) - PSY": "Gangnam Style",
	'Happy - From "Despicable Me 2" - Pharrell Williams': "Happy - Pharell Williams",
	'Can I Have This Dance - Original Version - High School Musical Cast, Vanessa Hudgens, Zac Efron':'Can I have This Dance - High School Musical',
	'We\'re All In This Together - From "High School Musical"/Soundtrack Version - High School Musical Cast': 'We\'re All in This Together - High School Musical',
	'A Night to Remember - Original Version - High School Musical Cast': 'A Night to Remember - High School Musical',
	'Stick to the Status Quo - From "High School Musical"/Soundtrack Version - High School Musical Cast': 'Stick to the Status Quo - High School Musical',
	'Right Here, Right Now - High School Musical Cast, Vanessa Hudgens, Zac Efron': 'Right Here, Right Now - High School Musical',
	'City Of Stars - From "La La Land" Soundtrack - Ryan Gosling, Emma Stone': 'City of Stars - Ryan Gosling, Emma Stone',
	'CAN\'T STOP THE FEELING! (Original Song from DreamWorks Animation\'s "TROLLS") - Justin Timberlake': 'CAN\'T STOP THE FEELING! - Justin Timberlake',
	'Let It Go - From "Frozen"/Soundtrack Version - Idina Menzel': 'Let it Go - Idina Menzel',
	'Boom Clap - From the Motion Picture Das Schicksal ist ein mieser Verräter - Charli XCX': 'Boom Clap - Charli XXX',
	'Just Like Fire (From the Original Motion Picture "Alice Through The Looking Glass") - P!nk': 'Just like Fire - P!nk',
	'Lose Yourself - From "8 Mile" Soundtrack - Eminem': 'Lose Yourself - Eminem',
	'Levels - Original Version - Avicii': 'Levells - Avicci',
	'ME! (feat. Brendon Urie of Panic! At The Disco) - Taylor Swift, Brendon Urie, Panic! At The Disco': 'Me! - Taylor Swift, Brandon Urie',
	'Sunflower - Spider-Man: Into the Spider-Verse - Post Malone, Swae Lee': 'Sunflower - Post Malone, Swae Lee',
	'Savage Love (Laxed - Siren Beat) - Jawsh 685, Jason Derulo': "Savage Love - Jawsh 685, Jason Derulo",
}


def runBash(command):
	os.system(command)

def crop(start,end,input,output):
	command = "ffmpeg -i \"" +  input + "\" -ss  " + start + " -to " + end + " -c copy " + output
	print(command)
	runBash(command)

import json
# Download songs in the background because I hate my computer
def downloadSong():
	global urls
	while True:
		# Write to file
		f = open('dict.txt', 'w')
		f.write(json.dumps(urls))
	
		index = 0
		try:
			f = open("index.txt", "r")
			index = int(f.read())
		except:
			continue
		#await asyncio.sleep(1)
		if len(urls) >= 1000:
			break 
		if len(urls) > index + 5: 
			continue
		print(urls)
		song = getSong()
		try:
			if song in songDict:
				song = songDict[song]
			newUrl = youtubeSearch(song + " lyrics")[0]

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

			#with youtube_dl.YoutubeDL(ydl_opts) as ydl:
			with yt_dlp.YoutubeDL(ydl_opts) as ydl:
				#await asyncio.create_task(asyncio.coroutine(ydl.download([newUrl])))
				ydl.download([newUrl])
		except:
			continue

		for file in os.listdir("./"):
			if file.endswith(".mp3") and not file.startswith('song'):
				
				if randomTime: # Cut the file, too slow
					try:
						audio = MP3(file)
						length = audio.info.length 
						rand = random.randint(0, 50)/100
						print(rand)
						print(file)
						crop(str(length*rand), str(length), file, "song" + str(len(urls)) + ".mp3")
						os.remove(file)
						print("No")
						# Too slow
						#print("HEre")
						#audio = MP3(file)
						#length = audio.info.length 
						#rand = random.randint(0, 50)/100
						#print(length)
						#print(rand)
						#cutSong = AudioSegment.from_mp3(file)
						#extract = cutSong[length*rand*1000:length*1000]
						#os.remove(file)
						#extract.export("song" + str(len(urls)) + ".mp3", format="mp3")
						#print("yeah")
					except Exception as e:
						#print(e)
						os.rename(file, "song" + str(len(urls)) + ".mp3") # If fail just do it regularly again
				else:
					os.rename(file, "song" + str(len(urls)) + ".mp3")
		urls.append({'url': newUrl, 'name': song})

# Delete old files in case of crash from before
for file in os.listdir("./"):
	if file.endswith(".mp3") and not file.startswith('song'):
		os.remove(file)
getSpotifyPlaylist()
#checkDuplicates()
#printSongs()
downloadSong()