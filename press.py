#!/usr/bin/env python3
"""UNFORGE Press — printable A5 card from a .unforge.json."""
from __future__ import annotations
import argparse, html, json
from pathlib import Path
CSS = "@page{size:A5 portrait;margin:14mm}body{font-family:Palatino,Georgia,serif;color:#111;margin:0}.card{border:2px solid #111;min-height:180mm;padding:12mm 10mm}.marque{letter-spacing:.35em;font-size:11px;text-transform:uppercase}h1{font-size:22px;font-weight:600}.hex,.meta{font-family:ui-monospace,Menlo,monospace}.hex{letter-spacing:.08em;font-size:13px}.meta{font-size:10px}.pied{font-size:11px;color:#333}"
def carte(paquet):
    objet = paquet.get("objet") or {}
    nom = objet.get("nom") or paquet.get("id") or "preuve"
    fait = (paquet.get("fait") or "").split("\n")[0]
    sha = objet.get("sha256") or paquet.get("empreinte") or ""
    blocs = " ".join(sha[i:i+8] for i in range(0, min(len(sha),64), 8))
    rows = [("id", paquet.get("id")), ("card", paquet.get("card_id")), ("token", paquet.get("token_id")), ("when", paquet.get("created_at")), ("file", nom)]
    meta = "".join(f"<div><b>{html.escape(k)}</b> {html.escape(str(v or '—'))}</div>" for k,v in rows)
    return f"<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'/><title>UNFORGE Press</title><style>{CSS}</style></head><body><article class='card'><div class='marque'>UNFORGE · PRESS</div><h1>{html.escape(nom)}</h1><p>{html.escape(fait)}</p><div class='hex'>{html.escape(blocs)}</div><div class='meta'>{meta}</div><p class='pied'>The node stays yours. The attestation leaves.</p></article></body></html>"
def main():
    p = argparse.ArgumentParser(); p.add_argument("preuve"); p.add_argument("-o","--out")
    a = p.parse_args(); src = Path(a.preuve); paquet = json.loads(src.read_text(encoding="utf-8"))
    dest = Path(a.out) if a.out else src.with_suffix(".press.html")
    dest.write_text(carte(paquet), encoding="utf-8"); print(dest); return 0
if __name__ == "__main__":
    raise SystemExit(main())
