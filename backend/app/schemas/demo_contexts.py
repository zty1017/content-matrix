from pydantic import Field

from backend.app.schemas.assets import VideoContentAsset
from backend.app.schemas.common import FlexibleSchema
from backend.app.schemas.tasks import SessionContext


class DemoUserAssetContext(FlexibleSchema):
    demo_user_context_id: str
    display_name: str
    asset_ids: list[str]
    context_summary: str
    high_risk_domain: bool = False
    risk_domain_tags: list[str] = Field(default_factory=list)


class DemoSeedAssetBundle(FlexibleSchema):
    session_context: SessionContext
    demo_user_contexts: list[DemoUserAssetContext]
    seed_video_content_assets: list[VideoContentAsset]
