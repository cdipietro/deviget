import falcon

from minesweeper.config import config
from minesweeper.common.logging import setup_logger
from minesweeper.databases.mongo import connect_to_mongo_db
from minesweeper.middlewares import *
from minesweeper.resources.game import GameResource
from minesweeper.resources.user import UserResource
from minesweeper.resources.test import TestResource


# Load application configuration
config.load()

# Create application logger
logger = setup_logger()

# Connect to the application database
connect_to_mongo_db()

# Create application middlewares
middleware = [RequireJSONMiddleware()]

# Create application
app = application = falcon.API(middleware=middleware)

# Add app special handlers
app.add_error_handler(Exception, internal_error_handler)

# Setup Test resource endpoints
test_resource = TestResource()
app.add_route('/test', test_resource)

# Setup User resource endpoints
user_resource = UserResource()
app.add_route('/user', user_resource, suffix='collection')
app.add_route('/user/{user}', user_resource)

# Setup Game resource endpoints
game_resource = GameResource()
app.add_route('/game', game_resource, suffix='collection')
app.add_route('/game/{game}', game_resource)

logger.info('Minesweeper API started')
