# Sample submission

These four files are the output of the shipped baseline (`make submit`) and are
here only so the shapes are unambiguous:

- `forecast.csv` — 13 weekly rows with P10/P50/P90 closing balances;
- `buffer_plan.csv` — 13 weekly minimum-cash targets;
- `hedge.json` — a single-tenor 100% forward book;
- `manifest.json` — file hashes and metadata.

The numbers are **not** a good answer. The baseline ignores the open invoice
book, the Diwali bonus and the purchase commitments. Copy the schema, not the
numbers.
