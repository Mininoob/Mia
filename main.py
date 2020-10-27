#Made by Joshua Le project MIA My Intelligent Assistant
#Usage
#Mia - activates her
#
#Commands
#time - tells you the time
#Locate - Promts you a place to locate and brings up google maps
#Search - search something on google
#Search (on youtube) - searches on youtube
#where is (location) - it will show you where it is on google maps

import enum
from requests.models import HTTPError
import speech_recognition as sr
import webbrowser
import time
import os
import playsound
import random
import datetime
import pickle
import os.path
from speech_recognition import Microphone
import spotipy as sp
import pandas as pd
from spotipy.exceptions import SpotifyException
from spotipy.oauth2 import SpotifyOAuth

from spotifyCommands import *
from PyDictionary import PyDictionary
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from gtts import gTTS
from time import ctime

#setup 
setup = pd.read_csv('setup.txt', sep='=', index_col=0, squeeze=True, header=None)

#spotify setup
client_id = setup['client_id']
client_secret = setup['client_secret']
device_name = setup['client_id']
redirect_uri = setup['redirect_uri']
scope = setup['scope']
username = setup['username']
mic = setup['mic']

auth_manager = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope=scope,
    username=username
)
spotify = sp.Spotify(auth_manager=auth_manager)

devices = spotify.devices()
deviceID = None
for d in devices['devices']:
    d['name'] = d['name'].replace('’', '\'')
    if d['name'] == device_name:
        deviceID = d['id']
        break

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

dictionary=PyDictionary()
r = sr.Recognizer()

for i,microphone_name in enumerate(Microphone.list_microphone_names()):
    if microphone_name == "Line (3- AudioBox USB 96)":
        mic = Microphone(device_index=1)

active = 0



def mia_setMode(mode):
    global active
    #print(mode)
    active = mode
    #print(active)

def mia_getMode():
    global active
    a = active
    return a

def auth_google():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    #now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    #print('Getting the upcoming 10 events')
    #events_result = service.events().list(calendarId='primary', timeMin=now,
                                        #maxResults=10, singleEvents=True,
                                        #orderBy='startTime').execute()
    #events = events_result.get('items', [])

    #if not events:
        #print('No upcoming events found.')
    #for event in events:
        #start = event['start'].get('dateTime', event['start'].get('date'))
        #print(start, event['summary'])

def mia_speak(audio_string):
    tts = gTTS(text=audio_string, lang='ja')
    r = random.randint(1,10000000)
    audio_file = 'audio' + str(r) + 'mia.mp3'
    tts.save(audio_file)
    playsound.playsound(audio_file)
    #os.system(audio_file)
    #mixer.music.load(audio_file)
    #mixer.music.play()
    print(audio_string)
    os.remove(audio_file)

def record_audio(ask=False):
    with sr.Microphone() as source:
        if ask:
            mia_speak(ask)
        #r.adjust_for_ambient_noise(source=source)
        audio = r.listen(source)
        voice_data = ''
        try:
            voice_data = r.recognize_google(audio)
            print(voice_data)
        except sr.UnknownValueError:
            if mia_getMode == 1:
                mia_speak('Sorry, I did not get that')
        except sr.RequestError:
            mia_speak('Sorry, my speech service is down')
        return voice_data

