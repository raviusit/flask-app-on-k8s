"""
    Example app that integrates with redis and save/get timing
"""
from os import environ
from datetime import datetime
import json
import redis
from flask import Flask, redirect
import logging
from logging.handlers import RotatingFileHandler

# Logging
logger = logging.getLogger('logger_1')
logger.setLevel(logging.ERROR)

formatter = logging.Formatter('%(name)s -- %(asctime)s -- %(levelname)s -- %(message)s')

log_handler = RotatingFileHandler('logs/log.log', maxBytes=500*1024, backupCount=2) # 500KB
log_handler.setLevel(logging.ERROR)
log_handler.setFormatter(formatter)

logger.addHandler(log_handler)



VERSION = "1.1.1"
REDIS_ENDPOINT = environ.get("REDIS_ENDPOINT", "localhost")
REDIS_PORT = int(environ.get("REDIS_PORT", "6379"))


APP = Flask(__name__)


@APP.route("/")
def redisapp():
    """Main redirect"""
    return redirect("/get", code=302)


@APP.route("/set")
def set_var():
    """Set the time"""
    red = redis.StrictRedis(host=REDIS_ENDPOINT, port=REDIS_PORT, db=0)
    red.set("time", str(datetime.now()))
    return json.dumps({"time": str(red.get("time"))})


@APP.route("/get")
def get_var():
    """Get the time"""
    red = redis.StrictRedis(host=REDIS_ENDPOINT, port=REDIS_PORT, db=0)
    return json.dumps({"time": str(red.get("time"))})


@APP.route("/reset")
def reset():
    """Reset the time"""
    red = redis.StrictRedis(host=REDIS_ENDPOINT, port=REDIS_PORT, db=0)
    red.delete("time")
    return json.dumps({"time": str(red.get("time"))})


@APP.route("/version")
def version():
    """Get the app version"""
    return json.dumps({"version": VERSION})


@APP.route("/healthz")
def health():
    """Check the app health"""
    try:
        red = redis.StrictRedis(host=REDIS_ENDPOINT, port=REDIS_PORT, db=0)
        red.ping()
    except redis.exceptions.ConnectionError:
        return json.dumps({"ping": "FAIL"})

    return json.dumps({"ping": red.ping()})


@APP.route("/readyz")
def ready():
    """Check the app readiness"""
    return health()


if __name__ == "__main__":
    APP.run(debug=True, host="0.0.0.0", port=8000)
