from aiohttp import web
import sys
from model_for_emb.model_part3 import AlignDlib
from model_for_emb.model_part2 import create_model
from app.routes import setup_route
from app.utils.configurator import get_config
from app.utils.logs import init_logger
from asyncpg import create_pool
from keras.models import load_model
import os
import jinja2
import aiohttp_jinja2


def init_app(argv):
    app = web.Application()
    app['config'] = get_config(argv)
    here = os.path.join(os.getcwd(), 'app/templates/')
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(str(here)))
    app['static_root_url'] = 'static/'
    gender_path = os.path.join(os.getcwd(), 'app/gender_detection.model')
    app['gender_detection'] = load_model(gender_path)
    app['nn4_small2_pretrained'] = create_model()
    app['nn4_small2_pretrained'].load_weights(os.path.join(os.getcwd(), 'app/nn4.small2.v1.h5'))
    app['alignment'] = AlignDlib(os.path.join(os.getcwd(), 'app/models/landmarks.dat'))
    app.on_startup.append(init_database_pool)
    app.on_cleanup.append(close_database_pool)
    init_logger(app['config'])
    setup_route(app)
    return app


async def init_database_pool(app):
    user = app['config']['service']['user']
    password = app['config']['service']['password']
    database = app['config']['service']['database']
    app['pool'] = await create_pool(f'postgresql://{user}:{password}@172.17.0.6/{database}')


async def close_database_pool(app):
    await app['pool'].close()


def start(argv):
    app = init_app(argv)
    web.run_app(app, port=app['config']['service']['port'])


if __name__ == '__main__':
    start(sys.argv[1:])



