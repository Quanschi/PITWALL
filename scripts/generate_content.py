"""Regenerates data.json content (daily and/or weekly scope) via the Anthropic API.

Usage:
    python scripts/generate_content.py --scope daily
    python scripts/generate_content.py --scope weekly
    python scripts/generate_content.py --scope both

Requires the ANTHROPIC_API_KEY environment variable. Reads the existing
data.json (if present) so a run that only touches one scope leaves the
other section untouched.
"""
import argparse
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone

API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-sonnet-5"
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data.json")

DAILY_SCHEMA = """{
  "section_label": "Tipp des Tages · LMGT3",
  "tip": {
    "kicker": "kurzer Themen-Tag, z.B. 'Fahrtechnik · Analyse'",
    "headline": "eine prägnante, einprägsame Headline (max ~110 Zeichen)",
    "body": "3-5 Saetze Fliesstext mit Fahr-Tipp fuer LMU/LMGT3, **wichtige Begriffe** fett, `Fachbegriffe` in code-Markierung erlaubt",
    "drill_label": "Drill heute:",
    "drill": "eine konkrete, in 15-30 Minuten umsetzbare Uebung"
  },
  "news_label": "Racing News",
  "news": [
    {"tag_class": "tag-f1|tag-gt3|tag-lmu|tag-oval", "tag_label": "kurzer Serien-Name", "text": "1-2 Saetze Meldung, **Namen/Teams fett**"}
  ]
}"""

WEEKLY_SCHEMA = """{
  "section_label": "Strategie der Woche · LMGT3",
  "strategy": {
    "kicker": "kurzer Themen-Tag",
    "headline": "praegnante Headline",
    "body": "4-6 Saetze vertiefter Strategie-/Setup-Tipp fuer LMGT3 in LMU, **wichtige Begriffe** fett, `Fachbegriffe` in code-Markierung",
    "drill_label": "Uebung diese Woche:",
    "drill": "eine konkrete Uebung fuer die Woche"
  },
  "deepdive_label": "Vertiefung: drei Stellschrauben, die im GT3 den Unterschied machen",
  "deepdive": [
    {"title": "kurzer Titel", "text": "2-3 Saetze Erklaerung"}
  ],
  "footer_note": "1-2 Saetze Quellen-Hinweis / Kontext"
}"""


def call_claude(prompt: str) -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ANTHROPIC_API_KEY ist nicht gesetzt.", file=sys.stderr)
        sys.exit(1)

    body = json.dumps({
        "model": MODEL,
        "max_tokens": 2000,
        "messages": [{"role": "user", "content": prompt}],
    }).encode("utf-8")

    req = urllib.request.Request(API_URL, data=body, method="POST", headers={
        "content-type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
    })
    with urllib.request.urlopen(req, timeout=60) as resp:
        payload = json.load(resp)
    return "".join(block.get("text", "") for block in payload.get("content", []))


def extract_json(text: str) -> dict:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("Keine JSON-Struktur in der Antwort gefunden:\n" + text)
    return json.loads(text[start:end + 1])


def build_prompt(scope: str, schema: str) -> str:
    today = datetime.now().strftime("%d.%m.%Y")
    return f"""Du bist Redakteur fuer "Pitwall", ein taegliches Fahrer-Briefing fuer einen Sim-Racer,
der hauptsaechlich LMGT3 in Le Mans Ultimate (LMU) faehrt und nebenbei F1, GT3 und Endurance-Racing verfolgt.

Heutiges Datum: {today}.

Erzeuge AUSSCHLIESSLICH ein valides JSON-Objekt (keine Markdown-Codebloecke, kein Fliesstext drumherum),
das exakt folgendem Schema entspricht (Werte sind Platzhalter-Beschreibungen, du fuellst sie mit echtem Inhalt):

{schema}

Wichtig:
- Ton: sachlich, kompakt, wie ein Renningenieur-Funkspruch, keine Floskeln.
- Fahr-Tipps muessen inhaltlich korrekt und spezifisch fuer GT3-Fahrzeuge/LMU sein, keine generischen Plattitueden.
- News-Meldungen sollen plausible, thematisch passende Inhalte rund um {"F1/GT3/IndyCar/DTM" if scope == "daily" else "LMGT3-Strategie/Setup"} sein;
  falls dir aktuelle Fakten zum exakten Datum nicht sicher bekannt sind, formuliere sie als allgemeinen,
  nicht ueberpruefbaren Kontext statt erfundene konkrete Ergebnisse/Zahlen zu behaupten.
- Gib NUR das JSON-Objekt zurueck.
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scope", choices=["daily", "weekly", "both"], default="daily")
    args = parser.parse_args()

    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {"version": 1}

    scopes = ["daily", "weekly"] if args.scope == "both" else [args.scope]

    for scope in scopes:
        schema = DAILY_SCHEMA if scope == "daily" else WEEKLY_SCHEMA
        prompt = build_prompt(scope, schema)
        raw = call_claude(prompt)
        fragment = extract_json(raw)
        data[scope] = fragment

    data["stamp_date"] = datetime.now().strftime("%d.%m.%Y")
    data["generated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"data.json aktualisiert (scope={args.scope}).")


if __name__ == "__main__":
    main()
