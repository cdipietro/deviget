from marshmallow import (
    EXCLUDE,
    fields,
    Schema,
)

from .loaders import (
    load_name,
    load_password
)
from .validators import validate_email


class UserStatsSchema(Schema):
    """Serialization schema for UserStatsModel
    """
    class Meta:
        unknown = EXCLUDE
        ordered = True

    won = fields.Int(
        data_key='games_won',
        required=True,
        allow_none=False,
        dump_only=True,
    )

    lost = fields.Int(
        data_key='games_lost',
        required=True,
        allow_none=False,
        dump_only=True,
    )


class UserSchema(Schema):
    """Serialization schema for UserModel
    """
    class Meta:
        unknown = EXCLUDE
        ordered = True

    id = fields.Function(
        data_key='id',
        required=True,
        allow_none=False,
        dump_only=True,
        serialize=lambda obj: str(obj.id),
    )

    name_last = fields.Function(
        data_key='name_last',
        required=True,
        allow_none=False,
        deserialize=load_name,
        serialize=lambda obj: obj.name_last.title(),
    )

    name_first = fields.Function(
        data_key='name_first',
        required=True,
        allow_none=False,
        deserialize=load_name,
        serialize=lambda obj: obj.name_first.title(),
    )

    email = fields.String(
        data_key='email',
        required=True,
        allow_none=False,
        validate=validate_email,
    )

    password = fields.Function(
        data_key='password',
        required=True,
        allow_none=False,
        load_only=True,
        deserialize=load_password,
    )

    stats = fields.Nested(
        'UserStatsSchema',
        required=True,
        dump_only=True,
    )
