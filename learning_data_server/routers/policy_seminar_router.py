import csv
import io
from fastapi import APIRouter, HTTPException, UploadFile, File
from bson.objectid import ObjectId
from pydantic import TypeAdapter
from typing import List

from ..models import PolicySeminar
from ..utils import objectIdDecoder

def get_router(mongo_connection):
    router = APIRouter()

    # 발의안 추가 (CSV 파일 업로드)
    @router.post("/policy-seminar/")
    async def upload_policy_seminar_file(file: UploadFile = File(...)):
        content = await file.read()
        # 파일 내용을 CP949로 디코딩 (다른 인코딩이 필요한 경우 변경)
        content = io.StringIO(content.decode("cp949"))
        csv_reader = csv.DictReader(content)

        # CSV 파일의 각 행을 MongoDB에 저장
        for row in csv_reader:
            # Pydantic 모델로 변환 (필드 이름이 CSV 헤더와 동일하다고 가정)
            policy_seminar = PolicySeminar(**row)
            # Pydantic 모델에서 'id' 필드 제거
            policy_seminar_data = policy_seminar.model_dump(by_alias=True)
            policy_seminar_data.pop('_id', None)  # 'id' 필드가 없으면 무시
            mongo_connection.get_collection("policy_seminar").insert_one(policy_seminar_data)

        return {"message": "파일 업로드 및 데이터 저장 완료"}

    # 모든 발의안 조회
    @router.get("/policy-seminar/", response_model=List[PolicySeminar])
    async def read_policy_seminars():
        response = objectIdDecoder(list(mongo_connection.get_collection("policy_seminar").find()))
        return response

    # ObjectId를 통해 특정 발의안 조회
    @router.get("/policy-seminar/{policy_seminar_id}", response_model=PolicySeminar)
    async def read_policy_seminar(policy_seminar_id: str):
        response = mongo_connection.get_collection("policy_seminar").find_one({"_id": ObjectId(policy_seminar_id)})
        if response is None:
            raise HTTPException(status_code=404, detail="해당 ID값을 가지는 발의안을 찾을 수 없습니다.")
        
        # MongoDB의 ObjectId를 문자열로 변환
        response["_id"] = str(response["_id"])

        # Pydantic 모델로 변환
        policy_seminar = TypeAdapter(PolicySeminar).validate_python(response)
        return policy_seminar

    # 발의안 업데이트
    @router.put("/policy-seminar/{policy_seminar_id}")
    async def update_policy_seminar(policy_seminar_id: str, policy_seminar: PolicySeminar):
        response = mongo_connection.get_collection("policy_seminar").update_one({"_id": ObjectId(policy_seminar_id)}, {"$set": policy_seminar.model_dump()})
        if response.matched_count == 0:
            raise HTTPException(status_code=404, detail="해당 ID값을 가지는 발의안을 찾을 수 없습니다.")
        return policy_seminar

    # 발의안 삭제
    @router.delete("/policy-seminar/{policy_seminar_id}")
    async def delete_policy_seminar(policy_seminar_id: str):
        response = mongo_connection.get_collection("policy_seminar").delete_one({"_id": ObjectId(policy_seminar_id)})
        if response.deleted_count == 0:
            raise HTTPException(status_code=404, detail="해당 ID값을 가지는 발의안을 찾을 수 없습니다.")
        
        return {"message": "발의안 삭제 됨"}

    return router