# -*- coding: utf-8 -*-

import sqlalchemy.types as types

from nailgun.jsonloader import json


class JSON(types.TypeDecorator):

    impl = types.Text

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value
