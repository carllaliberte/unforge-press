#!/usr/bin/env python3
"""Public print tests. Never issue. Never invent a valid signature."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from press import (  # noqa: E402
    SCHEMA_ID,
    blocs_hex,
    dest_defaut,
    feuille,
    habiller,
    html_carte,
    imprimer,
    ligne_humaine,
    phrase_press,
    resoudre,
    schema,
    voisin_carte,
)

CARTE = ROOT / "examples" / "bienvenue.txt.unforge.json"
FICHIER = ROOT / "examples" / "bienvenue.txt"
PY = sys.executable


def _run(args: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run(
        [PY, str(ROOT / "press.py"), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        **kw,
    )


def _paquet() -> dict:
    return json.loads(CARTE.read_text(encoding="utf-8"))


class Feuille(unittest.TestCase):
    def test_carte_demo(self):
        rec = feuille(_paquet())
        self.assertTrue(rec["ok"])
        self.assertEqual(rec["geste"], "press")
        self.assertEqual(rec["schema"], SCHEMA_ID)
        self.assertEqual(rec["noeud"], "non requis")
        self.assertEqual(rec["id"], "QT-PR-DEMO0001")
        self.assertEqual(rec["card_id"], "QT-EM-DEMO0001")
        self.assertEqual(rec["token_id"], "QT-JK-DEMO0001")
        self.assertEqual(rec["objet"], "bienvenue.txt")
        self.assertEqual(rec["sha256"], "e8fe730c49dc859358e3b94376fb0a5f0916aca21b18457eb3d8391c4ebc0838")
        self.assertEqual(rec["empreinte"], "985d3ff3389f8c64c87eeb829ccebf4ae09b943fd3500e442614b1e1731498e5")
        self.assertEqual(rec["fait"], "fichier d'accueil UNFORGE")
        self.assertEqual(rec["phrase"], "Press n'ouvre pas la signature. Check le fait.")
        self.assertNotIn("signature", rec)

    def test_n_ouvre_pas_une_empreinte_cassée(self):
        p = _paquet()
        p["empreinte"] = "0" * 64
        rec = feuille(p)
        self.assertTrue(rec["ok"], "press prints ids; check refuses a broken fingerprint")
        self.assertEqual(rec["empreinte"], "0" * 64)
        self.assertNotIn("empreinte_ok", rec)
        self.assertNotIn("signature_ok", rec)

    def test_n_ouvre_pas_une_signature_cassée(self):
        p = _paquet()
        p["signature"] = "A" * len(p["signature"])
        rec = feuille(p)
        self.assertTrue(rec["ok"], "press does not open the signature")
        self.assertNotIn("signature", rec)

    def test_mauvais_format(self):
        rec = feuille({"format": "NON"})
        self.assertFalse(rec["ok"])
        self.assertEqual(rec["erreur"], "format")
        self.assertEqual(rec["phrase"], "pas UNFORGE-PREUVE-v1.")

    def test_itinéraire_n_est_pas_une_carte(self):
        rec = feuille(
            {
                "format": "UNFORGE-TRAIL-v1",
                "etapes": [{"geste": "créé", "preuve": "bienvenue.txt.unforge.json"}],
            }
        )
        self.assertFalse(rec["ok"])
        self.assertEqual(rec["erreur"], "itinéraire")
        self.assertIn("itinéraire", rec["phrase"])
        self.assertIn(".unforge.json", rec["phrase"])


class Html(unittest.TestCase):
    def test_échappe(self):
        p = {
            "format": "UNFORGE-PREUVE-v1",
            "id": "<script>alert(1)</script>",
            "card_id": "QT-EM-X",
            "fait": "<b>xss</b>",
            "objet": {"nom": "a\"b.txt", "sha256": "ab" * 32},
        }
        page = html_carte(p)
        self.assertNotIn("<script>alert(1)</script>", page)
        self.assertNotIn("<b>xss</b>", page)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", page)
        self.assertIn("&lt;b&gt;xss&lt;/b&gt;", page)
        self.assertIn("application/json", page)
        self.assertIn("id='unforge-press'", page)
        self.assertIn("Not a seal", page)
        self.assertNotIn("VERT", page)
        self.assertNotIn("#39ff88", page)
        self.assertNotIn("quantique", page.lower())

    def test_blocs_hex(self):
        self.assertEqual(blocs_hex("e8fe730c49dc8593"), "e8fe730c 49dc8593")
        self.assertEqual(blocs_hex(""), "")


class Imprimer(unittest.TestCase):
    def test_écrit_html(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "carte.html"
            rec = imprimer(CARTE, dest)
            self.assertTrue(rec["ok"])
            self.assertEqual(rec["html"], str(dest))
            page = dest.read_text(encoding="utf-8")
        self.assertIn("QT-PR-DEMO0001", page)
        self.assertIn("QT-EM-DEMO0001", page)
        self.assertIn("e8fe730c", page)
        self.assertIn("bienvenue.txt", page)
        self.assertIn("unforge-check", page)
        self.assertIn("unforge-trail", page)
        payload = page.split("id='unforge-press'>", 1)[1].split("</script>", 1)[0]
        embedded = json.loads(payload)
        self.assertEqual(embedded["geste"], "press")
        self.assertTrue(embedded["ok"])
        self.assertNotIn("signature", embedded)

    def test_dest_defaut(self):
        self.assertEqual(
            dest_defaut(Path("doc.pdf.unforge.json")).name,
            "doc.pdf.press.html",
        )
        self.assertEqual(voisin_carte(FICHIER), CARTE)
        self.assertEqual(resoudre(FICHIER), CARTE)
        self.assertEqual(resoudre(CARTE), CARTE)
        with self.assertRaises(FileNotFoundError):
            resoudre(ROOT / "README.md")


class SchemaEtHabit(unittest.TestCase):
    def test_schema_fichier(self):
        s = schema()
        self.assertEqual(s["title"], "unforge.press.v0")
        self.assertIn("ok", s["required"])
        self.assertIn("geste", s["required"])
        self.assertIn("not a match", s["description"].lower())

    def test_habiller_erreur(self):
        rec = habiller({"ok": False, "erreur": "json"})
        self.assertEqual(rec["geste"], "press")
        self.assertEqual(phrase_press(rec), "JSON illisible.")

    def test_humain_n_est_pas_vert(self):
        rec = feuille(_paquet())
        rec["html"] = "x.press.html"
        ligne = ligne_humaine(rec)
        self.assertIn("IMPRIMÉ", ligne)
        self.assertNotIn("VERT", ligne)
        self.assertNotIn("ROUGE", ligne)


class CLI(unittest.TestCase):
    def test_carte_exit_0(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "out.html"
            r = _run([str(CARTE), "-o", str(dest)])
            self.assertEqual(r.returncode, 0, r.stderr)
            rec = json.loads(r.stdout)
            self.assertTrue(rec["ok"])
            self.assertEqual(rec["geste"], "press")
            self.assertEqual(rec["schema"], SCHEMA_ID)
            self.assertTrue(dest.is_file())

    def test_voisin_une_commande(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "out.html"
            r = _run([str(FICHIER), "-o", str(dest)])
        self.assertEqual(r.returncode, 0, r.stderr)
        rec = json.loads(r.stdout)
        self.assertTrue(rec["ok"])
        self.assertEqual(rec["objet"], "bienvenue.txt")

    def test_human(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "out.html"
            r = _run([str(CARTE), "-o", str(dest), "--human"])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("IMPRIMÉ", r.stdout)
        self.assertIn("bienvenue.txt", r.stdout)
        self.assertNotIn("VERT", r.stdout)
        self.assertNotIn("{", r.stdout)

    def test_schema_flag(self):
        r = _run(["--schema"])
        self.assertEqual(r.returncode, 0, r.stderr)
        rec = json.loads(r.stdout)
        self.assertEqual(rec["title"], "unforge.press.v0")

    def test_sans_args(self):
        r = _run([])
        self.assertEqual(r.returncode, 2)
        self.assertIn(".unforge.json", r.stderr)

    def test_format_exit_1(self):
        with tempfile.TemporaryDirectory() as tmp:
            faux = Path(tmp) / "x.unforge.json"
            faux.write_text(json.dumps({"format": "NON"}), encoding="utf-8")
            r = _run([str(faux)])
        self.assertEqual(r.returncode, 1)
        rec = json.loads(r.stdout)
        self.assertFalse(rec["ok"])
        self.assertEqual(rec["erreur"], "format")

    def test_itinéraire_exit_1(self):
        with tempfile.TemporaryDirectory() as tmp:
            trail = Path(tmp) / "x.unforge-trail.json"
            trail.write_text(
                json.dumps({"format": "UNFORGE-TRAIL-v1", "etapes": []}),
                encoding="utf-8",
            )
            r = _run([str(trail)])
        self.assertEqual(r.returncode, 1)
        rec = json.loads(r.stdout)
        self.assertEqual(rec["erreur"], "itinéraire")

    def test_carte_absente(self):
        with tempfile.TemporaryDirectory() as tmp:
            seul = Path(tmp) / "orphelin.txt"
            seul.write_text("x", encoding="utf-8")
            r = _run([str(seul)])
        self.assertEqual(r.returncode, 2)
        rec = json.loads(r.stdout)
        self.assertEqual(rec["erreur"], "preuve introuvable")

    def test_json_illisible(self):
        with tempfile.TemporaryDirectory() as tmp:
            mauvais = Path(tmp) / "x.unforge.json"
            mauvais.write_text("{", encoding="utf-8")
            r = _run([str(mauvais)])
        self.assertEqual(r.returncode, 2)
        rec = json.loads(r.stdout)
        self.assertEqual(rec["erreur"], "json")


class InteropCarte(unittest.TestCase):
    def test_demo_a_les_clefs_check_et_trail(self):
        p = _paquet()
        for cle in (
            "format",
            "marque",
            "id",
            "card_id",
            "card_public",
            "token_id",
            "empreinte",
            "signature",
            "fait",
            "created_at",
        ):
            self.assertIn(cle, p)
        self.assertEqual(p["format"], "UNFORGE-PREUVE-v1")
        self.assertEqual(p["objet"]["sha256"], "e8fe730c49dc859358e3b94376fb0a5f0916aca21b18457eb3d8391c4ebc0838")
        self.assertEqual(FICHIER.stat().st_size, 92)
        self.assertEqual(p["objet"]["octets"], 92)


if __name__ == "__main__":
    unittest.main()
