from __future__ import print_function, division
from enum import Enum

# Define an enum to hold a list of expansions
# --------------------------------------------------------------------------------
class MBSet (Enum):
    UNDEFINED = 0
    BASE = 1
    SET_ROTATION = 2
    CROSSOVER = 3
    SPONSORS = 4
    FUSION_CHAOS = 5
    FINAL_BOSSES = 6
    FUTURES = 7
    PROFESSIONALS = 8

# Define an enum to hold the different types of cards we can have
# --------------------------------------------------------------------------------
class MBType (Enum):
    UNDEFINED = 0
    CHARACTER = 1
    STARTER = 2
    EXPANSION = 3
    PREMIUM = 4
    MASTER = 5
    BRONZE = 6
    SILVER = 7
    GOLD = 8

# Define a card class to throw our loaded data into
# --------------------------------------------------------------------------------
class MBCard:
    # Default constructor for our card class
    # --------------------------------------------------------------------------------
    def __init__(self, setName = 'Not Found'):
        self.name       = setName   # Holds the name of the set being defined
        self.chosen     = False     # Holds whether the set has already been chosen
                                    # or not
    
    # Set Expansion Set Function
    # -------------------------------------------------------------------------------
    # Uses a big switch to convert the key name loaded in from json to an enum
    def setExpansionSet(self, cardSet):
        if cardSet == "Base Set":
            self.__expansionSet = MBSet.BASE
        elif cardSet == "Set Rotation":
            self.__expansionSet = MBSet.SET_ROTATION
        elif cardSet == "Crossover: Mini Expansion #1":
            self.__expansionSet = MBSet.CROSSOVER
        elif cardSet == "Sponsors: Mini Expansion #2":
            self.__expansionSet = MBSet.SPONSORS
        elif cardSet == "Fusion Chaos: Mini Expansion #3":
            self.__expansionSet = MBSet.FUSION_CHAOS
        elif cardSet == "Final Bosses: Mini Expansion #4":
            self.__expansionSet = MBSet.FINAL_BOSSES
        elif cardSet == "Futures: Mini Expansion #5":
            self.__expansionSet = MBSet.FUTURES
        elif cardSet == "Professionals: Mini Expansion #6":
            self.__expansionSet = MBSet.PROFESSIONALS
        else:
            self.__expansionSet = MBSet.UNDEFINED

    # Set Card Type Function
    # -------------------------------------------------------------------------------
    # Uses a big switch to convert the key name loaded in from json to an enum
    def setCardType(self, cardType):
        if cardType == "character profiles":
            self.__cardType = MBType.CHARACTER
        elif cardType == "starter decks":
            self.__cardType = MBType.STARTER
        elif cardType == "bronze promos":
            self.__cardType = MBType.BRONZE
        elif cardType == "silver promos":
            self.__cardType = MBType.SILVER
        elif cardType == "gold promos":
            self.__cardType = MBType.GOLD
        elif cardType == "expansion packs":
            self.__cardType = MBType.EXPANSION
        elif cardType == "premium packs":
            self.__cardType = MBType.PREMIUM
        elif cardType == "master packs":
            self.__cardType = MBType.MASTER
        else:
            self.__cardType == MBType.UNDEFINED

    # Getters and Setters
    # -------------------------------------------------------------------------------
    # Past this point is where I throw all the default getters and setters.
    def getExpansionSet(self):
        return self.__expansionSet
    
    def getCardType(self):
        return self.__cardType