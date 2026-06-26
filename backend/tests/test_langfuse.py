"""Tests for Langfuse observability configuration."""

import os

from app.observability.langfuse import build_invoke_config


def test_build_invoke_config_sets_langfuse_session_id() -> None:
    config = build_invoke_config(
        session_id="abc-123",
        channel="web",
        segment=None,
    )
    metadata = config["metadata"]
    assert isinstance(metadata, dict)
    assert metadata["langfuse_session_id"] == "abc-123"
    assert metadata["channel"] == "web"
    assert metadata["langfuse_tags"] == ["channel:web"]


def test_build_invoke_config_includes_segment_tag() -> None:
    config = build_invoke_config(
        session_id="abc-123",
        channel="telegram",
        segment="b2c",
    )
    metadata = config["metadata"]
    assert isinstance(metadata, dict)
    assert metadata["segment"] == "b2c"
    assert metadata["langfuse_tags"] == ["channel:telegram", "segment:b2c"]


def test_build_invoke_config_omits_callbacks_during_pytest() -> None:
    assert os.environ.get("PYTEST_CURRENT_TEST") is not None
    config = build_invoke_config(
        session_id="abc-123",
        channel="web",
        segment=None,
    )
    assert "callbacks" not in config
