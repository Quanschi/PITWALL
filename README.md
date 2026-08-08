# Pitwall

LMU GT3 / F1 / Endurance Fahrer-Briefing als installierbare PWA (Windows + Android), Inhalte aus `data.json`,
automatisch aktualisiert per GitHub Actions + Anthropic API.

## Struktur

- `index.html` — die App selbst (Design unveraendert, laedt Inhalte aus `data.json`)
- `data.json` — alle Texte (Daily-Tipp, News, Weekly-Strategie, Deep-Dive). Wird automatisch ueberschrieben.
- `manifest.json`, `sw.js`, `icons/` — PWA-Grundlagen (installierbar, Offline-Fallback auf den letzten Stand)
- `scripts/generate_content.py` — ruft die Anthropic API auf und schreibt `data.json` neu
- `.github/workflows/update-content.yml` — Zeitplan: taeglich (Daily-Tab) + montags (Weekly-Tab)

## Einmaliges Setup

### 1. API-Key hinterlegen
Repo auf GitHub -> **Settings -> Secrets and variables -> Actions -> New repository secret**
- Name: `ANTHROPIC_API_KEY`
- Value: dein Anthropic-API-Key ([console.anthropic.com](https://console.anthropic.com))

### 2. Workflow-Schreibrechte pruefen
**Settings -> Actions -> General -> Workflow permissions** -> "Read and write permissions" auswaehlen und speichern.
(Ohne das kann der Workflow `data.json` nicht zurueck ins Repo committen.)

### 3. GitHub Pages aktivieren
**Settings -> Pages -> Source** -> "Deploy from a branch" -> Branch `main`, Ordner `/ (root)` -> Save.
Nach ein bis zwei Minuten ist die Seite erreichbar unter `https://quanschi.github.io/PITWALL/`.

### 4. Als App installieren
- **Windows (Edge/Chrome):** Seite oeffnen -> Adresszeile -> "App installieren" (oder Menue -> Apps -> Diese Seite installieren)
- **Android (Chrome):** Seite oeffnen -> Menue (drei Punkte) -> "App installieren" / "Zum Startbildschirm hinzufuegen"

Danach erscheint Pitwall als eigenstaendige App mit eigenem Icon, ganz ohne Browser-Leiste.

## Wie die Automatisierung laeuft

- Jeden Tag ~07:00 (Europe/Berlin) generiert der Workflow einen neuen Daily-Tipp + News.
- Jeden Montag ~07:15 zusaetzlich die Weekly-Strategie + Deep-Dive.
- Ergebnis wird als `data.json` committet. Beim naechsten Oeffnen der App ist der Inhalt sofort aktuell.
- Manuell anstossen: Repo -> **Actions -> Update Pitwall Content -> Run workflow** (Scope waehlbar: daily/weekly/both).

## Wichtige Einschraenkung

Das Modell generiert Inhalte aus seinem Trainingswissen — es hat **keinen Echtzeit-Zugriff auf aktuelle
Rennergebnisse**. Der Prompt ist bewusst so formuliert, dass er bei unsicheren Fakten auf allgemeinen,
nicht ueberpruefbaren Kontext statt erfundener Ergebnisse/Zahlen ausweicht. Fuer echte Live-News (Ergebnisse,
Startlisten etc.) muesste zusaetzlich eine Sport-News-API oder eine web-suchfaehige API-Anbindung eingebaut
werden — sag Bescheid, falls das gewuenscht ist.

## Lokal testen

Browser kann `data.json` per `fetch()` aus Sicherheitsgruenden nicht von `file://` laden. Lokal daher mit
einem einfachen HTTP-Server testen:

```bash
python -m http.server 8000
```

Dann `http://localhost:8000` oeffnen.

## Manuell Inhalte aktualisieren (ohne Automatisierung)

```bash
set ANTHROPIC_API_KEY=dein-key
python scripts/generate_content.py --scope both
```

Danach `data.json` committen und pushen (oder GitHub Pages baut automatisch neu, sobald es im `main`-Branch liegt).
