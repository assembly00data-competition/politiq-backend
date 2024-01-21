from fastapi import FastAPI

from .db import MongoDBConnection

from .routers.initiative_router import get_router as initiative_router
from .routers.personal_data_router import get_router as personal_data_router
from .routers.policy_seminar_router import get_router as policy_seminar_router
from .routers.legislative_notice_router import get_router as legislative_notice_router

app = FastAPI()

# MongoDB 연결 설정
mongo_connection = MongoDBConnection()
mongo_connection.connect()

# 라우터에 데이터베이스 연결 전달
app.include_router(initiative_router(mongo_connection))
app.include_router(personal_data_router(mongo_connection))
app.include_router(policy_seminar_router(mongo_connection))
app.include_router(legislative_notice_router(mongo_connection))
