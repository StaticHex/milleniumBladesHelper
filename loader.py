from __future__ import print_function, division
from json import loads
from mbcard import MBType, MBSet, MBCard

# Set Loader Class
# --------------------------------------------------------------------------------
# Stub class used to load in data from json file and parse into a dictionary
class SetLoader:
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