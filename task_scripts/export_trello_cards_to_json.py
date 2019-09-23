#!/usr/bin/env python
# -*- coding: utf-8 -*-
from src.trello_board import TrelloBoard
import configparser
import json, sys, os


config = configparser.ConfigParser()

try:
    path = os.path.join("../", "config.ini")
    config.read(os.path.relpath(path))
except configparser.Error as e:
    print(e, "Cannot get settings from config file")
    sys.exit(1)

trello_config = dict(
    key                 = config["trello"]["key"],
    token               = config["trello"]["token"],
    board_id            = config["trello"]["board_id"],
    test_board_id       = config["trello"]["test_board_id"],
    archive_board_id    = config["trello"]["archive_board_id"],
)


def main():

    trello = TrelloBoard(trello_config)

    exportCardsToJson(trello)

    return


if __name__ == '__main__':
    main()


def exportCardsToJson(trelloboard):

    if len(trelloboard.cards) < 1:
        print('\tNo cards found')
        return

    else:
        output = []
        print('Exporting card data to JSON...')
        cards = []
        lists = trelloboard.trello.boards.get_list(trelloboard.board_id)
        for l in lists:
            cardsFromList = trelloboard.trello.lists.get_card(l['id'])
            for card in cardsFromList:
                cards.append({
                    'listID': l['id'],
                    'listName': l['name'],
                    'cardID': card['id'],
                    'cardName': card['name'],
                    'cardDesc': card['desc']
                })

        for finalCard in cards:
            output.append(finalCard)

    with open(os.path.join('testTrelloData.json'), 'w') as trelloData:
        json.dump(output, trelloData)
