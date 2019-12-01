from __future__ import print_function, division
from loader import SetLoader
from mbcard import MBSet, MBType, MBCard
from player import Player
import pyforms
from pyforms.basewidget import BaseWidget
from pyforms.controls import ControlList
from pyforms.controls import ControlButton
from pyforms.controls import ControlCheckBox
from pyforms.controls import ControlCheckBoxList
from pyforms.controls import ControlLabel
from pyforms.controls import ControlText
from pyforms.controls import ControlCombo
from pyforms.controls import ControlEmptyWidget
from random import randint
from random import seed
from datetime import datetime
from threading import Thread
from playsound import playsound

# Create our loader
loader = SetLoader()
players = []
timerThread = None

# Add Person UI Class
# --------------------------------------------------------------------------------
# Used by the Millennium Blades UI Class to add new players to the game
class AddPlayerUI(Player, BaseWidget):
    global loader
    global players

    def __init__(self, checkedList):
        Player.__init__(self, '','','')
        BaseWidget.__init__(self,'Add New Player')

        # Init local vars
        self.__checked = checkedList

        # Init UI Elements
        self._txtPlayerName         = ControlText('Player Name')
        self._cboCharacterName      = ControlCombo('Character Name')
        self._cboStarterDeck        = ControlCombo('Starter Deck')
        self._btnAddPlayer          = ControlButton('Add Player')

        # Set up properties of UI elements, attach callbacks, etc.
        self._btnAddPlayer.value    = self.__onAddPlayerClick

        # Populate Character Names and Starter Decks
        characters = loader.getFilteredList(MBType.CHARACTER, self.__checked)
        decks = loader.getFilteredList(MBType.STARTER, self.__checked)
        for char in characters:
            self._cboCharacterName.add_item(char, char)
        for deck in decks:
            self._cboStarterDeck.add_item(deck, deck)
        
        # set up flow of components
        self.formset = [
            '_txtPlayerName',
            '_cboCharacterName',
            '_cboStarterDeck',
            '_btnAddPlayer'
        ]
    
    # Button Action Callback
    def __onAddPlayerClick(self):
        self.name = self._txtPlayerName.value
        self.character = self._cboCharacterName.value
        self.deck = self._cboStarterDeck.value
        if self.parent!=None: self.parent.addPlayer(self)

# Generate Players UI Class
# --------------------------------------------------------------------------------
# Displays a small window for randomly generating new players to the game
class GeneratePlayersUI(BaseWidget):
    # pass in global vars:
    global loader

    # Default Constructor
    # --------------------------------------------------------------------------------
    # Primarily used to define and setup UI components
    def __init__(self, checkedList):
        # Call constructors for super classes
        BaseWidget.__init__(self,'Generate Players')

        # init local vars
        self.__checked      = checkedList # List of expansions which are enabled

        # Init UI Components
        self.txtP1Name      = ControlText("Player 1 Name:")
        self.txtP2Name      = ControlText("Player 2 Name:")
        self.txtP3Name      = ControlText("Player 3 Name:")
        self.txtP4Name      = ControlText("Player 4 Name:")
        self.txtP5Name      = ControlText("Player 5 Name:")
        self.btnGen         = ControlButton("Generate Setup")

        # Set up properties of UI elements, attach callbacks etc.
        self.btnGen.value   = self.__onGenPlayerClick

    # Button Action Callbacks
    def __onGenPlayerClick(self):
        # init local vars
        names       = [
            self.txtP1Name.value,
            self.txtP2Name.value, 
            self.txtP3Name.value,
            self.txtP4Name.value, 
            self.txtP5Name.value
        ] # Hold the name of each player
        players     = [] # Our list of player objects to pass into our multi-add function

        # Seed the random number generator
        seed(datetime.now())

        # Generate players
        for name in names:
            if name != "":
                # Load in all allowed characters and starter decks remaining
                characters  = loader.getFilteredList(MBType.CHARACTER, self.__checked)
                decks       = loader.getFilteredList(MBType.STARTER, self.__checked)

                # Grab a random character and deck for the current player
                charIdx     = randint(0, len(characters) - 1)
                deckIdx     = randint(0, len(decks) - 1)

                # Create a new player object to add to our player list
                players.append(Player(name, characters[charIdx], decks[deckIdx]))

                # Mark deck and character as chosen
                loader.markSetChosen(characters[charIdx])
                loader.markSetChosen(decks[deckIdx])

        # If this has a parent, pass the generated list to it (should target our
        # instance of MBUI)
        if self.parent!=None: self.parent.addMultiPlayer(players, self)
    

