from typing import Annotated

from fastapi import APIRouter, Body, Query
from pydantic import BaseModel

from backend.app.schemas import ApiErrorResponse, VideoContentAsset
from backend.app.services.asset_builder import AssetBuilder
from backend.app.services.retrieval import RetrievalService

router = APIRouter(prefix="/assets", tags=["assets"])


class AssetBuildRequest(BaseModel):
    resolved_source_id: str


ASSET_BUILD_EXAMPLES = {
    "preset_resolution": {
        "summary": "Build asset from a resolved preset source",
        "value": {"resolved_source_id": "preset_current_techu_huaian_hotel_candidate"},
    }
}

ASSET_BUILD_RESPONSE_EXAMPLE = {
    "asset_id": "asset_current_techu_huaian_hotel_candidate",
    "status": "asset_complete",
    "source_resolution": {
        "resolved_source_id": "preset_current_techu_huaian_hotel_candidate",
        "source_type": "preset",
        "mapping_id": "mapping_demo_current_techu_huaian_hotel_candidate",
        "video_asset_id": "asset_current_techu_huaian_hotel_candidate",
        "task_id": "task_demo_p0a_low_budget_student",
        "demo_user_context_id": "ctx_low_budget_student",
        "title": "这条探店视频适合我周六下午去吗？",
        "resolution_strategy": "cache_matched",
    },
    "asset": {
        "asset_id": "asset_current_techu_huaian_hotel_candidate",
        "source": {"type": "local_mapping", "title": "这条探店视频适合我周六下午去吗？"},
        "reconstruction_type": "decision",
        "content_domain_tags": ["短时间体验本地特色", "2 小时以内", "预算 100 元以内"],
        "base_summary": "基于视频事实和低预算历史资产，适合先确认价格与排队情况后再决定。",
        "key_points": ["确认人均价格", "避开排队高峰"],
        "evidence": [],
        "facts": [],
        "confidence_level": "medium",
        "needs_confirmation": True,
    },
}

ASSET_DETAIL_RESPONSE_EXAMPLE = {
    "asset_id": "asset_current_techu_huaian_hotel_candidate",
    "source": {
        "type": "local_mapping",
        "title": "这条探店视频适合我周六下午去吗？",
        "mapping_id": "mapping_demo_current_techu_huaian_hotel_candidate",
    },
    "reconstruction_type": "decision",
    "content_domain_tags": ["短时间体验本地特色", "2 小时以内", "预算 100 元以内"],
    "base_summary": "基于视频事实和低预算历史资产，适合先确认价格与排队情况后再决定。",
    "key_points": ["确认人均价格", "避开排队高峰"],
    "evidence": [],
    "facts": [],
    "confidence_level": "medium",
    "needs_confirmation": True,
}


@router.post(
    "/build",
    responses={200: {"content": {"application/json": {"example": ASSET_BUILD_RESPONSE_EXAMPLE}}}, 404: {"model": ApiErrorResponse}, 500: {"model": ApiErrorResponse}},
)
def build_asset(request: AssetBuildRequest = Body(openapi_examples=ASSET_BUILD_EXAMPLES)) -> dict:
    return AssetBuilder().build_from_resolved_source(request.resolved_source_id).to_payload()


@router.get(
    "/search",
    response_model=list[VideoContentAsset],
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": [
                        {
                            "asset_id": "asset_weekend_queue_avoidance",
                            "source": {"type": "demo_seed", "title": "周末排队规避经验"},
                            "reconstruction_type": "experience",
                            "content_domain_tags": ["效率", "排队"],
                            "base_summary": "适合需要减少排队时间的本地体验选择。",
                            "key_points": ["错峰", "预约"],
                            "evidence": [],
                            "facts": [],
                            "confidence_level": "medium",
                            "needs_confirmation": False,
                        }
                    ]
                }
            }
        }
    },
)
def search_assets(
    query: str | None = None,
    tag: Annotated[list[str] | None, Query()] = None,
) -> list[VideoContentAsset]:
    return RetrievalService().search_assets(query=query, tags=tag)


@router.get(
    "/{asset_id}",
    response_model=VideoContentAsset,
    responses={
        200: {"content": {"application/json": {"example": ASSET_DETAIL_RESPONSE_EXAMPLE}}},
        404: {"model": ApiErrorResponse},
        500: {"model": ApiErrorResponse},
    },
)
def get_asset(asset_id: str) -> VideoContentAsset:
    return AssetBuilder().get_asset(asset_id)
