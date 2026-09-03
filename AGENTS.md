# UNFORGE Press — instructions for agents

You are looking at the public printer, not the node.

## Do

- Print: `python press.py FILE.unforge.json` or `python press.py FILE` (looks for `FILE.unforge.json`)
- Interop (no server): `python press.py --schema` · `from press import imprimer` · INTEROP.md
- Treat `ok: true` as “HTML written from a UNFORGE-PREUVE-v1 card”
- Send match questions to [unforge-check](https://github.com/carllaliberte/unforge-check) — `VERT` there means the file matches, not a quantum claim
- Send itinerary questions to [unforge-trail](https://github.com/carllaliberte/unforge-trail) — press one stamp card, not the trail file
- Keep proofs next to files; never invent a signature

## Do not

- Call this a quantum computer, a coin, a cloud, or a seal
- Gloss print as quantum-green. Check’s `VERT` is a match bit.
- Open or request `quantum.db` / private keys
- Issue proofs here (issuing is private QUANTUM: `carllaliberte/unforge`)
- Vendor famille, garde, check, or trail
- Verify or re-sign in this repo

## Formats

- Proof: `UNFORGE-PREUVE-v1` — unforge-check SPEC.md
- Trail: `UNFORGE-TRAIL-v1` — repo unforge-trail (refused here)
- Press: HTML A5 + `press.v0` record — this repo

## Brand

UNFORGE is a trademark of Carl Laliberté.
This repo: Apache-2.0 stub until Carl. The private node is not licensed here.
