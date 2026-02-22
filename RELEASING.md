# Releasing `cc-hooks-py`

## 1. Prepare

```bash
make check
make package-check
make e2e-all
make release-readiness
make release-check
# Optional but recommended when local Claude CLI is available:
make e2e-claude
```

## 2. Update metadata

1. Bump version using hatch:

```bash
make bump-patch   # or make bump-minor / make bump-major
make version
```

2. Confirm `CHANGELOG.md` includes the new version entry.
3. Commit and tag:

```bash
VERSION=$(make -s version)
git add -A
git commit -m "release: v${VERSION}"
git tag "v${VERSION}"
git push origin main --tags
```

## 3. Build and verify artifacts (local optional)

```bash
python -m build
python -m twine check dist/*
```

## 4. Upload to PyPI

Preferred: tag push triggers `.github/workflows/publish.yml`.

Set repository secret:

- `PYPI_API_TOKEN`
- `TEST_PYPI_API_TOKEN` (for manual TestPyPI publish)

Manual TestPyPI via GitHub Actions:

- Open `Publish` workflow
- Run workflow with `target=testpypi`

Trusted Publishing (OIDC) option:

- Configure Trusted Publisher in PyPI/TestPyPI
- Run `Publish` workflow with:
  - `target=testpypi-oidc` or
  - `target=pypi-oidc`

Manual fallback:

```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-xxxxxxxxxxxxxxxx
python -m twine upload dist/*
```

## 5. Create GitHub Release

Use `.github/RELEASE_TEMPLATE.md` as the release notes base.
