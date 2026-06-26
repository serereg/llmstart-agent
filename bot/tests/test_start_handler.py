"""Tests for /start deep-link session parsing."""

from uuid import UUID

from bot.handlers.start_parser import build_handoff_message, parse_handoff_session_id

SAMPLE_UUID = UUID("550e8400-e29b-41d4-a716-446655440000")


def test_parse_handoff_session_id_valid() -> None:
    result = parse_handoff_session_id(f"session_{SAMPLE_UUID}")
    assert result == SAMPLE_UUID


def test_parse_handoff_session_id_none_for_empty_args() -> None:
    assert parse_handoff_session_id(None) is None


def test_parse_handoff_session_id_invalid_format() -> None:
    assert parse_handoff_session_id("invalid") is None
    assert parse_handoff_session_id("session_not-a-uuid") is None


def test_build_handoff_message() -> None:
    assert build_handoff_message(SAMPLE_UUID) == f"/start session_{SAMPLE_UUID}"
