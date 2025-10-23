"""型定義."""

from typing import Any, TypedDict


class SlackMessage(TypedDict, total=False):
    """Slackメッセージの型定義."""

    user: str
    text: str
    ts: str
    type: str
    team: str
    channel: str


class SlackResponse(TypedDict):
    """Slack APIレスポンスの型定義."""

    ok: bool
    error: str | None
    messages: list[SlackMessage]
    has_more: bool
    response_metadata: dict[str, Any]


class SearchResponse(TypedDict):
    """Slack search APIレスポンスの型定義."""

    ok: bool
    error: str | None
    messages: dict[str, Any]

