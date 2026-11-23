# Seeded checkout demo

This repository intentionally contains the checkout regression shown in the RELAY AI pitch deck. `src/checkout.py` subtracts a fixed discount twice. The $100 cart with a $10 discount should total $90.00, while the seeded implementation returns $80.00.

Run the seeded regression from this directory with `python -m pytest -q`. The expected baseline is one failed discount test and one passing zero-discount test. The dashboard's **Seeded demo: checkout discount applied twice** scenario uses these same source and test files.

`patches/discount-once.patch` is the reviewed example fix used by the deterministic demo rehearsal. It changes only `src/checkout.py`. After applying it, both checkout tests should pass.
