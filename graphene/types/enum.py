import six
from graphql.type import GraphQLEnumType, GraphQLEnumValue

from .definitions import ClassTypeMeta, GrapheneType
try:
    from enum import Enum as PyEnum
except ImportError:
    from ..utils.enum import Enum as PyEnum

from .proxy import TypeProxy


class GrapheneEnumType(GrapheneType, GraphQLEnumType):
    __slots__ = ('graphene_type', '_name', '_description', '_values', '_value_lookup', '_name_lookup')

    def __init__(self, *args, **kwargs):
        graphene_type = kwargs.pop('graphene_type')
        self.graphene_type = graphene_type
        self._name = None
        self._description = None
        self._values = None
        self._value_lookup = None
        self._name_lookup = None

    def get_values(self):
        # list of values GraphQLEnumValue
        enum = self.graphene_type._meta.enum
        values = []
        for name, value in enum.__members__.items():
            values.append(GraphQLEnumValue(name=name, value=value.value))
        return values


class EnumTypeMeta(ClassTypeMeta):

    def get_options(cls, meta):
        options = cls.options_class(
            meta,
            name=None,
            description=None,
            enum=None,
            graphql_type=None,
        )
        options.valid_attrs = ['graphql_type', 'name', 'description', 'enum', 'abstract']
        return options

    def construct_graphql_type(cls, bases):
        if not cls._meta.graphql_type and not cls._meta.abstract:
            cls._meta.graphql_type = GrapheneEnumType(
                graphene_type=cls,
                name=cls._meta.name or cls.__name__,
                description=cls._meta.description,
            )

    def construct(cls, bases, attrs):
        if not cls._meta.enum:
            cls._meta.enum = type(cls.__name__, (PyEnum,), attrs)
        return super(EnumTypeMeta, cls).construct(bases, {})

    def __call__(cls, *args, **kwargs):
        if cls is Enum:
            return Enum.create(PyEnum(*args, **kwargs))
        return super(EnumTypeMeta, cls).__call__(*args, **kwargs)

    def create(cls, python_enum):
        class Meta:
            enum = python_enum
        return type(Meta.enum.__name__, (Enum,), {'Meta': Meta})


class Enum(six.with_metaclass(EnumTypeMeta, TypeProxy)):
    class Meta:
        abstract = True

    def __getattr__(self, name):
        return getattr(self._meta.enum, name)