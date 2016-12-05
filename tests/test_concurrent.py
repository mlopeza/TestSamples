import logging
import sys
import threading

from nose.tools import assert_true, assert_false
from ldtest import LiarDiceTestBase
import datetime

LOG = logging.getLogger(__name__)

class ApiTest(LiarDiceTestBase):

  def test_create_concurrent_games(self):
    """
    Test the API to see if there's any error with concurrent game creation and
    verify that the performance is optimal
    """
    # Available only for this test
    # Nose is very explicit when it says that every tests is independent
    self.game_ids = list()
    self.errors = list()
    self.response_times = list()
    threads = list()
    for i in range(20):
      t = threading.Thread(target=self.create_games, kwargs={"N": 500})
      threads.append(t)
      t.start()

    for thread in threads:
      thread.join()
    avg_response_time = sum(self.response_times, datetime.timedelta(0)) / len(self.response_times)

    LOG.info("Average response: {0}".format(avg_response_time))
    if len(self.errors):
      assert_true(False, "Errors occurred while executing concurrent game creation.\n%s"
                  % "\n".join(self.errors)
                  )
    # These are arbitrary times, can be changed depending on the app needs
    assert_false(avg_response_time > datetime.timedelta(seconds=1),
                "API response time takes more than 1 second")
    assert_false(max(self.response_times) > datetime.timedelta(seconds=2),
                "One of the responses took more than 2 seconds")

  def create_games(self, N):
    """
    Use the API to create N games, we validate for errors and we include
    them in a global list created by the test that called the method.
    :param N: Number of games to create.
    :return: None
    """
    for game in xrange(N):
      if not hasattr(self, "response_times") or \
          not hasattr(self, "errors") or \
          not hasattr(self, "game_ids"):
        raise Exception("Nedded list objects haven't been initialized by the test method.")
      try:
        r = self.new_game(data={"numPlayers": 5, "numDice": 5})
        json_body = self.assert_OK(r)
        self.assert_game_response_keys(json_body)
        self.game_ids.append(json_body["_id"])
        self.response_times.append(r.elapsed)
      except Exception as e:
        self.errors.append(e.message)