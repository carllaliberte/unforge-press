# UNFORGE Press

A pocket card is HTML named `*.press.html` printed from a `*.unforge.json` that sits beside the object it attests.

Card format: `UNFORGE-PREUVE-v2` (v1 still prints, with a banner: v1 n'inclut pas objet — resseller v2) — see [unforge-check SPEC](https://github.com/carllaliberte/unforge-check/blob/main/SPEC.md).

Required keys on the card: `format`, `marque`, `id`, `card_id`, `card_public`, `token_id`, `empreinte`, `signature`, `fait`, `created_at`.

Press copies ids onto paper. It does not recompute `empreinte`. It does not open `signature`. It does not hash the file.

Roles:

- QUANTUM signs (private keys stay home). Not this repo.
- Check re-verifies Ed or `UFHY1` + file SHA-256. `VERT` = match.
- Press does not open the signature; it prints ids.
- Trail compares SHAs across one-passage stamps; it does not re-sign.
- Retract uses other material, on QUANTUM.

Do not merge check or trail into this repository. Interop is the card.
