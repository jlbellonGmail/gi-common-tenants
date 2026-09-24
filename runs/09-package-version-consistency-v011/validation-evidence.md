# Evidence

- Published release `v0.1.1` exists at GitHub with wheel SHA-256
  `0d43d24f...18c0bda7`; from a clean venv its distribution metadata is
  `0.1.1` but the imported module reports `0.1.0`.
- The corrected PR build wheel is `gi_common_tenants-0.1.1-py3-none-any.whl`,
  SHA-256 recorded by the build, and from a clean venv reports `0.1.1` for
  both distribution and module.
- Tenants suite: `12 passed, 1 skipped`; the skip is real PostgreSQL because
  `DATABASE_URL` is not configured.
- No new tag or release was created; the existing published artifact remains
  immutable pending the release decision for the correction.
