# hAI.News

[![Container image](https://img.shields.io/github/actions/workflow/status/jbkunama1/hAI.News/docker.yml?branch=main&label=GHCR%20Build&logo=github)](https://github.com/jbkunama1/hAI.News/actions/workflows/docker.yml)
[![GHCR](https://img.shields.io/badge/GHCR-ghcr.io%2Fjbkunama1%2Fhai.news-2496ED?logo=docker&logoColor=white)](https://github.com/jbkunama1/hAI.News/pkgs/container/hai.news)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1-000000?logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?logo=sqlite&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![Portainer](https://img.shields.io/badge/Portainer-Stack-13BEF9?logo=portainer&logoColor=white)
![Mobile First](https://img.shields.io/badge/UI-Mobile%20First-2866d6)
![Platforms](https://img.shields.io/badge/Platforms-amd64%20%7C%20arm64-555555)

Mobile-first RSS-Nachrichtenübersicht mit Flask und SQLite. Die App zeigt Titel, Teaser, den vom Feed gelieferten Inhalt und Original-Links; kein Volltext-Abruf von den Verlagsseiten, keine Paywall-Umgehung, keine Google-API. Kein Google-News-Klon mit semantischem Clustering: chronologische Ansicht, Kategorien, Quellenauswahl, Suche und Nachladen.

## Funktionen

- Öffentliche Leseansicht, passwortgeschützte Administration.
- Leseansicht je Artikel: zeigt den Inhalt, den der Feed mitliefert (Teaser oder Auszug), mit Hinweis und Link „Beim Verlag lesen“.
- Feeds hinzufügen, aktivieren/deaktivieren und entfernen; Kategorie beim Hinzufügen; Button „Feed testen“ prüft eine URL vor dem Speichern.
- Serverseitiger Abruf, Standard alle **15 Minuten**, im Admin einstellbar (5–1440 Minuten), manueller Abruf.
- Persistente SQLite-Daten, URL-Deduplizierung, 30 Tage Aufbewahrung.
- Quellstatus mit Fehler, letztem Versuch und letztem erfolgreichen Abruf.
- Hell-/Dunkelmodus, responsive Kartenansicht, keine externen Fonts/CDNs/Bilder.

## Voreingestellte Quellen

| Kategorie | Quellen |
|---|---|
| Nachrichten | DER SPIEGEL, ntv, Tagesschau, ZDFheute, Deutschlandfunk |
| Wirtschaft | Financial Times |
| International | BBC News World, Al Jazeera, CNN (experimentell) |
| Technologie | heise online, TechCrunch, Ars Technica, Golem.de, The Verge, Hacker News |

Bei bestehenden Installationen kommen die neu hinzugefügten Quellen (ZDFheute, Deutschlandfunk, BBC, Al Jazeera, Golem.de, The Verge, Hacker News) beim ersten Start der neuen Version einmalig dazu; vorhandene Quellen und Einstellungen bleiben unverändert. Wer eine Quelle entfernt, bekommt sie nicht erneut angelegt.

Stand der Feed-Prüfung (einmaliger Abruf am 26.11.2026): SPIEGEL, Financial Times, heise, ZDFheute, Deutschlandfunk, Golem, BBC und Al Jazeera lieferten aktuelle Einträge. CNN und Tagesschau waren im Test nicht abrufbar. Bei n-tv, Hacker News und der (nicht voreingestellten) Deutschen Welle zeigte der Test einen älteren Stand. Feeds ändern sich; der Status je Quelle steht im Admin-Bereich.

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
- Login: nach 8 Fehlversuchen pro Quell-IP 15 Minuten gesperrt (im RAM). Hinter Reverse Proxy teilen sich Nutzer ggf. eine IP.
- Für Internetbetrieb HTTPS und zusätzlichen Zugriffsschutz vorschalten.
- Feed-URLs: private/reservierte Ziele und Redirects werden geprüft; keine vollständige DNS-Rebinding-Abwehr, daher ausgehenden Zugriff auf interne Netze zusätzlich per Firewall begrenzen.
- Feed-Inhalt wird als reiner Text gespeichert und angezeigt (HTML wird entfernt, keine Bilder). Maximal 8000 Zeichen je Artikel.
- Ältere, schon gespeicherte Artikel haben nach dem Update zunächst keinen Zusatzinhalt, bis sie im Feed erneut auftauchen; die Leseansicht zeigt dann den Teaser.
- Backup: Container stoppen, Volume `news_data` sichern.
- Updates: neues Image abwarten, Stack in Portainer aktualisieren und Image neu ziehen; für reproduzierbare Stände SHA-Tag verwenden.

## GitHub Pages

Projektseite unter `docs/index.html` (Settings → Pages → Branch `main`, Ordner `/docs`).

## Prüfstatus

Python-Syntax und JavaScript-Syntax geprüft; Hilfsfunktionen für Textbereinigung und die Datenbank-Migration lokal getestet. Docker-Build, Browser-Test und Feed-Liveabrufe durch die App stehen bis zum ersten erfolgreichen Workflow-Lauf aus.
