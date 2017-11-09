from pytube import YouTube
import youtube_dl
import sys

# for audio
ydl_opts = {
    'format': 'bestaudio/best',
    'preprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192'}]}

with open('download_links.txt') as f:
    links = f.read().split('\n')
    links = [x for x in links if x != ''] # remove all instances of empty strings
    if sys.argv[1] == 'video':
        for link in links:
            YouTube(link).streams.first().download()
    elif sys.argv[1] == 'audio':
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download(links)
