"""ChatML record schema for llmstart-agent validation dataset (Level 2 extraction)."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

Segment = Literal["b2c", "b2b"]
DatasetType = Literal["T1", "T2", "T3", "T4", "T5", "T6", "T7"]
TaxonomyGroup = Literal["G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8", "G9"]
SourceBranch = Literal["extraction", "synthesis"]
GroundTruthMode = Literal["expert_dialog", "kb_rag", "rubric", "tool_call"]


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str


class SourceRef(BaseModel):
    chat_id: str
    message_indices: list[int] = Field(description="Индексы messages[] в исходном JSON")


class TaxonomyRef(BaseModel):
    group: TaxonomyGroup
    subcategory: str


class RubricCheck(BaseModel):
    id: str
    description: str
    required: bool = True


class ExpectedToolCall(BaseModel):
    name: str
    args: dict[str, Any] = Field(default_factory=dict)


class RecordMetadata(BaseModel):
    source_branch: SourceBranch
    source: SourceRef | None = None
    segment: Segment
    taxonomy: TaxonomyRef
    dataset_type: DatasetType
    abilities: list[str] = Field(description="S1..S9 из dataset-plan")
    ground_truth_mode: GroundTruthMode
    product_ids: list[str] = Field(default_factory=list)
    expected_tools: list[ExpectedToolCall] = Field(default_factory=list)
    rubric: list[RubricCheck] = Field(default_factory=list)
    expert_reference: str | None = Field(
        default=None,
        description="Дословный фрагмент ответа эксперта из диалога (sanitized)",
    )
    notes: str | None = None


class DatasetRecord(BaseModel):
    """Одна запись валидационного датасета."""

    id: str
    input: list[ChatMessage]
    expected_output: str = Field(description="Эталонный ответ агента или краткая стратегия")
    metadata: RecordMetadata
