from __future__ import annotations

from typing import Any, Mapping


class DomainError(Exception):
    code = "domain_error"
    status_code = 400

    def __init__(self, message: str, detail: Mapping[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.detail = dict(detail) if detail is not None else None

    def to_payload(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "detail": self.detail,
        }


class NotFoundError(DomainError):
    code = "not_found"
    status_code = 404


class InvalidSourceError(DomainError):
    code = "invalid_source"
    status_code = 400


class ConstrainedRequestError(DomainError):
    code = "constrained_request"
    status_code = 422


class FixtureDataError(DomainError):
    code = "fixture_data_failure"
    status_code = 500
