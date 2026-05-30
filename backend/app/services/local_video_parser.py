from __future__ import annotations

from backend.app.core.config import Settings, get_settings
from backend.app.core.errors import NotFoundError
from backend.app.schemas.assets import AssetSource, EvidenceItem, FactItem, SourceType, VideoContentAsset
from backend.app.schemas.common import ConfidenceLevel, ReconstructionType
from backend.app.schemas.local_video import (
    LocalVideoAsrResult,
    LocalVideoParseMode,
    LocalVideoParseRequest,
    LocalVideoParseResult,
)


class LocalVideoParser:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def parse(self, request: LocalVideoParseRequest) -> LocalVideoParseResult:
        record = LOCAL_VIDEO_PARSE_REGISTRY.get(request.local_reference_id)
        if record is None:
            raise NotFoundError(
                "Local demo video reference was not found.",
                {
                    "resource": "local_video_reference",
                    "identifier": request.local_reference_id,
                    "available_reference_ids": sorted(LOCAL_VIDEO_PARSE_REGISTRY),
                },
            )

        asr = self._resolve_asr(record, request.parse_mode)
        asset = self._build_asset(record, asr)
        return LocalVideoParseResult(
            local_reference_id=request.local_reference_id,
            parse_mode=request.parse_mode,
            content_type=record["content_type"],
            title=record["title"],
            asset=asset,
            asr=asr,
            display_blocks=list(record["display_blocks"]),
            demo_user_context_id=request.demo_user_context_id,
            warnings=list(record.get("warnings", [])),
        )

    def _resolve_asr(self, record: dict, parse_mode: LocalVideoParseMode) -> LocalVideoAsrResult:
        doubao_boundary_configured = (
            parse_mode == LocalVideoParseMode.doubao_if_configured
            and self.settings.asr_provider == "doubao_flash"
            and not self.settings.asr_mock_mode
            and self.settings.doubao_api_key
        )
        if doubao_boundary_configured:
            return LocalVideoAsrResult(
                provider="doubao-bigasr-flash",
                is_fallback=True,
                transcript=record["fallback_transcript"],
                transcript_path=record.get("fallback_transcript_path"),
                detail={
                    "network_call": "not_performed_in_demo",
                    "reason": "Doubao ASR boundary is configured, but this endpoint keeps a deterministic local fallback for live demos.",
                    "future_provider": self.settings.asr_doubao_resource_id,
                },
            )

        return LocalVideoAsrResult(
            provider="local-hardcoded-fallback",
            is_fallback=True,
            transcript=record["fallback_transcript"],
            transcript_path=record.get("fallback_transcript_path"),
            detail={"network_call": "not_performed", "reason": "parse_mode=fallback or Doubao API key is unavailable"},
        )

    @staticmethod
    def _build_asset(record: dict, asr: LocalVideoAsrResult) -> VideoContentAsset:
        evidence = [
            EvidenceItem(
                evidence_id=f"{record['asset_id']}_ev_asr",
                source_type="video_explicit",
                content=asr.transcript,
                origin="asr",
                confidence=ConfidenceLevel.high,
                needs_confirmation=False,
            ),
            EvidenceItem(
                evidence_id=f"{record['asset_id']}_ev_fallback",
                source_type="ai_inference",
                content=record["fallback_summary"],
                origin="model_inference",
                confidence=ConfidenceLevel.medium,
                needs_confirmation=False,
            ),
        ]
        facts = [
            FactItem(
                fact_id=f"{record['asset_id']}_fact_type",
                type="content_type",
                content=record["content_type_description"],
                entities=list(record["entities"]),
                evidence_refs=[evidence[0].evidence_id],
                confidence=ConfidenceLevel.medium,
            )
        ]
        return VideoContentAsset(
            asset_id=record["asset_id"],
            source=AssetSource(
                type=SourceType.local_mapping,
                title=record["title"],
                local_path=record["video_path"],
                cover_path=record.get("cover_path"),
                duration_seconds=record.get("duration_seconds"),
            ),
            reconstruction_type=ReconstructionType(record["reconstruction_type"]),
            content_domain_tags=list(record["content_domain_tags"]),
            base_summary=record["fallback_summary"],
            key_points=list(record["key_points"]),
            evidence=evidence,
            facts=facts,
            confidence_level=ConfidenceLevel.medium,
            needs_confirmation=True,
            custom_blocks=list(record["display_blocks"]),
            demo_metadata={
                "local_reference_id": record["local_reference_id"],
                "content_type": record["content_type"],
                "asr_provider": asr.provider,
                "asr_is_fallback": asr.is_fallback,
            },
        )


