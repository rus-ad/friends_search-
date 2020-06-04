import asyncio
import asyncpg
from asyncpg import pool, Record, exceptions
import pandas as pd

async def create_vectors(id_val, vector_voman, vector_man, id_voman, id_man, pool: pool.Pool):
    async with pool.acquire() as conn:
        result: Record = await conn.fetchrow(
                f'''
                    INSERT INTO public.vectors(
                        id, vector_man, vector_voman, id_man, id_voman)
                        VALUES ({id_val}, '{vector_man}', '{vector_voman}', '{id_man}', '{id_voman}');
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


async def main(id_val, photo_girls, photo_mens, id_girls,  id_men,
               user='postgres', password='', data_name='vk_data'):

    pool: asyncpg.pool.Pool = await init_database(user, password, data_name)
    await create_vectors(id_val, photo_girls, photo_mens, id_girls,  id_men, pool)
    # select_result = await do_simple_select(pool)
    # df = pd.DataFrame(columns=['id', 'photo_mens', 'photo_girls', 'id_mens', 'id_girls'])
    # for idx, i in enumerate(select_result):
    #     df.loc[idx] = [i[0], str2list(i[1]), str2list(i[2]), i[3], i[4]]
    # print(df)



    # for i in select_result:
    #     print(i.get('photo_girls'))
    #     print(str2list(i.get('photo_girls')))
    #     print(type(str2list(i.get('photo_girls'))))
    await pool.close()

#
# if __name__ == '__main__':
#     asyncio.run(main())
