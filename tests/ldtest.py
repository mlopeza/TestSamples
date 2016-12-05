import requests
import logging
import json
from nose.exc import SkipTest
from urlparse import urlparse, urljoin
import collections
from nose.tools import assert_equals, assert_true

LOG = logging.getLogger(__name__)

class LiarDiceTestBase(object):
  # This is a test object
  __test__ = True

  # These attributes get assigned by the nose Context Object before the init method
  server_url = "http://localhost"
  server_port = 8080
  secure_connection = True

  def __init__(self, *args, **kwargs):
    super(LiarDiceTestBase, self).__init__(*args, **kwargs)

  @classmethod
  def setUpClass(cls):
    """
    Verify that the site is available before the test and format the
    urls so we can make the requests more easily
    :return:
    """
    # We must have only a connection string, this will make sure that we only test the
    # server we intend to test, for now we won't worry about unix sockets
    if not cls.server_url.startswith("http"):
      cls.server_url = "http://%s" % cls.server_url
    url = urlparse(cls.server_url)
    cls.connection_string = "{scheme}://{hostname}:{port}".format(
      scheme=url.scheme,
      hostname=url.hostname,
      port=url.port if url.port else cls.server_port)
    # Problem communicating with the site, raising an exception
    if not cls.site_available():
      raise SkipTest("Site %s not available", (cls.connection_string))

  def new_game(self, **kwargs):
    """
    Create a new game
    :param kwargs: extra arguments for requests
    :return: requests.Response object
    """
    return self.post("games", **kwargs)

  def get_game(self, id, **kwargs):
    """
    Get a game by id
    :param id: game id
    :param kwargs: extra arguments for requests
    :return: requests.Response object
    """
    return self.get("games/{0}".format(id), **kwargs)

  def list_games(self, **kwargs):
    """
    List current games
    :param kwargs: extra arguments for requests
    :return: requests.Response object
    """
    return self.get("games", **kwargs)

  def claim(self, id, **kwargs):
    """
    Make a claim
    :param id: game id to which the claim will be directed to
    :param kwargs: extra arguments for requests
    :return: requests.Response object
    """
    return self.post("games/{0}/claim".format(id), **kwargs)

  def challenge(self, id, **kwargs):
    """
    Make a challenge
    :param id: game id to which the challenge will be directed to
    :param kwargs: extra arguments for requests
    :return: requests.Response object
    """
    return self.post("games/{0}/challenge".format(id), **kwargs)

  """
  All the methods use the requests library and the results will be analized as such
  """
  def put(self, endpoint, **kwargs):
    """
    Make a put call.
    :param endpoint: endpoint we are going to make the call to.
    :param kwargs: extra arguments for requests
    :return: requests.Response object
    """
    url = urljoin(self.connection_string, endpoint)
    LOG.debug("PUT %s DATA: %s" % (url, json.dumps(kwargs["data"]) if "data" in kwargs else "",))
    return requests.put(url,
                        verify=self.secure_connection, **kwargs)

  def get(self, endpoint, **kwargs):
    """
    Make a get call.
    :param endpoint: endpoint we are going to make the call to.
    :param kwargs: extra arguments for requests
    :return: requests.Response object
    """
    url = urljoin(self.connection_string, endpoint)
    LOG.debug("GET %s DATA: %s" % (url, json.dumps(kwargs["data"]) if "data" in kwargs else "",))
    return requests.get(url,
                        verify=self.secure_connection, **kwargs)

  def post(self, endpoint, **kwargs):
    """
    Make a post call.
    :param endpoint: endpoint we are going to make the call to.
    :param kwargs: extra arguments for requests
    :return: requests.Response object
    """
    url = urljoin(self.connection_string, endpoint)
    LOG.debug("POST %s DATA: %s" % (url, json.dumps(kwargs["data"]) if "data" in kwargs else "",))
    return requests.post(url,
                         verify=self.secure_connection, **kwargs)

  @classmethod
  def site_available(cls):
    """
    Verify if the selected site is available by making a requests to the landing page
    :return: True if the site is available
    """
    try:
      requests.get(cls.connection_string).raise_for_status()
      return True
    except requests.exceptions.HTTPError as e:
      LOG.error(e)
      return False

  def __get_json_or_raise(self, r):
    """
    Verify that the Response object has a valid json response.
    :param r: requests.Response
    :raises ValueError if the response doesn't have a valid json object
    """
    try:
      return r.json()
    except ValueError as v:
      raise ValueError("Invalid text found in response: %s" % self.format_response(r))

  def assert_ERROR(self, r, message=""):
    """
    :param r: requests.Response object
    :return: json object with the json response already validated (a valid json object)
    :raises ValueError if the reponse is not a json response
    :raises Exception if the response is not an error response
    """
    json_response = self.__get_json_or_raise(r)
    # Look for an error in the body message or the http code of user/server error
    if (isinstance(json_response, collections.Iterable) and "error" not in json_response) \
        or (r.status_code >= 400  and r.status_code < 600):
      assert_true(False, self.format_response(r))
    return json_response

  def assert_OK(self, r, message=""):
    """

    :param r: requests.Response
    :param message: Extra message appended to trace
    :return: json object with the json response already validated (a valid json object)
    """
    json_response = self.__get_json_or_raise(r)
    assert_equals(r.status_code, 200, "{0}\n{1}".format(message,self.format_response(r)))
    return json_response

  def format_response(self, r):
    """
    Format data for debug purposes
    :param r: requests.Response object
    :return:
    """
    return """
    Status Code: {0}
    Method: {1}
    User Headers: {2}
    Server Headers: {3}
    Url: {4}
    Encoding: {5}
    Content: {6}
    History:
    {7}
    Reason: {8}
    Elapsed: {9} ms""".format(r.status_code,
                              r.request.method,
                              r.request.headers,
                              r.headers,
                              r.url,
                              r.encoding,
                              r.text,
                              "\n".join(r.history),
                              r.reason,
                              r.elapsed)

  def assert_game_response_keys(self, response):
    keys = ("numDice", "numPlayers", "board", "actions", "playerHands", "_id")
    for key in keys:
      if key not in response:
        raise ValueError("Key '%s' wasn't avaialble in New Game Response." % key)