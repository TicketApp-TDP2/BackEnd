from fastapi import FastAPI
from app.controllers.utils.ping import router as ping_router
from app.controllers.utils.reset import router as reset_router
from app.controllers.users import router as users_router
from app.controllers.organizers import router as organizers_router
from app.controllers.events import router as events_router
from app.controllers.favourites import router as favourites_router
from app.controllers.bookings import router as bookings_router
from app.controllers.complaints import router as complaints_router
from app.controllers.stats import router as stats_router
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
app.include_router(organizers_router, prefix="/api")
app.include_router(events_router, prefix="/api")
app.include_router(favourites_router, prefix="/api")
app.include_router(bookings_router, prefix="/api")
app.include_router(complaints_router, prefix="/api")
app.include_router(stats_router, prefix="/api")

logger.info(f"Server started on port: {PORT}")
log_config()
