# UNFORGE Press

The proof should fit in a pocket.

```bash
python3 press.py examples/bienvenue.txt.unforge.json
```

`--human` prints `IMPRIMÉ` / `REFUS`. That is not a match verdict. Open `examples/bienvenue.txt.press.html` and print A5.

v1 = bandeau legacy (« v1 n'inclut pas objet — resseller v2 »). v2 = normal. Demo card here is v1.

Or name the file. Press looks for `FILE.unforge.json` beside it:

```bash
python3 press.py examples/bienvenue.txt
python3 press.py examples/bienvenue.txt.unforge.json --human
```

Machine record on stdout (`press.v0`).

Press prints ids. It does not open the signature.
Unforge ne signe pas.
Unforge does not sign.
Verify the file with [unforge-check](https://github.com/carllaliberte/unforge-check). Check’s `VERT` means the file matches the card — not a quantum claim.
Itinerary of stamps: [unforge-trail](https://github.com/carllaliberte/unforge-trail). Press one card, not the trail file.

Agents: `python3 press.py --schema` · `from press import imprimer` · [INTEROP.md](INTEROP.md).

Press is a printer, not a seal. Apache-2.0 does not license QUANTUM.
No node. No cloud. No coin.
Schema: `press.v0` (`python3 press.py --schema`). Famille juge.v0 is a different rail.
Brand UNFORGE reserved. Code: Apache-2.0. See [LICENSE](LICENSE), [NOTICE](NOTICE), [COPYRIGHT.md](COPYRIGHT.md).
The private QUANTUM node is not licensed here.

<!-- ville/garde-hooks -->
