from auth.views import Login, SignIn, logout
from chat_app.views.api import get_chats
from chat_app.views.dashboard import dashboard_router, dashboard_redirect
from chat_app.views.websocket import WebSocket


routes = (
    ('*',   '/',  dashboard_redirect,    'root'),
    ('*',   '/login',  Login,    'login'),
    ('*',   '/signin',  SignIn,    'signin'),
    ('*',   '/dashboard',  dashboard_router,    'dashboard'),
    ('*',   '/logout', logout,   'logout'),
    ('*',   '/api/get_chats', get_chats,   'get_chats'),
    ('*', '/ws', WebSocket, 'ws'),

)