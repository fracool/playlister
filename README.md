# Spotify playlist web scraper

 **I wrote this to create playlists from lists of songs published on the BBC's website.**
 
 It's a bit basic, but can be seen as an example of how to use the Spotipy Libary.
 
 I use it for 6 music, but replace any of the pages url in the script, it should work. The way it detects the songs is pretty much tailored to the BBC's website, however this method would work for other radio stations, or lists of songs online with minor modification.

To get the script to run, you need API credentials from spotify, and then to set the following environment variables:

`SPOTIPY_CLIENT_SECRET='YOUR_CLIENT_SECRET';
SPOTIPY_CLIENT_ID='YOUR_CLIENT_KEY';
SPOTIPY_REDIRECT_URI='https://anyrandomurl.hahaha';`

You can put any url you like, however it must match what you set in the spotify dev console

You need to create a playlist and add its ID
