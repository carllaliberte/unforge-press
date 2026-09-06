#!/usr/bin/env python3
"""Public print tests. Never issue. Never invent a valid signature."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from press import (  # noqa: E402
    SCHEMA_ID,
    blocs_hex,
    consulter_mesure,
    dest_defaut,
    feuille,
    habiller,
    html_carte,
    imprimer,
    ligne_humaine,
    phrase_press,
    resoudre,
    schema,
    verifier_ancrage,
    voisin_ancrage,
    voisin_carte,
    voisin_mesure,
)

CARTE = ROOT / "examples" / "bienvenue.txt.unforge.json"
MESURE = ROOT / "examples" / "bienvenue.txt.mesure.json"
BILLET = ROOT / "examples" / "billet.ancrage.json"
GARANTIE = ROOT / "examples" / "garantie.ancrage.json"
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
        self.assertTrue(rec.get("legacy"))
        self.assertIn("resseller v2", rec["phrase"])
        self.assertNotIn("signature", rec)
        self.assertNotIn("VERT", rec["phrase"])

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
        self.assertEqual(rec["phrase"], "pas UNFORGE-PREUVE-v1/v2.")

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



    def test_v2_pas_erreur_format(self):
        p = _paquet()
        p["format"] = "UNFORGE-PREUVE-v2"
        rec = feuille(p)
        self.assertTrue(rec["ok"])
        self.assertNotEqual(rec.get("erreur"), "format")
        self.assertFalse(rec.get("legacy"))
        self.assertEqual(rec["format"], "UNFORGE-PREUVE-v2")
        self.assertNotIn("VERT", rec["phrase"])


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


    def test_v1_bandeau(self):
        page = html_carte(_paquet())
        self.assertIn("resseller v2", page)

    def test_v2_sans_bandeau(self):
        p = _paquet()
        p["format"] = "UNFORGE-PREUVE-v2"
        page = html_carte(p)
        self.assertNotIn("resseller v2", page)

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


    def test_v2_cli_exit_0(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "out.html"
            card = Path(tmp) / "x.unforge.json"
            p = _paquet()
            p["format"] = "UNFORGE-PREUVE-v2"
            card.write_text(json.dumps(p), encoding="utf-8")
            r = _run([str(card), "-o", str(dest)])
        self.assertEqual(r.returncode, 0, r.stderr)
        rec = json.loads(r.stdout)
        self.assertTrue(rec["ok"])
        self.assertNotEqual(rec.get("erreur"), "format")
        self.assertFalse(rec.get("legacy"))

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



    def test_une_ligne_readme_et_imprime(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("python3 press.py examples/bienvenue.txt.unforge.json", readme)
        self.assertIn("--mesure", readme)
        self.assertIn("--ancrage", readme)
        self.assertIn("IMPRIMÉ", readme)
        self.assertIn("REFUS", readme)
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "out.html"
            rec = imprimer(CARTE, dest)
            self.assertTrue(rec["ok"])
            page = dest.read_text(encoding="utf-8")
            self.assertIn("resseller v2", page)

class Readme(unittest.TestCase):
    def test_n_est_pas_le_contrat_juge(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertNotIn("juge.v0.json", text)
        self.assertNotRegex(text, r"(?i)contrat\s*:?\s*\S*juge\.v0")
        self.assertIn("press.v0", text)
        self.assertIn("--schema", text)

    def test_interdit_ne_signe_pas(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("Unforge ne signe pas", text)
        self.assertNotIn("ne signe pas /", text)
        self.assertNotRegex(text, r"(?i)unforge signs")
        self.assertNotRegex(text, r"(?i)press signs")
        self.assertNotRegex(text, r"(?i)invent(ed|e|er)?\s+(a\s+)?(valid\s+)?signature")


class Mesure(unittest.TestCase):
    def _copie(self, tmp: str) -> Path:
        dest = Path(tmp) / "bienvenue.txt.mesure.json"
        dest.write_text(MESURE.read_text(encoding="utf-8"), encoding="utf-8")
        return dest

    def test_voisin(self):
        self.assertEqual(voisin_mesure(CARTE), MESURE)
        self.assertEqual(voisin_mesure(MESURE), MESURE)

    def test_consulter_consomme(self):
        with tempfile.TemporaryDirectory() as tmp:
            carte = self._copie(tmp)
            dest = Path(tmp) / "kit.html"
            rec = imprimer(CARTE, dest, carte)
            self.assertTrue(rec["ok"])
            self.assertTrue(rec["mesure"]["consomme"])
            self.assertEqual(rec["mesure"]["lectures"], 0)
            self.assertTrue(rec["mesure"]["detruit"])
            self.assertEqual(
                rec["mesure"]["sha256"],
                "e8fe730c49dc859358e3b94376fb0a5f0916aca21b18457eb3d8391c4ebc0838",
            )
            self.assertIn("MESURE consommée", rec["phrase"])
            self.assertNotIn("VERT", rec["phrase"])
            page = dest.read_text(encoding="utf-8")
            self.assertIn("MESURE consommée", page)
            self.assertIn("Not a receipt", page)
            self.assertIn("Not a seal", page)
            self.assertNotIn("VERT", page)
            payload = page.split("id='unforge-press'>", 1)[1].split("</script>", 1)[0]
            embedded = json.loads(payload)
            self.assertTrue(embedded["mesure"]["consomme"])
            self.assertNotIn("signature", embedded)
            disk = json.loads(carte.read_text(encoding="utf-8"))
            self.assertEqual(disk["lectures"], 0)
            self.assertTrue(disk["detruit"])
            self.assertNotIn("consomme", disk)
            self.assertEqual(disk["format"], "MESURE-v0")
            again = consulter_mesure(carte)
            self.assertFalse(again["ok"])
            self.assertEqual(again["erreur"], "mesure lectures")

    def test_fixture_reste_ouverte(self):
        raw = json.loads(MESURE.read_text(encoding="utf-8"))
        self.assertEqual(raw["format"], "MESURE-v0")
        self.assertEqual(raw["lectures"], 1)
        self.assertFalse(raw["detruit"])
        self.assertEqual(raw["sha_sur"], "fichier")
        self.assertEqual(FICHIER.stat().st_size, 92)
        self.assertEqual(raw["sha256"], _paquet()["objet"]["sha256"])

    def test_sans_mesure_n_invente_pas(self):
        rec = feuille(_paquet())
        self.assertNotIn("mesure", rec)
        page = html_carte(_paquet())
        self.assertNotIn("MESURE consommée", page)

    def test_refuse_detruit(self):
        with tempfile.TemporaryDirectory() as tmp:
            carte = Path(tmp) / "x.mesure.json"
            carte.write_text(
                json.dumps(
                    {
                        "format": "MESURE-v0",
                        "objet": "bienvenue.txt",
                        "lectures": 0,
                        "sha256": "e8fe730c49dc859358e3b94376fb0a5f0916aca21b18457eb3d8391c4ebc0838",
                        "sha_sur": "fichier",
                        "detruit": True,
                    }
                ),
                encoding="utf-8",
            )
            dest = Path(tmp) / "kit.html"
            rec = imprimer(CARTE, dest, carte)
            self.assertFalse(rec["ok"])
            self.assertEqual(rec["erreur"], "mesure lectures")
            self.assertFalse(dest.exists())

    def test_refuse_mauvais_format(self):
        with tempfile.TemporaryDirectory() as tmp:
            carte = Path(tmp) / "x.mesure.json"
            carte.write_text(json.dumps({"format": "NON", "lectures": 1}), encoding="utf-8")
            rec = imprimer(CARTE, Path(tmp) / "kit.html", carte)
            self.assertFalse(rec["ok"])
            self.assertEqual(rec["erreur"], "mesure")

    def test_cli_mesure(self):
        with tempfile.TemporaryDirectory() as tmp:
            carte = self._copie(tmp)
            dest = Path(tmp) / "out.html"
            r = _run([str(CARTE), "-o", str(dest), "--mesure", str(carte)])
            self.assertEqual(r.returncode, 0, r.stderr)
            rec = json.loads(r.stdout)
            self.assertTrue(rec["ok"])
            self.assertTrue(rec["mesure"]["consomme"])
            self.assertIn("MESURE consommée", rec["phrase"])
            self.assertNotIn("VERT", r.stdout)

    def test_cli_mesure_voisin(self):
        with tempfile.TemporaryDirectory() as tmp:
            card = Path(tmp) / "bienvenue.txt.unforge.json"
            card.write_text(CARTE.read_text(encoding="utf-8"), encoding="utf-8")
            (Path(tmp) / "bienvenue.txt.mesure.json").write_text(
                MESURE.read_text(encoding="utf-8"), encoding="utf-8"
            )
            dest = Path(tmp) / "out.html"
            r = _run([str(card), "-o", str(dest), "--mesure"])
            self.assertEqual(r.returncode, 0, r.stderr)
            rec = json.loads(r.stdout)
            self.assertTrue(rec["mesure"]["consomme"])

    def test_cli_mesure_absente(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "out.html"
            r = _run([str(CARTE), "-o", str(dest), "--mesure", str(Path(tmp) / "nope.mesure.json")])
            self.assertEqual(r.returncode, 1, r.stderr)
            rec = json.loads(r.stdout)
            self.assertFalse(rec["ok"])
            self.assertEqual(rec["erreur"], "mesure introuvable")
            self.assertFalse(dest.exists())


class Ancrage(unittest.TestCase):
    def test_voisin(self):
        self.assertEqual(
            voisin_ancrage(CARTE),
            ROOT / "examples" / "bienvenue.txt.ancrage.json",
        )
        self.assertEqual(voisin_ancrage(BILLET), BILLET)

    def test_verifier_billet_et_garantie(self):
        for carte, objet in ((BILLET, "billet"), (GARANTIE, "garantie")):
            before = carte.read_text(encoding="utf-8")
            with tempfile.TemporaryDirectory() as tmp:
                dest = Path(tmp) / f"{objet}.html"
                rec = imprimer(CARTE, dest, ancrage=carte)
                self.assertTrue(rec["ok"])
                self.assertTrue(rec["ancrage"]["verifie"])
                self.assertEqual(rec["ancrage"]["objet"], objet)
                self.assertEqual(rec["ancrage"]["avant"], "2028-08-31")
                self.assertEqual(rec["ancrage"]["format"], "ANCRAGE-v0")
                self.assertIn("ANCRAGE tient", rec["phrase"])
                self.assertNotIn("VERT", rec["phrase"])
                page = dest.read_text(encoding="utf-8")
                self.assertIn("ANCRAGE tient", page)
                self.assertIn("re-mesurer", page)
                self.assertIn(objet, page)
                self.assertIn("2028-08-31", page)
                self.assertIn("Not a receipt", page)
                self.assertIn("Not a seal", page)
                self.assertNotIn("VERT", page)
                payload = page.split("id='unforge-press'>", 1)[1].split("</script>", 1)[0]
                embedded = json.loads(payload)
                self.assertTrue(embedded["ancrage"]["verifie"])
                self.assertNotIn("signature", embedded)
            disk = json.loads(carte.read_text(encoding="utf-8"))
            self.assertEqual(disk["format"], "ANCRAGE-v0")
            self.assertEqual(disk["objet"], objet)
            self.assertEqual(disk["avant"], "2028-08-31")
            self.assertNotIn("verifie", disk)
            self.assertEqual(carte.read_text(encoding="utf-8"), before)

    def test_fixture_n_est_pas_ecrite(self):
        for carte, objet in ((BILLET, "billet"), (GARANTIE, "garantie")):
            raw = json.loads(carte.read_text(encoding="utf-8"))
            self.assertEqual(raw["format"], "ANCRAGE-v0")
            self.assertEqual(raw["objet"], objet)
            self.assertEqual(raw["avant"], "2028-08-31")
            self.assertNotIn("verifie", raw)
            again = verifier_ancrage(carte, today=date(2026, 9, 6))
            self.assertTrue(again.get("verifie"))
            self.assertEqual(json.loads(carte.read_text(encoding="utf-8")), raw)

    def test_sans_ancrage_n_invente_pas(self):
        rec = feuille(_paquet())
        self.assertNotIn("ancrage", rec)
        page = html_carte(_paquet())
        self.assertNotIn("ANCRAGE tient", page)

    def test_refuse_perime(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "no.html"
            rec = imprimer(CARTE, dest, ancrage=BILLET, today=date(2028, 8, 31))
            self.assertFalse(rec["ok"])
            self.assertEqual(rec["erreur"], "ancrage perime")
            self.assertIn("re-mesurer", rec["phrase"])
            self.assertIn("pas faux", rec["phrase"])
            self.assertNotIn("VERT", rec["phrase"])
            self.assertFalse(dest.exists())
            raw = json.loads(BILLET.read_text(encoding="utf-8"))
            self.assertEqual(raw["avant"], "2028-08-31")
            self.assertNotIn("verifie", raw)

    def test_refuse_date_passee_sur_disque(self):
        with tempfile.TemporaryDirectory() as tmp:
            carte = Path(tmp) / "expire.ancrage.json"
            carte.write_text(
                json.dumps(
                    {"format": "ANCRAGE-v0", "objet": "billet", "avant": "2020-01-01"}
                ),
                encoding="utf-8",
            )
            dest = Path(tmp) / "no.html"
            rec = imprimer(CARTE, dest, ancrage=carte)
            self.assertFalse(rec["ok"])
            self.assertEqual(rec["erreur"], "ancrage perime")
            self.assertFalse(dest.exists())
            self.assertEqual(json.loads(carte.read_text(encoding="utf-8"))["avant"], "2020-01-01")

    def test_refuse_mauvais_format(self):
        with tempfile.TemporaryDirectory() as tmp:
            carte = Path(tmp) / "x.ancrage.json"
            carte.write_text(json.dumps({"format": "NON", "avant": "2028-08-31"}), encoding="utf-8")
            rec = imprimer(CARTE, Path(tmp) / "out.html", ancrage=carte)
            self.assertFalse(rec["ok"])
            self.assertEqual(rec["erreur"], "ancrage")

    def test_refuse_date_illisible(self):
        with tempfile.TemporaryDirectory() as tmp:
            carte = Path(tmp) / "x.ancrage.json"
            carte.write_text(
                json.dumps({"format": "ANCRAGE-v0", "objet": "billet", "avant": "demain"}),
                encoding="utf-8",
            )
            rec = imprimer(CARTE, Path(tmp) / "out.html", ancrage=carte)
            self.assertFalse(rec["ok"])
            self.assertEqual(rec["erreur"], "ancrage date")

    def test_cli_billet(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "out.html"
            r = _run([str(CARTE), "-o", str(dest), "--ancrage", str(BILLET)])
            self.assertEqual(r.returncode, 0, r.stderr)
            rec = json.loads(r.stdout)
            self.assertTrue(rec["ok"])
            self.assertTrue(rec["ancrage"]["verifie"])
            self.assertEqual(rec["ancrage"]["objet"], "billet")
            self.assertIn("ANCRAGE tient", rec["phrase"])
            self.assertNotIn("VERT", r.stdout)

    def test_cli_garantie(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "out.html"
            r = _run([str(CARTE), "-o", str(dest), "--ancrage", str(GARANTIE)])
            self.assertEqual(r.returncode, 0, r.stderr)
            rec = json.loads(r.stdout)
            self.assertEqual(rec["ancrage"]["objet"], "garantie")

    def test_cli_voisin(self):
        with tempfile.TemporaryDirectory() as tmp:
            card = Path(tmp) / "bienvenue.txt.unforge.json"
            card.write_text(CARTE.read_text(encoding="utf-8"), encoding="utf-8")
            (Path(tmp) / "bienvenue.txt.ancrage.json").write_text(
                BILLET.read_text(encoding="utf-8"), encoding="utf-8"
            )
            dest = Path(tmp) / "out.html"
            r = _run([str(card), "-o", str(dest), "--ancrage"])
            self.assertEqual(r.returncode, 0, r.stderr)
            rec = json.loads(r.stdout)
            self.assertTrue(rec["ancrage"]["verifie"])
            self.assertEqual(rec["ancrage"]["objet"], "billet")

    def test_cli_perime(self):
        with tempfile.TemporaryDirectory() as tmp:
            carte = Path(tmp) / "expire.ancrage.json"
            carte.write_text(
                json.dumps(
                    {"format": "ANCRAGE-v0", "objet": "garantie", "avant": "2020-01-01"}
                ),
                encoding="utf-8",
            )
            dest = Path(tmp) / "out.html"
            r = _run([str(CARTE), "-o", str(dest), "--ancrage", str(carte)])
            self.assertEqual(r.returncode, 1, r.stderr)
            rec = json.loads(r.stdout)
            self.assertFalse(rec["ok"])
            self.assertEqual(rec["erreur"], "ancrage perime")
            self.assertIn("re-mesurer", rec["phrase"])
            self.assertNotIn("VERT", r.stdout)
            self.assertFalse(dest.exists())

    def test_cli_absent(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "out.html"
            r = _run([str(CARTE), "-o", str(dest), "--ancrage", str(Path(tmp) / "nope.ancrage.json")])
            self.assertEqual(r.returncode, 1, r.stderr)
            rec = json.loads(r.stdout)
            self.assertFalse(rec["ok"])
            self.assertEqual(rec["erreur"], "ancrage introuvable")
            self.assertFalse(dest.exists())


class Juge(unittest.TestCase):
    def test_n_est_pas_le_contrat_juge(self):
        text = (ROOT / "JUGE.md").read_text(encoding="utf-8")
        self.assertNotIn("juge.v0.json", text)
        self.assertNotRegex(text, r"(?i)contrat\s*:?\s*\S*juge\.v0")
        self.assertIn("press.v0", text)
        self.assertIn("--schema", text)
        self.assertIn("printer", text.lower())
        self.assertIn("not a juge", text.lower())

    def test_interdit_ne_signe_pas(self):
        text = (ROOT / "JUGE.md").read_text(encoding="utf-8")
        self.assertIn("Unforge ne signe pas", text)
        self.assertNotIn("ne signe pas /", text)
        self.assertIn("PREVIEW ≠ quittance", text)
        self.assertIn("MESURE consommée ≠ quittance", text)
        self.assertIn("ANCRAGE périmé ≠ faux", text)


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
