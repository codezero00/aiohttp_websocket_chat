import sqlalchemy as sa
import constants

meta = sa.MetaData()



user = sa.Table(
    'user', meta,
    sa.Column('id', sa.Integer, nullable=False),
    sa.Column('name', sa.String(200), nullable=False),
    sa.Column('birthdate', sa.Date(), nullable=False),
    sa.Column('password', sa.String(256), nullable=False),
    sa.Column('email', sa.String(64), nullable=False),
    sa.Column('phone', sa.String(11), nullable=False),
    sa.Column('role_id', sa.Integer, nullable=False, default=constants.Roles.DRIVER),
    sa.Column('supervisor_id', sa.Integer, nullable=True),
    # Indexes #
    sa.PrimaryKeyConstraint('id', name='question_id_pkey'),
    sa.ForeignKeyConstraint(['supervisor_id'], ['user.id'],
                            name='supervisor_fk')
)

# sa.Column('start_time', sa.Time(), nullable=False),


schedule = sa.Table(
    'schedule', meta,
    sa.Column('id', sa.Integer, nullable=False),
    sa.Column('user_id', sa.Integer, nullable=False),
    sa.PrimaryKeyConstraint('id', name='sched_pk'),
    sa.ForeignKeyConstraint(['user_id'], [user.c.id],
                            name='sched_user_fk',
                            ondelete='CASCADE')
)

schedule_items = sa.Table(
    'schedule_items', meta,
    sa.Column('id', sa.Integer, nullable=False),
    sa.Column('schedule_id', sa.Integer, nullable=False),
    sa.Column('start_time', sa.Time(), nullable=False),
    sa.Column('end_time', sa.Time(), nullable=False),
    # Indexes #
    sa.PrimaryKeyConstraint('id', name='sched_item_pk'),
    sa.ForeignKeyConstraint(['schedule_id'], [schedule.c.id],
                            name='sched_item_sched_fk',
                            ondelete='CASCADE'),
)


async def select_with_filter(db_engine, table, **fltr):
    clause = None
    for k, v in fltr.items():
        if k == 'id_':
            k = 'id'
        if clause is None:
            clause = getattr(table.c, k) == v
        else:
            clause &= getattr(table.c, k) == v

    async with db_engine.acquire() as conn:
        query = table.select().where(clause)

        return await conn.execute(query)
