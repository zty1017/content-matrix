from fastapi import APIRouter, Body, Depends

from backend.app.schemas.errors import ApiErrorResponse
from backend.app.schemas.local_video import LocalVideoParseRequest, LocalVideoParseResult
from backend.app.services.local_video_parser import LocalVideoParser


router = APIRouter(prefix="/local-video", tags=["local-video"])


LOCAL_VIDEO_PARSE_EXAMPLES = {
    "unparsed_finance_fallback": {
        "summary": "Parse a downloaded workplace skit through deterministic fallback",
        "value": {
            "local_reference_id": "demo_unparsed_workplace_06",
            "parse_mode": "fallback",
            "demo_user_context_id": "ctx_efficiency_worker",
        },
    },
    "doubao_boundary_with_fallback": {
        "summary": "Exercise the Doubao ASR boundary while keeping local fallback deterministic",
        "value": {"local_reference_id": "demo_unparsed_workplace_06", "parse_mode": "doubao_if_configured"},
    },
}


def get_local_video_parser() -> LocalVideoParser:
    return LocalVideoParser()


@router.post(
    "/parse",
    response_model=LocalVideoParseResult,
    responses={
        200: {"description": "Local video parsed into demo-ready display blocks"},
        404: {"model": ApiErrorResponse},
    },
)
def parse_local_video(
    request: LocalVideoParseRequest = Body(openapi_examples=LOCAL_VIDEO_PARSE_EXAMPLES),
    parser: LocalVideoParser = Depends(get_local_video_parser),
) -> LocalVideoParseResult:
    return parser.parse(request)
