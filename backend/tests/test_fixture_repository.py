import json
from copy import deepcopy
from pathlib import Path

import pytest

from backend.app.repositories import FixtureRepositoryError, JsonFixtureRepository
from backend.app.schemas import ReconstructionTask, SavedReconstructionSnapshot


FIXTURES_DIR = Path(__file__).resolve().parents[1] / "app" / "data" / "fixtures"


def test_committed_fixtures_validate_through_schema_models():
    repository = JsonFixtureRepository()

    assets = repository.load_video_content_assets()
    contexts = repository.load_demo_user_asset_contexts()
    tasks = repository.load_reconstruction_tasks(include_runtime=False)
    snapshots = repository.load_saved_reconstruction_snapshots(include_runtime=False)
    mappings = repository.load_source_mappings()

    assert len(assets) == 11
    assert len(contexts) == 3
    assert len(tasks) == 5
    assert len(snapshots) == 2
    assert len(mappings) == 4
    assert {mapping["video_asset_id"] for mapping in mappings} == {
        "asset_current_techu_huaian_hotel_candidate",
        "asset_douyin_08_chongqing_food_daydream",
        "asset_douyin_07_chongqing_bbq_travel",
    }
    assert assets[0].asset_id == "asset_huaian_low_budget_daytrip"
    assert contexts[0].asset_ids == [
        "asset_huaian_low_budget_daytrip",
        "asset_bus_accessible_foods",
        "asset_under_100_local_experience",
    ]


def test_fixture_lookup_and_search_are_deterministic():
    repository = JsonFixtureRepository()

    context = repository.get_demo_user_asset_context("ctx_efficiency_worker")
    search_results = repository.search_video_content_assets(tags=["效率"], query="排队")
    source_mapping = repository.get_source_mapping("preset_current_techu_huaian_hotel_candidate")
    food_mapping = repository.get_source_mapping("w3JLRkaZ6UQ")
    huaian_alias = repository.get_source_mapping("K5I9o0ITcJ8")
    later_task = repository.get_reconstruction_task("task_demo_douyin_07_later_related_bbq", include_runtime=False)

    assert context is not None
    assert context.display_name == "效率优先上班族资产上下文"
    assert [asset.asset_id for asset in search_results] == [
        "asset_reservation_offpeak_tips",
        "asset_weekend_queue_avoidance",
    ]
    assert repository.get_video_content_asset("missing_asset") is None
    assert source_mapping is not None
    assert source_mapping["task_id"] == "task_demo_p0a_low_budget_student"
    assert food_mapping is not None
    assert food_mapping["video_asset_id"] == "asset_douyin_08_chongqing_food_daydream"
    assert huaian_alias is not None
    assert huaian_alias["task_id"] == "task_demo_p0a_low_budget_student"
    assert later_task is not None
    assert later_task.related_assets[0].related_asset_id == "asset_douyin_08_chongqing_food_daydream"


def test_malformed_fixture_fails_predictably(tmp_path: Path):
    fixtures_dir = tmp_path / "fixtures"
    fixtures_dir.mkdir()
    (fixtures_dir / "video_content_assets.json").write_text(
        json.dumps([{"asset_id": "asset_bad", "source": {"type": "webpage"}}]),
        encoding="utf-8",
    )
    repository = JsonFixtureRepository(fixtures_dir=fixtures_dir, runtime_dir=tmp_path / "runtime")

    with pytest.raises(FixtureRepositoryError, match="Invalid records"):
        repository.load_video_content_assets()


def test_runtime_task_writes_do_not_mutate_committed_fixtures(tmp_path: Path):
    fixture_path = FIXTURES_DIR / "reconstruction_tasks.json"
    before = fixture_path.read_bytes()
    repository = JsonFixtureRepository(runtime_dir=tmp_path / "runtime")
    base_task = repository.get_reconstruction_task("task_demo_p0a_low_budget_student")
    assert base_task is not None
    payload = base_task.model_dump(mode="json")
    payload["task_id"] = "task_runtime_demo"
    payload["primary_card"]["common"]["title"] = "运行时保存任务"

    saved = repository.save_runtime_reconstruction_task(ReconstructionTask.model_validate(payload))

    runtime_path = tmp_path / "runtime" / "reconstruction_tasks.json"
    assert saved.task_id == "task_runtime_demo"
    assert runtime_path.exists()
    assert fixture_path.read_bytes() == before
    assert repository.get_reconstruction_task("task_runtime_demo") is not None
    assert repository.get_reconstruction_task("task_runtime_demo", include_runtime=False) is None


def test_runtime_snapshot_writes_do_not_mutate_committed_fixtures(tmp_path: Path):
    fixture_path = FIXTURES_DIR / "saved_reconstruction_snapshots.json"
    before = fixture_path.read_bytes()
    repository = JsonFixtureRepository(runtime_dir=tmp_path / "runtime")
    base_snapshot = repository.get_saved_reconstruction_snapshot("snap_demo_p0a_low_budget_student")
    assert base_snapshot is not None
    payload = deepcopy(base_snapshot.model_dump(mode="json"))
    payload["snapshot_id"] = "snap_runtime_demo"
    payload["title"] = "运行时保存快照"

    saved = repository.save_runtime_reconstruction_snapshot(SavedReconstructionSnapshot.model_validate(payload))

    runtime_path = tmp_path / "runtime" / "saved_reconstruction_snapshots.json"
    assert saved.snapshot_id == "snap_runtime_demo"
    assert runtime_path.exists()
    assert fixture_path.read_bytes() == before
    assert repository.get_saved_reconstruction_snapshot("snap_runtime_demo") is not None
    assert repository.get_saved_reconstruction_snapshot("snap_runtime_demo", include_runtime=False) is None
