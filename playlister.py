import urllib.request
from bs4 import BeautifulSoup
import time
import datetime
import spotipy
from spotipy.oauth2 import SpotifyOAuth


def load_present_tracks(track_list):
    """Extract the ID's from the playlist object it is passed. Also returns a dictionary of ID's and song titles."""

    present_track_id = set()
    lookup_id = {}
    for i in track_list:
        present_track_id.add(i['track']['id'])
        lookup_id[i['track']['id']] = i['track']['name']
    return present_track_id, lookup_id


def get_track_ids(six_music):
    """ Take a dict of track names and song titles, queries the Spotify ID's. Returns a set of track ID's."""
    track_id = set()
    for i in six_music:
        string = i + ' ' + six_music[i]
        try:
            query = spot.search(string, limit=1)['tracks']['items'][0]
            lookupID[query['id']] = query['name']
            track_id.add(query['id'])
            print('Found on Spotify: {}'.format(string))

        except IndexError as error:
            print("""FUUUUUCK,{}, couldn't find this one: {}""".format(error, string))
    return track_id


def filter_list(paragraphs):
    """Take a list of paragraphs from the scraped page - returns them as track:artist dict."""
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
            x = 0
            for word in split:
                if word == '–':
                    split[x] = '-'
                x += 1
            split = ' '.join(split)
            song = split.split('-')
            print('song= {}'.format(song))
            current_playing[song[0].strip()] = song[1].strip()
    return current_playing


def fetch_playlist(url):
    """Scrape all of the paragraphs from the webpage. This works for 6 Music quite well due to their page format."""

    # html=download('https://www.bbc.co.uk/programmes/articles/5JDPyPdDGs3yCLdtPhGgWM7/bbc-radio-6-music-playlist')
    html = urllib. request.urlopen(url)
    print('{} seconds fetch.'.format(time.time()-start))
    content = html.read()
    soup = BeautifulSoup(content,'html.parser')
    all_p = soup.find_all('p')
    return all_p


def add_to_playlist(id_list):
    """Add a list or ser of tracks to the playlist."""
    confirm = input('Add to playlist, are you sure??? (y) ')
    if confirm == 'y':
        spot.playlist_add_items(PLAYLIST_ID, id_list)
        return True

    return False


def remove_old_entries(days, track_list):
    """Find tracks in the playlist object that are older than the specified days, removes them."""

    id_list = []
    for item in track_list:
        date = item['added_at'][:10] # trim only the date from something like this: 2020-11-30T10:22:00Z
        date = datetime.datetime(int(date[0:4]), int(date[5:7]), int(date[8:10]))
        age = datetime.datetime.now() - date
        # print(date.strftime("%d %m %y"),end='')
        # print('....Age= {}'.format(age.days))
        if age.days > days:
            id_list.append(item['track']['id'])

    confirm = input('Are you sure you want to remove {} tracks?? (y) '.format(len(id_list)))
    if confirm == 'y':
        spot.playlist_remove_all_occurrences_of_items(PLAYLIST_ID, id_list, snapshot_id=None)
        print('removed')
    else:
        return False


def find_duplicate_names(id_list):
    """Find any tracks that have the same title and artist."""
    seen_track_names = set()
    duplicate_ids = set()

    for spot_id in id_list:
        track_hash = lookupID[spot_id]
        if track_hash in seen_track_names:
            duplicate_ids.add(spot_id)
        elif track_hash not in seen_track_names:
            seen_track_names.add(track_hash)
    return duplicate_ids


WEBSITE = 'https://www.bbc.co.uk/programmes/articles/5JDPyPdDGs3yCLdtPhGgWM7/bbc-radio-6-music-playlist'
PLAYLIST_ID = '7wYrBV5GqvjLYjfR2tz0YQ'

start = time.time()
allP = fetch_playlist(WEBSITE)
try:
    playlist = filter_list(allP)
except IndexError as e:
    print("ERROR: {}".format(e))
    try_num = 0
    while len(allP) <= 0:
        try_num += 1
        print("Trying again in 5... try {}".format(try_num))
        time.sleep(5)
        allP = fetch_playlist(WEBSITE)
    playlist = filter_list(allP)

scope = 'user-library-read playlist-modify-public'
spot = spotipy.Spotify(client_credentials_manager=SpotifyOAuth(scope=scope))
res = spot.playlist(PLAYLIST_ID)  # the playlist item from spotify api
res = res['tracks']
results = res['items']
while res['next']:
    res = spot.next(res)
    results.extend(res['items'])


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


dupes = find_duplicate_names(presentIDs)
print("{} duplicate items found...".format(len(dupes)))
for d in dupes:
    print(lookupID[d])
if input("Wanna Remove them? (y)") =="y":
    spot.playlist_remove_all_occurrences_of_items(PLAYLIST_ID, dupes)