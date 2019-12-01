from __future__ import print_function, division
from json import loads
from mbcard import MBType, MBSet, MBCard

# Set Loader Class
# --------------------------------------------------------------------------------
# Stub class used to load in data from json file and parse into a dictionary
class SetLoader:
    # Default constructor
    # --------------------------------------------------------------------------------
    # Loads in data from json file to memory
    def __init__(self):
        # Read in data from json file and store in temporary object
        f = open('./setData.json', 'r')
        jsonData = f.read()
        f.close()
        jsonObj = loads(jsonData)

        # Create a dictionary to throw our data into
        self.setDict = {}

        # Parse entire json file
        for expansion in jsonObj:
            for cardType in expansion:
                if cardType != "name":
                    for setName in expansion[cardType]:
                        # Create a new card object and store the name of the
                        # enum object in a temp variable
                        newCard = MBCard(setName)
                        newCard.setCardType(cardType)
                        newCard.setExpansionSet(expansion["name"])
                        enumSetName = newCard.getExpansionSet().name

                        # Safely append to our dict i.e. if we haven't added
                        # to this set before, create an empty array before adding
                        if enumSetName not in self.setDict:
                            self.setDict[enumSetName] = []
                        self.setDict[enumSetName].append(newCard)

    # Mark Set Chosen Method
    # --------------------------------------------------------------------------------
    # Marks a specific set as having been picked before. Prevents a set from being
    # chosen multiple times
    def markSetChosen(self, setName):
        for curSetName in self.setDict:
            for cardSet in self.setDict[curSetName]:
                if cardSet.name == setName:
                    cardSet.chosen = True

    # Get Filtered List Method
    # --------------------------------------------------------------------------------
    # Returns all entries for a specific category of set with all chosen cards and
    # all cards belonging to disabled sets filtered out.
    def getFilteredList(self, setType=MBType.UNDEFINED, filters=[]):
        # Add 1 to each filter's index to account for 0 being UNDEFINED
        filters = [x + 1 for x in filters]

        # Convert numeric indicies into enum names
        allowedSets = []
        for mtype in MBSet:
            for fil in filters:
                if fil == mtype.value:
                    allowedSets.append(mtype.name)

        # Get filtered results
        filteredList = []
        for setName in self.setDict:
            if setName in allowedSets:
                for item in self.setDict[setName]:
                    if item.getCardType() == setType:
                        if not item.chosen:
                            filteredList.append(item.name)
        
        # Return filtered list
        return filteredList

    # Clear Player Setup Method
    # --------------------------------------------------------------------------------
    # Marks all PLAYER and STARTER cards as unchosen. Essentially resets player setup.
    def clearPlayerSetup(self):
        for curSetName in self.setDict:
            for cardSet in self.setDict[curSetName]:
                if cardSet.getCardType() == MBType.CHARACTER or \
                    cardSet.getCardType() == MBType.STARTER:
                    cardSet.chosen = False

    # Clear Store Setup Method
    # --------------------------------------------------------------------------------
    # Marks all BRONZE, SILVER, GOLD, EXPANSION, PREMIUM, and MASTER cards as
    # unchosen. Essentially resets the store
    def clearStoreSetup(self):
        for curSetName in self.setDict:
            for cardSet in self.setDict[curSetName]:
                if cardSet.getCardType() != MBType.CHARACTER or \
                    cardSet.getCardType() != MBType.STARTER:
                    cardSet.chosen = False