def respond(voice__data):
    #global active
    if 'it\'s fine' in voice_data or 'nevermind' in voice_data:
        mia_setMode(0)
        print('alright')
    elif 'what is your name' in voice__data:
        mia_speak('My name is Mia')
        mia_setMode(0)
    elif 'time' in voice_data:
        mia_speak('The time is: ' + ctime())
        mia_setMode(0)
    elif 'search' in voice_data or 'Search' in voice__data:
        if 'YouTube' in voice_data:
            datasplit = voice__data.split()
            removewords = ['search','YouTube','on','youtube','for']
            reswords = [word for word in datasplit if word.lower() not in removewords]
            sear = '+'.join(reswords)
            url = 'https://youtube.com/results?search_query=' + sear
            webbrowser.get().open(url)
            mia_setMode(0)
            mia_speak('Searched ' + sear + ' on youtube')
        else:
            search = record_audio('What do you want me to find')
            url = 'https://google.com/search?q=' + search
            webbrowser.get().open(url)
            mia_setMode(0)
            mia_speak('Here is what I found for ' + search)
    elif 'locate' in voice_data:
        loc = record_audio('What place do you want me to find')
        url = 'https://google.nl/maps/place/' + loc + '/&amp;'
        webbrowser.get().open(url)
        mia_speak('Here is the location for ' + loc)
        mia_setMode(0)
    elif 'where is' in voice_data or 'where\'s' in voice_data :
        datasplit = voice__data.split()
        removewords = ['where','where\'s','is']
        reswords = [word for word in datasplit if word.lower() not in removewords]
        wher = ''.join(reswords)
        url = 'https://google.nl/maps/place/' + wher + '/&amp;'
        webbrowser.get().open(url)
        mia_speak('Here is the location for ' + wher)
        mia_setMode(0)
    elif 'shut down' in voice_data:
        mia_speak('Shutting down')
        exit()
        mia_setMode(0)
    elif 'open' in voice__data:
        if 'calendar' in voice__data:
            mia_speak('ok')
            webbrowser.open('https://calendar.google.com/calendar/u/0/r/month/2020/10/1?tab=rc')
            mia_setMode(0)
    elif 'play' in voice__data:
        if 'spotify' in voice_data or 'Spotify' in voice__data:
            datasplit = voice__data.split()
            removewords = ['play','on','spotify','Spotify','artist','album']
            reswords = [word for word in datasplit if word.lower() not in removewords]
            pla = ' '.join(reswords)
            if 'artist' in voice__data:
                try:
                    uri= get_artist_uri(spotify=spotify,name=pla)
                    play_artist(spotify=spotify, device_id=deviceID,uri=uri)
                    mia_speak('playing' + pla)
                except HTTPError:
                    mia_speak('Unable to find artist')
                except SpotifyException:
                    mia_speak('Premium Required')
                except InvalidSearchError:
                    mia_speak('Unable to find artist')
            elif 'album' in voice__data:
                try:
                    uri= get_album_uri(spotify=spotify,name=pla)
                    play_album(spotify=spotify, device_id=deviceID,uri=uri)
                    mia_speak('playing' + pla)
                except HTTPError:
                    mia_speak('Unable to play album')
                except SpotifyException:
                    mia_speak('Premium Required')
                except InvalidSearchError:
                    mia_speak('Unable to find album')
            else:
                try:
                    uri= get_track_uri(spotify=spotify,name=pla)
                    play_track(spotify=spotify, device_id=deviceID,uri=uri)
                    mia_speak('playing' + pla)
                except HTTPError:
                    mia_speak('Unable to play track')
                except SpotifyException:
                    mia_speak('Premium Required')
                except InvalidSearchError:
                    mia_speak('Unable to find track')
            
    elif 'mean' in voice__data:
        datasplit = voice__data.split()
        removewords = ['what','does','this','word','mean']
        reswords = [word for word in datasplit if word.lower() not in removewords]
        word = ''.join(reswords)
        print(word)
        try:
            meaning = dictionary.meaning(word)
            phrase = 'The word' + word + ' means ' + meaning
        except IndexError:
            mia_speak('Word not found')
        mia_setMode(0)
    elif 'thank you' in voice_data:
        mia_speak('No problem')
        mia_setMode(0)
    elif 'do you love me' in voice_data:
        mia_speak('yes senpai it was on the day under the pink sakura tress where we fell in love')
        mia_setMode(0)
    elif len(voice__data) != 0:
        if not 'Mia' in voice_data:
            mia_speak('I do not have that function yet')
        mia_setMode(0)

time.sleep(1)
auth_google()
mia_speak('Mia Online')
while 1:
    voice_data = record_audio()
    mia_state = mia_getMode()
    if 'Mia' in voice_data or 'aimia' in voice_data:
        mia_speak('yes senpai?')
        mia_setMode(1)
    if mia_state == 1:
        #print('listening')
        respond(voice_data)

