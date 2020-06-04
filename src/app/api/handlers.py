from aiohttp import web
from app.predictor import predict_class
import aiohttp_jinja2


@aiohttp_jinja2.template('index.html')
async def handler(requests: web.Request):
    print(requests.app['config'])
    # dict_index = {'static': requests.app['static']}
    # return dict_index
    # return web.Response(status=200)


@aiohttp_jinja2.template('result.html')
async def predict_handler(requests: web.Request):
    data = await requests.post()
    f = data['image'].file
    answer = await predict_class(f, requests.app['nn4_small2_pretrained'], requests.app['alignment'],
                           requests.app['gender_detection'], requests.app['pool'])
    link_vk = 'https://vk.com/id'
    dict_result = {}
    for i in range(5):
        dict_result['link_' + str(i)] = link_vk + str(answer[i][0])
        dict_result['photo_' + str(i)] = answer[i][1]
    return dict_result
    # return web.Response(status=200)




