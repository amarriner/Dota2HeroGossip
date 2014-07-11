#!/usr/bin/python

import json
import keys
import os.path
import random
import re
import requests
import string
import twitter
import urllib
import xml.etree.ElementTree as ET

# Working directory
pwd = '/home/amarriner/python/dota_news'

# Regex to temporarily strip non alpha characters from a word
p = re.compile('[^A-Za-z]')

# List of RSS feeds
feeds = []
feeds.append('http://www.tmz.com/category/hook-ups/rss.xml')
feeds.append('http://www.tmz.com/category/celebrity-feuds/rss.xml')
feeds.append('http://www.tmz.com/category/celebrity-justice/rss.xml')
feeds.append('http://www.tmz.com/category/gossip-rumors/rss.xml')
feeds.append('http://www.tmz.com/category/party-all-the-time/rss.xml')
feeds.append('http://www.tmz.com/category/stars-in-heat/rss.xml')

# Read in a list of words
f = open('words.txt')
words = f.read().split('\n')
f.close()

# Read in a list of names
f = open('names/yob2013.txt')
names = f.read().split('\n')
f.close()

# Make names uppercase and strip out unecessary data
i = 0
while i < len(names):
   names[i] = names[i].split(',')[0].upper()
   i = i + 1

# Read in a JSON file of Dota 2 heroes
# From WebAPI: https://api.steampowered.com/IEconDOTA2_570/GetHeroes/v0001/?key=<API_KEY>&language=en_us
f = open('heroes.json')
heroes = json.loads(f.read())
f.close()

# Read random RSS feed from TMZ
request = requests.get(random.choice(feeds))
root = ET.fromstring(request.content)
headline = random.choice(root.findall('*/item/title')).text.split(' ')

# Loop through the headline words looking for names
# Not perfect because some names do appear in the word list
i = 0
tweet = ''
found = False
image = ''
while i < len(headline):
   w = p.sub('', headline[i].upper())

   if len(w):
      if w not in words:
         if w in names:

            # Get a random Dota 2 Hero
            hero = random.choice(heroes['result']['heroes'])

            # If we don't have the hero's image, download it
            if not os.path.isfile(pwd + '/images/' + hero['name'].replace('npc_dota_hero_', '') + '.png'):
               url = 'http://cdn.dota2.com/apps/dota2/images/heroes/' + hero['name'].replace('npc_dota_hero_', '') + '_lg.png'
               urllib.urlretrieve(url, pwd + '/images/' + hero['name'].replace('npc_dota_hero_', '') + '.png')

            # Replace the name we've found with the hero's name
            # Can be improved, assumes a last name in the next slot, but doesn't always happen
            tweet = tweet + hero['localized_name'] + ' '
            image = hero['name'].replace('npc_dota_hero_', '') + '.png'
            i = i + 1

            # Flag to ensure we only tweet when we've made a name replacement
            found = True

         else:
            tweet = tweet + headline[i] + ' '

      else:
         tweet = tweet + headline[i] + ' '

   else:
      tweet = tweet + headline[i] + ' '

   i = i + 1

# Tweet
if found:
   # Connect to Twitter
   api = twitter.Api(keys.consumer_key, keys.consumer_secret, keys.access_token, keys.access_token_secret)

   # Post tweet text and image
   status = api.PostMedia(tweet, pwd + '/images/' + image)