# Scoring UI Class
# --------------------------------------------------------------------------------
# Class which sets up the score sheet for each player as well as the round timers
class ScoringUI(BaseWidget):
    # pass in global vars:
    global timerThread

    # Default Constructor
    # --------------------------------------------------------------------------------
    # Primarily used to define and setup UI components and class vars
    def __init__(self, playerList):
        # Call constructors for super classes
        BaseWidget.__init__(self, "Players")

        # init class vars
        self.__playerList       = playerList # List of defined players

        self.__timerStarted     = False # True if one of the round timers is running

        self.__timerPaused      = False # True if one of the round timers is paused

        self.__activeBtn        = None # Holds a reference to one of the timer
                                       # buttons and is used to make clicking each
                                       # button mutually exclusive among shared
                                       # functions

        # Init UI Components for Round 1 Deckbuilding
        self._lblR1DB           = ControlLabel("Round 1 Deckbuilding")
        self._btnR1Timer1       = ControlButton("7:00")
        self._btnR1Timer2       = ControlButton("7:00")
        self._btnR1Timer3       = ControlButton("6:00")
        self._txtR1DBPlayer1    = ControlText("Player 1")
        self._txtR1DBPlayer2    = ControlText("Player 2")
        self._txtR1DBPlayer3    = ControlText("Player 3")
        self._txtR1DBPlayer4    = ControlText("Player 4")
        self._txtR1DBPlayer5    = ControlText("Player 5")

        # Init callbacks for timers
        self._btnR1Timer1.value = self.__onRound1Phase1Click
        self._btnR1Timer2.value = self.__onRound1Phase2Click
        self._btnR1Timer3.value = self.__onRound1Phase3Click

        # Only show components for players currently defined
        self.__adjustTextFields([
            self._txtR1DBPlayer1,
            self._txtR1DBPlayer2,
            self._txtR1DBPlayer3,
            self._txtR1DBPlayer4,
            self._txtR1DBPlayer5
        ])

        # Init UI Components for Round 1 Tournament
        self._lblR1T            = ControlLabel("Round 1 Tournament")
        self._txtR1TPlayer1     = ControlText("Player 1")
        self._txtR1TPlayer2     = ControlText("Player 2")
        self._txtR1TPlayer3     = ControlText("Player 3")
        self._txtR1TPlayer4     = ControlText("Player 4")
        self._txtR1TPlayer5     = ControlText("Player 5")

        # Only show components for players currently defined
        self.__adjustTextFields([
            self._txtR1TPlayer1,
            self._txtR1TPlayer2,
            self._txtR1TPlayer3,
            self._txtR1TPlayer4,
            self._txtR1TPlayer5
        ])

        # Init UI Components for Round 2 Deckbuilding
        self._lblR2DB           = ControlLabel("Round 2 Deckbuilding")
        self._btnR2Timer1       = ControlButton("7:00")
        self._btnR2Timer2       = ControlButton("7:00")
        self._btnR2Timer3       = ControlButton("6:00")
        self._txtR2DBPlayer1    = ControlText("Player 1")
        self._txtR2DBPlayer2    = ControlText("Player 2")
        self._txtR2DBPlayer3    = ControlText("Player 3")
        self._txtR2DBPlayer4    = ControlText("Player 4")
        self._txtR2DBPlayer5    = ControlText("Player 5")

        # Init callbacks for timers
        self._btnR2Timer1.value = self.__onRound2Phase1Click
        self._btnR2Timer2.value = self.__onRound2Phase2Click
        self._btnR2Timer3.value = self.__onRound2Phase3Click

        # Only show components for players currently defined
        self.__adjustTextFields([
            self._txtR2DBPlayer1,
            self._txtR2DBPlayer2,
            self._txtR2DBPlayer3,
            self._txtR2DBPlayer4,
            self._txtR2DBPlayer5
        ])

        # Init UI Components for Round 2 Tournament
        self._lblR2T            = ControlLabel("Round 2 Tournament")
        self._txtR2TPlayer1     = ControlText("Player 1")
        self._txtR2TPlayer2     = ControlText("Player 2")
        self._txtR2TPlayer3     = ControlText("Player 3")
        self._txtR2TPlayer4     = ControlText("Player 4")
        self._txtR2TPlayer5     = ControlText("Player 5")

        # Only show components for players currently defined
        self.__adjustTextFields([
            self._txtR2TPlayer1,
            self._txtR2TPlayer2,
            self._txtR2TPlayer3,
            self._txtR2TPlayer4,
            self._txtR2TPlayer5
        ])

        # Init UI Components for Round 3 Deckbuilding
        self._lblR3DB           = ControlLabel("Round 3 Deckbuilding")
        self._btnR3Timer1       = ControlButton("7:00")
        self._btnR3Timer2       = ControlButton("7:00")
        self._btnR3Timer3       = ControlButton("6:00")
        self._txtR3DBPlayer1    = ControlText("Player 1")
        self._txtR3DBPlayer2    = ControlText("Player 2")
        self._txtR3DBPlayer3    = ControlText("Player 3")
        self._txtR3DBPlayer4    = ControlText("Player 4")
        self._txtR3DBPlayer5    = ControlText("Player 5")

        # Init callbacks for timers
        self._btnR3Timer1.value = self.__onRound3Phase1Click
        self._btnR3Timer2.value = self.__onRound3Phase2Click
        self._btnR3Timer3.value = self.__onRound3Phase3Click

        # Only show components for players currently defined
        self.__adjustTextFields([
            self._txtR3DBPlayer1,
            self._txtR3DBPlayer2,
            self._txtR3DBPlayer3,
            self._txtR3DBPlayer4,
            self._txtR3DBPlayer5
        ])

        # Init UI Components for Round 3 Tournament
        self._lblR3T            = ControlLabel("Round 3 Tournament")
        self._txtR3TPlayer1     = ControlText("Player 1")
        self._txtR3TPlayer2     = ControlText("Player 2")
        self._txtR3TPlayer3     = ControlText("Player 3")
        self._txtR3TPlayer4     = ControlText("Player 4")
        self._txtR3TPlayer5     = ControlText("Player 5")

        # Only show components for players currently defined
        self.__adjustTextFields([
            self._txtR3TPlayer1,
            self._txtR3TPlayer2,
            self._txtR3TPlayer3,
            self._txtR3TPlayer4,
            self._txtR3TPlayer5
        ])

        # Init UI Components for Friendship
        self._lblFriend         = ControlLabel("Friendship")
        self._txtFrPlayer1      = ControlText("Player 1")
        self._txtFrPlayer2      = ControlText("Player 2")
        self._txtFrPlayer3      = ControlText("Player 3")
        self._txtFrPlayer4      = ControlText("Player 4")
        self._txtFrPlayer5      = ControlText("Player 5")

        # Only show components for players currently defined
        self.__adjustTextFields([
            self._txtFrPlayer1,
            self._txtFrPlayer2,
            self._txtFrPlayer3,
            self._txtFrPlayer4,
            self._txtFrPlayer5
        ])

        # Init UI components for Totals
        self._lblTotal          = ControlLabel("Total")
        self._txtTotPlayer1     = ControlText("Player 1")
        self._txtTotPlayer2     = ControlText("Player 2")
        self._txtTotPlayer3     = ControlText("Player 3")
        self._txtTotPlayer4     = ControlText("Player 4")
        self._txtTotPlayer5     = ControlText("Player 5") 

        # Only show components for players currently defined
        self.__adjustTextFields([
            self._txtTotPlayer1,
            self._txtTotPlayer2,
            self._txtTotPlayer3,
            self._txtTotPlayer4,
            self._txtTotPlayer5
        ], True)

        # Create Button To Calculate Everyone's Score and attach callback
        self._btnCalcTotal  = ControlButton("Calculate Player Score")
        self._btnCalcTotal.value = self.__onCalcScoreClick

        # Set up position of all form elements
        self.formset = [
            ('_lblR1DB','_btnR1Timer1','_btnR1Timer2','_btnR1Timer3'),
            ('_txtR1DBPlayer1','_txtR1DBPlayer2','_txtR1DBPlayer3','_txtR1DBPlayer4','_txtR1DBPlayer5'),
            '_lblR1T',
            ('_txtR1TPlayer1','_txtR1TPlayer2','_txtR1TPlayer3','_txtR1TPlayer4','_txtR1TPlayer5'),
            ('_lblR2DB','_btnR2Timer1','_btnR2Timer2','_btnR2Timer3'),
            ('_txtR2DBPlayer1','_txtR2DBPlayer2','_txtR2DBPlayer3','_txtR2DBPlayer4','_txtR2DBPlayer5'),
            '_lblR2T',
            ('_txtR2TPlayer1','_txtR2TPlayer2','_txtR2TPlayer3','_txtR2TPlayer4','_txtR2TPlayer5'),
            ('_lblR3DB','_btnR3Timer1','_btnR3Timer2','_btnR3Timer3'),
            ('_txtR3DBPlayer1','_txtR3DBPlayer2','_txtR3DBPlayer3','_txtR3DBPlayer4','_txtR3DBPlayer5'),
            '_lblR3T',
            ('_txtR3TPlayer1','_txtR3TPlayer2','_txtR3TPlayer3','_txtR3TPlayer4','_txtR3TPlayer5'),
            '_lblFriend',
            ('_txtFrPlayer1','_txtFrPlayer2','_txtFrPlayer3','_txtFrPlayer4','_txtFrPlayer5'),
            '_lblTotal',
            ('_txtTotPlayer1','_txtTotPlayer2','_txtTotPlayer3','_txtTotPlayer4','_txtTotPlayer5'),
            '_btnCalcTotal'
        ]

    # Adjust Text Fields Method
    # --------------------------------------------------------------------------------
    # Used to adjust groups of player text fields on the scoring sheet. This function
    # hides all fields which are unassigned to players and also disables text entry
    # if an optional flag is passed in. This is defined to avoid writing a bunch
    # of redundant code.   
    def __adjustTextFields(self, fields, disableGroup = False):
        for f in fields:
            if disableGroup:
                f.enabled = False
            f.hide()
        
        for i in range(0, len(self.__playerList)):
            fields[i].label = self.__playerList[i].name
            fields[i].show()

    # Tally All Method
    # --------------------------------------------------------------------------------
    # This is a stub function which takes in a 2d array for inputs and a 1d array
    # as an output. This calls the Tally Score method for each group of inputs
    # and stores it in an appropriate output. This is used to total the score for all
    # players
    def __tallyAll(self, inputs, outputs):
        for i in range(0, len(self.__playerList)):
            self.__tallyScore(inputs[i],outputs[i])

    # Tally Score Method
    # --------------------------------------------------------------------------------
    # Sums the values for all passed inputs and stores them in the passed output's
    # value field. It is assumed that both inputs and output are ControlText pyform
    # objects.   
    def __tallyScore(self, inputs, output):
        # init local vars:
        totalScore = 0 # The summed up score for all inputs

        # loop over inputs
        for inp in inputs:
            # If the text field is empty, assign 0 to it
            if inp.value == "":
                inp.value = '0'
            totalScore += int(inp.value)
        
        # Convert total score to a string and put it in the output field
        output.value = str(totalScore)

    # Start Phase Method
    # --------------------------------------------------------------------------------
    # This method is called by all the timerButton callbacks and is used to initialize
    # and start a new thread with a timer for the corresponding phase.
    def __startPhase(self, phaseButton, phase=1):
        # Only do stuff if there is either not an active button or if this is the
        # active button.
        if self.__activeBtn == None or self.__activeBtn == phaseButton:
            # If the timer hasn't been started yet, mark it as started, start a new
            # async thread for the timer, and set the active button as this button
            if self.__timerStarted == False:
                    self.__timerStarted = True
                    timerThread         = Thread(
                                            target=self.__phaseThread, 
                                            args=(phaseButton,phase)
                                        )
                    timerThread.start()
                    self.__activeBtn    = phaseButton
            else:
                # if the timer is started, and we aren't paused, pause the timer. If
                # we ARE paused, unpause the timer.
                if self.__timerPaused == False:
                    self.__timerPaused = True
                else:
                    self.__timerPaused = False

    # Phase Thread Method
    # --------------------------------------------------------------------------------
    # This method is the method which is attached to our async thread and controls the
    # ticking of the phase timer for a given UI button.  
    def __phaseThread(self, phaseButton, phase=1):
        # init local vars
        startTime   = datetime.now().timestamp() # Set start time as current time
        current     = startTime # Set current time as equal to start time
        dt          = 0 # Set dt as 0 to start, no need to do calculations
        pMin        = 7 # Set starting number of minutes as 7
        pSec        = 0 # Set starting number of seconds as 0

        # If we're on phase 3, set number of minutes to 6 vs. 7
        if phase == 3:
            pMin -= 1

        # Continue ticking as long as our timer hasn't expired
        while((pMin+pSec) > 0):
            # Tick once per second (it's a stopwatch)
            if dt > 1 and self.__timerPaused == False:
                # Reset start time
                startTime = datetime.now().timestamp()

                # Adjust minutes and seconds accordingly
                pSec -= 1
                if pSec < 0:
                    pMin -= 1
                    pSec = 59
                
                # Create new label for button
                timeStr = str(pMin)+':'
                if pSec < 10:
                    timeStr += '0'
                timeStr += str(pSec)
                phaseButton.label = timeStr
            
            # Update current time and calculate new dt in preparation for
            # next loop interval
            current = datetime.now().timestamp()
            dt = current - startTime

        # Cleanup for timer expired
        self.__timerStarted = False # Set timer started to false
        phaseButton.hide() # Hide the expired timer
        playsound('./bell.mp3') # Play a chime to let users know timer expired
        self.__activeBtn = None # Clear out active button
        timerThread.join() # Join this to main thread so it doesn't block

    # Button click callbacks
    def __onRound1Phase1Click(self):
        self.__startPhase(self._btnR1Timer1, 1)
    
    def __onRound1Phase2Click(self):
        self.__startPhase(self._btnR1Timer2, 2)

    def __onRound1Phase3Click(self):
        self.__startPhase(self._btnR1Timer3, 3)

    def __onRound2Phase1Click(self):
        self.__startPhase(self._btnR2Timer1, 1)
    
    def __onRound2Phase2Click(self):
        self.__startPhase(self._btnR2Timer2, 2)

    def __onRound2Phase3Click(self):
        self.__startPhase(self._btnR2Timer3, 3)

    def __onRound3Phase1Click(self):
        self.__startPhase(self._btnR3Timer1, 1)
    
    def __onRound3Phase2Click(self):
        self.__startPhase(self._btnR3Timer2, 2)

    def __onRound3Phase3Click(self):
        self.__startPhase(self._btnR3Timer3, 3)

    def __onCalcScoreClick(self):
        self.__tallyAll([
            [
                self._txtR1DBPlayer1,
                self._txtR1TPlayer1,
                self._txtR2DBPlayer1,
                self._txtR2TPlayer1,
                self._txtR3DBPlayer1,
                self._txtR3TPlayer1,
                self._txtFrPlayer1
            ],
            [
                self._txtR1DBPlayer2,
                self._txtR1TPlayer2,
                self._txtR2DBPlayer2,
                self._txtR2TPlayer2,
                self._txtR3DBPlayer2,
                self._txtR3TPlayer2,
                self._txtFrPlayer2
            ],
            [
                self._txtR1DBPlayer3,
                self._txtR1TPlayer3,
                self._txtR2DBPlayer3,
                self._txtR2TPlayer3,
                self._txtR3DBPlayer3,
                self._txtR3TPlayer3,
                self._txtFrPlayer3
            ],
            [
                self._txtR1DBPlayer4,
                self._txtR1TPlayer4,
                self._txtR2DBPlayer4,
                self._txtR2TPlayer4,
                self._txtR3DBPlayer4,
                self._txtR3TPlayer4,
                self._txtFrPlayer4
            ],
            [
                self._txtR1DBPlayer5,
                self._txtR1TPlayer5,
                self._txtR2DBPlayer5,
                self._txtR2TPlayer5,
                self._txtR3DBPlayer5,
                self._txtR3TPlayer5,
                self._txtFrPlayer5
            ]
        ],
        [
            self._txtTotPlayer1,
            self._txtTotPlayer2,
            self._txtTotPlayer3,
            self._txtTotPlayer4,
            self._txtTotPlayer5,
        ])


