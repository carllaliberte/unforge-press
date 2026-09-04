# UNFORGE Press

The proof should fit in a pocket.

```bash
python3 press.py examples/bienvenue.txt.unforge.json
# writes examples/bienvenue.txt.press.html — open, print A5
```

Or name the file. Press looks for `FILE.unforge.json` beside it:

```bash
python3 press.py examples/bienvenue.txt
python3 press.py examples/bienvenue.txt.unforge.json --human
```

Machine record on stdout (`press.v0`). `--human` prints `IMPRIMÉ` / `REFUS`. That is not a match verdict.

Press prints ids. It does not open the signature.
Unforge ne signe pas.
Unforge does not sign.
Verify the file with [unforge-check](https://github.com/carllaliberte/unforge-check). Check’s `VERT` means the file matches the card — not a quantum claim.
Itinerary of stamps: [unforge-trail](https://github.com/carllaliberte/unforge-trail). Press one card, not the trail file.

Agents: `python3 press.py --schema` · `from press import imprimer` · [INTEROP.md](INTEROP.md).

No node. No cloud. No coin. This is not a seal.
Schema: `press.v0` (`python3 press.py --schema`). Famille juge.v0 is a different rail.
Brand UNFORGE reserved. Code: Apache-2.0.

<!-- ville/garde-hooks -->
