import falcon

from .base import BaseResource
from .user import UserResource
from minesweeper.models.game import GameModel
from minesweeper.serializers.game import GameSchema


class GameResource(BaseResource):
    """Class for modeling an API game resource.
    """
    resource_name = 'game'
    model_cls = GameModel
    schema_cls = GameSchema

    def on_put(self, req, resp, **params):
        """Overwrites BaseResource.on_put to disable it.
        """
        raise falcon.HTTPMethodNotAllowed(
            ('POST', 'GET', 'DELETE'),
            description=f'{req.method} method is not allowed for {self.resource_name} resources.'
        )

    def on_patch(self, req, resp, **params):
        """Overwrites BaseResource.on_patch to disable it.
        """
        raise falcon.HTTPMethodNotAllowed(
            ('POST', 'GET', 'DELETE'),
            description=f'{req.method} method is not allowed for {self.resource_name} resources.'
        )

    def on_get_collection(self, req, resp, **params):
        """Overwrites BaseResource.on_get_collection.
        """
        # TODO: Security needs to be added in this method in order to prevent
        # users from seing other users games
        return super().on_get_collection(req, resp, **params)

    def _create_resource(cls, resource_data):
        """Overwrites BaseResource._create_resource.
        """
        # Find the user that is going to own the game
        player_obj = UserResource.get_or_raise_404(resource_data.pop('player_id'))

        # Create the game object
        game_obj = cls.model_cls(**resource_data)
        game_obj.player = player_obj

        return game_obj
