# One-off catalog scripts

Every script here was written for a single catalog import, asset pass or
verification run that has already been completed and published. They are kept
as the record of how specific product data was produced — several reports in
`reports/` only make sense next to them — but none of them is part of the
reusable pipeline, and none is run in normal work.

The reusable pipeline is the set of scripts directly in `scripts/`:
`import-catalog.py` and the modules it loads, `finalize-translation.py`,
`enhance-catalog-images.py`, `verify-catalog-codes.py`, `prepare-code-ocr.py`,
`quality-audit.py` and `review-server.py`.

To re-run one of these archived scripts, put the pipeline modules on the path,
because eleven of them import shared modules that stayed behind:

```bash
PYTHONPATH=scripts .venv-catalog/bin/python scripts/one-off/<name>.py
```

Before re-running anything that touches `content/products/`, read rule 1 in the
root `README.md`: published records and their catalog numbers are not changed
without an explicit request, and `import-catalog.py` refuses to overwrite
published or hand-edited content for exactly that reason.
