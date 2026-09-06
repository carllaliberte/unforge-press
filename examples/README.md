# Example

```bash
python3 press.py examples/bienvenue.txt.unforge.json
python3 press.py examples/bienvenue.txt
```

Same demo card as [unforge-check](https://github.com/carllaliberte/unforge-check) / [unforge-trail](https://github.com/carllaliberte/unforge-trail): `QT-PR-DEMO0001`.
Ed25519-only so CI stays small. Not Carl's node.
Press does not verify it. Check does.

`bienvenue.txt.mesure.json` is an open MESURE-v0 embargo (1 lecture, `sha_sur: fichier` = the demo file). Copy it, then `--mesure` the copy. Default print does not consume. Do not consult the fixture in place.
