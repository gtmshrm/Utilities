#!/usr/bin/env python3 
import csv
import re


class WhiteListVerifier:
    """
    Class to check if non-whitelisted players are playing any steam-based server.
    """
    def __init__(self, users_filepath, whitelist_filepath, blacklist_filepath):
        """
        Get filepaths and load the following files: users, whitelist and blacklist.

        users_filepath: Path to a text file which contains info about users playing on any steam-based server.
        whitelist_filepath: Path to a csv file which contains Steam IDs and player-names of the white-listed players.
        blacklist_filepath: Path to a csv file which contains Steam IDs and player-names of the black-listed players.
        """
        with open(users_filepath) as f:
            self.users_rawcontents = f.read()
        raw_whitelist = list(csv.DictReader(open(whitelist_filepath)))
        raw_blacklist = list(csv.DictReader(open(blacklist_filepath)))
        self.whitelist = { p['Steam_ID']: p for p in raw_whitelist }
        self.blacklist = { p['Steam_ID']: p for p in raw_blacklist }

    def get_playername(self, steamid, player_records):
        """
        Function to return name of a person if steamid exits in given records 
        and return 'Unknown' otherwise.
        """
        return player_records.get(steamid, 'Unknown')

    def get_active_users_steamids(self):
        """
        Function to extract the Steam IDs using output of 'rcon users' command.
        """
        active_users_steamids = re.findall(r'STEAM_[0-5]:[01]:\d+', self.users_rawcontents)
        return active_users_steamids

    def verify_steamids(self):
        """
        Function to alert if people other than the ones mentioned in the whitelist are playing.
        """
        active_users_steamids = self.get_active_users_steamids()
        num_nonwhitelisted_users = 0

        for active_user in active_users_steamids:
            player = self.get_playername(active_user, self.whitelist)
            if player is 'Unknown':
                num_nonwhitelisted_users += 1
                nonwhitelisted_playername = self.get_playername(active_user, self.blacklist)
                print(f'-- Non-whitelisted player: {nonwhitelisted_playername}<{active_user}>')
        print(f'>> Total number of non-whitelisted players: {num_nonwhitelisted_users}')


if __name__ == '__main__':
    checker = WhiteListVerifier('data/users.txt', 'data/whitelist.csv', 'data/blacklist.csv')
    checker.verify_steamids()
