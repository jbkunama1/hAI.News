# hAI.News

[![Container image](https://img.shields.io/github/actions/workflow/status/jbkunama1/hAI.News/docker.yml?branch=main&label=GHCR%20Build&logo=github)](https://github.com/jbkunama1/hAI.News/actions/workflows/docker.yml)
[![GHCR](https://img.shields.io/badge/GHCR-ghcr.io%2Fjbkunama1%2Fhai.news-2496ED?logo=docker&logoColor=white)](https://github.com/jbkunama1/hAI.News/pkgs/container/hai.news)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1-000000?logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?logo=sqlite&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![Portainer](https://img.shields.io/badge/Portainer-Stack-13BEF9?logo=portainer&logoColor=white)
![Mobile First](https://img.shields.io/badge/UI-Mobile%20First-2866d6)
![Themes](https://img.shields.io/badge/Themes-11-8bb5ff)
![Platforms](https://img.shields.io/badge/Platforms-amd64%20%7C%20arm64-555555)

Mobile-first RSS-Nachrichtenübersicht mit Flask und SQLite. Die App zeigt Titel, Teaser, Vorschaubild, den vom Feed gelieferten Inhalt und Original-Links; kein Volltext-Abruf von den Verlagsseiten, keine Paywall-Umgehung, keine Google-API. Kein Google-News-Klon mit semantischem Clustering: chronologische Ansicht, Themen, Quellenauswahl, Suche und Nachladen.

## Funktionen

- Öffentliche Leseansicht, passwortgeschützte Administration.
- **Mobile-first:** einspaltige Karten mit Vorschaubild rechts, wischbare Themenleiste, die beim Scrollen oben bleibt, Bedienelemente mit mindestens 44 px Höhe, Lese- und Admin-Dialog als Sheet von unten, relative Zeitangaben („vor 5 Min.“). Ab 700 px zwei, ab 1050 px drei Spalten mit Bild über dem Text.
- **Themes (11):** Auto (folgt dem System), Hell, Dunkel, Schwarz (OLED), Sepia, Nord, Solarized (dunkel), Ozean, Wald, Rosé und Kontrast (schwarz auf weiß, für schlechte Lichtverhältnisse). Die Auswahl steht im Kopfbereich und wird im Browser gespeichert. Die Browser-Statusleiste passt sich an.
- **Schriftarten:** Sans, Serif, Mono und Rund. Es sind Systemschriften ohne Webfonts, das Aussehen hängt vom Gerät ab („Rund“ wirkt vor allem auf Apple-Geräten). Auswahl im Kopfbereich, im Browser gespeichert.
- **Schriftgröße:** im Lesedialog mit A− und A+ in vier Stufen, gilt für die ganze Seite und wird im Browser gespeichert.
- **Vorschaubilder:** aus `media:thumbnail`, `media:content`, Bild-Anhang oder dem ersten Bild im Feed-Text. Fehlt ein Bild oder lädt es nicht, zeigt die Karte nur Text.
- Leseansicht je Artikel: zeigt den Inhalt, den der Feed mitliefert (Teaser oder Auszug), mit Hinweis und Link „Beim Verlag lesen“.
- Feeds hinzufügen, aktivieren/deaktivieren und entfernen; Kategorie beim Hinzufügen. „Feed testen“ prüft eine URL vor dem Speichern und meldet Titel, Anzahl der Einträge, Beispiele sowie ob Inhalt und Vorschaubilder geliefert werden.
- Serverseitiger Abruf, Standard alle **15 Minuten**, im Admin einstellbar (5–1440 Minuten), manueller Abruf.
- Persistente SQLite-Daten, URL-Deduplizierung, 30 Tage Aufbewahrung.
- Quellstatus mit Fehler, letztem Versuch und letztem erfolgreichen Abruf.

## Voreingestellte Quellen

| Kategorie | Quellen |
|---|---|
| Nachrichten | DER SPIEGEL, ntv, Tagesschau, ZDFheute, Deutschlandfunk |
| Wirtschaft | Financial Times |
| International | BBC News World, Al Jazeera |
| Technologie | heise online, TechCrunch, Ars Technica, Golem.de, The Verge, Hacker News |
| Sport | Sportschau |
| 2. Bundesliga | Sportschau 2. Bundesliga |
| Biologie | Phys.org Biologie, ScienceDaily Biologie |
| Internet | t3n, netzpolitik.org |
| Bildung | News4teachers |
| KI | The Decoder |
| Maker | Hackaday, Prilchen Labs |
| 3D-Druck | All3DP |
| Smart Home | Home Assistant Release Notes |
| Lokal | ka-news Karlsruhe, ka-news KSC |

Bei bestehenden Installationen kommen neu hinzugefügte Quellen beim ersten Start der neuen Version einmalig dazu. Das geschieht in Stufen: ZDFheute, Deutschlandfunk, BBC, Al Jazeera, Golem.de, The Verge, Hacker News; dann Sportschau, Sportschau 2. Bundesliga, Phys.org, ScienceDaily, t3n, netzpolitik.org; dann News4teachers, The Decoder, Hackaday, Prilchen Labs, All3DP, Home Assistant; zuletzt ka-news Karlsruhe und KSC. Vorhandene Quellen und Einstellungen bleiben unverändert. Wer eine Quelle entfernt, bekommt sie nicht erneut angelegt.

**CNN** ist nicht mehr in der Standardliste: Der Feed `rss.cnn.com` liefert keine neuen Meldungen mehr und bricht die Verbindung ab. Installationen, die CNN schon haben, entfernen die Quelle im Admin-Bereich.

**Lokal:** ka-news hat die RSS-Unterstützung beim Relaunch offiziell eingestellt und nennt `/rss`-Adressen nur als Behelf. Diese Adressen können jederzeit wegfallen. Für die Gemeinde Pfinztal ist kein Feed bekannt; wer einen findet, trägt ihn im Admin-Bereich unter „Lokal“ ein.

Stand der Feed-Prüfung (einmaliger Abruf am 26.11.2026): SPIEGEL, Financial Times, heise, ZDFheute, Deutschlandfunk, Golem, BBC und Al Jazeera lieferten aktuelle Einträge. Die Tagesschau war im Test nicht abrufbar, bei n-tv und Hacker News zeigte der Test einen älteren Stand. t3n und Phys.org ließen sich abrufen. Nicht abgerufen und damit ungeprüft sind die Feed-URLs von Sportschau, ScienceDaily, netzpolitik.org, The Decoder, Prilchen Labs, News4teachers, All3DP, Home Assistant und ka-news; ihren Status zeigt der Admin-Bereich nach dem ersten Lauf. Feeds ändern sich; der Status je Quelle steht im Admin-Bereich.

## Inhalte und Rechte

Die App zeigt nur, was der jeweilige Feed ausliefert, und verlinkt zum Original. Nutzungsbedingungen der Feeds beachten: ntv erlaubt RSS-Meldungen z. B. nur unverändert, nur online und ohne Weitergabe an Dritte. Bei öffentlich erreichbarer Instanz ist das zu prüfen; die Leseansicht gehört dann hinter einen Zugriffsschutz. Financial Times und andere Bezahlquellen liefern nur Teaser.

## Deployment mit Portainer

GitHub Actions baut das Image und veröffentlicht es in GHCR; Portainer liest `docker-compose.yml` aus dem Repository und zieht das fertige Image.

1. Workflow **Container image** prüfen (Actions). Er baut amd64/arm64 und veröffentlicht `ghcr.io/jbkunama1/hai.news:latest` sowie einen SHA-Tag.
2. Das GHCR-Paket ist bei einem privaten Repository zunächst privat: Entweder Paket öffentlich stellen oder in Portainer eine GHCR-Registry mit Access Token (`read:packages`) hinterlegen.
3. Docker-Netzwerk anlegen, falls nicht vorhanden: `docker network create highfishNetwork`. Der Stack nutzt es als externes Netzwerk.
4. Portainer → Stacks → Add stack → Repository: Repository-URL, Reference `refs/heads/main`, Compose path `docker-compose.yml`. Bei privatem Repository Authentifizierung aktivieren.
5. Umgebungsvariablen setzen und deployen. Aufruf: `http://SERVER-IP:8055`.

| Variable | Bedeutung |
|---|---|
| `NEWS_IMAGE` | Optional, Standard `ghcr.io/jbkunama1/hai.news:latest` |
| `NEWS_PORT` | Host-Port, Standard `8055` (Container-intern 8080) |
| `ADMIN_PASSWORD` | Pflicht, mindestens 6 Zeichen (kürzere Passwörter sind leicht zu erraten; für Internetbetrieb länger wählen) |
| `SECRET_KEY` | Pflicht, mindestens 32 Zeichen, stabil halten (`openssl rand -hex 32`) |
| `COOKIE_SECURE` | `false` bei HTTP im LAN, `true` bei HTTPS |

Secrets nicht committen.

## Lokal testen

```sh
cp .env.example .env   # Passwort und Schlüssel eintragen
docker compose --env-file .env -f compose.local.yml up -d --build
curl http://localhost:8055/health
```

## Betrieb und Grenzen

- Genau ein Gunicorn-Worker, sonst laufen mehrere Abrufschleifen. Kein `--preload`.
- Der Container läuft als Benutzer `haiapp` (UID 10001). Der Name `news` ist im Basis-Image schon vergeben.
- Login: nach 8 Fehlversuchen pro Quell-IP 15 Minuten gesperrt (im RAM). Hinter Reverse Proxy teilen sich Nutzer ggf. eine IP.
- Für Internetbetrieb HTTPS und zusätzlichen Zugriffsschutz vorschalten.
- Feed-URLs: private/reservierte Ziele und Redirects werden geprüft; keine vollständige DNS-Rebinding-Abwehr, daher ausgehenden Zugriff auf interne Netze zusätzlich per Firewall begrenzen.
- Feed-Inhalt wird als reiner Text gespeichert und angezeigt (HTML wird entfernt). Maximal 8000 Zeichen je Artikel.
- Vorschaubilder lädt der Browser direkt vom Server des Verlags (nur HTTPS, ohne Referrer, verzögert geladen). Die Verlage sehen dabei die IP-Adresse des Besuchers. Es gibt keinen Bild-Proxy und keinen Bild-Cache; die Content-Security-Policy erlaubt dafür `img-src 'self' https:`. Bilder aus `http://`-Quellen werden auf `https://` umgestellt.
- Schriften sind Systemschriften. Webfonts würden eine Schriftdatei im Repository unter `static/` erfordern; externe Schriftquellen blockiert die Content-Security-Policy.
- Ältere, schon gespeicherte Artikel haben nach einem Update zunächst keinen Zusatzinhalt und kein Bild, bis sie im Feed erneut auftauchen; die Leseansicht zeigt dann den Teaser.
- Backup: Container stoppen, Volume `news_data` sichern.
- Updates: neues Image abwarten, Stack in Portainer aktualisieren und Image neu ziehen; für reproduzierbare Stände SHA-Tag verwenden.

## GitHub Pages

Projektseite unter `docs/index.html` (Settings → Pages → Branch `main`, Ordner `/docs`).

## Prüfstand

Der Docker-Build läuft über GitHub Actions; eine frühere Version des Containers lief auf dem Zielserver und rief Feeds ab. Für die jüngsten Änderungen (Themes, Schriften, neue Quellen, lokale Feeds) ist das Build-Ergebnis nicht bestätigt. Die mobile Ansicht, die Themes, die Schriften und die Vorschaubilder sind nicht in einem Browser getestet.
