# Interop — no server

Other agents and tools print a card with a local process. No node. No cloud. No coin. Nothing here signs.

Press prints ids. It does not open the signature. It does not verify a file.

## Command

```bash
python3 press.py FILE.unforge.json
python3 press.py FILE
python3 press.py --schema
```

`FILE` alone looks for `FILE.unforge.json` beside it.
Writes `FILE.press.html` (A5). Machine record on stdout.

## Python

```python
from pathlib import Path
from press import imprimer, feuille, schema

rec = imprimer(Path("doc.pdf.unforge.json"))
assert rec["ok"] is True          # card is UNFORGE-PREUVE-v1 and HTML was written
assert rec["geste"] == "press"
schema()                          # press.v0
```

`feuille`, `html_carte`, `imprimer` stay importable.

`ok: true` is **not** a match. Match is [unforge-check](https://github.com/carllaliberte/unforge-check): `ok: true` there, `VERT` in `--human`, means the file still matches the card. Not a quantum claim.

A trail is not a card. [unforge-trail](https://github.com/carllaliberte/unforge-trail) stamps are each a `UNFORGE-PREUVE-v1` file. Press that file. A `UNFORGE-TRAIL-v1` itinerary is refused here.

## Exit

| Code | Meaning |
|---|---|
| 0 | printed (`ok: true`, HTML written) |
| 1 | refuse (not `UNFORGE-PREUVE-v1`, or an itinerary) |
| 2 | unreadable (missing path, bad JSON) |

## Record

JSON on stdout. Shape: `schema/press.v0.json`. Stable keys: `ok`, `geste`, `id`, `card_id`, `token_id`, `objet`, `sha256`, `empreinte`, `html`, `marque`, `noeud`, `phrase`. Extra keys may appear. `--human` prints `IMPRIMÉ` / `REFUS` — not `VERT`.

The HTML embeds the same record in `<script type="application/json" id="unforge-press">`.

`sha256` and `empreinte` are copied from the card. They are not recomputed.

## Do not

Stand up a server. Open `quantum.db`. Invent a signature. Call this a coin. Call this a seal. Call print quantum-green.
