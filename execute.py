#!/usr/bin/env python2.7
import argparse
import datetime
import errno
import logging
import nose
import os
import sys

LOG = logging.getLogger(__name__)

class EnabledByDefaultPlugin(nose.plugins.base.Plugin):
  def __init__(self, name):
    super(EnabledByDefaultPlugin, self).__init__()
    self.name = name
    self.enabled = True

  def options(self, parser, env):
    """
    We inject the plugin in the options. There's no opt out
    """
    parser.add_option("--with-%s" % (self.name, ), dest=self.enableOpt, default=True)

class TFContextPlugin(EnabledByDefaultPlugin):
  def __init__(self, test_params):
    super(TFContextPlugin, self).__init__("test-framework-context")
    self.context = test_params

  def startContext(self, context):
    for attr, value in self.context.items():
      if hasattr(context, attr):
        setattr(context, attr, value)

def run_tests(nose_args, server_url, server_port, skip_ssl, output_directory, *args, **kwargs):
  LOG.info("Running tests")
  # Send the current local variables to the plugin
  plugin = TFContextPlugin(test_params=locals())
  start = datetime.datetime.now()
  runner = nose.main(
      exit=False,
      argv=["nosetests",
            "--with-xunit",
            "--exe",
            "--xunit-file=%s/nosetests.xml" % output_directory,
            "--nologcapture"] + nose_args,
      addplugins=[plugin],
      **kwargs)

  end = datetime.datetime.now()
  LOG.info("Total time: {0}".format(end - start))
  return runner.success

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--nose-args", action="store", default=[], dest="nose_args",
                      help="Extra nose arguments")
  parser.add_argument("--server-url", action="store", required=True, dest="server_url",
                      help="Server that is going to be tested.")
  parser.add_argument("--skip-ssl-verification", action="store", default=False, dest="skip_ssl",
                      help="Skip ssl validation if server is in https.")
  parser.add_argument("--server-port", action="store", default=8080, dest="server_port",
                      help="Port used by the server.", type=int)
  parser.add_argument("--xml-output", "-o", action="store", default="results",
                      dest="output_directory",
                      help="Directory in which the xml results are going to be written.")
  args = vars(parser.parse_args())
  try:
    os.mkdir(args["output_directory"])
  except OSError as e:
    if e.errno != errno.EEXIST:
        raise e
    pass
  if run_tests(**args):
    sys.exit(0)
  sys.exit(1)
