# Publishing

This guide covers publishing Akashic to PyPI. The PyPI package name is
`akashic-kb`; the installed command is `akashic`.

## Prerequisites

- A clean working tree, except for intentional release changes.
- Access to the `akashic-kb` project on PyPI.
- A PyPI API token configured locally.
- `uv` available on `PATH`.

Install release tooling from the project:

```bash
uv sync --dev
```

If you use `twine` directly, store credentials in `~/.pypirc` or pass a token
at upload time. For API tokens, the username is `__token__` and the password is
the token value.

## 1. Prepare the Release

Update the version in `pyproject.toml`:

```toml
[project]
version = "0.1.1"
```

Then update the lockfile if needed:

```bash
uv sync
```

Run the checks:

```bash
uv run pytest -q
uv run akashic --version
```

Commit the release change:

```bash
git status
git add pyproject.toml uv.lock
git commit -m "Release 0.1.1"
```

## 2. Build the Artifacts

Remove old local builds, then build a fresh source distribution and wheel:

```bash
rm -rf dist
uv build
```

Expected output:

```text
dist/akashic_kb-0.1.1.tar.gz
dist/akashic_kb-0.1.1-py3-none-any.whl
```

Validate the package metadata:

```bash
uv run twine check dist/*
```

## 3. Inspect Package Contents

Check what will be uploaded before publishing:

```bash
tar -tzf dist/akashic_kb-0.1.1.tar.gz | sed -n '1,120p'
unzip -l dist/akashic_kb-0.1.1-py3-none-any.whl | sed -n '1,160p'
```

Current packaging behavior:

- The wheel includes the Python package under `akashic/`.
- The wheel also includes `frontend/` twice: once at top level and once under
  `akashic/frontend/`, because of the current Hatch `force-include` settings.
- Top-level directories that are not listed in the wheel config, such as
  `presentation/`, are not installed from the wheel.
- Hatch source distributions include tracked project files unless excluded, so
  top-level assets such as `presentation/` can still be uploaded to PyPI inside
  the `.tar.gz` source distribution.

If a top-level asset directory should not be published in the source
distribution, add it to `[tool.hatch.build].exclude` before building:

```toml
[tool.hatch.build]
exclude = [
  "/presentation",
]
```

Keep the existing excludes when adding new ones.

## 4. Publish to TestPyPI

Use TestPyPI first for a release dry run:

```bash
uv run twine upload --repository testpypi dist/*
```

Install from TestPyPI in a temporary environment:

```bash
python3 -m venv /tmp/akashic-testpypi
/tmp/akashic-testpypi/bin/python -m pip install \
  --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ \
  akashic-kb==0.1.1
/tmp/akashic-testpypi/bin/akashic --version
```

## 5. Publish to PyPI

After TestPyPI looks correct, upload the same artifacts to PyPI:

```bash
uv run twine upload dist/*
```

Verify the published package:

```bash
python3 -m venv /tmp/akashic-pypi
/tmp/akashic-pypi/bin/python -m pip install akashic-kb==0.1.1
/tmp/akashic-pypi/bin/akashic --version
```

## 6. Tag the Release

Create and push a Git tag after PyPI verification:

```bash
git tag v0.1.1
git push origin main
git push origin v0.1.1
```

## Troubleshooting

- `File already exists`: PyPI versions are immutable. Bump the version and
  rebuild.
- `Invalid or non-existent authentication information`: check the repository
  target and token credentials.
- Unexpected files in the package: inspect both artifacts. The wheel controls
  what most users install; the source distribution controls what PyPI stores as
  the source archive.
