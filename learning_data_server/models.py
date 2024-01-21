from pydantic import BaseModel, Field
from typing import Optional

# 발의안 스키마 정의
class Initiative(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    대수: int
    법률안명: str
    제안자: str
    대표발의자: str
    공동발의자: str
    상세페이지: str
    소관위원회: str
    제안일: str
    본회의심의결과: str
    제안자목록링크: str
    법률안설명: str

class PersonalData(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    이름: str
    정당명: str
    선거구: str
    대표위원회: str
    당선: str
    소속: str
    위원회: str
    목록: str
    전화번호: str
    사무실: str
    호실: str
    이메일: str
    홈페이지: str

class PolicySeminar(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    제목: str
    의원실링크: str
    개최일: str
    주최기관: str

class LegislativeNotice(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    법률안명: str
    제안자: str
    소관위원회: str
    게시종료일: str
    링크주소: str