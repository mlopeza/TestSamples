import logging
import sys

from nose.tools import assert_equals, assert_true, assert_false
from utils.generators import random_string
from nose.exc import SkipTest
from ldtest import LiarDiceTestBase

LOG = logging.getLogger(__name__)

class ApiTest(LiarDiceTestBase):

  def test_list_games(self):
    """
    Verify that listing the games returns an actual list
    :return:
    """
    r = self.list_games()
    self.assert_OK(r)
    try:
      r.json()
    except ValueError as e:
      assert_true(False, " A json object wasn't returned when asking for the game list.")

  def test_invalid_game_ids(self):
    """
    We ask for invalid game ids to verify if the server can handle such requests.
    """
    raise SkipTest("Requesting for invalid games crashes the server.")
    """
    /home/mario/Repos/liars-dice-front-end/game.js:15
    if (!this.document.board) this.document.board = [];
                    ^
    TypeError: Cannot read property 'board' of null
        at Object.Game (/home/mario/Repos/liars-dice-front-end/game.js:15:21)
        at /home/mario/Repos/liars-dice-front-end/game.js:33:8
        at callback (/home/mario/Repos/liars-dice-front-end/node_modules/nedb/lib/executor.js:30:17)
        at Cursor.execFn (/home/mario/Repos/liars-dice-front-end/node_modules/nedb/lib/datastore.js:464:14)
        at Cursor._exec (/home/mario/Repos/liars-dice-front-end/node_modules/nedb/lib/cursor.js:172:17)
        at /home/mario/Repos/liars-dice-front-end/node_modules/nedb/lib/executor.js:40:13
        at Immediate.q.process [as _onImmediate] (/home/mario/Repos/liars-dice-front-end/node_modules/async/lib/async.js:731:21)
        at processImmediate [as _immediateCallback] (timers.js:368:17)

    """
    for id_length in xrange(1, 1500):
      r = self.get_game(random_string(id_length))
      self.assert_ERROR(r)

  def test_number_of_dice_max_int(self):
    """
    We check if the server can handle or error out when asking for a really huge number of dice
    """
    raise SkipTest("Max Int crashes the server.")
    r = self.new_game(data={"numPlayers": 5, "numDice": sys.maxint})
    json_body = self.assert_OK(r)
    self.assert_game_response_keys(json_body)
    assert_equals(len(json_body["numDice"]), sys.maxint)
    assert_equals(len(json_body["numPlayers"]), 5)

  def test_number_of_players_max_int(self):
    """
    We check if the server can handle or error out when asking for a really huge number of players
    """
    raise SkipTest("Max Int crashes the server.")
    r = self.new_game(data={"numPlayers": sys.maxint, "numDice": 5})
    json_body = self.assert_OK(r)
    self.assert_game_response_keys(json_body)
    assert_equals(len(json_body["numPlayers"]), sys.maxint)
    assert_equals(len(json_body["numDice"]), 5)

  def test_valid_game(self):
    """
    Simple check for a valid game
    """
    r = self.new_game(data={"numPlayers": 5, "numDice": 5})
    json_body = self.assert_OK(r)
    self.assert_game_response_keys(json_body)

  def test_empty_claim(self):
    """
    Send an empty claim to a valid game.
    """
    raise SkipTest("Empty claims crashes the server.")
    """
    /home/mario/Repos/liars-dice-front-end/action.js:69
      return hand.reduce(function(accumulator, current) {
                   ^
    TypeError: Cannot read property 'reduce' of undefined
        at Function.Action.numberInHand (/home/mario/Repos/liars-dice-front-end/action.js:69:14)
        at Function.Action.removeDice (/home/mario/Repos/liars-dice-front-end/action.js:4:27)
        at Function.Action.add (/home/mario/Repos/liars-dice-front-end/action.js:29:23)
        at /home/mario/Repos/liars-dice-front-end/index.js:45:12
        at /home/mario/Repos/liars-dice-front-end/game.js:33:5
        at callback (/home/mario/Repos/liars-dice-front-end/node_modules/nedb/lib/executor.js:30:17)
        at Cursor.execFn (/home/mario/Repos/liars-dice-front-end/node_modules/nedb/lib/datastore.js:462:14)
        at Cursor._exec (/home/mario/Repos/liars-dice-front-end/node_modules/nedb/lib/cursor.js:172:17)
        at /home/mario/Repos/liars-dice-front-end/node_modules/nedb/lib/executor.js:40:13
        at Immediate.q.process [as _onImmediate] (/home/mario/Repos/liars-dice-front-end/node_modules/async/lib/async.js:731:21)
    """
    r = self.new_game(data={"numPlayers": 5, "numDice": 5})
    json_body = self.assert_OK(r)
    self.assert_game_response_keys(json_body)
    # make an empty claim
    r = self.claim(json_body["_id"], data={})
    self.assert_ERROR(r)


  def test_invalid_games(self):
    """
    We send a list of invalid games to the server to see if can
    verify them as correct or invalid.
    """
    tests=[
      { "description": "Create game, no data"
      },
      { "description": "numPlayers is a String",
        "numPlayers": random_string(20),
        "numDice": 5,
      },
      { "description": "numPlayers is a float.",
        "numPlayers": 17.5,
        "numDice": 5,
      },
      { "description": "numPLayers is negative.",
        "numPlayers": -1,
        "numDice": 5,
      },
      { "description": "numPlayers is zero",
        "numPlayers": 0,
        "numDice": 5,
      },
      # We have the assumption that 5 dice is the only valid number
      { "description": "Invalid numDice",
        "numPlayers": 5,
        "numDice": 4,
      },
      { "description": "numDice is negative",
        "numPlayers": 5,
        "numDice": -1,
      },
      { "description": "numDice is zero",
        "numPlayers": 5,
        "numDice": 0,
      },
      { "description": "numDice is a String",
        "numPlayers": 5,
        "numDice": 0,
      },
      { "description": "no numDice",
        "numPlayers": 5
      },
      { "description": "No numPlayers",
        "numDice": 5
      }
    ]
    for data in tests:
      fn = lambda x: self.execute_invalid_games(x)
      fn.description = data.pop("description", "")
      yield fn, data

  def execute_invalid_games(self, data):
    """
    This method will execute each combination generated the test generator of new games
    param: data json body sto be sent to the new game endpoint
    """
    r = self.new_game(data=data)
    self.assert_ERROR(r)

  def test_do_valid_claim(self):
    """
    Test if a valid game works as expected.
    """
    r = self.new_game(data={"numPlayers": 5, "numDice": 5})
    json_body = self.assert_OK(r)
    self.assert_game_response_keys(json_body)
    player_0_any_die_face = list(set(json_body["playerHands"][0]))[0]
    r = self.claim(json_body["_id"], data={
      "player": 0,
      "claimNumber": 1,
      "claimFace": player_0_any_die_face,
    })
    self.assert_OK(r, "Failed to do a valid claim")

  def test_valid_claims(self):
    """
    Execute a list of valid claims and verify if the work as expected
    """
    tests=[
      # We assume that only one die can be moved to the middle, after the player lost
      { "description": "Move one dice",
        "moveNumber": 1,
        "moveFace": "compute"
      },
      { "description": "Make a claim",
        "claimNumber": 1,
        "claimFace": 10,
      },
      { "description": "Make a claim with a current die",
        "claimNumber": 1,
        "claimFace": "compute",
      },
    ]
    # Fill the player number on all the moves if the player number doesn't exist
    for test in tests:
      if "player" not in test:
        test["player"] = 0
    for data in tests:
      fn = lambda x: self.execute_valid_claims(x)
      fn.description = data.pop("description", "")
      yield fn, data

  def execute_valid_claims(self, data):
    """
    This method executes all the combinations created by the valid claims generator
    :param data: json body sent to the server to do the claim
    """
    r = self.new_game(data={"numPlayers": 5, "numDice": 5})
    json_body = self.assert_OK(r)
    self.assert_game_response_keys(json_body)
    # Retrieve a valid face
    if "moveFace" in data and data["moveFace"] == "compute":
      data["moveFace"] = list(set(json_body["playerHands"][0]))[0]
    if "claimFace" in data and data["claimFace"] == "compute":
      data["claimFace"] = list(set(json_body["playerHands"][0]))[0]
    r = self.claim(json_body["_id"], data={
      "player": 0,
      "moveNumber": 1,
    })
    self.assert_OK(r)

  def test_invalid_claims(self):
    """
    Execute a list of invalid claims.
    """
    tests=[
      { "description": "Move more dices than available in hand should be invalid.",
        "moveNumber": sys.maxint,
        "moveFace": "compute"
      },
      { "description": "Invalid moveNumber (Neg).",
        "moveNumber": -100,
        "moveFace": "compute"
      },
      { "description": "Invalid moveNumber (No moveNumber).",
        "moveFace": "compute"
      },
      { "description": "Invalid moveNumber (No moveFace).",
        "moveNumber": sys.maxint
      },
      { "description": "Invalid moveNumber (moveNumber 0).",
        "moveNumber": 0,
        "moveFace": "compute"
      },
      { "description": "Invalid moveNumber (String).",
        "moveNumber": random_string(20),
        "moveFace": "compute"
      },
      { "description": "Invalid moveFace (No moveNumber).",
        "moveFace": "compute"
      },
      { "description": "Invalid moveFace (Neg).",
        "moveNumber": 1,
        "moveFace": -1
      },
      { "description": "Invalid moveFace (Non valid Die).",
        "moveNumber": 1,
        "moveFace": 200
      },
      { "description": "Invalid moveFace (No moveFace).",
        "moveNumber": 1
      },
      { "description": "Invalid moveFace (String).",
        "moveNumber": 1,
        "moveFace": random_string(20)
      },
      { "description": "claim more dices than available in hand should be invalid.",
        "claimNumber": sys.maxint,
        "claimFace": "compute"
      },
      { "description": "Invalid claimNumber (Neg).",
        "claimNumber": -100,
        "claimFace": "compute"
      },
      { "description": "Invalid claimNumber (No claimNumber).",
        "claimFace": "compute"
      },
      { "description": "Invalid claimNumber (No claimFace).",
        "claimNumber": sys.maxint
      },
      { "description": "Invalid claimNumber (claimNumber 0).",
        "claimNumber": 0,
        "claimFace": "compute"
      },
      { "description": "Invalid claimNumber (String).",
        "claimNumber": random_string(20),
        "claimFace": "compute"
      },
      { "description": "Invalid claimFace (No claimNumber).",
        "claimFace": "compute"
      },
      { "description": "Invalid claimFace (Neg).",
        "claimNumber": 1,
        "claimFace": -1
      },
      { "description": "Invalid claimFace (Non valid Die).",
        "claimNumber": 1,
        "claimFace": 200
      },
      { "description": "Invalid claimFace (No claimFace).",
        "claimNumber": 1
      },
      { "description": "Invalid claimFace (String).",
        "claimNumber": 1,
        "claimFace": random_string(20)
      }
    ]
    # Fill the player number on all the moves if the player number doesn't exist
    for test in tests:
      if "player" not in test:
        test["player"] = 0
    for data in tests:
      fn = lambda x: self.execute_invalid_claims(x)
      fn.description = data.pop("description", "")
      yield fn, data

  def execute_invalid_claims(self, data):
    """
    This method executes all the combinations created by the invalid claims generator.
    :param data: json body sent to the server to do the claim
    """
    r = self.new_game(data={"numPlayers": 5, "numDice": 5})
    json_body = self.assert_OK(r)
    self.assert_game_response_keys(json_body)
    # Retrieve a valid face
    if "moveFace" in data and data["moveFace"] == "compute":
      data["moveFace"] = list(set(json_body["playerHands"][0]))[0]
    if "claimFace" in data and data["claimFace"] == "compute":
      data["claimFace"] = list(set(json_body["playerHands"][0]))[0]
    r = self.claim(json_body["_id"], data={
      "player": 0,
      "moveNumber": 1,
    })
    self.assert_ERROR(r)

  def test_move_dice_to_center_re_rolls_dice(self):
    """
    Verify if every time we move a die or dice to the center our dice get re-rolled as
    stated in the game description.
    """
    r = self.new_game(data={"numPlayers": 5, "numDice": 5})
    json_body = self.assert_OK(r)
    self.assert_game_response_keys(json_body)
    id = json_body["_id"]
    # Player 0 hand
    before_list = json_body["playerHands"][0][1:]
    player_0_any_die_face = json_body["playerHands"][0][0]
    r = self.claim(id, data={
      "player": 0,
      "moveNumber": 1,
      "moveFace": player_0_any_die_face,
    })
    r = self.get_game(id)
    json_body = self.assert_OK(r)
    self.assert_game_response_keys(json_body)
    after_list = json_body["playerHands"][0]
    assert_true(len(before_list) == len(after_list), "Die didn't get removed from player's 0 hand. "
                                                     "Game: %s" % id)
    before_list.sort()
    after_list.sort()
    same_list = True
    for i in xrange(len(before_list)):
      same_list = same_list and (before_list[i] == after_list [i])
    # Check that at least one element is different
    assert_false(same_list, "Dice didn't get re-rolled when moving to the center.")


  def test_claim_twice(self):
    """
    We assume that only a claim can be done per turn
    """
    r = self.new_game(data={"numPlayers": 5, "numDice": 5})
    json_body = self.assert_OK(r)
    self.assert_game_response_keys(json_body)
    player_0_any_die_face = list(set(json_body["playerHands"][0]))[0]
    r = self.claim(json_body["_id"], data={
      "player": 0,
      "claimNumber": 1,
      "claimFace": player_0_any_die_face,
    })
    self.assert_OK(r, "Failed to do a valid claim")
    r = self.claim(json_body["_id"], data={
      "player": 0,
      "claimNumber": 1,
      "claimFace": player_0_any_die_face,
    })
    self.assert_ERROR(r, "Failed to error on invalid double claim.")

  def test_make_a_claim_in_invalid_game(self):
    """
    Test if we can send a claim to an non existing game
    """
    raise SkipTest("Asking for inexistent game crashes the server.")
    r = self.claim(random_string(20), data={
      "player": 0,
      "moveNumber": 0,
      "moveFace": 1,
    })
    self.assert_ERROR(r)

  def test_make_a_challenge_in_invalid_game(self):
    """
    Test if we can do a challenge to a non existent game
    """
    raise SkipTest("Asking for inexistent game crashes the server.")
    r = self.challenge(random_string(20), data={"player": 0})
    self.assert_ERROR(r)

  def test_challenge_before_making_claim(self):
    """
    Try to do a challenge before doing an actual claim. This should error out.
    """
    r = self.new_game(data={"numPlayers": 5, "numDice": 5})
    json_body = self.assert_OK(r)
    self.assert_game_response_keys(json_body)
    r = self.challenge(json_body["_id"], data={"player": 1})
    self.assert_ERROR(r)

  def test_challenge_after_making_a_claim(self):
    """
    Check if the challenge response is correct by counting number of die in the game
    and doing a good claim and an erroneous claim.
    """
    r = self.new_game(data={"numPlayers": 5, "numDice": 5})
    json_body = self.assert_OK(r)
    self.assert_game_response_keys(json_body)
    id = json_body["_id"]
    all_hands = list()
    for hand in json_body["playerHands"]:
      all_hands.extend(hand)
    # Check how many 0s we have
    ones = all_hands.count(1)
    r = self.claim(id, data={"player": 0, "claimNumber": ones, "claimFace": 1})
    self.assert_OK(r)
    # Challenge a true statement
    r = self.challenge(id, data={"player": 0})
    json_body = self.assert_OK(r)
    assert_true(json_body,"Claim executed by user should be correct. Game %s" % id)
    # Challenge a false statement
    r = self.claim(id, data={"player": 1, "claimNumber": ones + 1, "claimFace": 1})
    self.assert_OK(r)
    r = self.challenge(id, data={"player": 1})
    json_body = self.assert_OK(r)
    assert_false(json_body, "Claim executed by user is not correct. Game %s" % id)