import asyncpg
from asyncpg import pool, Record

async def create_vectors(id_val, link_photo, vector, sex, pool: pool.Pool):
    async with pool.acquire() as conn:
        result: Record = await conn.fetchrow(
                f'''
                    INSERT INTO public.freeFemale(
                        id, link_photo, vector, sex)
                        VALUES ({id_val}, '{link_photo}', '{vector}', '{sex}');
                ''')


async def init_database(user, password, database):
    pool = await asyncpg.create_pool(f'postgresql://{user}:{password}@172.17.0.6/{database}')
    return pool


async def do_simple_select(pool: asyncpg.pool.Pool):
    async with pool.acquire() as conn:

        result: asyncpg.Record = await conn.fetch('''SELECT * FROM public.vectors;''')
    return result


async def close_connection_pool(pool: asyncpg.pool.Pool):
    await pool.close()


def str2list(vec):
    vec = vec[1:-1].replace('  ', ' ')
    vec = vec.replace('\n', '')
    vec = vec.split(' ')
    vec = list(filter(None, vec))
    vec = [float(x) for x in vec[:]]
    return vec


async def main(id_val, link_photo, vector, sex,
               user='postgres', password='', data_name='vk_data'):

    pool: asyncpg.pool.Pool = await init_database(user, password, data_name)
    await create_vectors(id_val, link_photo, vector, sex, pool)
    await pool.close()

