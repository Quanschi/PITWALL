# Setup & Betrieb

## Struktur

- `index.html` — die App selbst (laedt Inhalte aus `data.json`)
- `data.json` — alle Texte (Daily-Tipp, News, Weekly-Strategie, Deep-Dive). Wird automatisch ueberschrieben.
- `manifest.json`, `sw.js`, `icons/` — PWA-Grundlagen (installierbar, Offline-Fallback auf den letzten Stand)
- `scripts/generate_content.py` — ruft die Gemini API auf und schreibt `data.json` neu
- `.github/workflows/update-content.yml` — Zeitplan: taeglich (Daily-Tab) + montags (Weekly-Tab)

## Einmaliges Setup

### 1. Kostenlosen API-Key holen
[aistudio.google.com/apikey](https://aistudio.google.com/apikey) -> mit Google-Konto anmelden -> **Create API key**.
Der Key ist im kostenlosen Kontingent sofort nutzbar (Gemini 2.5 Flash: 1.500 Requests/Tag Gratis-Limit,
bei diesem Projekt braucht es 1-2 Requests/Tag — keine Kreditkarte noetig).

### 2. Key als Secret hinterlegen
Repo auf GitHub -> **Settings -> Secrets and variables -> Actions -> New repository secret**
- Name: `GEMINI_API_KEY`
- Value: der eben erstellte Key

### 3. Workflow-Schreibrechte pruefen
**Settings -> Actions -> General -> Workflow permissions** -> "Read and write permissions" auswaehlen und speichern.
(Ohne das kann der Workflow `data.json` nicht zurueck ins Repo committen.)

### 4. GitHub Pages aktivieren
**Settings -> Pages -> Source** -> "Deploy from a branch" -> Branch `main`, Ordner `/ (root)` -> Save.
Nach ein bis zwei Minuten ist die Seite erreichbar unter `https://quanschi.github.io/PITWALL/`.

### 5. Als App installieren
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
werden.

## Lokal testen

Browser kann `data.json` per `fetch()` aus Sicherheitsgruenden nicht von `file://` laden. Lokal daher mit
einem einfachen HTTP-Server testen:

```bash
python -m http.server 8000
```

Dann `http://localhost:8000` oeffnen.

## Manuell Inhalte aktualisieren (ohne Automatisierung)

```bash
set GEMINI_API_KEY=dein-key
python scripts/generate_content.py --scope both
```

Danach `data.json` committen und pushen (oder GitHub Pages baut automatisch neu, sobald es im `main`-Branch liegt).
