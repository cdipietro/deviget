from bson import ObjectId

from marshmallow import (
    EXCLUDE,
    fields,
    Schema,
)

from .validators import (
    validate_nbr_columns,
    validate_nbr_mines,
    validate_nbr_rows,
    validate_status
)


class BoardSchema(Schema):
    """Serialization schema for BoardModel
    """
    class Meta:
        unknown = EXCLUDE
        ordered = True

    nbr_rows = fields.Int(
        data_key='nbr_rows',
        required=True,
        allow_none=False,
        validate=validate_nbr_rows
    )

    nbr_columns = fields.Int(
        data_key='nbr_columns',
        required=True,
        allow_none=False,
        validate=validate_nbr_columns
    )

    nbr_mines = fields.Int(
        data_key='nbr_mines',
        required=True,
        allow_none=False,
        validate=validate_nbr_mines
    )

    mines = fields.Function(
        data_key='mines',
        required=True,
        allow_none=False,
        dump_only=True,
        many=True,
        serialize=lambda obj: sorted(obj.mines),
    )

    flagged = fields.Function(
        data_key='flagged',
        required=True,
        allow_none=False,
        dump_only=True,
        many=True,
        serialize=lambda obj: sorted(obj.flagged),
    )

    opened = fields.Function(
        data_key='opened',
        required=True,
        allow_none=False,
        dump_only=True,
        many=True,
        serialize=lambda obj: sorted(obj.opened),
    )


class GameSchema(Schema):
    """Serialization schema for GameModel
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

    player_id = fields.Function(
        data_key='player_id',
        required=True,
        allow_none=False,
        deserialize=lambda val: ObjectId(val),
        serialize=lambda obj: str(obj.player.id),
    )

    status = fields.String(
        data_key='status',
        required=True,
        allow_none=False,
        dump_only=True,
        validate=validate_status,
    )

    elapsed_time = fields.String(
        data_key='elapsed_time',
        required=True,
        allow_none=False,
        dump_only=True,
    )

    board = fields.Nested(
        'BoardSchema',
        required=True,
    )
