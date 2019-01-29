import I2C_LCD_driver
import time
import requests
import json
from pprint import pprint
import sys
 
mylcd = I2C_LCD_driver.lcd()
previous_song = ''
base_url = 'http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user='
user = 'lurttu69'
key = '9c395faf48c698e191c2a0a14220c31e'
artist = ''
song = ''
 
 
# Main loop that has the logic
def get_playing():
 
    query_song()
    global artist
    global song
    global previous_song
    La = len(artist)
    Ls = len(song)
    if SongChanged() == True: # Song changed
        print('SC: %s -> %s' % (previous_song, song))
        previous_song = song
        mylcd.lcd_clear()
        # Now we need to display track info
 
        if(La < 16 and Ls < 16): # No need for scroll
            mylcd.lcd_display_string(artist,1) # Show artist on the screen
            mylcd.lcd_display_string(song,2)   # Show song on the screen
            time.sleep(3) # Lets wait 3 sec and recheck
            get_playing()
        else: # Need to scroll
            Scroll()
 
    else: # Song didn't change
        if(La < 16 and Ls < 16): # Need to scroll?
            time.sleep(3)
            get_playing() # Check again
        else:
            Scroll()
 
# Checks what we need to scroll, and after 1x full scroll we call get_playing() again
def Scroll():
    global artist
    global song
    La = len(artist)
    Ls = len(song)
 
    if (La > 16 and Ls < 16): # Artist overflow (over 16 char)
        mylcd.lcd_display_string(song,2) # Show song on the screen
        scrollOne(1, artist) # Scroll the artist
 
    elif (La < 16 and Ls > 16): # Song overflow (over 16 char)
        mylcd.lcd_display_string(artist,1) # Show artist on the screen
        scrollOne(2, song) # Scroll the song
 
    elif (La > 16 and Ls > 16): # Both overflow (over 16 char)
        scrollBoth(artist, song)
 
    get_playing() # 1x scrolling shoulg be done, recheck song
 
# This will scroll one line of text, then it will query if song changed
def scrollOne(line, content):
    str_pad = " " * 16
    for i in range (0, len(content)):
        if (i < len(content)-15):
            lcd_text = content[i:(i+16)]
            mylcd.lcd_display_string(lcd_text,line)
            time.sleep(0.25)
            mylcd.lcd_display_string(str_pad,line)
   
    # scrolling done, return
 
# Work in progress, this should scroll both, then recheck song
def scrollBoth(artist, song):
    str_pad = " " * 16
    if (len(artist) > len(song)): ### ARTIST IS LONGER ###
        for i in range (0, len(artist)):
            if(i < len(song) - 15): # Will go until song is scrolled
                lcd_text1 = artist[i:(i+16)]
                lcd_text2 = song[i:(i+16)]
                mylcd.lcd_display_string(lcd_text1,1)
                mylcd.lcd_display_string(lcd_text2,2)
                time.sleep(0.25)
                mylcd.lcd_display_string(str_pad,1)
                mylcd.lcd_display_string(str_pad,2)
                print(i)
                print(len(song)-15)
                if (i == len(song)-16): mylcd.lcd_display_string(song[0:16],2)
            elif(i < len(artist) - 15): # Then only artist is scrolled to the end
                lcd_text1 = artist[i:(i+16)]
                mylcd.lcd_display_string(lcd_text1,1)
                time.sleep(0.25)
                mylcd.lcd_display_string(str_pad,1)
 
    elif (len(artist) < len(song)): ### SONG IS LONGER ###
        for i in range (0, len(song)):
            if(i < len(artist) - 15): # Will go until artist is scrolled
                lcd_text1 = artist[i:(i+16)]
                lcd_text2 = song[i:(i+16)]
                mylcd.lcd_display_string(lcd_text1,1)
                mylcd.lcd_display_string(lcd_text2,2)
                time.sleep(0.25)
                mylcd.lcd_display_string(str_pad,1)
                mylcd.lcd_display_string(str_pad,2)
                print(i)
                print(len(artist)-15)
                if (i == len(artist)-16): mylcd.lcd_display_string(artist[0:16],1)
            elif(i < len(song) - 15): # Then only song is scrolled to the end
                lcd_text2 = song[i:(i+16)]
                mylcd.lcd_display_string(lcd_text2,2)
                time.sleep(0.25)
                mylcd.lcd_display_string(str_pad,2)
    else: # Equal :)
        for i in range (0, len(artist)):
            if(i < len(artist)-15):
                lcd_text1 = artist[i:(i+16)]
                lcd_text2 = song[i:(i+16)]
                mylcd.lcd_display_string(lcd_text1,1)
                mylcd.lcd_display_string(lcd_text2,2)
                time.sleep(0.25)
                mylcd.lcd_display_string(str_pad,1)
                mylcd.lcd_display_string(str_pad,2)
 
# True || False if song has changed
def SongChanged():
    global song
    global previous_song
   
    if song != previous_song:
        return True
    else: return False
 
# Includes query and info update
def query_song():
    update_info(get_track())  # Update global artist & song
 
# Query to server
def get_track():
    # Request
    r = requests.get(base_url+user+'&api_key='+key+'&format=json')
    # Get data
    data = json.loads(r.text)
 
    return data['recenttracks']['track'][0]
 
# Updates globals with track info
def update_info(track):
    global artist
    global song
    try:
        if track['@attr']['nowplaying'] == 'true':
            artist = track['artist']['#text']
            song = track['name']
 
        # Error... didn't found a song playing        
    except KeyError:
        mylcd.lcd_clear()
        mylcd.lcd_display_string(u"Nothing playing.")
        query_song()
 
get_playing()