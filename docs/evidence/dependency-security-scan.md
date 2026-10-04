# Dependency Security Scan

## Backend

`pip-audit` reported **no known vulnerabilities** in the Python dependency set.

## Frontend Production Dependencies

`npm audit --omit=dev` reported **0 vulnerabilities** in production dependencies.

## Frontend Development Dependencies

The full `npm audit` reported **5 high-severity findings** through the frontend build toolchain. The dependency path is Tailwind CSS 3.4.19 -> chokidar / fast-glob / micromatch -> braces 3.0.3.

The available automatic fix requires a breaking Tailwind CSS major-version upgrade. This was not forced during final integration because the production dependency audit is clean and a breaking framework migration would require separate regression testing.

## Release Verification

- Backend tests: 25 passed, 1 warning
- Frontend production build: successful
- Python dependency scan: no known vulnerabilities
- Frontend production dependency scan: 0 vulnerabilities
