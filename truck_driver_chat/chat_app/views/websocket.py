"""
Websocket chat implementation here
"""
import datetime
import json
from aiohttp import http_websocket
from aiohttp import web
from aiohttp_session import get_session
from chat_app import cache_utils
from common_web import get_user_from_session
from chat_app.views import logger
import db as app_db


class WebSocket(web.View):
    """
    Chat websocket view
    """

    async def get(self):
        ws = web.WebSocketResponse()
        await ws.prepare(self.request)
        user = await get_user_from_session(app_db, self.request)
        self.request.app['websockets'].append(ws)
        r = self.request.app.redis
        await cache_utils.update_username_cache(r, user.id, user.name)
        ws.send_str('ping')
        async for msg in ws:
            if msg.tp == http_websocket.WSMsgType.error:
                logger.debug('ws connection closed with exception %s' % ws.exception())
            cmd_payload = msg.json()
            cmd_code = "cmd_{}".format(cmd_payload['cmd'])
            cmd_processor = getattr(self, cmd_code, self.cmd_default_processor)
            await cmd_processor(msg, ws, cmd_payload)

    async def cmd_default_processor(self, msg, ws, cmd_payload):
        logger.error('Unknown cmd getted %s %s %s', cmd_payload['cmd'], self.request, msg)
        ws.send_json('Unknown cmd {}'.format(cmd_payload['cmd']))

    async def cmd_start(self, msg, ws, cmd_payload):
        session = await get_session(self.request)
        r = self.request.app.redis
        dst_user_id = cmd_payload['dst_user']['id']
        src_user_id = session['user_id']
        chat_key = make_chat_key(dst_user_id, src_user_id)
        ws_list = self.request.app['chats_websockets'].get(chat_key, [])
        if ws not in ws_list:
            ws_list.append(ws)
        self.request.app['chats_websockets'][chat_key] = ws_list
        items = await r.lrange(chat_key, 0, 10)
        items = reversed(items)
        if not items:
            items = []
        for json_item in items:
            item = json.loads(json_item)
            user_id = item['_all_fields']['src_client_id']
            if not user_id:
                username = 'Unknown_user'
            else:
                username = await cache_utils.get_username_from_cache(r, item.get('user_id'))
            item['username'] = username
            ws.send_json(item)

    async def cmd_new_msg(self, msg, ws, cmd_payload):
        session = await get_session(self.request)
        r = self.request.app.redis
        dst_user_id = cmd_payload['user_id']
        src_user_id = session['user_id']
        chat_key = make_chat_key(dst_user_id, src_user_id)
        username = await cache_utils.get_username_from_cache(r, src_user_id)
        now_dt = datetime.datetime.now()
        msg = ChatMsg(dst_client_id=dst_user_id,
                      src_client_id=src_user_id,
                      text=cmd_payload['text'],
                      timestamp=now_dt.isoformat(),
                      username=username)
        await r.lpush(chat_key, msg.to_json())
        for ws in self.request.app['chats_websockets'].get(chat_key, []):
            ws.send_str(msg.to_json())

    async def cmd_load_history(self, msg, ws, cmd_payload):
        session = await get_session(self.request)
        pass


class ChatMsg:
    """
    Chat message entity
    """

    def __init__(self, src_client_id, dst_client_id, text, timestamp, username=None):
        self.username = username
        self.src_client_id, self.dst_client_id = src_client_id, dst_client_id
        self.text, self.timestamp = text, timestamp

    def to_json(self):
        return json.dumps({'_all_fields': self.__dict__, 'text': str(self)})

    def __str__(self):
        return '{username} ({timestamp}): {text}'.format(**self.__dict__)


def make_chat_key(id1, id2):
    """
    create uniq user-to-user chat key
    :param id1: id first user
    :param id2: id second user
    :return: str with chat key
    """
    l = [id1, id2]
    l.sort()
    l = map(str, l)
    return "chat:{}".format("_".join(l))
