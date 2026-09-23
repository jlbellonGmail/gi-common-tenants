"""Safe, transport-neutral public errors."""


class TenantsError(Exception):
    code = "TENANTS_ERROR"
    status = 500
    safe_message = "The tenants operation failed."

    def __init__(self, message: str | None = None, *, details: dict | None = None):
        super().__init__(message or self.safe_message)
        self.details = details or {}

    def public(self) -> dict:
        return {"code": self.code, "message": self.safe_message, "details": self.details}


class ValidationError(TenantsError):
    code, status, safe_message = "VALIDATION_ERROR", 400, "The request is invalid."


class AuthenticationRequiredError(TenantsError):
    code, status, safe_message = "AUTHENTICATION_REQUIRED", 401, "Authentication is required."


class ForbiddenError(TenantsError):
    code, status, safe_message = "FORBIDDEN", 403, "The operation is not permitted."


class NotFoundError(TenantsError):
    code, status, safe_message = "NOT_FOUND", 404, "The requested resource was not found."


class ConflictError(TenantsError):
    code, status, safe_message = "CONFLICT", 409, "The requested change conflicts with existing data."


class VersionConflictError(ConflictError):
    code, safe_message = "VERSION_CONFLICT", "The resource changed; refresh and retry."


class CoreUnavailableError(TenantsError):
    code, status, safe_message = "CORE_UNAVAILABLE", 503, "The Core authorization provider is unavailable."


class UnsupportedCoreContractError(TenantsError):
    code, status, safe_message = "UNSUPPORTED_CORE_CONTRACT", 502, "The Core contract is unsupported."


class CapabilityUnavailableError(TenantsError):
    code, status, safe_message = "CAPABILITY_UNAVAILABLE", 501, "The requested Core capability is not published."


class IsolationError(ForbiddenError):
    code, safe_message = "TENANT_ISOLATION_ERROR", "The resource is outside the authorized tenant."
