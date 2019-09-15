import datetime
from random import randint

from mongoengine import (
    CASCADE,
    Document,
    EmbeddedDocument,
)

from mongoengine import (
    signals,
    ValidationError
)
from mongoengine.fields import (
    EmbeddedDocumentField,
    IntField,
    ListField,
    ReferenceField,
    StringField,
)

from .base import BaseModel
from .user import UserModel
from minesweeper.config import config


class BoardModel(EmbeddedDocument):
    """Database model for the board of a GameResource
    """
    nbr_rows = IntField(min_value=2,)
    nbr_columns = IntField(min_value=2)
    nbr_mines = IntField(min_value=1)
    mines = ListField(StringField(min_length=6), default=[])
    flagged = ListField(StringField(min_length=6), default=[])
    opened = ListField(StringField(min_length=9), default=[])

    @classmethod
    def post_init(cls, sender, document, **kwargs):
        """Post-init hook to validate and update some dependant fields.
        """
        max_rows = config['app']['game'].get('max_rows', 99)
        max_columns = config['app']['game'].get('max_columns', 99)
        max_mines = config['app']['game'].get('max_columns', 99)

        # Check nbr_rows is in range
        if not 2 <= document.nbr_rows <= max_rows:
            raise ValidationError(f'Number of rows exceeds the maximum of {max_rows}')

        # Check nbr_columns is in range
        if not 2 <= document.nbr_columns <= max_columns:
            raise ValidationError(f'Number of columns exceeds the maximum of {max_columns}')

        # Check nbr_mines is in range
        if not 2 <= document.nbr_mines <= max(max_mines, max_rows * max_columns):
            raise ValidationError(f'Number of mines exceeds the maximum of {max_mines}')

        # Generate mines positions
        if not document.mines:
            mines = document.nbr_mines
            while mines:
                mine = str([randint(0, document.nbr_rows - 1), randint(0, document.nbr_columns - 1)])
                if mine in document.mines:
                    continue
                else:
                    document.mines.append(mine)
                    mines -= 1

    @property
    def nbr_cells(self):
        """Returns the number of cells in the board.

        :return: The number of cells in the board
        :rtype: int
        """
        return self.nbr_rows * self.nbr_columns

    def flag(self, cell):
        """Toggles a board cell as flagged/unflagged.

        :param cell: The coordinates of a cell in the board
        :type cell: string
        """
        if self.is_flagged(cell):
            self.flagged.remove(cell)
        elif not self.is_open(cell):
            self.flagged.append(cell)

    def open(self, cell):
        """Reveals a board cell and its surroundings.

        :param cell: The coordinates of a cell in the board
        :type cell: string
        :return: True if cell was opened, False otherwise
        :rtype: bool
        """
        # If cell can't be opened, return
        if self.is_flagged(cell) or self.is_open(cell):
            return False

        # Otherwise
        else:
            # Add cell to the list of opened cells
            self.opened.append(str(eval(cell) + [self.value(cell)]))

            # And if the cell didn't explode then...
            if not self.is_mine(cell):
                # Find neighbours that also need to be opened
                neighbours = set(n for n in self.neighbours(cell) if not self.is_open(n))
                while neighbours:
                    neighbour = neighbours.pop()
                    if not self.is_mine(neighbour):
                        self.opened.append(str(eval(neighbour) + [self.value(neighbour)]))
                        if not self.value(neighbour):
                            neighbours |= set(n for n in self.neighbours(neighbour) if not self.is_open(n))
            return True

    def is_cell(self, cell):
        """Indicates whether a cell is inside the board or not.

        :param cell: The coordinates of a cell in the board
        :type cell: string
        :return: True if the cell is within the board, False otherwise
        :rtype: bool
        """
        row, col = eval(cell)
        return 0 <= row < self.nbr_rows and 0 <= col < self.nbr_columns

    def is_mine(self, cell):
        """Indicates whether a cell is a mine or not.

        :param cell: The coordinates of a cell in the board
        :type cell: string
        :return: True if the cell is a mine, False otherwise
        :rtype: bool
        """
        return cell in self.mines

    def is_flagged(self, cell):
        """Indicates whether a cell is flagged or not.

        :param cell: The coordinates of a cell in the board
        :type cell: string
        :return: True if the cell is flagged, False otherwise
        :rtype: bool
        """
        return cell in self.flagged

    def is_open(self, cell):
        """Indicates whether a cell is opened or not.

        :param cell: The coordinates of a cell in the board
        :type cell: string
        :return: True if the cell is opened, False otherwise
        :rtype: bool
        """
        return any(opened_cell.startswith(cell[:-1]) for opened_cell in self.opened)

    def value(self, cell):
        """Indicates the number of mines surrounding the cell.

        :param cell: The coordinates of a cell in the board
        :type cell: string
        :return: The number of mines surrounding the cell
        :rtype: int
        """
        if self.is_mine(cell):
            return -1
        else:
            return sum(1 for cell in self.neighbours(cell) if self.is_mine(cell))

    def neighbours(self, cell):
        """Returns the list of cells that are neighbours of the given cell.

        :param cell: The coordinates of a cell in the board
        :type cell: string
        :return: The list of cells that are neighbours of the given cell
        :rtype: list
        """
        row, column = eval(cell)
        prev_row, next_row = max(0, row - 1), min(self.nbr_rows - 1, row + 1)
        prev_col, next_col = max(0, column - 1), min(self.nbr_columns - 1, column + 1)

        neighbours = set((
            f'[{prev_row}, {column}]',     # top
            f'[{prev_row}, {next_col}]',   # top_right
            f'[{row}, {next_col}]',        # right
            f'[{next_row}, {next_col}]',   # bottom_right
            f'[{next_row}, {column}]',     # bottom
            f'[{next_row}, {prev_col}]',   # bottom_left
            f'[{row}, {prev_col}]',        # left
            f'[{prev_row}, {prev_col}]',   # top_left
        ))

        if cell in neighbours:
            neighbours.remove(cell)

        return sorted(list(neighbours))


