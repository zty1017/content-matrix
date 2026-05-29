from typing import Any

from pydantic import Field

from backend.app.schemas.common import FlexibleSchema


class ApiErrorResponse(FlexibleSchema):
    code: str = Field(examples=["invalid_source"])
    message: str = Field(examples=["Unsupported or unmapped source."])
    detail: dict[str, Any] | None = Field(
        default=None,
        examples=[{"field": "source_url", "allowed": ["preset", "douyin_url", "upload_reference"]}],
    )
