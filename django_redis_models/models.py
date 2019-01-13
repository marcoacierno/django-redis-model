from __future__ import unicode_literals

import six
import django_rq


class GenericType(object):
    """
    Not used for now
    """


class RedisModel(object):
    def __init__(self, **kwargs):
        for field, value in kwargs.iteritems():
            setattr(self, field, value)

        self.primary_key_name = self.__class__.Meta.primary_key_name

        if not self.primary_key_name:
            raise ValueError('Meta.primary_key_name is required')

        self.redis_conn = django_rq.get_connection()

    def save(self):
        primary_key = getattr(self, self.primary_key_name, None)

        if primary_key is None:
            raise ValueError('We do not support auto primarykey yet')

        class_name = self.__class__.__name__

        self.redis_conn.lpush(
            '{}:all'.format(class_name),
            primary_key,
        )

        exposed_fields = dict(self.__dict__)
        exposed_fields.pop('redis_conn', None)
        exposed_fields.pop('primary_key_name', None)

        redis_key_to_use = '{}::{}'.format(class_name, primary_key)

        for field, value in exposed_fields.iteritems():
            if isinstance(value, six.string_types):
                value = value.encode('ascii', 'ignore')

            self.redis_conn.hset(redis_key_to_use, field, value)

        return True

    @classmethod
    def all(cls):
        redis_conn = django_rq.get_connection()
        class_name = cls.__name__
        all_items = redis_conn.lrange('{}:all'.format(class_name), 0, -1)

        objs = []

        for item in all_items:
            lookup_key = '{}::{}'.format(class_name, item)
            values = redis_conn.hgetall(lookup_key)

            objs.append(cls(**values))

        return objs

    @classmethod
    def get(cls, pk):
        redis_conn = django_rq.get_connection()
        class_name = cls.__name__

        lookup_key = '{}::{}'.format(class_name, pk)
        values = redis_conn.hgetall(lookup_key)

        return cls(**values)

    def delete(self):
        class_name = self.__class__.__name__
        primary_key = getattr(self, self.primary_key_name, None)

        if primary_key is None:
            return False

        self.redis_conn.lrem('{}:all'.format(class_name), value=primary_key, num=1)

        key_to_remove = '{}::{}'.format(class_name, primary_key)
        self.redis_conn.delete(key_to_remove)
        return True
