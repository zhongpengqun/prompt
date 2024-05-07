import logging
from logging.handlers import TimedRotatingFileHandler

from flask import Flask
from flask.logging import create_logger
from flask_apidoc import Generator

from views import v1


formatter = logging.Formatter(
    "[%(asctime)s][%(filename)s:%(lineno)d][%(levelname)s][%(thread)d] - %(message)s")

handler = TimedRotatingFileHandler("flask.log", when="D", interval=1,
                                   backupCount=15, encoding="UTF-8", delay=False, utc=True)


app = Flask(__name__)

app.logger = create_logger(app)
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

app.register_blueprint(v1, url_prefix='/v1')

generator = Generator(app)
generator.prepare()
