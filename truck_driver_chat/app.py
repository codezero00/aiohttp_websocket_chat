#! /usr/bin/env python
import asyncio
import aiohttp_jinja2
import aiohttp_debugtoolbar
import aiopg.sa
import aioredis
import jinja2
from aiohttp_session import session_middleware
import aiohttp_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from aiohttp import web
from routes import routes
# from middlewares import db_handler, authorize
import settings

logger = settings.get_logger(__name__)


async def on_shutdown(app):
    for ws in app['websockets']:
        await ws.close(code=1001, message='Server shutdown')


async def shutdown(server, app, handler):
    server.close()
    await server.wait_closed()
    app.client.close()  # database connection close
    await app.shutdown()
    await handler.finish_connections(10.0)
    await app.cleanup()


async def init_postgres_engine(loop):
    engine = await aiopg.sa.create_engine(
        database=settings.DB_NAME,
        user=settings.DB_USER,
        password=settings.DB_SECRET,
        host=settings.DB_HOST,
        minsize=1,
        maxsize=5,
        loop=loop)
    return engine

async def init_redis(loop):
    return await aioredis.create_redis((settings.REDIS_HOST, settings.REDIS_PORT),
                                       loop=loop,
                                       db=settings.REDIS_DB_N,
                                       encoding='utf-8')


async def init(loop):
    logger.info('Start truck chat')
    middle = [
        session_middleware(EncryptedCookieStorage(settings.SECRET_KEY)),
    ]
    # add debug
    if settings.DEBUG:
        middle.append(aiohttp_debugtoolbar.middleware)
    app = web.Application(loop=loop, middlewares=middle)
    # init app common storages
    app['websockets'] = []
    app['chats_websockets'] = {}

    if settings.DEBUG:
        aiohttp_debugtoolbar.setup(app)
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('templates'))
    # init routes
    for route in routes:
        logger.debug('Add route %s', route)
        app.router.add_route(route[0], route[1], route[2], name=route[3])
    # set static
    app.router.add_static('/static', 'static', name='static')
    # init db and redis
    db_engine = await init_postgres_engine(loop)
    app.db_engine = db_engine
    app.redis = await init_redis(loop)
    app_handler = app.make_handler(access_log=logger)
    srv = await loop.create_server(app_handler, settings.SITE_HOST, settings.SITE_PORT)
    return srv, app_handler


def main():
    loop = asyncio.get_event_loop()
    srv, app_handler = loop.run_until_complete(init(loop))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        srv.close()
        loop.run_until_complete(srv.wait_closed())
    loop.close()

if __name__ == '__main__':
    main()