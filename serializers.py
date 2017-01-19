from rest_framework.serializers import *

#from lucommon import settings
from django.conf import settings
from django.core.exceptions import FieldError

"""
Override `create` method: basically, this method are copied from
ModelSerializer class, just for the database switch function here.

Why?
It's a bug for rest framework(version:3.3.3), django(1.7.9) that
POST method write data to `default` db, and it's no interface for
user to configured
"""


class LuModelSerializer(ModelSerializer):
    """
    Lu ModelSerializer from ModelSerializer
    """
    def __init__(self, *args, **kwargs):
        # Instantiate the superclass normally
        super(LuModelSerializer, self).__init__(*args, **kwargs)

        if 'request' in self.context:
            # Implement for the response fields feature
            fields = self.context['request'].query_params.get(settings.RESPONSE_FIELD)
            if fields:
                fields = fields.split(settings.RESPONSE_FIELD_DELIMITER)
                # Drop any fields that are not specified in the `fields` argument.
                allowed = set(fields)
                existing = set(self.fields.keys())

                for field_name in existing - allowed:
                    self.fields.pop(field_name)

                if not self.fields:
                    raise FieldError('Fields `%s` invalid' % str(fields))

    def create(self, validated_data):
        """
        We have a bit of extra checking around this in order to provide
        descriptive messages when something goes wrong, but this method is
        essentially just:

            return ExampleModel.objects.create(**validated_data)

        If there are many to many fields present on the instance then they
        cannot be set until the model is instantiated, in which case the
        implementation is like so:

            example_relationship = validated_data.pop('example_relationship')
            instance = ExampleModel.objects.create(**validated_data)
            instance.example_relationship = example_relationship
            return instance

        The default implementation also does not handle nested relationships.
        If you want to support writable nested relationships you'll need
        to write an explicit `.create()` method.
        """
        raise_errors_on_nested_writes('create', self, validated_data)

        ModelClass = self.Meta.model

        # Remove many-to-many relationships from validated_data.
        # They are not valid arguments to the default `.create()` method,
        # as they require that the instance has already been saved.
        info = model_meta.get_field_info(ModelClass)
        many_to_many = {}
        for field_name, relation_info in info.relations.items():
            if relation_info.to_many and (field_name in validated_data):
                many_to_many[field_name] = validated_data.pop(field_name)

        try:
            ###################################
            #  Add switch database function   #
            ###################################
            db='default'
            try:
                db = validated_data.pop('using')
            except KeyError:
                pass

            instance = ModelClass.objects.using(db).create(**validated_data)
        except TypeError as exc:
            msg = (
                'Got a `TypeError` when calling `%s.objects.create()`. '
                'This may be because you have a writable field on the '
                'serializer class that is not a valid argument to '
                '`%s.objects.create()`. You may need to make the field '
                'read-only, or override the %s.create() method to handle '
                'this correctly.\nOriginal exception text was: %s.' %
                (
                    ModelClass.__name__,
                    ModelClass.__name__,
                    self.__class__.__name__,
                    exc
                )
            )
            raise TypeError(msg)

        # Save many-to-many relationships after the instance is created.
        if many_to_many:
            for field_name, value in many_to_many.items():
                setattr(instance, field_name, value)

        return instance


