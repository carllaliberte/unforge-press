#!/usr/bin/env python3
"""UNFORGE Press — printable A5 carte de poche from a .unforge.json.

Prints ids. Does not open the signature. Does not verify the file.
Share or print. Not a payment Wallet. Not a seal. Not a receipt.
No node. No cloud. No coin.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from datetime import date
from pathlib import Path

try:
    import fcntl
except ImportError:
    fcntl = None  # type: ignore

FORMAT_V1 = "UNFORGE-PREUVE-v1"
FORMAT_V2 = "UNFORGE-PREUVE-v2"
FORMATS = {FORMAT_V1, FORMAT_V2}
TRAIL_FORMAT = "UNFORGE-TRAIL-v1"
MESURE_FORMAT = "MESURE-v0"
ANCRAGE_FORMAT = "ANCRAGE-v0"
DATE_ANCRAGE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
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
    ".bandeau{border:1px solid #111;padding:8px 10px;margin:0 0 14px;font-size:12px}"
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


def voisin_mesure(preuve: Path) -> Path:
    """MESURE-v0 card that sits beside a proof: FILE.mesure.json."""
    name = preuve.name
    if name.endswith(".unforge.json"):
        return preuve.with_name(name[: -len(".unforge.json")] + ".mesure.json")
    if name.endswith(".mesure.json"):
        return preuve
    return Path(str(preuve) + ".mesure.json")


def voisin_ancrage(preuve: Path) -> Path:
    """ANCRAGE-v0 card that sits beside a proof: FILE.ancrage.json."""
    name = preuve.name
    if name.endswith(".unforge.json"):
        return preuve.with_name(name[: -len(".unforge.json")] + ".ancrage.json")
    if name.endswith(".ancrage.json"):
        return preuve
    return Path(str(preuve) + ".ancrage.json")


def blocs_hex(valeur: str) -> str:
    hexa = "".join(c for c in (valeur or "") if c.isalnum())[:64]
    return " ".join(hexa[i : i + 8] for i in range(0, len(hexa), 8))


def premiere_ligne(texte: str) -> str:
    return (texte or "").split("\n", 1)[0]


def phrase_press(rec: dict) -> str:
    err = rec.get("erreur")
    if err == "format":
        return "pas UNFORGE-PREUVE-v1/v2."
    if err == "itinéraire":
        return "ceci est un itinéraire. Presse une carte .unforge.json."
    if err == "preuve introuvable":
        return "preuve introuvable."
    if err == "json":
        return "JSON illisible."
    if err == "mesure introuvable":
        return "MESURE introuvable. Kit presse: FILE.mesure.json."
    if err == "mesure":
        return "pas MESURE-v0."
    if err == "mesure lectures":
        return "MESURE déjà détruite ou plus de lecture."
    if err == "ancrage introuvable":
        return "ANCRAGE introuvable. Re-press: FILE.ancrage.json."
    if err == "ancrage":
        return "pas ANCRAGE-v0."
    if err == "ancrage date":
        return "ANCRAGE: date illisible."
    if err == "ancrage perime":
        return "ANCRAGE périmé — à re-mesurer, pas faux."
    if rec.get("ok") and rec.get("ancrage") and rec.get("mesure"):
        if rec.get("legacy"):
            return "ANCRAGE tient. MESURE consommée. v1 n'inclut pas objet — resseller v2. Press n'ouvre pas la signature."
        return "ANCRAGE tient. MESURE consommée. Press n'ouvre pas la signature. Check le fait."
    if rec.get("ok") and rec.get("ancrage"):
        if rec.get("legacy"):
            return "ANCRAGE tient. v1 n'inclut pas objet — resseller v2. Press n'ouvre pas la signature."
        return "ANCRAGE tient. Press n'ouvre pas la signature. Check le fait."
    if rec.get("ok") and rec.get("mesure"):
        if rec.get("legacy"):
            return "MESURE consommée. v1 n'inclut pas objet — resseller v2. Press n'ouvre pas la signature."
        return "MESURE consommée. Press n'ouvre pas la signature. Check le fait."
    if rec.get("ok") and rec.get("legacy"):
        return "v1 n'inclut pas objet — resseller v2. Press n'ouvre pas la signature."
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


def _mesure_lock(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = path.with_suffix(path.suffix + ".lock")
    fh = open(lock_path, "a+", encoding="utf-8")
    if fcntl is not None:
        fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
    return fh


def _mesure_unlock(fh) -> None:
    if fcntl is not None:
        fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
    fh.close()


def consulter_mesure(path: Path) -> dict:
    """Spend one MESURE-v0 reading. Does not sign. Does not fork.

    Interop with mesure-protocol: consulter consomme. The card on disk
    stays MESURE-v0 (no extra keys). Press records the spend; it is not
    a seal and not a receipt.
    """
    fh = _mesure_lock(path)
    try:
        if not path.is_file():
            return habiller({"ok": False, "erreur": "mesure introuvable", "attendu": str(path)})
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return habiller({"ok": False, "erreur": "json"})
        if data.get("format") != MESURE_FORMAT:
            return habiller({"ok": False, "erreur": "mesure"})
        if data.get("detruit") or int(data.get("lectures", 0)) < 1:
            return habiller({"ok": False, "erreur": "mesure lectures"})
        data["lectures"] = int(data["lectures"]) - 1
        if data["lectures"] == 0:
            data["detruit"] = True
        allowed = ("format", "objet", "lectures", "sha256", "sha_sur", "detruit")
        carte = {k: data[k] for k in allowed if k in data}
        path.write_text(json.dumps(carte, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return {
            "format": carte.get("format"),
            "objet": carte.get("objet"),
            "lectures": carte.get("lectures"),
            "sha256": carte.get("sha256"),
            "sha_sur": carte.get("sha_sur"),
            "detruit": bool(carte.get("detruit")),
            "consomme": True,
        }
    finally:
        _mesure_unlock(fh)


def verifier_ancrage(path: Path, today: date | None = None) -> dict:
    """Read ANCRAGE-v0. Does not write. Does not sign.

    Interop with ancrage-protocol: verifier refuses a past date.
    Expired avant = à re-mesurer, not fake. A new date is a new act
    (ancrage.py ecrire), not this printer. Reculer in place is forbidden.
    """
    if not path.is_file():
        return habiller({"ok": False, "erreur": "ancrage introuvable", "attendu": str(path)})
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return habiller({"ok": False, "erreur": "json"})
    if data.get("format") != ANCRAGE_FORMAT:
        return habiller({"ok": False, "erreur": "ancrage"})
    avant = str(data.get("avant") or "")
    if not DATE_ANCRAGE.match(avant):
        return habiller({"ok": False, "erreur": "ancrage date"})
    y, m, d = map(int, avant.split("-"))
    try:
        day = date(y, m, d)
    except ValueError:
        return habiller({"ok": False, "erreur": "ancrage date"})
    now = today or date.today()
    if day <= now:
        return habiller({"ok": False, "erreur": "ancrage perime", "avant": avant})
    return {
        "format": ANCRAGE_FORMAT,
        "objet": data.get("objet"),
        "avant": avant,
        "verifie": True,
    }


def feuille(paquet: dict) -> dict:
    """Ids from a card. Does not open the signature. Does not hash a file."""
    if paquet.get("format") == TRAIL_FORMAT:
        return habiller({"ok": False, "erreur": "itinéraire"})
    fmt = paquet.get("format")
    if fmt not in FORMATS:
        return habiller({"ok": False, "erreur": "format"})
    objet = paquet.get("objet") or {}
    sha = objet.get("sha256") or ""
    return habiller(
        {
            "ok": True,
            "format": fmt,
            "legacy": fmt == FORMAT_V1,
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
    """A5 carte de poche HTML. Escapes every field. Does not verify.

    Share or print. Not a payment Wallet. Not a seal. Not a receipt.
    """
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
    mesure = rec.get("mesure") or {}
    if mesure.get("consomme"):
        etat = "detruit" if mesure.get("detruit") else f"lectures={mesure.get('lectures')}"
        rows.append(("mesure", f"MESURE-v0 consommée · {etat}"))
    ancrage = rec.get("ancrage") or {}
    if ancrage.get("verifie"):
        rows.append(
            (
                "ancrage",
                f"ANCRAGE-v0 · {ancrage.get('objet') or '—'} · avant {ancrage.get('avant')}",
            )
        )
    meta = "".join(
        f"<div><b>{html.escape(k)}</b> {html.escape(str(v if v not in (None, '') else '—'))}</div>"
        for k, v in rows
    )
    record = {k: rec[k] for k in rec}
    payload = html.escape(json.dumps(record, ensure_ascii=False, indent=2), quote=False)
    bandeau = ""
    if paquet.get("format") == FORMAT_V1:
        bandeau = "<p class='bandeau'>v1 n'inclut pas objet — resseller v2</p>"
    return (
        "<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'/>"
        f"<title>UNFORGE Press — {html.escape(str(nom))}</title>"
        f"<style>{CSS}</style></head><body>"
        f"<script type='application/json' id='unforge-press'>{payload}</script>"
        "<article class='card'>"
        "<div class='marque'>UNFORGE · PRESS</div>"
        f"<h1>{html.escape(str(nom))}</h1>"
        f"{bandeau}"
        f"<p class='fait'>{html.escape(fait)}</p>"
        "<div class='libelle'>objet sha256 — printed, not recomputed</div>"
        f"<div class='hex'>{html.escape(blocs_hex(str(sha)))}</div>"
        f"<div class='meta'>{meta}</div>"
        "<footer class='pied'>"
        "<p>Carte de poche. Share or print.</p>"
        "<p>Not a payment Wallet. Not a seal. Not a receipt.</p>"
        "<p>Verify the file with unforge-check. Stamps: unforge-trail.</p>"
        + (
            "<p>MESURE consommée. Consulter consomme. Not a receipt.</p>"
            if mesure.get("consomme")
            else ""
        )
        + (
            "<p>ANCRAGE tient. Périmé = re-mesurer, pas faux. Not a receipt.</p>"
            if ancrage.get("verifie")
            else ""
        )
        + "<p>The node stays yours. The attestation leaves.</p>"
        "</footer></article></body></html>"
    )


def imprimer(
    preuve: Path,
    dest: Path | None = None,
    mesure: Path | None = None,
    ancrage: Path | None = None,
    *,
    today: date | None = None,
) -> dict:
    """Read a card, write A5 carte de poche HTML, return the press.v0 record. Never signs.

    If ``mesure`` is set, spend one MESURE-v0 reading (kit presse / porte 8).
    Consulting consumes. Press does not open a measure. It does not fork one.

    If ``ancrage`` is set, verify an ANCRAGE-v0 date (re-press / portes 3+7).
    Read-only. Expired avant refuses the print — à re-mesurer, not fake.
    Press does not write a new date. A new act is ancrage-protocol ecrire.
    """
    paquet = json.loads(preuve.read_text(encoding="utf-8"))
    rec = feuille(paquet)
    if not rec.get("ok"):
        return rec
    if ancrage is not None:
        checked = verifier_ancrage(ancrage, today=today)
        if checked.get("ok") is False:
            return checked
        rec["ancrage"] = checked
        rec["phrase"] = phrase_press(rec)
    if mesure is not None:
        spent = consulter_mesure(mesure)
        if spent.get("ok") is False:
            return spent
        rec["mesure"] = spent
        rec["phrase"] = phrase_press(rec)
    cible = dest if dest is not None else dest_defaut(preuve)
    fh = _mesure_lock(cible)
    try:
        cible.write_text(html_carte(paquet, rec), encoding="utf-8")
        rec["html"] = str(cible)
        rec["phrase"] = phrase_press(rec)
        return rec
    finally:
        _mesure_unlock(fh)


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
            "UNFORGE Press — print a carte de poche (A5) from a .unforge.json. "
            "Share or print. Not a payment Wallet. Not a seal. Not a receipt. "
            "No node. No cloud. No coin. Does not open the signature."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "examples:\n"
            "  python3 press.py document.pdf.unforge.json\n"
            "  python3 press.py document.pdf\n"
            "  python3 press.py document.pdf.unforge.json -o /tmp/card.html\n"
            "  python3 press.py document.pdf.unforge.json --human\n"
            "  python3 press.py document.pdf.unforge.json --mesure\n"
            "  python3 press.py document.pdf.unforge.json --ancrage examples/billet.ancrage.json\n"
            "\n"
            "If a file is given, Press looks for FILE.unforge.json beside it.\n"
            "Kit presse (porte 8): --mesure spends one MESURE-v0 reading\n"
            "(sibling FILE.mesure.json, or a path). Consulting consumes.\n"
            "Re-press (portes 3+7): --ancrage verifies ANCRAGE-v0 (sibling\n"
            "FILE.ancrage.json, or a path). Read-only. Expired = re-measure,\n"
            "not fake. Press does not write a new date.\n"
            "Writes A5 carte de poche HTML. Not a payment Wallet.\n"
            "Machine record (press.v0) on stdout.\n"
            "Exit 0 = printed. Exit 1 = refuse. Exit 2 = unreadable.\n"
            "ok: true means the card is UNFORGE-PREUVE-v1 or v2 and HTML was written.\n"
            "v1 is printed with a banner: resseller v2. It is not a file match.\n"
            "It does not mean the file matches — that verdict is unforge-check.\n"
            "Agents: python3 press.py --schema   or   from press import imprimer"
        ),
    )
    p.add_argument(
        "preuve",
        nargs="?",
        help="card .unforge.json, or a file whose card sits beside it",
    )
    p.add_argument(
        "-o",
        "--out",
        help="destination HTML (default: FILE.press.html). Carte de poche, not a Wallet.",
    )
    p.add_argument(
        "--mesure",
        nargs="?",
        const="",
        default=None,
        help="consume a MESURE-v0 reading (sibling FILE.mesure.json, or a path). Not a receipt.",
    )
    p.add_argument(
        "--ancrage",
        nargs="?",
        const="",
        default=None,
        help=(
            "verify an ANCRAGE-v0 date (sibling FILE.ancrage.json, or a path). "
            "Expired = re-measure, not fake. Not a receipt."
        ),
    )
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
        mesure = None
        ancrage = None
        if args.mesure is not None:
            mesure = Path(args.mesure) if args.mesure else voisin_mesure(preuve)
        if args.ancrage is not None:
            ancrage = Path(args.ancrage) if args.ancrage else voisin_ancrage(preuve)
        rec = imprimer(preuve, dest, mesure, ancrage)
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
