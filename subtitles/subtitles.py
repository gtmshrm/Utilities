#!/usr/bin/env python3
import argparse
import logging
import pathlib
import shutil
from PTN import parse
from zipfile import ZipFile


class Subtitles:
    """
    Class to perform subtitle-related operations.
    """
    def __init__(self, subtitle_zip_files_dir, target_dir, temp_storage_dir):
        """
        Function to get file paths.

        subtitle_zip_files_dir: Path to source directory for subtitle zip files.
        target_dir:             Path to directory which contains files
                                to which subtitles need to be linked.
        temp_storage_dir:       Path to directory to be used as storage
                                for saving files temporarily.
        """
        self.subtitle_zip_files_dir = pathlib.Path(subtitle_zip_files_dir)
        self.target_dir = pathlib.Path(target_dir)
        self.temp_storage_dir = pathlib.Path(temp_storage_dir)
        self._video_file_formats = ['3gp', 'avi', 'mkv', 'mp4', 'webm']

    def get_target_filenames(self):
        """
        Function to get a list a file names which are to be
        linked to corresponding subtitle file.
        """
        target_filenames = []
        for ext in self._video_file_formats:
            target_filenames.extend(
                    fn.name for fn in self.target_dir.glob(f'*.{ext}'))
        return target_filenames

    def unzip_subtitles(self, zip_filepath):
        """
        Function to unzip a file, extract all subtitles from it
        to temporary storage directory and return list of
        subtitle filenames.
        """
        with ZipFile(zip_filepath, 'r') as zip_obj:
           filenames = zip_obj.namelist()

           subtitle_filenames = [
               fn for fn in filenames if fn.endswith('.srt')
           ]
           for fn in subtitle_filenames:
               zip_obj.extract(fn, self.temp_storage_dir)
        return subtitle_filenames

    def gen_file_metadata_summary(self, metadata):
        """
        Function to generate summary of metadata in the format
        {title}.S{season}E{episode}.{quality} and return it.
        """
        title = metadata['title']
        season = str(metadata['season']).zfill(2)
        episode = str(metadata['episode']).zfill(2)
        quality = metadata['quality']

        file_metadata_summary = f'{title}.S{season}E{episode}.{quality}'
        return file_metadata_summary

    def cache_file_metadata(self, filenames):
        """
        Function to build a dictionary containing metadata
        about each of the files and return it.
        """
        file_metadata = {}
        for fn in filenames:
            metadata = parse(fn)
            metadata['fn'] = fn[:-4]
            file_metadata_summary = self.gen_file_metadata_summary(metadata)
            file_metadata[file_metadata_summary] = metadata
        return file_metadata

    def clean_temp_storage_dir(self, filenames):
        """
        Function to remove a list of files from a temporary
        storage directory.
        """
        for fn in filenames:
            try:
                pathlib.Path(pathlib.PurePath(self.temp_storage_dir, fn)).unlink()
            except FileNotFoundError:
                pass

    def link_subtitles_to_files(self):
        """
        Function to link a subtitle to corresponding file.
        """
        target_filenames = self.get_target_filenames()
        subtitle_filenames = []

        zip_filenames = self.subtitle_zip_files_dir.glob('*.zip')
        for zip_fn in zip_filenames:
            subtitle_filenames.extend(self.unzip_subtitles(zip_fn))

        subtitle_metadata = self.cache_file_metadata(subtitle_filenames)
        target_metadata = self.cache_file_metadata(target_filenames)

        for target_file_metadata_summary in target_metadata:
            try:
                source_filename = subtitle_metadata[target_file_metadata_summary]['fn']+'.srt'
                target_filename = target_metadata[target_file_metadata_summary]['fn']+'.srt'
                source_filepath = pathlib.PurePath(self.temp_storage_dir, source_filename)
                target_filepath = pathlib.PurePath(self.target_dir, target_filename)
                shutil.move(source_filepath, target_filepath)
                print(f'Subtitle for \'{target_file_metadata_summary}\' successfully linked.')
            except KeyError:
                logging.warning(f'Subtitle for \'{target_file_metadata_summary}\' not found!')

        self.clean_temp_storage_dir(subtitle_filenames)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="subtitle operations")
    # TODO Add subtitles operation: offset a subtitle by +/- x secs
    # parser.add_argument('-s', '--subtitle_filepath', 
    #         default=None, help='path to a subtitle file')
    parser.add_argument('-z', '--subtitle_zip_files_dir', 
            default=None, help='path to directory containing subtitle zip-files')
    parser.add_argument('-t', '--target_dir', 
            default=None, help='path to directory containing all target files')
    parser.add_argument('-r', '--temp_storage_dir', 
            default='/tmp', help='path to directory to be used for temporary storage')
    args = parser.parse_args()

    subittle_op = Subtitles(args.subtitle_zip_files_dir, args.target_dir, args.temp_storage_dir)
    subittle_op.link_subtitles_to_files()
