import csv
import io
from fastapi import APIRouter, HTTPException, UploadFile, File
from bson.objectid import ObjectId
from pydantic import TypeAdapter
from typing import List

from ..models import PersonalData
from ..utils import objectIdDecoder

def get_router(mongo_connection):
    router = APIRouter()

    # 발의안 추가 (CSV 파일 업로드)
    @router.post("/personal-data/")
    async def upload_personal_data_file(file: UploadFile = File(...)):
        content = await file.read()
        # 파일 내용을 CP949로 디코딩 (다른 인코딩이 필요한 경우 변경)
        content = io.StringIO(content.decode("cp949"))
        csv_reader = csv.DictReader(content)

        # CSV 파일의 각 행을 MongoDB에 저장
        for row in csv_reader:
            # Pydantic 모델로 변환 (필드 이름이 CSV 헤더와 동일하다고 가정)
            personal_data = PersonalData(**row)
            # Pydantic 모델에서 'id' 필드 제거
            personal_data_data = personal_data.model_dump(by_alias=True)
            personal_data_data.pop('_id', None)  # 'id' 필드가 없으면 무시
            mongo_connection.get_collection("personal_data").insert_one(personal_data_data)

        return {"message": "파일 업로드 및 데이터 저장 완료"}

    # 모든 발의안 조회
    @router.get("/personal-data/", response_model=List[PersonalData])
    async def read_personal_data():
        response = objectIdDecoder(list(mongo_connection.get_collection("personal_data").find()))
        return response

    # ObjectId를 통해 특정 발의안 조회
    @router.get("/personal-data/{personal_data_id}", response_model=PersonalData)
    async def read_personal_data(personal_data_id: str):
        response = mongo_connection.get_collection("personal_data").find_one({"_id": ObjectId(personal_data_id)})
        if response is None:
            raise HTTPException(status_code=404, detail="해당 ID값을 가지는 발의안을 찾을 수 없습니다.")
        
        # MongoDB의 ObjectId를 문자열로 변환
        response["_id"] = str(response["_id"])

        # Pydantic 모델로 변환
        personal_data = TypeAdapter(PersonalData).validate_python(response)
        return personal_data

    # 발의안 업데이트
    @router.put("/personal-data/{personal_data_id}")
    async def update_personal_data(personal_data_id: str, personal_data: PersonalData):
        response = mongo_connection.get_collection("personal_data").update_one({"_id": ObjectId(personal_data_id)}, {"$set": personal_data.model_dump()})
        if response.matched_count == 0:
            raise HTTPException(status_code=404, detail="해당 ID값을 가지는 발의안을 찾을 수 없습니다.")
        return personal_data

    # 발의안 삭제
    @router.delete("/personal-data/{personal_data_id}")
    async def delete_personal_data(personal_data_id: str):
        response = mongo_connection.get_collection("personal_data").delete_one({"_id": ObjectId(personal_data_id)})
        if response.deleted_count == 0:
            raise HTTPException(status_code=404, detail="해당 ID값을 가지는 발의안을 찾을 수 없습니다.")
        
        return {"message": "발의안 삭제 됨"}

    return router