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

Kit presse (porte 8) — copy the MESURE fixture, then consume one reading. Consulting spends. Not a receipt:

```bash
cp examples/bienvenue.txt.mesure.json /tmp/bienvenue.txt.mesure.json
python3 press.py examples/bienvenue.txt.unforge.json --mesure /tmp/bienvenue.txt.mesure.json -o /tmp/kit.html
```

`--mesure` without a path looks for `FILE.mesure.json` beside the card. Default print does not touch MESURE.

Re-press (portes 3+7) — verify an ANCRAGE-v0 date. Read-only. Expired = re-measure, not fake. Not a receipt:

```bash
python3 press.py examples/bienvenue.txt.unforge.json --ancrage examples/billet.ancrage.json -o /tmp/billet.html
python3 press.py examples/bienvenue.txt.unforge.json --ancrage examples/garantie.ancrage.json -o /tmp/garantie.html
```

`--ancrage` without a path looks for `FILE.ancrage.json` beside the card. Press does not write a new date. A new act is [ancrage-protocol](https://github.com/carllaliberte/ancrage-protocol) `ecrire`. Default print does not touch ANCRAGE.

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
