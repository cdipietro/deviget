import falcon

from minesweeper.config import config
from minesweeper.common.logging import setup_logger
from minesweeper.middlewares import internal_error_handler
from minesweeper.resources.test import TestResource


# Load application configuration
config.load()

# Create application logger
logger = setup_logger()

# Create application middlewares
middleware = []

# Create application
app = application = falcon.API(middleware=middleware)

# Add app special handlers
app.add_error_handler(Exception, internal_error_handler)

# Instantiate application resources
test_resource = TestResource()

# Declare application routes
app.add_route('/test', test_resource)

logger.info('Minesweeper API started')