# Millennium Blades UI Class
# --------------------------------------------------------------------------------
# A class to hold all the UI components for the main form. This is the class from
# Which all other UI classes and windows are called from.
class MBUI(BaseWidget):
    # pass in global vars
    global loader
    global timerThread

    # Default Constructor
    # --------------------------------------------------------------------------------
    # Primarily used to create and set up UI components and class variables.
    def __init__(self):
        # Class Vars:
        self.__players = [] # List of players

        # Player Setup Tab -- Init UI Elements
        #super(MBUI, self).__init__("Millennium Blades Helper")
        BaseWidget.__init__(self, "Millennium Blades Helper")
        self._lstPlayers    = ControlList('Player List')
        self._btnAddPl      = ControlButton('Add Player')
        self._btnRemPl      = ControlButton('Remove Selected Player')
        self._btnGenPl      = ControlButton('Generate Player Setup')

        # Player Setup Tab -- Set up properties of UI elements, attach callbacks, etc.
        self._lstPlayers.horizontal_headers = ['Name', 'Character', 'Starter Deck']
        self._btnAddPl.value = self.__onAddPlayerClick
        self._btnRemPl.value = self.__onRemoveSelectedPlayerClick
        self._btnGenPl.value = self.__onGeneratePlayerSetupClick

        # Store Setup Tab -- Init UI Elements
        self._lstStore      = ControlList('Store Components')
        self._ckAreaLabel   = ControlLabel('Sets To Use')
        self._btnGenerateSt = ControlButton('Generate Store')

        # Store Setup Tab -- Set up properties of UI elements, attach callbacks etc.
        self._lstStore.horizontal_headers = ['Category', 'Sets']
        self._btnGenerateSt.value = self.__onGenerateStoreClick

        # Scoring Tab -- Init UI Components
        self._scoringPanel = ControlEmptyWidget()
        self._btnGetScoring = ControlButton('Generate Score Sheet')

        # Scoring Tab -- Set up properties of UI elements, attach callbacks etc.
        self._btnGetScoring.value = self.__onGenerateScoringClick

        # Set Selection Tab -- Init UI Components
        self._chkArea       = ControlCheckBoxList('Sets To Use')

        # Set Selection Tab -- Set up properties of UI elements, attach callbacks etc.
        self._chkArea += ('Base Set', True)
        self._chkArea += ('Set Rotation', True)
        self._chkArea += ('MX #1: Crossover', True)
        self._chkArea += ('MX #2: Sponsors', True)
        self._chkArea += ('MX #3: Fusion Chaos', True)
        self._chkArea += ('MX #4: Final Bosses', True)
        self._chkArea += ('MX #5: Futures', True)
        self._chkArea += ('MX #6: Professionals', True)

        # Set up tabs and component flow for UI
        self.formset = [{
            '1. Player Setup':['_lstPlayers',' ',('_btnAddPl','_btnRemPl','_btnGenPl')],
            '2. Store Setup':['_lstStore',' ','_btnGenerateSt'],
            '3. Scoring':['_scoringPanel','_btnGetScoring'],
            '4. Set Selection':['_chkArea']
        }]

    # Add Player Method
    # --------------------------------------------------------------------------------
    # Used to add a single player to the list of players in the Player Setup tab.   
    def addPlayer(self, player):
        # Add player to list
        self._lstPlayers += [player.name+'\t\t', player.character+'\t\t', player.deck]

        # Mark deck and character player chose as chosen
        loader.markSetChosen(player.character)
        loader.markSetChosen(player.deck)

        # Append player to list of players
        self.__players.append(player)

        # Close the choose player UI
        player.close()

    # Add Multi Player Method
    # --------------------------------------------------------------------------------
    # Used to add multiple players to the player list. Unlike the add player method, 
    # this assumes that the player objects have already been marked chosen and simply
    # appends them to the list under Player Setup and also adds them to the global
    # players list. It also takes in a separate reference to a window to close.    
    def addMultiPlayer(self, players, window):
        for player in players:
            self._lstPlayers += [player.name+'\t\t', player.character+'\t\t', player.deck]
            self.__players.append(player)
        window.close()

    # Player Setup Tab -- Button Callbacks
    def __onAddPlayerClick(self):
        win = AddPlayerUI(self._chkArea.checked_indexes)
        win.parent = self
        win.show()
    
    def __onRemoveSelectedPlayerClick(self):
        self._lstPlayers -= self._lstPlayers.selected_row_index

    def __onGeneratePlayerSetupClick(self):
        loader.clearPlayerSetup()
        self._lstPlayers.clear()
        win = GeneratePlayersUI(self._chkArea.checked_indexes)
        win.parent = self
        win.show()

    # Store Setup Tab -- Button Callbacks
    def __onGenerateStoreClick(self):
        expansion = ""
        premium = ""
        master = ""
        fusion = ""
        tournament = ""
        seed(datetime.now())
        loader.clearStoreSetup()
        self._lstStore.clear()

        # Randomly select expansion sets and add to store
        for _ in range(0, 5):
            expansions = loader.getFilteredList(MBType.EXPANSION, self._chkArea.checked_indexes)
            exIdx = randint(0, len(expansions) - 1)
            expansion += expansions[exIdx]+', '
            loader.markSetChosen(expansions[exIdx])
        expansion = expansion[:-2]
        self._lstStore += ['Expansion Sets\t\t', expansion]

        # Randomly select premium sets and add to store
        for _ in range(0, 4):
            premiums = loader.getFilteredList(MBType.PREMIUM, self._chkArea.checked_indexes)
            preIdx = randint(0, len(premiums) - 1)
            premium += premiums[preIdx]+', '
            loader.markSetChosen(premiums[preIdx])
        premium = premium[:-2]
        self._lstStore += ['Premium Sets\t\t', premium]

        # Randomly select master sets and add to store
        for _ in range(0, 3):
            masters = loader.getFilteredList(MBType.MASTER, self._chkArea.checked_indexes)
            masIdx = randint(0, len(masters) - 1)
            master += masters[masIdx]+', '
            loader.markSetChosen(masters[masIdx])
        master = master[:-2]
        self._lstStore += ['Master Sets\t\t', master]

        # Randomly select fusion area sets and add to store
        fusionBronze    = loader.getFilteredList(MBType.BRONZE, self._chkArea.checked_indexes)
        fusionSilver    = loader.getFilteredList(MBType.SILVER, self._chkArea.checked_indexes)
        fusionGold      = loader.getFilteredList(MBType.GOLD, self._chkArea.checked_indexes)
        fbIdx = randint(0, len(fusionBronze) - 1)
        fsIdx = randint(0, len(fusionSilver) - 1)
        fgIdx = randint(0, len(fusionGold) - 1)
        fusion = '(Bronze) '+fusionBronze[fbIdx]+', '
        fusion+= '(Silver) '+fusionSilver[fsIdx]+', '
        fusion+= '(Gold) '+fusionGold[fgIdx]
        loader.markSetChosen(fusionBronze[fbIdx])
        loader.markSetChosen(fusionSilver[fsIdx])
        loader.markSetChosen(fusionGold[fgIdx])
        self._lstStore += ['Fusion Area Sets\t\t', fusion]

        # Randomly select tournament prizes and add to store
        tournamentBronze = loader.getFilteredList(MBType.BRONZE, self._chkArea.checked_indexes)
        tournamentSilver = loader.getFilteredList(MBType.SILVER, self._chkArea.checked_indexes)
        tbIdx = randint(0, len(tournamentBronze) - 1)
        tsIdx = randint(0, len(tournamentSilver) - 1)
        tournament = '(Bronze) '+tournamentBronze[tbIdx]+', '
        tournament+= '(Silver) '+tournamentSilver[tsIdx]
        loader.markSetChosen(tournamentBronze[tbIdx])
        loader.markSetChosen(tournamentSilver[tsIdx])
        self._lstStore += ['Tournament Prize Sets\t\t', tournament]
    
    # Scoring Tab -- Callback Functions
    def __onGenerateScoringClick(self):
        win = None
        if len(self.__players) > 0:
            win = ScoringUI(self.__players)
            win.parent = self
            self._scoringPanel.value = win
            win.show()

    # Close Application Callback
    def before_close_event(self):
        # If we have an executing timer thread, join it before exiting otherwise this
        # will hang
        if timerThread is not None:
            timerThread.join() 

# Start our application and load main window
pyforms.start_app(MBUI)