LOCAL_VIDEO_PARSE_REGISTRY: dict[str, dict] = {
    "demo_unparsed_workplace_06": {
        "local_reference_id": "demo_unparsed_workplace_06",
        "asset_id": "asset_runtime_demo_unparsed_workplace_06",
        "content_type": "workplace_skit",
        "content_type_description": "职场剧情/广告植入类内容，适合展示剧情结构、产品露出、观点态度和可复用脚本元素。",
        "title": "已下载未预解析职场视频：关于同事外卷这件事",
        "video_path": "../content-matrix-asset-inbox/05-douyin-resolver-test-links/2026-05-30-douyin-official-share-batch/03-media-assets/videos/06-职场-关于同事外卷这件事.mp4",
        "cover_path": "../content-matrix-asset-inbox/05-douyin-resolver-test-links/2026-05-30-douyin-official-share-batch/03-media-assets/covers/06-职场-关于同事外卷这件事-cover.jpg",
        "duration_seconds": 112.9,
        "fallback_transcript_path": "../content-matrix-asset-inbox/05-douyin-resolver-test-links/2026-05-30-douyin-official-share-batch/04-transcripts-asr/doubao-bigasr-flash/06-职场-关于同事外卷这件事.md",
        "fallback_transcript": "到点了，你们怎么不进公司？同事迟到了，我们等他一起迟到，外卷嘛。以前大家内卷，比谁干得更多，结果工作量越来越多，所以我们要外卷。晚上都留下加个班啊。我晚上有事，加不了。你不干有的是人干。他干不了，我们也干不了。要彻底杜绝这种现象，给老板营造一种你不干大家都不干的危机感。内卷最后的结果就是越卷待遇越差，外卷才是前途光明。后半段自然植入蓝月亮至尊洗衣精华，强调快洗、低泡、15分钟洗净等卖点。",
        "fallback_summary": "这是一个已下载但不进入主 fixture 链路的职场短剧解析演示：后端把视频拆成剧情冲突、核心观点、广告植入点和可复用脚本元素。",
        "reconstruction_type": "experience",
        "content_domain_tags": ["职场", "短剧", "广告植入", "剧情结构", "本地解析演示"],
        "key_points": ["识别“内卷/外卷”的剧情冲突", "提取产品植入位置和卖点", "区分内容观点与广告信息", "默认使用本地兜底 ASR，避免现场网络不稳定"],
        "entities": ["职场", "外卷", "蓝月亮", "洗衣精华", "广告植入"],
        "display_blocks": [
            {"type": "plot_structure", "title": "剧情结构", "items": ["迟到/加班等职场冲突", "同事集体反内卷", "以产品快洗卖点收束生活痛点"]},
            {"type": "brand_placement", "title": "产品露出", "items": ["蓝月亮至尊洗衣精华", "15分钟快洗", "低泡易漂洗", "活性物浓度 47%"]},
            {"type": "remix_hooks", "title": "可复用脚本钩子", "items": ["一起迟到/一起请假/一起死机", "你不会我们也不会", "打工人何必为难打工人"]},
        ],
        "warnings": ["当前返回本地硬编码兜底结果；Doubao ASR 真实调用边界已预留但默认不联网。"],
    },
    "demo_unparsed_finance_12": {
        "local_reference_id": "demo_unparsed_finance_12",
        "asset_id": "asset_runtime_demo_unparsed_finance_12",
        "content_type": "finance_analysis",
        "content_type_description": "财经/宏观分析类内容，适合展示观点摘要、关键术语、风险提示和待验证数据。",
        "title": "已下载未预解析财经视频：宏观观点解析演示",
        "video_path": "../content-matrix-asset-inbox/05-douyin-resolver-test-links/2026-05-30-douyin-official-share-batch/03-media-assets/videos/12-财经-第9期-马政经中的顶级思维-金融的自由化-观.mp4",
        "cover_path": "../content-matrix-asset-inbox/05-douyin-resolver-test-links/2026-05-30-douyin-official-share-batch/03-media-assets/covers/12-财经-第9期-马政经中的顶级思维-金融的自由化-观-cover.jpg",
        "duration_seconds": 480.3,
        "fallback_transcript_path": "../content-matrix-asset-inbox/05-douyin-resolver-test-links/2026-05-30-douyin-official-share-batch/04-transcripts-asr/doubao-bigasr-flash/12-财经-第9期-马政经中的顶级思维-金融的自由化-观.md",
        "fallback_transcript": "这就是泡沫经济背后的始作俑者，金融的自由化。视频用植物大战僵尸中的铁门作为类比，解释资本从生产获利转向以钱生钱，再到金融自由化、资产炒作和证券化。它强调金融脱离实体后并不创造财富，而是在价格泡沫中转移财富和风险，最后提示普通人被迫承担原本不该承担的风险。",
        "fallback_summary": "这是一个已下载但不进入主 fixture 链路的财经长视频解析演示：后端返回可展示的观点摘要、风险提示、待确认数据和原始证据块。",
        "reconstruction_type": "knowledge",
        "content_domain_tags": ["财经", "宏观", "观点摘要", "风险提示", "本地解析演示"],
        "key_points": ["提取核心观点，而不是生成投资建议", "展示术语和关键数据需要人工确认", "默认使用本地兜底 ASR，避免现场网络不稳定"],
        "entities": ["财经", "宏观", "风险", "数据确认"],
        "display_blocks": [
            {"type": "viewpoint_summary", "title": "观点摘要", "items": ["提炼视频主张", "标记证据来源", "区分事实与推测"]},
            {"type": "risk_notice", "title": "风险提示", "items": ["不构成投资建议", "关键数据需二次确认", "适合做知识卡而非决策买卖卡"]},
            {"type": "verification_checklist", "title": "待确认数据", "items": ["时间范围", "引用数据来源", "是否存在反例"]},
        ],
        "warnings": ["当前返回本地硬编码兜底结果；Doubao ASR 真实调用边界已预留但默认不联网。"],
    }
}
