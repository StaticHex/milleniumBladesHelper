from __future__ import print_function, division
from json import loads
from mbcard import MBType, MBSet, MBCard

class SetLoader:
    def __init__(self):
        # Read in data from json file and store in temporary object
        f = open('./setData.json', 'r')
        jsonData = f.read()
        f.close()
        jsonObj = loads(jsonData)
        self.setDict = {}
        for expansion in jsonObj:
            for cardType in expansion:
                if cardType != "name":
                    for setName in expansion[cardType]:
                        newCard = MBCard(setName)
                        newCard.setCardType(cardType)
                        newCard.setExpansionSet(expansion["name"])

                        enumSetName = newCard.getExpansionSet().name
                        if enumSetName not in self.setDict:
                            self.setDict[enumSetName] = []
                        self.setDict[enumSetName].append(newCard)