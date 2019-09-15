from mongoengine import (
    Document,
    EmbeddedDocument
)
from mongoengine.fields import (
    EmailField,
    EmbeddedDocumentField,
    IntField,
    ListField,
    StringField,
)

from .base import BaseModel


class UserStatsModel(EmbeddedDocument):
    """Database model for the game statistics of a UserResource
    """
    won = IntField(min_value=0, default=0)
    lost = IntField(min_value=0, default=0)


class UserModel(BaseModel, Document):
    """Database model for UserResource
    """
    name_first = StringField(required=True, max_length=255)
    name_last = StringField(required=True, max_length=255)
    email = EmailField(required=True, unique=True)
    password = StringField(required=True, min_length=8)
    stats = EmbeddedDocumentField(UserStatsModel, default=UserStatsModel)

    def __repr__(self):
        return f'<User {self.id} ({self.email})>'

    def __str__(self):
        return f'<User {self.id} ({self.email})>'
