#!/usr/bin/env python
# -*- coding: utf-8 -*-
from src.trello_board import TrelloBoard
import configparser
import sys
import os

config = configparser.ConfigParser()

try:
    config.read(os.path.relpath("../../config/config.ini"))
except OSError as e:
    print(e, "Cannot get settings from config file")
    sys.exit(1)


try:
    # Trello config values
    trello_config = dict(
        key                 = config["trello"]["key"],
        token               = config["trello"]["token"],
        board_id            = config["trello"]["board_id"],
        test_board_id       = config["trello"]["test_board_id"],
        archive_board_id    = config["trello"]["archive_board_id"],
    )
except KeyError as KE:
    print(KE, "Key does not exist")
    sys.exit(-1)

except configparser.Error as E:
    print(E, "Failed to get settings from config file")
    sys.exit(-1)


def main():

    trello = TrelloBoard(trello_config, testMode=True)

    copyProdToTest(trello)

    return


if __name__ == "__main__":
    main()


# TODO
def copyProdToTest(trello_board):

    print("Checking for existing cards in test")
    if len(trello_board.cards) > 0:
        print("\tExisting cards found... Deleting them")
        for card in trello_board.cards:
            trello_board.trello.cards.delete(card["id"])
        print("\t\tDone")
    else:
        print("\tNo cards found")

    print("Copying cards from production board to test...")
    cards = []
    lists = trello_board.trello.boards.get_list("7am1KHtj")
    for trello_list in lists:
        cardsFromList = trello_board.trello.lists.get_card(trello_list["id"])
        for card in cardsFromList:
            cards.append(
                dict(
                    listID      = trello_list["id"],
                    listName    = trello_list["name"],
                    id          = card["id"],
                    name        = card["name"],
                    cardDesc    = card["desc"]
            ))

    for finalCard in cards:
        if str(finalCard["listName"]).lower() == "atomic":
            trello_board._addNewCard(finalCard["name"], "5bbd035a167a425640682895", finalCard["cardDesc"])
        elif str(finalCard["listName"]).lower() == "hotfix":
            trello_board._addNewCard(finalCard["name"], "5addfdd969676faab792ee85", finalCard["cardDesc"])
        elif str(finalCard["listName"]).lower() == "staging":
            trello_board._addNewCard(finalCard["name"], "5addfdd969676faab792ee86", finalCard["cardDesc"])
        elif str(finalCard["listName"]).lower() == "other":
            trello_board._addNewCard(finalCard["name"], "5b8ea3917032ae342f1b3a4a", finalCard["cardDesc"])
        elif str(finalCard["listName"]).lower() == "master":
            trello_board._addNewCard(finalCard["name"], "5addfdd969676faab792ee87", finalCard["cardDesc"])
        if str(finalCard["listName"]).lower() == "complete":
            trello_board._addNewCard(finalCard["name"], "5b86fac5d1ec5b1724e03a4f", finalCard["cardDesc"])
    print("\tDone copying")
