#!/usr/bin/env python3
"""UNFORGE Press — printable A5 pocket card from a .unforge.json.

Prints ids. Does not open the signature. Does not verify the file.
Not a seal. Not QUANTUM. No node. No cloud. No coin.
"""
from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path

FORMAT = "UNFORGE-PREUVE-v1"
TRAIL_FORMAT = "UNFORGE-TRAIL-v1"
SCHEMA_ID = "press.v0"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema" / "press.v0.json"

CSS = (
    "@page{size:A5 portrait;margin:14mm}"
    "html{color-scheme:light}"
    "body{font-family:Palatino,'Palatino Linotype',Georgia,serif;color:#111;margin:0;background:#fff}"
    ".card{border:2px solid #111;min-height:180mm;padding:12mm 10mm;box-sizing:border-box;"
    "display:flex;flex-direction:column}"
    ".marque{letter-spacing:.35em;font-size:11px;text-transform:uppercase}"
    "h1{font-size:22px;font-weight:600;margin:18px 0 8px}"
    ".fait{margin:0 0 16px;font-size:14px;line-height:1.4}"
    ".hex{font-family:ui-monospace,Menlo,Consolas,monospace;letter-spacing:.08em;"
    "font-size:13px;line-height:1.7;margin:4px 0 18px}"
    ".libelle{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:9px;"
    "letter-spacing:.16em;text-transform:uppercase;color:#333}"
    ".meta{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:10px;line-height:1.85}"
    ".meta b{display:inline-block;min-width:9em;font-weight:600}"
    ".pied{margin-top:auto;padding-top:16px;font-size:11px;color:#333;border-top:1px solid #111}"
    ".pied p{margin:0 0 6px}"
)


def voisin_carte(fichier: Path) -> Path:
    """Card that sits beside a file: FILE.unforge.json."""
    if fichier.name.endswith(".unforge.json"):
        return fichier
    return Path(str(fichier) + ".unforge.json")


def resoudre(chemin: Path) -> Path:
    """Accept a card, or a file whose card sits beside it."""
    if chemin.name.endswith(".unforge.json") or chemin.name.endswith(".unforge-trail.json"):
        return chemin
    voisin = voisin_carte(chemin)
    if voisin.is_file():
        return voisin
    raise FileNotFoundError("preuve introuvable")


def dest_defaut(preuve: Path) -> Path:
    name = preuve.name
    if name.endswith(".unforge.json"):
        return preuve.with_name(name[: -len(".unforge.json")] + ".press.html")
    return preuve.with_name(name + ".press.html")


def blocs_hex(valeur: str) -> str:
    hexa = "".join(c for c in (valeur or "") if c.isalnum())[:64]
    return " ".join(hexa[i : i + 8] for i in range(0, len(hexa), 8))


def premiere_ligne(texte: str) -> str:
    return (texte or "").split("\n", 1)[0]


def phrase_press(rec: dict) -> str:
    err = rec.get("erreur")
    if err == "format":
        return "pas UNFORGE-PREUVE-v1."
    if err == "itinéraire":
        return "ceci est un itinéraire. Presse une carte .unforge.json."
    if err == "preuve introuvable":
        return "preuve introuvable."
    if err == "json":
        return "JSON illisible."
    if rec.get("ok"):
        return "Press n'ouvre pas la signature. Check le fait."
    if err:
        return str(err)
    return "refus."


def habiller(rec: dict) -> dict:
    rec.setdefault("geste", "press")
    rec.setdefault("marque", "UNFORGE")
    rec.setdefault("noeud", "non requis")
    rec.setdefault("schema", SCHEMA_ID)
    rec["phrase"] = phrase_press(rec)
    return rec


def feuille(paquet: dict) -> dict:
    """Ids from a card. Does not open the signature. Does not hash a file."""
    if paquet.get("format") == TRAIL_FORMAT:
        return habiller({"ok": False, "erreur": "itinéraire"})
    if paquet.get("format") != FORMAT:
        return habiller({"ok": False, "erreur": "format"})
    objet = paquet.get("objet") or {}
    sha = objet.get("sha256") or ""
    return habiller(
        {
            "ok": True,
            "id": paquet.get("id"),
            "card_id": paquet.get("card_id"),
            "token_id": paquet.get("token_id"),
            "label": paquet.get("card_label"),
            "objet": objet.get("nom"),
            "sha256": sha or None,
            "empreinte": paquet.get("empreinte"),
            "algo": paquet.get("signature_algos") or "ed25519",
            "created_at": paquet.get("created_at"),
            "fait": premiere_ligne(paquet.get("fait") or ""),
        }
    )


