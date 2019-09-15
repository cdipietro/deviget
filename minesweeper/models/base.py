from datetime import datetime

from mongoengine import signals
from mongoengine.fields import DateTimeField


class BaseModel(object):
    """Base resource database model class.
    """

    created = DateTimeField(default=datetime.utcnow)
    updated = DateTimeField(default=datetime.utcnow)

    @classmethod
    def pre_save(cls, sender, document, **kwargs):
        """Pre-save hook to update the `update` field before instance gets persisted.
        """
        document.updated = datetime.utcnow()

    @classmethod
    def get_by_id(cls, identifier):
        """Gets a model instance matching the given id, or returns None otherwise.

        :param cls: A resource model class
        :type cls: minsweeper.models.BaseModel
        :param identifier: The id of the instance to be searched
        :type identifier: string
        :return: A model class instance or None
        :rtype: minsweeper.models.BaseModel | None
        """
        return cls.objects.with_id(identifier)


signals.pre_save.connect(BaseModel.pre_save, sender=BaseModel)
