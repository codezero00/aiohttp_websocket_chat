import datetime
from aiohttp import web
from aiohttp_session import get_session
from sqlalchemy.sql import text
import json


def redirect(request, router_name):
    url = request.app.router[router_name].url()
    raise web.HTTPFound(url)


async def get_user_from_session(app_db, request):
    session = await get_session(request)
    if 'user_id' not in session:
        return None
    db_engine = request.app.db_engine
    user_rows = await app_db.select_with_filter(db_engine,
                                                app_db.user,
                                                id_=session['user_id'])
    for u in user_rows:
        return u


async def get_user_schedule(db_engine, user_id):
    async with db_engine.acquire() as conn:
        sql = text("""select i::time, case when exists(select 1 from schedule_items si
                                                           join schedule s on si.schedule_id = s.id
                                                           where user_id=:user_id and i::time >= si.start_time and i::time < si.end_time)
                                      then 1 else 0 end as in_work
                            from generate_series('2008-03-01 00:00'::timestamp, '2008-03-01 23:59', interval '1' hour) i""")
        return await conn.execute(sql, user_id=user_id)


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


def json_dumps(obj):
    return json.dumps(obj, default=json_serial)
