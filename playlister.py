import urllib.request
from bs4 import BeautifulSoup
import time
import datetime
import spotipy
from spotipy.oauth2 import SpotifyOAuth


def load_present_tracks(playlist):
    items = playlist['tracks']['items']
    present_track_id = set()
    lookup_id = {}
    for i in items:
        present_track_id.add(i['track']['id'])
        lookup_id[i['track']['id']] = i['track']['name']
    return present_track_id, lookup_id


def get_track_ids(six_music):

    track_id = set()
    for i in six_music:
        string = i + ' ' + six_music[i]
        try:
            query = spot.search(string, limit=1)['tracks']['items'][0]['id']
            track_id.add(query)
            print('Found on Spotify: {}'.format(string))

        except IndexError as error:
            print("""FUUUUUCK,{}, couldn't find this one: {}""".format(error, string))
    return track_id


def filter_list(paragraphs):
    paragraphs.pop(0)
    paragraphs.pop(0)
    current_playing = {}
    for p in allP:
        removal_list = ['ft.', 'Ft.', 'X', 'feat.', '&']
        split = p.text.split()
        split = [word for word in split if word not in removal_list]
        if len(split) > 1:
            if split[0] == 'Hear' and split[1] == 'tracks':
                break
            i=0
            for word in split:
                if word == '–':
                    split[i] = '-'
                i += 1
            split = ' '.join(split)
            song = split.split('-')
            print('song= {}'.format(song))
            current_playing[song[0].strip()] = song[1].strip()
    return current_playing


def fetch_playlist():
    # html=download('https://www.bbc.co.uk/programmes/articles/5JDPyPdDGs3yCLdtPhGgWM7/bbc-radio-6-music-playlist')
    html = urllib. request.urlopen('https://www.bbc.co.uk/programmes/articles/5JDPyPdDGs3yCLdtPhGgWM7/bbc-radio-6-music-playlist')
    print('{} seconds fetch.'.format(time.time()-start))
    content = html.read()
    soup = BeautifulSoup(content,'html.parser')
    all_p = soup.find_all('p')
    return all_p


def add_to_playlist(id_list):
    confirm = input('Add to playlist, are you sure??? (y) ')
    if confirm == 'y':
        spot.playlist_add_items(playlistID, id_list)
        return True
    else:
        return False


def remove_old_entries(days, playlist):
    playlist = playlist['tracks']['items']
    id_list = []
    for item in playlist:
        date = item['added_at'][:10] # trim only the date from something like this: 2020-11-30T10:22:00Z
        date = datetime.datetime(int(date[0:4]), int(date[5:7]), int(date[8:10]))
        age = datetime.datetime.now() - date
        # print(date.strftime("%d %m %y"),end='')
        # print('....Age= {}'.format(age.days))
        if age.days > days:
            id_list.append(item['track']['id'])

    confirm = input('Are you sure you want to remove {} tracks?? (y) '.format(len(id_list)))
    if confirm == 'y':
        spot.playlist_remove_all_occurrences_of_items(playlistID, id_list, snapshot_id=None)
        print('removed')
    else:
        return False


def find_duplicate_names(id_list, playlist_id):
    seen_track_names = set()
    duplicate_ids = set()

    for spot_id in id_list:
        track_hash = lookupID[spot_id]
        if track_hash in seen_track_names:
            duplicate_ids.add(spot_id)
        elif track_hash not in seen_track_names:
            seen_track_names.add(track_hash)
    return duplicate_ids


start = time.time()
allP = fetch_playlist()
try:
    playlist = filter_list(allP)
except IndexError as e:
    print("ERROR: {}".format(e))
    try_num = 0
    while len(allP) <= 0:
        try_num += 1
        print("Trying again in 5... try {}".format(try_num))
        time.sleep(5)
        allP = fetch_playlist()
    playlist = filter_list(allP)

scope = 'user-library-read playlist-modify-public'
spot = spotipy.Spotify(client_credentials_manager=SpotifyOAuth(scope=scope))
playlistID = '7wYrBV5GqvjLYjfR2tz0YQ'  # Replace with your own playlist ID - You have to own it with the set credentials
results = spot.playlist(playlistID)  # the playlist item from spotify api

presentIDs, lookupID = load_present_tracks(results)
websiteIDs = get_track_ids(playlist)
newIDs = []
for ids in websiteIDs:
    if ids not in presentIDs:
        newIDs.append(ids)


print('############ NEW ############')
for ids in newIDs:
    print("Track: {} ID: {} ".format(lookupID[ids], ids))

print('Total time: {} seconds'.format(time.time()-start))

add_to_playlist(newIDs)
print('scanning for old entries over 180 days')
remove_old_entries(180, results)


dupes = find_duplicate_names(presentIDs, playlistID)
print("{} duplicate items found...".format(len(dupes)))
for i in dupes:
    print(lookupID[i])
if input("Wanna Remove them? (y)") =="y":
    spot.playlist_remove_all_occurrences_of_items(playlistID, dupes)