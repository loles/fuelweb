# -*- coding: utf-8 -*-

import traceback

import web
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm.query import Query
from sqlalchemy.exc import ProgrammingError
from sqlalchemy import create_engine

from nailgun.logger import logger
from nailgun.settings import settings

if settings.DATABASE['engine'] == 'sqlite':
    db_str = "{engine}://{path}".format(
        engine='sqlite',
        path="/" + settings.DATABASE['name']
    )
else:
    db_str = "{engine}://{user}:{passwd}@{host}:{port}/{name}".format(
        **settings.DATABASE
    )

engine = create_engine(db_str, client_encoding='utf8')


class NoCacheQuery(Query):
    """
    Override for common Query class.
    Needed for automatic refreshing objects
    from database during every query for evading
    problems with multiple sessions
    """
    def __init__(self, *args, **kwargs):
        self._populate_existing = True
        super(NoCacheQuery, self).__init__(*args, **kwargs)


orm = scoped_session(
    sessionmaker(bind=engine,
                 autoflush=True,
                 autocommit=False,
                 query_cls=NoCacheQuery)
    )


def load_db_driver(handler):
    try:
        return handler()
    except web.HTTPError:
        orm().commit()
        raise
    except:
        orm().rollback()
        raise
    finally:
        orm().commit()
        orm().expire_all()


def syncdb():
    from nailgun.api.models import Base
    Base.metadata.create_all(engine)


def dropdb():
    tables = [name for (name,) in orm().execute(
        "SELECT tablename FROM pg_tables WHERE schemaname = 'public'")]
    for table in tables:
        orm().execute("DROP TABLE IF EXISTS %s CASCADE" % table)

    # sql query to list all types, equivalent to psql's \dT+
    types = [name for (name,) in orm().execute("""
        SELECT t.typname as type FROM pg_type t
        LEFT JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace
        WHERE (t.typrelid = 0 OR (
            SELECT c.relkind = 'c' FROM pg_catalog.pg_class c
            WHERE c.oid = t.typrelid
        ))
        AND NOT EXISTS(
            SELECT 1 FROM pg_catalog.pg_type el
            WHERE el.oid = t.typelem AND el.typarray = t.oid
        )
        AND n.nspname = 'public'
        """)]
    for type_ in types:
        orm().execute("DROP TYPE IF EXISTS %s CASCADE" % type_)
    orm().commit()


def flush():
    import nailgun.api.models as models
    import sqlalchemy.ext.declarative as dec
    session = orm()
    for attr in dir(models):
        attr_impl = getattr(models, attr)
        if isinstance(attr_impl, dec.DeclarativeMeta) \
                and not attr_impl is models.Base:
            map(session.delete, session.query(attr_impl).all())
    # for table in reversed(models.Base.metadata.sorted_tables):
    #     session.execute(table.delete())
    session.commit()
