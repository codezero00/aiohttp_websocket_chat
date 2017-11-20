async def update_username_cache(r, user_id, name):
    key = "user_id_name:{0}".format(user_id)
    return await r.hset(key, 'username', name)


async def get_username_from_cache(r, user_id):
    key = "user_id_name:{0}".format(user_id)
    return await r.hget(key, 'username')
