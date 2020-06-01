import os

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.redis import RedisIntegration

from main import create_app

sentry_sdk.init(
    dsn=os.environ['SENTRY_DSN'], integrations=[FlaskIntegration(), RedisIntegration()]
)

app = create_app()
