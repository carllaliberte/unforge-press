# UNFORGE Press

A pocket card (carte de poche) is HTML named `*.press.html` printed from a `*.unforge.json` that sits beside the object it attests. Share or print. Not a payment Wallet. Not a seal. Not a receipt.

Card format: `UNFORGE-PREUVE-v2` (v1 still prints, with a banner: v1 n'inclut pas objet — resseller v2) — see [unforge-check SPEC](https://github.com/carllaliberte/unforge-check/blob/main/SPEC.md).

Required keys on the card: `format`, `marque`, `id`, `card_id`, `card_public`, `token_id`, `empreinte`, `signature`, `fait`, `created_at`.

Press copies ids onto paper. It does not recompute `empreinte`. It does not open `signature`. It does not hash the file.

Kit presse (porte 8) may `--mesure` a sibling `MESURE-v0` card. Consulting spends a reading ([mesure-protocol](https://github.com/carllaliberte/mesure-protocol)). Press records the spend. It does not open a measure, fork one, or call the print a receipt.

Re-press (portes 3+7) may `--ancrage` an `ANCRAGE-v0` card ([ancrage-protocol](https://github.com/carllaliberte/ancrage-protocol)). Verifier is read-only. Expired `avant` refuses the print — à re-mesurer, not fake. Press does not write a new date, reculer, or call the print a receipt.

Roles:

- QUANTUM signs (private keys stay home). Not this repo.
- Check re-verifies Ed or `UFHY1` + file SHA-256. `VERT` = match.
- Press does not open the signature; it prints ids.
- Trail compares SHAs across one-passage stamps; it does not re-sign.
- Retract uses other material, on QUANTUM.

Do not merge check or trail into this repository. Interop is the card.
