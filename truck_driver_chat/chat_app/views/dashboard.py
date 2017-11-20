"""
Dashboard code here
"""
import aiohttp_jinja2
from common_web import redirect, get_user_from_session
from aiohttp import web
import db as app_db
import constants

async def dashboard_redirect(request):
    redirect(request, 'dashboard')


async def dashboard_router(request):
    user = await get_user_from_session(app_db, request)
    if not user:
        redirect(request, 'login')
    if user.role_id == constants.Roles.DRIVER:
        return await DriverDashBoardView(request, user)
    elif user.role_id == constants.Roles.SUPERVISOR:
        return await SupervisorDashboard(request, user)


class BaseUserDashBoardView(web.View):
    def __init__(self, request, user):
        self.user = user
        super(BaseUserDashBoardView, self).__init__(request)


class DriverDashBoardView(BaseUserDashBoardView):
    @aiohttp_jinja2.template('dashboard/main.html')
    async def get(self):
        return {'user': self.user, 'title': 'Driver Dashboard'}

    async def post(self):
        pass


class SupervisorDashboard(BaseUserDashBoardView):
    @aiohttp_jinja2.template('dashboard/main.html')
    async def get(self):
        return {'user': self.user, 'title': 'SuperVisor Dashboard'}

    async def post(self):
        pass
