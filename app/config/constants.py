import os

PORT = int(os.environ.get('PORT', 8080))
DB_URL = os.getenv('DB_URL')
DB_NAME = os.environ.get('DB_NAME', "TicketApp")
ENV_NAME = os.environ.get('ENV_NAME')
MAX_IMAGE_SIZE = int(os.environ.get('MAX_IMAGE_SIZE', 10_000_000))
MAX_IMAGE_GROUP_SIZE = int(os.environ.get('MAX_IMAGE_GROUP_SIZE', 200_000_000))
IMAGES_PATH = os.environ.get('IMAGES_PATH', '/root/images')
