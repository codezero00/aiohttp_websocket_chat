import asyncio
from app import init_postgres_engine
from collections import namedtuple
from auth.utils import hash_password
import constants, settings
import db

logger = settings.get_logger(__name__)

user_fixture_t = namedtuple('user_fixture', ['id', 'name', 'birthdate', 'password', 'email', 'phone', 'role_id', 'supervisor_id'])

sched_fixture_t = namedtuple('sched_fixture', ['user_id', 'start_time', 'end_time'])


fixtures = (
    user_fixture_t(id=-1, name='root', birthdate='1992-08-10', password=hash_password('123456'),
                   email='oneek@gmail.com', phone='79995656900', role_id=constants.Roles.SUPERVISOR,
                   supervisor_id=None),
    user_fixture_t(id=4, name='first driver', birthdate='1980-08-10', password=hash_password('driver_first'),
                   email='first_driver@gmail.com', phone='79221234567', role_id=constants.Roles.DRIVER,
                   supervisor_id=-1),
    user_fixture_t(id=5, name='second driver', birthdate='1977-01-11', password=hash_password('driver_second'),
                   email='second_driver@gmail.com', phone='79121234777', role_id=constants.Roles.DRIVER,
                   supervisor_id=-1),
)

schedules = (
    # first driver work_periods: 10:00-14:00, 15:00-18:00, 19:00-20:00
    sched_fixture_t(user_id=4, start_time='10:00', end_time='14:00'),
    sched_fixture_t(user_id=4, start_time='15:00', end_time='18:00'),
    sched_fixture_t(user_id=4, start_time='19:00', end_time='20:00'),
    # second driver work_periods: 11:00-15:00, 17:00-19:00, 20:00-22:00
    sched_fixture_t(user_id=5, start_time='11:00', end_time='15:00'),
    sched_fixture_t(user_id=5, start_time='17:00', end_time='19:00'),
    sched_fixture_t(user_id=5, start_time='20:00', end_time='22:00'),

)


async def prepare(loop):
    db_engine = await init_postgres_engine(loop)
    async with db_engine.acquire() as conn:
        for f in fixtures:
            insert_args = {}
            for val_index, field_name in enumerate(f._fields):
                val = f[val_index]
                if val is None:
                    continue
                insert_args[field_name] = f[val_index]
            logger.debug(u'Insert args: %s', insert_args)
            await conn.execute(
                db.user.insert().values(**insert_args)
            )

async def prepare_schedule(loop):
    db_engine = await init_postgres_engine(loop)
    async with db_engine.acquire() as conn:
        user_schedules = {}
        for f in schedules:
            user_schedule = user_schedules.get(f.user_id)
            if user_schedule is None:
                uid = await conn.scalar(
                    db.schedule.insert().values(user_id=f.user_id)
                )
                user_schedules[f.user_id] = uid
            insert_args = {}
            for val_index, field_name in enumerate(f._fields):
                val = f[val_index]
                if val is None:
                    continue
                insert_args[field_name] = f[val_index]
            insert_args['schedule_id'] = user_schedules[f.user_id]
            logger.debug(u'Insert args: %s', insert_args)
            del insert_args['user_id']
            await conn.execute(
                db.schedule_items.insert().values(**insert_args)
            )



def main():
    loop = asyncio.get_event_loop()
    # srv, app_handler = loop.run_until_complete(prepare(loop))
    srv, app_handler = loop.run_until_complete(prepare_schedule(loop))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(app_handler.finish_connections())
        srv.close()
        loop.run_until_complete(srv.wait_closed())
    loop.close()


if __name__ == '__main__':
    main()
