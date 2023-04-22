import os

PORT = int(os.environ.get('PORT', 8080))
DB_URL = os.getenv('DB_URL')
DB_NAME = os.environ.get('DB_NAME', "TicketApp")
ENV_NAME = os.environ.get('ENV_NAME')
