"""
Convert all mkv files in current directory to mp4.
"""
import glob
import os


for i,f in enumerate(glob.glob('*.mkv')):
    filename = f.strip('.mkv')
    os.system('ffmpeg -i "{0}".mkv -c:v libx264 -c:a aac  "{0}".mp4'.format(filename))
