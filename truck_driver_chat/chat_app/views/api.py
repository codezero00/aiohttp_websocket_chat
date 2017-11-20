"""
As yet it is api with one method

TODO: implement REST
"""
from aiohttp import web
from common_web import get_user_from_session, get_user_schedule, json_dumps
import constants
import db as app_db




async def get_chats(request):
    """
    On page init
    """
    user_session = await get_user_from_session(app_db, request)
    if not user_session:
        return web.HTTPForbidden()
    user = app_db.user
    select = app_db.sa.select([c for c in list(user.c) if c.name not in 'password']).select_from(user)
    if user_session.role_id == constants.Roles.DRIVER:
        # For driver - only his supervisor
        query = select.where(user.c.id == user_session.supervisor_id)
    else:
        # For supervisor - only his subordinates
        query = select.where(user.c.supervisor_id == user_session.id)
    items = []
    async with request.app.db_engine.acquire() as conn:
        res = await conn.execute(query)
        for user_row in res:
            user_row = dict(user_row)
            user_row['birthdate'] = user_row['birthdate'].isoformat()
            user_row['schedule'] = []
            if user_session.role_id == constants.Roles.SUPERVISOR:
                # add schedule info for supervisor
                for schedule_row in await get_user_schedule(request.app.db_engine, user_row['id']):
                    schedule_row = dict(schedule_row)
                    user_row['schedule'].append(schedule_row)
            items.append(user_row)
    return web.json_response(items, dumps=json_dumps)
