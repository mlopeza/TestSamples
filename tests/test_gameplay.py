import logging
import sys
from nose.tools import assert_equals, assert_true
from utils.generators import random_string
from nose.exc import SkipTest
from ldtest import LiarDiceTestBase

LOG = logging.getLogger(__name__)

class GamePlayTest(LiarDiceTestBase):

  def play(self, players, dice):
    """
    Generate dummy gameplay to exercise a game from start to end
    The rules in the site aren't quite clear about how the game ends and the rule of placing
    certain number of dice in the center of the table before doing the bid is quite strange.
    The normal rules for a liars dice is to challenge until there's one user with dice in the table.
    :param players: Number of players
    :param dice: Number of dice
    :return: None
    """
    r = self.new_game(data={"numPlayers": players, "numDice": dice})
    json_body = self.assert_OK(r)
    self._assert_game_response_keys(json_body)
    game_id = json_body["_id"]
    while not GamePlayTest.end_game(json_body["playerHands"]):
      for player in xrange(players):
        # Skip players that already lost
        if not GamePlayTest.can_play(player, json_body["playerHands"]):
          continue

  @staticmethod
  def can_play(player, playerHands):
    return len(playerHands[player]) != 0

  @staticmethod
  def end_game(playerHands):
    sum = 0
    players = len(playerHands)
    for hand in playerHands:
      if len(hand) == 0:
        sum = sum + 1
    # Only one player left
    return sum != players - 1