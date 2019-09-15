import falcon

from .base import BaseResource
from minesweeper.models.user import UserModel
from minesweeper.serializers.user import UserSchema


class UserResource(BaseResource):
    """Class for modeling an API user resource.
    """
    resource_name = 'user'
    model_cls = UserModel
    schema_cls = UserSchema

    def _create_resource(cls, resource_data):
        """Overwrites BaseResource._create_resource.
        """
        # Check if new user email already exists in the database
        if UserModel.objects(email=resource_data['email']).count():
            raise falcon.HTTPBadRequest(
                f'Invalid {cls.resource_name} payload',
                {'email': [f'Address {resource_data["email"]} already in use.']}
            )
        return cls.model_cls(**resource_data)
