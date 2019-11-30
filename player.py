from __future__ import print_function, division

# Player Class
# --------------------------------------------------------------------------------
# Stub class which is used as a data model for the add player form
class Player(object):
    def __init__(self, playerName, characterName, deckName):
        self.name = playerName
        self.character = characterName
        self.deck = deckName
    