def html_carte(paquet: dict, rec: dict | None = None) -> str:
    """A5 pocket HTML. Escapes every field. Does not verify."""
    rec = rec if rec is not None else feuille(paquet)
    objet = paquet.get("objet") or {}
    nom = rec.get("objet") or rec.get("id") or "preuve"
    fait = rec.get("fait") or ""
    sha = rec.get("sha256") or paquet.get("empreinte") or ""
    rows = [
        ("id", rec.get("id")),
        ("card", rec.get("card_id")),
        ("token", rec.get("token_id")),
        ("when", rec.get("created_at")),
        ("file", objet.get("nom") or nom),
        ("sha256", rec.get("sha256")),
        ("empreinte", rec.get("empreinte")),
    ]
    meta = "".join(
        f"<div><b>{html.escape(k)}</b> {html.escape(str(v if v not in (None, '') else '—'))}</div>"
        for k, v in rows
    )
    record = {k: rec[k] for k in rec}
    payload = html.escape(json.dumps(record, ensure_ascii=False, indent=2), quote=False)
    return (
        "<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'/>"
        f"<title>UNFORGE Press — {html.escape(str(nom))}</title>"
        f"<style>{CSS}</style></head><body>"
        f"<script type='application/json' id='unforge-press'>{payload}</script>"
        "<article class='card'>"
        "<div class='marque'>UNFORGE · PRESS</div>"
        f"<h1>{html.escape(str(nom))}</h1>"
        f"<p class='fait'>{html.escape(fait)}</p>"
        "<div class='libelle'>objet sha256 — printed, not recomputed</div>"
        f"<div class='hex'>{html.escape(blocs_hex(str(sha)))}</div>"
        f"<div class='meta'>{meta}</div>"
        "<footer class='pied'>"
        "<p>Pocket card. Not a seal. Not QUANTUM.</p>"
        "<p>Verify the file with unforge-check. Stamps: unforge-trail.</p>"
        "<p>The node stays yours. The attestation leaves.</p>"
        "</footer></article></body></html>"
    )


def imprimer(preuve: Path, dest: Path | None = None) -> dict:
    """Read a card, write A5 HTML, return the press.v0 record. Never signs."""
    paquet = json.loads(preuve.read_text(encoding="utf-8"))
    rec = feuille(paquet)
    if not rec.get("ok"):
        return rec
    cible = dest if dest is not None else dest_defaut(preuve)
    cible.write_text(html_carte(paquet, rec), encoding="utf-8")
    rec["html"] = str(cible)
    rec["phrase"] = phrase_press(rec)
    return rec


def schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def ligne_humaine(rec: dict) -> str:
    if rec.get("ok"):
        bits = [x for x in ("IMPRIMÉ", rec.get("objet") or rec.get("id"), rec.get("html")) if x]
        return "  ".join(str(b) for b in bits)
    return f"REFUS  {rec.get('phrase')}"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="press.py",
        description=(
            "UNFORGE Press — print a pocket card from a .unforge.json. "
            "No node. No cloud. No coin. Does not open the signature."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "examples:\n"
            "  python3 press.py document.pdf.unforge.json\n"
            "  python3 press.py document.pdf\n"
            "  python3 press.py document.pdf.unforge.json -o /tmp/card.html\n"
            "  python3 press.py document.pdf.unforge.json --human\n"
            "\n"
            "If a file is given, Press looks for FILE.unforge.json beside it.\n"
            "Writes A5 HTML. Machine record (press.v0) on stdout.\n"
            "Exit 0 = printed. Exit 1 = refuse. Exit 2 = unreadable.\n"
            "ok: true means the card is UNFORGE-PREUVE-v1 and HTML was written.\n"
            "It does not mean the file matches — that verdict is unforge-check.\n"
            "Agents: python3 press.py --schema   or   from press import imprimer"
        ),
    )
    p.add_argument(
        "preuve",
        nargs="?",
        help="card .unforge.json, or a file whose card sits beside it",
    )
    p.add_argument("-o", "--out", help="destination HTML (default: FILE.press.html)")
    p.add_argument("--schema", action="store_true", help="print press.v0 JSON Schema and exit")
    sortie = p.add_mutually_exclusive_group()
    sortie.add_argument("--json", action="store_true", help="machine record on stdout (default)")
    sortie.add_argument("--human", action="store_true", help="one IMPRIMÉ / REFUS line — not a match verdict")
    args = p.parse_args(argv)

    if args.schema:
        try:
            print(json.dumps(schema(), ensure_ascii=False, indent=2))
        except Exception as e:
            print(json.dumps({"ok": False, "erreur": str(e)}, ensure_ascii=False, indent=2))
            return 2
        return 0

    if not args.preuve:
        p.error("drop a .unforge.json card, or a file whose card sits beside it")

    try:
        preuve = resoudre(Path(args.preuve))
        if not preuve.is_file():
            rec = habiller({"ok": False, "erreur": "preuve introuvable", "attendu": str(preuve)})
            _émettre(rec, args.human)
            return 2
        dest = Path(args.out) if args.out else None
        rec = imprimer(preuve, dest)
    except FileNotFoundError:
        attendu = str(voisin_carte(Path(args.preuve)))
        rec = habiller({"ok": False, "erreur": "preuve introuvable", "attendu": attendu})
        _émettre(rec, args.human)
        return 2
    except json.JSONDecodeError as e:
        rec = habiller({"ok": False, "erreur": "json", "detail": str(e)})
        _émettre(rec, args.human)
        return 2
    except OSError as e:
        rec = habiller({"ok": False, "erreur": str(e)})
        _émettre(rec, args.human)
        return 2

    _émettre(rec, args.human)
    return 0 if rec.get("ok") else 1


def _émettre(rec: dict, human: bool) -> None:
    if human:
        print(ligne_humaine(rec))
    else:
        print(json.dumps(rec, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    raise SystemExit(main())
