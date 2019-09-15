from marshmallow import (
    EXCLUDE,
    fields,
    Schema,
)


class BoardCellSchema(Schema):
    """Serialization schema for cells within the game board.
    """
    class Meta:
        unknown = EXCLUDE
        ordered = True

    row = fields.Int(
        data_key='row',
        required=True,
        allow_none=False,
        load_only=True,
    )

    column = fields.Int(
        data_key='column',
        required=True,
        allow_none=False,
        load_only=True,
    )
