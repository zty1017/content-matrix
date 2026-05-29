from fastapi import APIRouter

from backend.app.schemas import ApiErrorResponse, DemoUserAssetContext
from backend.app.services.retrieval import RetrievalService

router = APIRouter(prefix="/demo-contexts", tags=["demo-contexts"])


@router.get(
    "",
    response_model=list[DemoUserAssetContext],
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": [
                        {
                            "demo_user_context_id": "ctx_low_budget_student",
                            "display_name": "低预算学生资产上下文",
                            "context_summary": "历史资产偏向省钱、本地短途和低门槛体验。",
                            "asset_ids": ["asset_huaian_low_budget_daytrip"],
                        }
                    ]
                }
            }
        }
    },
)
def list_demo_contexts() -> list[DemoUserAssetContext]:
    return RetrievalService().list_demo_contexts()


@router.get(
    "/{context_id}",
    response_model=DemoUserAssetContext,
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {
                        "demo_user_context_id": "ctx_low_budget_student",
                        "display_name": "低预算学生资产上下文",
                        "context_summary": "历史资产偏向省钱、本地短途和低门槛体验。",
                        "asset_ids": ["asset_huaian_low_budget_daytrip", "asset_bus_accessible_foods"],
                    }
                }
            }
        },
        404: {"model": ApiErrorResponse},
        500: {"model": ApiErrorResponse},
    },
)
def get_demo_context(context_id: str) -> DemoUserAssetContext:
    return RetrievalService().get_demo_context(context_id)
