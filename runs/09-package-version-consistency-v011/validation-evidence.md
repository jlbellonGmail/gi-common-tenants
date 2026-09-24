# Evidence

- GitHub release `v0.1.1` exists on `main`, with tag `v0.1.1` and asset SHA-256 `0D43D24D376B6CF56EF7214DA2FA848B0543BC6A9C92D5DBB794F61918C0BDA7`. Its distribution metadata is `0.1.1`, but its imported module reports `0.1.0`; the immutable historical asset is not overwritten.
- Corrected PR artifact: `runs/09-package-version-consistency-v011/artifacts/gi_common_tenants-0.1.1-py3-none-any.whl`. SHA-256: `A9B40B6E8DA61371B928DE3BB40C29CFC27EF256180AAE922E3E67900390F593`. A clean virtual environment reports distribution `0.1.1`, module `__version__ == "0.1.1"`, and the public tenant APIs import successfully.
- `pytest -q tests_tenants`: `12 passed, 1 skipped` (the real PostgreSQL/RLS test is skipped because `DATABASE_URL` is not configured locally).
- GitHub CI for PR #11 passes `circuit-tests`, `product-tests` (PostgreSQL service/RLS path), and `local-reconciler-tests`.
- No new tag or release was created; the existing published asset remains immutable pending the human release decision.
