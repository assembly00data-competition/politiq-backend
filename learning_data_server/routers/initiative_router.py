import csv
import io
from fastapi import APIRouter, HTTPException, UploadFile, File
from bson.objectid import ObjectId
from pydantic import TypeAdapter
from typing import List

from ..models import Initiative
from ..utils import objectIdDecoder

def get_router(mongo_connection):
    router = APIRouter()

    # 발의안 추가 (CSV 파일 업로드)
    @router.post("/initiative/")
    async def upload_initiative_file(file: UploadFile = File(...)):
        content = await file.read()
        # 파일 내용을 CP949로 디코딩 (다른 인코딩이 필요한 경우 변경)
        content = io.StringIO(content.decode("cp949"))
        csv_reader = csv.DictReader(content)

        # CSV 파일의 각 행을 MongoDB에 저장
        for row in csv_reader:
            # Pydantic 모델로 변환 (필드 이름이 CSV 헤더와 동일하다고 가정)
            initiative = Initiative(**row)
            # Pydantic 모델에서 'id' 필드 제거
            initiative_data = initiative.model_dump(by_alias=True)
            initiative_data.pop('_id', None)  # 'id' 필드가 없으면 무시
            mongo_connection.get_collection("initiative").insert_one(initiative_data)

        return {"message": "파일 업로드 및 데이터 저장 완료"}

    # 모든 발의안 조회
    @router.get("/initiative/", response_model=List[Initiative])
    async def read_initiatives():
        response = objectIdDecoder(list(mongo_connection.get_collection("initiative").find()))
        return response

    # ObjectId를 통해 특정 발의안 조회
    @router.get("/initiative/{initiative_id}", response_model=Initiative)
    async def read_initiative(initiative_id: str):
        response = mongo_connection.get_collection("initiative").find_one({"_id": ObjectId(initiative_id)})
        if response is None:
            raise HTTPException(status_code=404, detail="해당 ID값을 가지는 발의안을 찾을 수 없습니다.")
        
        # MongoDB의 ObjectId를 문자열로 변환
        response["_id"] = str(response["_id"])

        # Pydantic 모델로 변환
        initiative = TypeAdapter(Initiative).validate_python(response)
        return initiative

    # 발의안 업데이트
    @router.put("/initiative/{initiative_id}")
    async def update_initiative(initiative_id: str, initiative: Initiative):
        response = mongo_connection.get_collection("initiative").update_one({"_id": ObjectId(initiative_id)}, {"$set": initiative.model_dump()})
        if response.matched_count == 0:
            raise HTTPException(status_code=404, detail="해당 ID값을 가지는 발의안을 찾을 수 없습니다.")
        return initiative

    # 발의안 삭제
    @router.delete("/initiative/{initiative_id}")
    async def delete_initiative(initiative_id: str):
        response = mongo_connection.get_collection("initiative").delete_one({"_id": ObjectId(initiative_id)})
        if response.deleted_count == 0:
            raise HTTPException(status_code=404, detail="해당 ID값을 가지는 발의안을 찾을 수 없습니다.")
        
        return {"message": "발의안 삭제 됨"}

    return router