signals.post_init.connect(BoardModel.post_init, sender=BoardModel)


class GameModel(BaseModel, Document):
    """Database model for GameResource
    """
    player = ReferenceField(UserModel, reverse_delete_rule=CASCADE)
    board = EmbeddedDocumentField(BoardModel)
    status = StringField(choices=('new', 'started', 'paused', 'won', 'lost'), default='new')
    elapsed_seconds = IntField(min_value=0, default=0)

    @classmethod
    def pre_save(cls, sender, document, **kwargs):
        """Pre-save hook to validate and update certain fields before instance gets persisted.
        """
        # If the game is being updated, perform some validations
        if document.id:
            current_document = cls.get_by_id(document.id)

            # If game is concluded we cannot change anything in the game
            if current_document.status in ('won', 'lost'):
                document = current_document

            # If game is still going
            if current_document.status == 'started':
                # Check if player won the game
                if len(document.board.opened) + document.board.nbr_mines == document.board.nbr_cells:
                    document.status = 'won'
                    document.player.stats.won += 1
                    document.elapsed_seconds += (datetime.datetime.utcnow() - document.updated).seconds

                # Check if player lost the game
                elif any(document.board.is_open(mine) for mine in document.board.mines):
                    document.status = 'lost'
                    document.player.stats.lost += 1
                    document.elapsed_seconds += (datetime.datetime.utcnow() - document.updated).seconds

                # Check if game was paused
                elif document.status == 'paused':
                    document.elapsed_seconds += (datetime.datetime.utcnow() - document.updated).seconds

            if current_document.status == 'paused':
                if document.status not in ('paused', 'started'):
                    document.status = current_document.status

            # Prevent from 'reseting' the game
            if current_document.status != 'new' and document.status == 'new':
                document.status = current_document.status

            # Prevent from finishing from idle statuses
            if current_document.status in ('new', 'paused') and document.status in ('won', 'lost'):
                document.status = current_document.status

        # Call super-class hook aswell
        super().pre_save(sender, document, **kwargs)

    @property
    def started(self):
        """Returns True when the game has already started.

        :return: True if the game has already started, False otherwise
        :rtype: bool
        """
        return self.status != 'new'

    @property
    def paused(self):
        """Returns True when the game is paused.

        :return: True if the game is paused, False otherwise
        :rtype: bool
        """
        return self.status == 'paused'

    @property
    def finished(self):
        """Returns True when the game is over.

        :return: True if the game is over, False otherwise
        :rtype: bool
        """
        return self.status in ('won', 'lost')

    @property
    def elapsed_time(self):
        """Returns the game elapsed time in a string representation.

        :return: The game elapsed time.
        :rtype: string
        """
        elapsed = datetime.timedelta(seconds=self.elapsed_seconds)
        if self.status == 'started':
            return str(elapsed + (datetime.datetime.utcnow() - self.updated))
        else:
            return str(elapsed)

    def start(self):
        """Starts a new game.
        """
        if not self.started:
            self.status = 'started'
            self.save()

    def pause(self):
        """Toggles the game status between 'started' and 'paused'.
        """
        if self.started and not self.finished:
            self.status = 'started' if self.paused else 'paused'
            self.save()

    def flag(self, cell):
        """Toggles a board cell as flagged/unflagged.

        :param cell: The coordinates of a cell in the board
        :type cell: string
        """
        if self.started and not self.finished:
            self.board.flag(cell)
            self.save()

    def open(self, cell):
        """Reveals a board cell and its surroundings.

        :param cell: The coordinates of a cell in the board
        :type cell: string
        :return: True if cell was opened, False otherwise
        :rtype: bool
        """
        res = False
        if self.started and not self.finished:
            res = self.board.open(cell)
            self.save()
        return res

    def __repr__(self):
        return f'<Game {self.id} ({self.status})>'

    def __str__(self):
        return f'<Game {self.id} ({self.status})>'


signals.pre_save.connect(GameModel.pre_save, sender=GameModel)
