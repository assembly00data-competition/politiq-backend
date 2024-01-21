# ObjectId 필드를 문자열로 변환하는 함수.
def objectIdDecoder(data):
    for item in data:
        if "_id" in item:
            item["_id"] = str(item["_id"])
    return data
