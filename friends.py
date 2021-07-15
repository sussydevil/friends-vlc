#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# --------Install--------
# pip install inputimeout
# pip install requests
# install vlc player with 'brew install vlc' for MacOS (brew needed) or 'apt get vlc' for linux
# -----------------------

from inputimeout import inputimeout, TimeoutOccurred
import configparser
import requests
import os
path = "friends.conf"


# extended
def create_configuration():
    if not os.path.exists(path):
        print("Configuration file not found. Creating...")
        config = configparser.ConfigParser()
        config.add_section("Settings")
        config.set("Settings", "Season", str(1))
        config.set("Settings", "Episode", str(1))
        with open(path, "w") as config_file:
            config.write(config_file)
        print("File created successfully.")
    return 0


# extended
def write_configuration(input_season, input_episode):
    config = configparser.ConfigParser()
    config.add_section("Settings")
    config.set("Settings", "Season", str(input_season))
    config.set("Settings", "Episode", str(input_episode))
    with open(path, "w") as config_file:
        config.write(config_file)
    print("File write successfully.")
    return 0


# extended
def read_configuration():
    read_season = 0
    read_episode = 0
    config = configparser.ConfigParser()
    config.read(path)
    try:
        read_season = int(config.get("Settings", "Season"))
        read_episode = int(config.get("Settings", "Episode"))
    except configparser.Error:
        print("Parsing error. Exit.")
        exit(1)
    except ValueError:
        print("Value error. Exit.")
        exit(1)
    print("File read successfully.")
    return read_season, read_episode


# extended
def main():
    create_configuration()
    season, episode = read_configuration()
    answer = None
    print("Current season: {0}\nCurrent episode: {1}".format(season, episode))

    # enter season and episode
    try:
        answer = inputimeout(prompt="If you want to change season or episode, please input them\n"
                                    "Example - 1:2 (Season:Episode)\n>>> ", timeout=10)
    except TimeoutOccurred:
        print("Skipping...")
    if answer is not None:
        answer = answer.split(":")
        try:
            season = int(answer[0])
            episode = int(answer[1])
        except ValueError:
            print("Value error. Exit.")
            exit(1)

    error = 0

    # check for status code (if not 200, then season +=1, if it not works, then serial is finished (just little logic))
    while True:
        if error == 2:
            print("Changing season is not work. This is the end of serial.")
            exit(1)

        # reformat data for request
        if episode in {1, 2, 3, 4, 5, 6, 7, 8, 9}:
            episode_string = "0{0}".format(episode)
        else:
            episode_string = str(episode)
        if season in {1, 2, 3, 4, 5, 6, 7, 8, 9}:
            season_string = "0{0}".format(season)
        else:
            season_string = str(season)

        # request for check availability of link
        try:
            answer = requests.head("http://friends.mp4v.club/Friends.s{0}e{1}.DruzyaSerial.ru.mp4"
                                   .format(season_string, episode_string))
        except requests.ConnectionError:
            print("Connection error. Exit...")
            exit(1)

        # if episode not exists
        if answer.status_code == 404:
            episode = 1
            season += 1
            error += 1
            print("Episode is not OK. Changing season...")
            continue

        # if bad answer
        if answer.status_code != 200:
            print("Server returned bad status code: {0}. Exiting...".format(answer.status_code))
            exit(1)
        break

    # open vlc and play
    print("Episode is OK. Start playing...")
    os.system('vlc "http://friends.mp4v.club/Friends.s{0}e{1}.DruzyaSerial.ru.mp4" --play-and-exit'
              .format(season_string, episode_string))

    # write next episode to configuration file
    write_configuration(season, episode + 1)
    print("Configuration file saved.")
    exit(0)


if __name__ == '__main__':
    main()
