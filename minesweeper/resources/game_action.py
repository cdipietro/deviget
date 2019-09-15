import falcon
from marshmallow import ValidationError

from .game import GameResource
from minesweeper.serializers.game_action import BoardCellSchema


class GameActionResource(object):
    """Class for modeling an API game actions resource.
    """

    def on_post(self, req, resp, **params):
        """Performs an action on a minesweeper game.

        :param req: An HTTP request object
        :type req: falcon.request.Request
        :param resp: An HTTP response object
        :type resp: falcon.response.Response

        :raise falcon.HTTPBadRequest: If payload has invalid data to perform any action
        """
        # Find requested game
        game_id = str(params[GameResource.resource_name])
        game_obj = GameResource.get_or_raise_404(game_id)

        # Process requested action
        action = params['action'].lower()

        if game_obj.finished:
            raise falcon.HTTPBadRequest(
                title='Bad Request',
                description='Cannot apply action as game has already finished.'
            )

        if action == 'start':
            self.process_game_start(game_obj)
        elif action == 'pause':
            self.process_game_pause(game_obj)
        elif action == 'flag':
            self.process_cell_flag(req, game_obj)
        elif action == 'open':
            self.process_cell_open(req, game_obj)

        game_obj.reload()
        resp.media = GameResource.serialize(game_obj)

    def process_game_start(self, game_obj):
        """Starts a minesweeper game.

        :param game_obj: A minesweeper game object
        :type game_obj: minesweeper.models.GameModel
        """
        # Verify game has never started
        if game_obj.started:
            raise falcon.HTTPBadRequest(
                title='Bad Request',
                description='Cannot apply action as game has already started.'
            )

        # Start game
        game_obj.start()

    def process_game_pause(self, game_obj):
        """Toggles the game status between 'started' and 'paused'.

        :param game_obj: A minesweeper game object
        :type game_obj: minesweeper.models.GameModel
        """
        # Verify game has already started
        if not game_obj.started:
            raise falcon.HTTPBadRequest(
                title='Bad Request',
                description='Cannot apply action as game has not yet started.'
            )

        # Toggle game status (started/paused)
        game_obj.pause()

    def process_cell_flag(self, req, game_obj):
        """Toggles a game board cell as flagged/unflagged.

        :param req: An HTTP request object
        :type req: falcon.request.Request
        :param game_obj: A minesweeper game object
        :type game_obj: minesweeper.models.GameModel
        """
        # Load cell coordinates from request payload
        cell = self.get_board_cell(game_obj, req.media)

        # Verify cell has not been opened yet
        if game_obj.board.is_open(cell):
            raise falcon.HTTPBadRequest(
                title='Bad Request',
                description='Cannot flag a cell that is already opened.'
            )

        # Toggle flag on cell
        game_obj.flag(cell)

    def process_cell_open(self, req, game_obj):
        """Reveals a game board cell and its surroundings.

        :param req: An HTTP request object
        :type req: falcon.request.Request
        :param game_obj: A minesweeper game object
        :type game_obj: minesweeper.models.GameModel
        """
        # Load cell coordinates from request payload
        cell = self.get_board_cell(game_obj, req.media)

        # Verify cell is not flagged
        if game_obj.board.is_open(cell):
            raise falcon.HTTPBadRequest(
                title='Bad Request',
                description='Cannot open a cell that is already opened.'
            )

        # Verify cell is not flagged
        if game_obj.board.is_flagged(cell):
            raise falcon.HTTPBadRequest(
                title='Bad Request',
                description='Cannot open a cell that is flagged.'
            )

        # Open cell
        game_obj.open(cell)

    @staticmethod
    def get_board_cell(game_obj, payload):
        """Parses the request payload and retrieves the coordinates of the cell on
        which the action must take place.

        :param game_obj: A minesweeper game object
        :type game_obj: minesweeper.models.GameModel
        :param payload: A game action request payload
        :type payload: json
        """
        # Verify game has started
        if not game_obj.started:
            raise falcon.HTTPBadRequest(
                title='Bad Request',
                description='Cannot apply action as game has not yet started.'
            )

        # Verify game is not paused
        if game_obj.paused:
            raise falcon.HTTPBadRequest(
                title='Bad Request',
                description='Cannot apply action as game is paused.'
            )

        # Load cell from request payload
        try:
            serializer = BoardCellSchema()
            cell_data = serializer.load(payload)
            cell = f"[{cell_data['row']}, {cell_data['column']}]"
        except ValidationError as err:
            raise falcon.HTTPBadRequest(
                f'Invalid game action payload',
                err.messages
            )

        # Check the obtained cell is within the game board
        if not game_obj.board.is_cell(cell):
            raise falcon.HTTPBadRequest(
                title='Bad Request',
                description='Given cell is not within the limits of the board.'
            )

        return cell
