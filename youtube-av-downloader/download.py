#!/usr/bin/env python
# -*- coding: utf-8 -*-

from youtube_dl import YoutubeDL
from functools import wraps
import glob, json, os, sys


class ContentDownloader(object):
    """
    Download torrents, youtube video and audio.

    Dependencies:
        - youtube_dl: `sudo -H pip install --upgrade youtube-dl`
        - ffmpeg: https://www.ffmpeg.org/
        - BitTornado: https://github.com/effigies/BitTornado (clone in ./)
    """

    def __init__(self, fconfigPath='./CONFIG.json'):
        """
        Initialize attributes based on config given by `fconfigPath`.
        """
        with open(fconfigPath) as jf:
            _fconfig = json.load(jf)
            self._ftype = _fconfig['type']
            self._destinationDir = _fconfig['destination_dir']
            self._defFormat = _fconfig['_default_op_format'][self._ftype]
            self._opts = _fconfig['_opts'][self._ftype]
            _flinksPath = _fconfig['links_path']
        with open(_flinksPath) as f:
            self._flinks = [x for x in f.read().split('\n') if x != '']
        self.download = eval('self.{}'.format(self._ftype))

    def _youtube(AV):
        """
        Decorator which contains wrapper for downloading youtube content.
        Wrapper can download playlist(s) if URL for playlist(s) is specified
        in place of individual video URLs.
        """
        @wraps(AV)
        def ytDownload(self):
            with YoutubeDL(self._opts) as ydl:
                ydl.download(self._flinks)
            return AV(self)
        return ytDownload

    def _torrent(T):
        """
        Decorator which contains wrapper for downloading torrents.
        Wrapper can download torrents from torrent files saved
        in destination directory.
        """
        @wraps(T)
        def tDownload(self):
            os.chdir('./BitTornado')
            os.system('python3 btlaunchmanycurses.py "{0}"'.format(
                                                            self._destinationDir))
            return T(self)
        return tDownload

    @_youtube
    def audio(self):
        """
        Convert default audio format which is '.m4a' to '.mp3' and
        '.m4r' using `ffmpeg` and save it to destination directory.
        Remove '.m4a' file.
        """
        for downloadedFile in glob.glob('*'+self._defFormat):
            destPath = os.path.join(
                        self._destinationDir,
                        downloadedFile.strip(self._defFormat))
            os.system(
                ('ffmpeg -i "{0}" -c:a libfdk_aac -f ipod -b:a 96k '
                 '"{1}"'.format(downloadedFile, destPath+'.m4r')))
            os.system(
                ('ffmpeg -v 5 -y -i "{0}" -acodec libmp3lame -ac '
                '2 -ab 192k "{1}" && rm "{0}"'.format(downloadedFile,
                                                    destPath+'.mp3')))

    @_youtube
    def video(self):
        """
        Move video files to destination directory.
        """
        for downloadedFile in glob.glob('*'+self._defFormat):
            os.rename(downloadedFile,
                      os.path.join(self._destinationDir, downloadedFile))

    @_torrent
    def torrent(self):
        """
        Ops to be performed after torrent has been downloaded
        """
        pass


if __name__ == '__main__':
    DownloadClient = ContentDownloader(fconfigPath='./CONFIG.json')
    DownloadClient.download()
