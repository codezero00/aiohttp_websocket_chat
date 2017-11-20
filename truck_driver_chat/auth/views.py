import json
from time import time
import aiohttp_jinja2
from aiohttp import web
from aiohttp_session import get_session
import db as app_db
from auth.utils import hash_password
import settings
from common_web import redirect

logger = settings.get_logger(__name__)


def set_session(session, user_id, request):
    session['user'] = str(user_id)
    session['last_visit'] = time()
    redirect(request, 'main')


async def get_user(db_engine, email, clear_password):
    salted_pwd = hash_password(clear_password)
    async with db_engine.acquire() as conn:
        t_user = app_db.user
        query = t_user.select().where((t_user.c.email == email) & (t_user.c.password == salted_pwd))
        # user = await conn.scalar(query)
        for row in await conn.execute(query):
            return row


class Login(web.View):
    @aiohttp_jinja2.template('auth/login.html')
    async def get(self):
        session = await get_session(self.request)
        if session.get('user'):
            redirect(self.request, 'dashboard')
        return {'context': 'Please enter email'}

    @aiohttp_jinja2.template('auth/login.html')
    async def post(self):
        data = await self.request.post()
        errors = []
        user = await get_user(self.request.app.db_engine,
                              data['email'],
                              data['password'])
        if user is None:
            errors.append(u'user not found')
        else:
            session = await get_session(self.request)
            session['user_id'] = user.id
            session['last_visit'] = time()
            return web.HTTPFound('/dashboard')
        return {'context': 'Please enter login or email', 'errors': errors}


class SignIn(web.View):
    @aiohttp_jinja2.template('auth/signin.html')
    async def get(self):
        session = await get_session(self.request)
        if session.get('user'):
            redirect(self.request, 'main')
        fields = {
            'email': {'type': 'text', 'label': 'Email', 'placeholder': 'you@example.com'},
            'password': {'type': 'password', 'label': 'Password', 'placeholder': 'at least 6 symbols'},
            'name': {'type': 'text', 'label': 'Name', 'placeholder': 'Your full name'},
            'phone': {'type': 'text', 'label': 'Phone', 'placeholder': '79995656666'},
            'birthdate': {'type': 'date', 'label': 'Birthdate', 'placeholder': 'DD.MM.YYYY'},
        }
        return {'fields': fields}

    @aiohttp_jinja2.template('auth/signin.html')
    async def post(self):
        data = await self.request.post()
        async with self.request.app.db_engine.acquire() as conn:
            insert_args = dict(data)
            insert_args['password'] = hash_password(data['password'])
            # strip vals from form
            # TODO: validate through self.fields.validators
            insert_args = dict((k, v.strip) for k, v in insert_args.items())
            uid = await conn.scalar(
                app_db.user.insert().values(**insert_args)
            )
        return {'result': 'success! user_id={0}'.format(uid)}


async def logout(request):
    session = await get_session(request)
    if session.get('user'):
        del session['user']
    redirect(request, 'login')