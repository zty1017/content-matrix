from typing import Literal

from fastapi import APIRouter, Body
from pydantic import BaseModel

from backend.app.schemas.errors import ApiErrorResponse
from backend.app.services.source_resolver import SourceResolver

router = APIRouter(prefix="/source", tags=["source"])


class SourceResolveRequest(BaseModel):
    source_type: Literal["preset", "douyin_url", "upload_reference"]
    source_id: str | None = None
    source_url: str | None = None
    upload_reference_id: str | None = None


SOURCE_RESOLVE_EXAMPLES = {
    "valid_preset": {
        "summary": "Valid preset source",
        "value": {"source_type": "preset", "source_id": "preset_current_techu_huaian_hotel_candidate"},
    },
    "valid_douyin_url": {
        "summary": "Valid Douyin-like URL mapped through local fixtures",
        "value": {
            "source_type": "douyin_url",
            "source_url": "https://v.douyin.com/preset_current_techu_huaian_hotel_candidate/",
        },
    },
    "invalid_source": {
        "summary": "Invalid or unmapped source",
        "value": {"source_type": "douyin_url", "source_url": "https://example.com/not-douyin"},
    },
}

SOURCE_RESOLVE_RESPONSE_EXAMPLE = {
    "resolved_source_id": "preset_current_techu_huaian_hotel_candidate",
    "source_type": "preset",
    "mapping_id": "mapping_demo_current_techu_huaian_hotel_candidate",
    "video_asset_id": "asset_current_techu_huaian_hotel_candidate",
    "task_id": "task_demo_p0a_low_budget_student",
    "demo_user_context_id": "ctx_low_budget_student",
    "title": "这条探店视频适合我周六下午去吗？",
    "resolution_strategy": "cache_matched",
}


@router.post(
    "/resolve",
    responses={
        200: {"content": {"application/json": {"example": SOURCE_RESOLVE_RESPONSE_EXAMPLE}}},
        400: {"model": ApiErrorResponse},
    },
)
def resolve_source(
    request: SourceResolveRequest = Body(openapi_examples=SOURCE_RESOLVE_EXAMPLES),
) -> dict:
    resolution = SourceResolver().resolve(
        source_type=request.source_type,
        source_id=request.source_id,
        source_url=request.source_url,
        upload_reference_id=request.upload_reference_id,
    )
    return resolution.to_payload()
