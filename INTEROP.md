# Interop — no server

Other agents and tools print a card with a local process. No node. No cloud. No coin. Nothing here signs.

Press prints ids. It does not open the signature. Companion file → real sha256 verify (jalon 1). No companion → card field, not recomputed.

## Command

```bash
python3 press.py FILE.unforge.json
python3 press.py FILE
python3 press.py FILE.unforge.json --fichier FILE
python3 press.py FILE.unforge.json --mesure
python3 press.py FILE.unforge.json --mesure carte.mesure.json
python3 press.py FILE.unforge.json --ancrage
python3 press.py FILE.unforge.json --ancrage examples/billet.ancrage.json
python3 press.py --schema
```

`FILE` alone looks for `FILE.unforge.json` beside it.
Writes `FILE.press.html` (A5 carte de poche). Share or print. Not a payment Wallet.
Concurrent HTML carte write uses `fcntl.flock` (jalon 1).
Machine record on stdout.

## Python

```python
from pathlib import Path
from press import imprimer, feuille, schema

rec = imprimer(Path("doc.pdf.unforge.json"))
assert rec["ok"] is True          # card is UNFORGE-PREUVE-v1 or v2 and HTML was written
assert rec["geste"] == "press"
schema()                          # press.v0
# companion file: sha256 from bytes (jalon 1) — mismatch refuses, no HTML
rec = imprimer(Path("doc.pdf.unforge.json"), fichier=Path("doc.pdf"))
# kit presse: copy the MESURE card first — consulter writes it
rec = imprimer(Path("doc.pdf.unforge.json"), mesure=Path("doc.pdf.mesure.json"))
assert rec["mesure"]["consomme"] is True
# re-press: ANCRAGE is read-only — verifier does not write
rec = imprimer(Path("doc.pdf.unforge.json"), ancrage=Path("examples/billet.ancrage.json"))
assert rec["ancrage"]["verifie"] is True
```

`feuille`, `html_carte`, `imprimer`, `consulter_mesure`, `verifier_ancrage`, `verifier_objet` stay importable.

`ok: true` is **not** a match. Match is [unforge-check](https://github.com/carllaliberte/unforge-check): `ok: true` there, `VERT` in `--human`, means the file still matches the card. Not a quantum claim.

A trail is not a card. [unforge-trail](https://github.com/carllaliberte/unforge-trail) stamps are each a `UNFORGE-PREUVE-v1` or `UNFORGE-PREUVE-v2` file. Press that file. A `UNFORGE-TRAIL-v1` itinerary is refused here.

## Exit

| Code | Meaning |
|---|---|
| 0 | printed (`ok: true`, HTML written) |
| 1 | refuse (not `UNFORGE-PREUVE-v1`/`v2`, itinerary, companion sha256/octets mismatch, spent MESURE, or expired ANCRAGE) |
| 2 | unreadable (missing path, bad JSON) |

## Record

JSON on stdout. Shape: `schema/press.v0.json`. Stable keys: `ok`, `geste`, `id`, `card_id`, `token_id`, `objet`, `sha256`, `empreinte`, `html`, `marque`, `noeud`, `phrase`. Extra keys may appear. `--human` prints `IMPRIMÉ` / `REFUS` — not `VERT`.

The HTML embeds the same record in `<script type="application/json" id="unforge-press">`.

`empreinte` is copied from the card. It is not recomputed. Companion file → `sha256` from real bytes vs `objet.sha256` (jalon 1). No companion → card field, not recomputed.

Kit presse (porte 8): `--mesure` consults a `MESURE-v0` card ([mesure-protocol](https://github.com/carllaliberte/mesure-protocol)). One reading is spent on the card on disk. The press record may then carry `mesure` (`consomme: true`, remaining `lectures`, `detruit`). That key is press.v0, not written back onto the MESURE card. Consulting without a remaining reading is refused — no HTML. Default print does not consult. Do not fork a measure. Not a seal. Not a receipt.

Re-press (portes 3+7): `--ancrage` verifies an `ANCRAGE-v0` card ([ancrage-protocol](https://github.com/carllaliberte/ancrage-protocol)). Read-only — press does not write `avant`. The press record may then carry `ancrage` (`verifie: true`, `objet`, `avant`). That key is press.v0, not written back onto the ANCRAGE card. An expired date refuses the print — à re-mesurer, not fake. No HTML. A new date is a new act (`ancrage.py ecrire`), then press again. Reculer in place is forbidden. Default print does not verify. Fixtures `examples/billet.ancrage.json` (porte 3) and `examples/garantie.ancrage.json` (porte 7) can be verified in place. Not a seal. Not a receipt.

## Do not

Stand up a server. Open `quantum.db`. Invent a signature. Call this a coin. Call this a seal. Call this a payment Wallet. Call print quantum-green.
