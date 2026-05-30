from fastapi import APIRouter, Depends

from backend.app.schemas.cube import CubeProgress, CubeView
from backend.app.schemas.errors import ApiErrorResponse
from backend.app.services.cube_view import CubeViewService


router = APIRouter(prefix="/cube", tags=["cube"])


def get_cube_view_service() -> CubeViewService:
    return CubeViewService()


@router.get(
    "/tasks/{task_id}",
    response_model=CubeView,
    responses={
        200: {
            "description": "Frontend-ready six-face cube projection for a reconstruction task",
        },
        404: {"model": ApiErrorResponse},
    },
)
def get_task_cube_view(
    task_id: str,
    service: CubeViewService = Depends(get_cube_view_service),
) -> CubeView:
    return service.get_task_cube_view(task_id)


@router.get(
    "/tasks/{task_id}/progress",
    response_model=CubeProgress,
    responses={
        200: {
            "description": "Fixture-derived demo progress for cube transformation animation",
        },
        404: {"model": ApiErrorResponse},
    },
)
def get_task_cube_progress(
    task_id: str,
    service: CubeViewService = Depends(get_cube_view_service),
) -> CubeProgress:
    return service.get_task_cube_progress(task_id)
