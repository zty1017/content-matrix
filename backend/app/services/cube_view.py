from __future__ import annotations

from typing import Any

from backend.app.core.errors import NotFoundError
from backend.app.repositories import JsonFixtureRepository
from backend.app.schemas.common import AssetStatus, RetrievalStatus, SourceStatus
from backend.app.schemas.cube import CubeAnimationPhase, CubeFace, CubeProgress, CubeProgressStep, CubeState, CubeView
from backend.app.schemas.tasks import ReconstructionTask


class CubeViewService:
    def __init__(self, repository: JsonFixtureRepository | None = None) -> None:
        self.repository = repository or JsonFixtureRepository()

    def get_task_cube_view(self, task_id: str) -> CubeView:
        task = self.repository.get_reconstruction_task(task_id)
        if task is None:
            raise NotFoundError(
                "Reconstruction task was not found.",
                {"resource": "reconstruction_task", "identifier": task_id},
            )

        progress = self.get_task_cube_progress(task.task_id, task=task)
        return CubeView(
            task_id=task.task_id,
            video_asset_id=task.video_asset_id,
            cube_state=self._cube_state(task),
            animation_phase=self._animation_phase(task),
            source_status=task.source_status.value,
            asset_status=task.asset_status.value,
            retrieval_status=task.retrieval_status.value,
            progress=progress,
            faces=self._faces(task),
            warnings=self._warnings(task),
        )

    def get_task_cube_progress(self, task_id: str, task: ReconstructionTask | None = None) -> CubeProgress:
        task = task or self.repository.get_reconstruction_task(task_id)
        if task is None:
            raise NotFoundError(
                "Reconstruction task was not found.",
                {"resource": "reconstruction_task", "identifier": task_id},
            )

        cube_state = self._cube_state(task)
        animation_phase = self._animation_phase(task)
        percent = self._progress_percent(task, animation_phase)
        return CubeProgress(
            task_id=task.task_id,
            cube_state=cube_state,
            animation_phase=animation_phase,
            percent=percent,
            message=self._progress_message(animation_phase, percent),
            steps=self._progress_steps(task, animation_phase),
        )

    def _faces(self, task: ReconstructionTask) -> list[CubeFace]:
        return [
            CubeFace(
                face_id="source",
                face_type="source_asset",
                title="原始视频与来源",
                status=self._face_status(task.source_status.value),
                target_ref={"type": "asset", "id": task.video_asset_id},
                display_blocks=[
                    {
                        "type": "source_summary",
                        "title": "来源状态",
                        "items": [task.source_status.value, task.video_asset_id],
                    }
                ],
            ),
            CubeFace(
                face_id="primary_card",
                face_type="reconstruction_card",
                title=task.primary_card.display_name or task.primary_card.common.get("title") or "主重构卡",
                status=self._face_status(task.asset_status.value),
                target_ref={"type": "task", "id": task.task_id},
                display_blocks=[
                    {
                        "type": "primary_card",
                        "card_type": task.primary_card.card_type.value,
                        "common": task.primary_card.common,
                        "specific": task.primary_card.specific,
                        "evidence_refs": task.primary_card.evidence_refs,
                    }
                ],
            ),
            CubeFace(
                face_id="related_assets",
                face_type="matrix_connections",
                title="历史资产关联",
                status=self._face_status(task.retrieval_status.value),
                target_ref={"type": "task_related_assets", "id": task.task_id},
                display_blocks=[self._related_assets_block(task)],
            ),
            CubeFace(
                face_id="inferences",
                face_type="ai_inferences",
                title="推理与待确认",
                status="needs_confirmation" if any(item.needs_confirmation for item in task.inferences) else "ready",
                target_ref={"type": "task_inferences", "id": task.task_id},
                display_blocks=[self._inferences_block(task)],
            ),
            CubeFace(
                face_id="evidence",
                face_type="evidence_trace",
                title="证据与原始线索",
                status="ready" if task.evidence else "empty",
                target_ref={"type": "task_evidence", "id": task.task_id},
                display_blocks=[self._evidence_block(task)],
            ),
            CubeFace(
                face_id="snapshot",
                face_type="save_snapshot",
                title="保存到内容魔方",
                status="ready" if task.asset_status == AssetStatus.asset_complete else "disabled",
                target_ref={"type": "task", "id": task.task_id},
                display_blocks=[
                    {
                        "type": "snapshot_action",
                        "title": "保存重构结果",
                        "items": ["生成完成后可保存为已转换资产", "保存后会出现在 /api/v1/snapshots"],
                    }
                ],
                action={"method": "POST", "href": f"/api/v1/tasks/{task.task_id}/save-snapshot"},
            ),
        ]

    @staticmethod
    def _cube_state(task: ReconstructionTask) -> CubeState:
        if task.source_status == SourceStatus.source_failed or task.asset_status == AssetStatus.asset_failed:
            return CubeState.failed
        if task.session_context.high_risk_domain or task.primary_card.high_risk_domain:
            return CubeState.blocked
        if task.asset_status == AssetStatus.asset_complete:
            return CubeState.ready
        if task.source_status in {SourceStatus.received, SourceStatus.cache_matched, SourceStatus.source_ready}:
            return CubeState.transforming
        return CubeState.input_ready

    @staticmethod
    def _animation_phase(task: ReconstructionTask) -> CubeAnimationPhase:
        if task.source_status == SourceStatus.source_failed or task.asset_status == AssetStatus.asset_failed:
            return CubeAnimationPhase.error
        if task.session_context.high_risk_domain or task.primary_card.high_risk_domain:
            return CubeAnimationPhase.needs_confirmation
        if task.asset_status == AssetStatus.asset_complete:
            return CubeAnimationPhase.final_form
        if task.retrieval_status in {RetrievalStatus.retrieval_running, RetrievalStatus.retrieval_matched}:
            return CubeAnimationPhase.matrix_linking
        if task.asset_status in {AssetStatus.basic_generating, AssetStatus.basic_ready, AssetStatus.card_generating}:
            return CubeAnimationPhase.content_reconstruction
        return CubeAnimationPhase.source_resolution

    @staticmethod
    def _face_status(status: str) -> str:
        if status.endswith("failed"):
            return "failed"
        if status.endswith("complete") or status.endswith("ready") or status.endswith("matched") or status.endswith("applied"):
            return "ready"
        if status.endswith("pending") or status.endswith("running") or status.endswith("generating"):
            return "loading"
        return status

    @staticmethod
    def _related_assets_block(task: ReconstructionTask) -> dict[str, Any]:
        return {
            "type": "related_assets",
            "title": "关联资产",
            "items": [
                {
                    "related_asset_id": item.related_asset_id,
                    "title": item.title,
                    "influence_type": item.influence_type.value,
                    "influence_summary": item.influence_summary,
                    "match_reason": item.match_reason,
                }
                for item in task.related_assets
            ],
        }

    @staticmethod
    def _inferences_block(task: ReconstructionTask) -> dict[str, Any]:
        return {
            "type": "inferences",
            "title": "推理结果",
            "items": [
                {
                    "inference_id": item.inference_id,
                    "type": item.type,
                    "content": item.content,
                    "confidence": item.confidence.value,
                    "needs_confirmation": item.needs_confirmation,
                }
                for item in task.inferences
            ],
        }

    @staticmethod
    def _evidence_block(task: ReconstructionTask) -> dict[str, Any]:
        return {
            "type": "evidence",
            "title": "证据链",
            "items": [
                {
                    "evidence_id": item.evidence_id,
                    "source_type": item.source_type.value,
                    "origin": item.origin.value,
                    "content": item.content,
                    "confidence": item.confidence.value,
                }
                for item in task.evidence
            ],
        }

    @staticmethod
    def _warnings(task: ReconstructionTask) -> list[str]:
        warnings: list[str] = []
        if task.asset_status != AssetStatus.asset_complete:
            warnings.append("Current demo uses fixture-derived progress; frontend may interpolate cube animation timing.")
        if task.primary_card.high_risk_domain or task.session_context.high_risk_domain:
            warnings.append("High-risk task requires confirmation before final card generation.")
        return warnings

    @staticmethod
    def _progress_percent(task: ReconstructionTask, animation_phase: CubeAnimationPhase) -> float:
        if task.source_status == SourceStatus.source_failed or task.asset_status == AssetStatus.asset_failed:
            return 0.0
        if animation_phase == CubeAnimationPhase.needs_confirmation:
            return 90.0
        if task.asset_status == AssetStatus.asset_complete and task.retrieval_status == RetrievalStatus.retrieval_applied:
            return 100.0
        phase_progress = {
            CubeAnimationPhase.source_resolution: 20.0,
            CubeAnimationPhase.content_reconstruction: 45.0,
            CubeAnimationPhase.matrix_linking: 70.0,
            CubeAnimationPhase.final_form: 100.0,
            CubeAnimationPhase.needs_confirmation: 90.0,
            CubeAnimationPhase.error: 0.0,
        }
        return phase_progress[animation_phase]

    @staticmethod
    def _progress_message(animation_phase: CubeAnimationPhase, percent: float) -> str:
        if percent == 100.0:
            return "内容魔方已完成，可以点击各面查看重构结果。"
        messages = {
            CubeAnimationPhase.source_resolution: "正在匹配复制的视频链接与本地演示素材。",
            CubeAnimationPhase.content_reconstruction: "正在重构视频内容，生成可展示的结构化卡片。",
            CubeAnimationPhase.matrix_linking: "正在关联历史资产与证据链，组装魔方面。",
            CubeAnimationPhase.needs_confirmation: "当前内容需要确认后才能完成最终生成。",
            CubeAnimationPhase.error: "内容魔方生成失败，请检查任务状态。",
            CubeAnimationPhase.final_form: "内容魔方已完成，可以点击各面查看重构结果。",
        }
        return messages[animation_phase]

    def _progress_steps(
        self,
        task: ReconstructionTask,
        animation_phase: CubeAnimationPhase,
    ) -> list[CubeProgressStep]:
        return [
            CubeProgressStep(
                step_id="source_resolution",
                title="链接映射",
                phase=CubeAnimationPhase.source_resolution,
                percent=20.0,
                status=self._step_status(
                    animation_phase,
                    CubeAnimationPhase.source_resolution,
                    task.source_status in {SourceStatus.cache_matched, SourceStatus.source_ready},
                ),
            ),
            CubeProgressStep(
                step_id="content_reconstruction",
                title="内容重构",
                phase=CubeAnimationPhase.content_reconstruction,
                percent=45.0,
                status=self._step_status(
                    animation_phase,
                    CubeAnimationPhase.content_reconstruction,
                    task.asset_status in {AssetStatus.basic_ready, AssetStatus.card_ready, AssetStatus.asset_complete},
                ),
            ),
            CubeProgressStep(
                step_id="matrix_linking",
                title="资产关联",
                phase=CubeAnimationPhase.matrix_linking,
                percent=70.0,
                status=self._step_status(
                    animation_phase,
                    CubeAnimationPhase.matrix_linking,
                    task.retrieval_status in {RetrievalStatus.retrieval_matched, RetrievalStatus.retrieval_applied},
                ),
            ),
            CubeProgressStep(
                step_id="final_form",
                title="魔方成型",
                phase=CubeAnimationPhase.final_form,
                percent=100.0,
                status="ready" if task.asset_status == AssetStatus.asset_complete else "pending",
            ),
        ]

    @staticmethod
    def _step_status(
        current_phase: CubeAnimationPhase,
        step_phase: CubeAnimationPhase,
        is_ready: bool,
    ) -> str:
        if is_ready:
            return "ready"
        if current_phase == step_phase:
            return "active"
        return "pending"
