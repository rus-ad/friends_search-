from app.api.handlers import handler, predict_handler
import os


def setup_route(app):
    app.router.add_get('/', handler)
    app.router.add_post('/predict', predict_handler)
    app.router.add_static("/static", os.path.join(os.getcwd(), 'templates/static'))


