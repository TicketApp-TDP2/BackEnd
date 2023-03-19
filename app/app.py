from fastapi import FastAPI
from app.controllers.utils.ping import router as ping_router
from app.controllers.utils.reset import router as reset_router
from app.controllers.users import router as users_router
from app.config.constants import PORT
from app.utils.config import log_config

from app.config.logger import setup_logger
from fastapi.middleware.cors import CORSMiddleware

# Setup logger
logger = setup_logger(name=__name__)

# Create app with FAST API
app = FastAPI(debug=True)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(ping_router, prefix="/api")
app.include_router(reset_router, prefix="/api")
app.include_router(users_router, prefix="/api")

logger.info(f"Server started on port: {PORT}")
log_config()
