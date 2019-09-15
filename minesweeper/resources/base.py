from abc import ABC, abstractmethod
from bson import ObjectId

import falcon
import mongoengine
from marshmallow import ValidationError


class BaseResource(ABC):
    """Abstract class for modeling a base API resource or collection of resources.
    """
    resource_name = None
    model_cls = None
    schema_cls = None

    def on_get(self, req, resp, **params):
        """Retrieves a resource instance from the database.

        :param req: An HTTP request object
        :type req: falcon.request.Request
        :param resp: An HTTP response object
        :type resp: falcon.response.Response
        :param params: A dict-like object representing any additional
        params derived from the route's URI template fields
        :type params: dict
        """
        # Look for the resource with the matching id in the database
        resource_obj = self.get_or_raise_404(params[self.resource_name])

        # Return serialized user object
        resp.media = self.serialize(resource_obj)

    def on_put(self, req, resp, **params):
        """Fully-updates a resource instance from the database.

        :param req: An HTTP request object
        :type req: falcon.request.Request
        :param resp: An HTTP response object
        :type resp: falcon.response.Response
        :param params: A dict-like object representing any additional
        params derived from the route's URI template fields
        :type params: dict
        """
        params.update({'partial': False})
        self._update_resource(req, resp, **params)

    def on_patch(self, req, resp, **params):
        """Partially updates a resource instance from the database.

        :param req: An HTTP request object
        :type req: falcon.request.Request
        :param resp: An HTTP response object
        :type resp: falcon.response.Response
        :param params: A dict-like object representing any additional
        params derived from the route's URI template fields
        :type params: dict
        """
        params.update({'partial': True})
        self._update_resource(req, resp, **params)

    def on_delete(self, req, resp, **params):
        """Removes a resource instance from the database.

        :param req: An HTTP request object
        :type req: falcon.request.Request
        :param resp: An HTTP response object
        :type resp: falcon.response.Response
        :param params: A dict-like object representing any additional
        params derived from the route's URI template fields
        :type params: dict
        """
        # Look for the resource with the matching id in the database
        resource_obj = self.get_or_raise_404(params[self.resource_name])

        # Delete resource
        resource_obj.delete()

    def on_get_collection(self, req, resp):
        """Retrieves several instances of a resource from the database.

        :param req: An HTTP request object
        :type req: falcon.request.Request
        :param resp: An HTTP response object
        :type resp: falcon.response.Response
        """
        resp.media = {'records': self.serialize(self.model_cls.objects, many=True)}

    def on_post_collection(self, req, resp):
        """Adds a new resource instance to the database.

        :param req: An HTTP request object
        :type req: falcon.request.Request
        :param resp: An HTTP response object
        :type resp: falcon.response.Response

        :raise falcon.HTTPBadRequest: If payload has invalid data to build a new resource instance
        """
        # Load new resource data
        resource_data = self.deserialize(req.media, partial=False)

        # Add new resource to the db
        resource_obj = self._create_resource(resource_data)
        resource_obj.save()

        # Return serialized new resource object
        resp.media = self.serialize(resource_obj)

    @abstractmethod
    def _create_resource(self, resource_data):
        """Auxiliary method for creating a resource instance.

        .note: This method need to be implemented by each especific resource class
        in order to properly build each new resource instance.

        :param resource_data: The new resource instance data
        :type resource_data: dict
        :return: A new resource instance
        :rtype: minesweeper.models.base.BaseModel
        """
        pass

    def _update_resource(self, req, resp, **params):
        """Auxiliary method for updating a resource instance from the database
        by its unique resource_id.

        :param req: An HTTP request object
        :type req: falcon.request.request
        :param resp: An HTTP response object
        :type resp: falcon.response.Response
        :param params: A dict-like object representing any additional
        params derived from the route's URI template fields
        :type params: dict

        :raise falcon.HTTPNotFound: If no resource instance matches the given resource id
        :raise falcon.HTTPBadRequest: If payload has invalid data to overwrite/update a resource instance
        """
        # Look for the resource with the matching id in the database
        resource_obj = self.get_or_raise_404(params[self.resource_name])

        # Load new resource data
        resource_data = self.deserialize(req.media, partial=params['partial'])
        resource_data['id'] = resource_obj.id

        # Update resource with new data
        for attr in dir(resource_obj):
            if attr in resource_data.keys():
                setattr(resource_obj, attr, resource_data[attr])
        resource_obj.save()

        # Return serialized user object
        resp.media = self.serialize(resource_obj)

    @classmethod
    def get_or_raise_404(cls, resource_id):
        """Auxiliary method for retrieving a resource instance from the database by its unique resource_id.

        :param resource_id: A resource instance unique identifier
        :type resource_id: string
        :return: The resource instance matching the given resource_id
        :rtype: minesweeper.models.base.BaseModel

        :raise falcon.HTTPNotFound: If no resource instance matches the given resource_id
        """

        resource_obj = cls.model_cls.get_by_id(ObjectId(resource_id))
        if resource_obj is None:
            raise falcon.HTTPNotFound(
                title='Not Found',
                description=f"Could not find {cls.resource_name} with id={resource_id}"
            )
        return resource_obj

    @classmethod
    def deserialize(cls, payload, partial=False):
        """Deserialize a resource method from a JSON form into a Python dict.

        :param payload: The payload with the resource data to be deserialized
        :type payload: json
        :param partial: Flag that indicates whether or not the payload must contain the whole resources schema
        :type partial: bool
        :return: A dictionary with deserialized data from the payload
        :rtype: dict
        """
        serializer = cls.schema_cls()
        try:
            resource_data = serializer.load(payload, partial=partial)
        except ValidationError as err:
            raise falcon.HTTPBadRequest(
                f'Invalid {cls.resource_name} payload',
                err.messages
            )
        return resource_data

    @classmethod
    def serialize(cls, resource, many=False):
        """Serialize a resource object or collection of resources objects into a JSON form.

        :param resource: An API resource or collection of resources
        :type resource: minesweeper.models.base.BaseModel
        :param many: Flag that indicates if more than one resource need to be serialized
        :type many: bool
        :return: A JSON object with the serialized data from the resource
        :rtype: json
        """
        serializer = cls.schema_cls(many=many)
        return serializer.dump(resource)
