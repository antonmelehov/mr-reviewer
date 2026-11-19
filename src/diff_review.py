import json
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

VALID_CATEGORIES = {"bug", "security", "missing_test", "style"}
VALID_SEVERITIES = {"high", "medium", "low"}


class DiffReviewError(Exception):
    pass


@dataclass
class Finding:
    category: str
    file: str
    line: int | None
    severity: str
    message: str


def review_diff(openai_client, touched_files: list[str], diff_text: str) -> list[Finding]:
    logger.info(
        "reviewing diff: %d touched file(s), %d chars of diff text",
        len(touched_files),
        len(diff_text),
    )

    user_input = f"Touched files: {json.dumps(touched_files)}\n\nDiff:\n{diff_text}"

    try:
        response = openai_client.responses.create(input=user_input)
    except Exception as exc:
        logger.error("Foundry agent call failed: %s", exc)
        raise DiffReviewError(f"Foundry agent call failed: {exc}") from exc

    findings = _parse_findings(response.output_text)

    logger.info("review complete: %d finding(s)", len(findings))
    return findings


def _parse_findings(output_text: str) -> list[Finding]:
    try:
        payload = json.loads(output_text)
    except json.JSONDecodeError as exc:
        raise DiffReviewError(f"agent response was not valid JSON: {exc}") from exc

    if not isinstance(payload, dict) or "findings" not in payload:
        raise DiffReviewError("agent response missing 'findings' key")

    raw_findings = payload["findings"]
    if not isinstance(raw_findings, list):
        raise DiffReviewError("'findings' was not a list")

    return [_parse_finding(raw) for raw in raw_findings]


def _parse_finding(raw: object) -> Finding:
    if not isinstance(raw, dict):
        raise DiffReviewError(f"finding was not an object: {raw!r}")

    required = {"category", "file", "severity", "message"}
    missing = required - raw.keys()
    if missing:
        raise DiffReviewError(f"finding missing required field(s): {missing}")

    if raw["category"] not in VALID_CATEGORIES:
        raise DiffReviewError(f"unrecognized category: {raw['category']!r}")

    if raw["severity"] not in VALID_SEVERITIES:
        raise DiffReviewError(f"unrecognized severity: {raw['severity']!r}")

    return Finding(
        category=raw["category"],
        file=raw["file"],
        line=raw.get("line"),
        severity=raw["severity"],
        message=raw["message"],
    )
