# Anleitung: Server & Domain kaufen (ganz einfach erklärt)

Damit die Webseite und der Bot Tag und Nacht laufen, brauchen wir drei
Dinge. Stell es dir so vor:

| Was | Wofür | Vergleich | Kosten ca. |
|---|---|---|---|
| 1. **Linux-Server** | Hier wohnen der Bot und die Webseite | Ein Computer, der nie ausgeschaltet wird | 5–10 € im Monat |
| 2. **Windows-Server** | Hier läuft MetaTrader 5 mit deinem FTMO-Konto | Ein zweiter Computer nur für MT5 | 12–20 € im Monat |
| 3. **Domain** | Die Adresse der Webseite (z. B. `mein-bot.ch`) | Das Namensschild an der Haustür | 10–20 € im Jahr |

**Wichtig:** Kaufen kannst nur du das (man braucht dein Konto und deine
Zahlungskarte). Aber du musst danach **nichts einrichten** — das mache
ich komplett fertig, du kopierst am Ende nur 2–3 Befehle hinein.

---

## Teil 1: Linux-Server mieten (bei Hetzner)

Hetzner ist ein großer deutscher Anbieter — günstig und zuverlässig.

1. Gehe auf **https://www.hetzner.com/cloud**
2. Klicke auf **„Jetzt bestellen"** / „Login" → **Konto erstellen**
   (E-Mail + Passwort, dann E-Mail bestätigen).
3. Hinterlege deine Zahlungsart (Karte oder PayPal).
4. Klicke auf **„+ Server erstellen"** und wähle:
   - **Standort:** Nürnberg oder Falkenstein (Deutschland)
   - **Betriebssystem (Image):** **Ubuntu 24.04**
   - **Typ:** „Shared vCPU" → **CX22** (2 CPU, 4 GB RAM — reicht völlig)
   - Alles andere: so lassen wie es ist.
5. Klicke unten auf **„Erstellen & jetzt kaufen"**.
6. Nach etwa 1 Minute ist der Server fertig. Du siehst dann eine
   **IP-Adresse** (vier Zahlen mit Punkten, z. B. `65.108.xx.xx`).
   → **Schreib dir diese IP-Adresse auf.**
7. Hetzner schickt dir per E-Mail ein **Root-Passwort** (oder zeigt es
   an). → **Speichere es im Passwort-Manager.**

✅ Fertig! Mehr nicht. Nichts anklicken, nichts installieren.

---

## Teil 2: Windows-Server mieten (bei Contabo)

Auf diesem Computer läuft später MetaTrader 5 rund um die Uhr.

1. Gehe auf **https://contabo.com/de/windows-vps/**
2. Wähle den **kleinsten Windows-VPS** (4 GB RAM oder mehr).
3. Bei Betriebssystem: **Windows Server 2022** (Contabo fragt das im
   Bestellvorgang; die Windows-Lizenz kommt automatisch dazu).
4. Konto erstellen, bezahlen, fertig.
5. Contabo schickt dir eine E-Mail mit:
   - der **IP-Adresse**
   - dem **Benutzernamen** (meist `Administrator`)
   - dem **Passwort**
   → **Alles drei aufschreiben/speichern.**

✅ Fertig! Auch hier: nichts weiter einrichten.

---

## Teil 3: Domain kaufen (bei Namecheap)

1. Gehe auf **https://www.namecheap.com**
2. Tippe oben in die Suche deinen Wunschnamen ein, z. B.
   `mechmodel-bot` — die Endung ist egal (`.com`, `.ch`, `.io` …),
   nimm eine günstige, die dir gefällt.
3. In den Warenkorb → Konto erstellen → bezahlen.
   (Alle Zusatzangebote im Warenkorb kannst du **abwählen** — wir
   brauchen nur die Domain. „WhoisGuard/Domain Privacy" ist gratis und
   darf anbleiben.)
4. → **Schreib dir auf, wie deine Domain heißt.**

✅ Fertig!

---

## Teil 4: Was du mir danach gibst

Wenn du alle drei Sachen hast, brauche ich von dir:

1. Die **IP-Adresse** vom Linux-Server
2. Die **IP-Adresse + Benutzername** vom Windows-Server
3. Den **Namen deiner Domain**

Die **Passwörter** gibst du **nicht** im Chat weiter — beim Einrichten
(Meilenstein M7) zeige ich dir, wie du sie sicher hinterlegst (z. B.
als Umgebungsvariable direkt auf dem Server), und wo du sie selbst
eintippst. So bleiben sie nur bei dir.

Danach bekommst du von mir ein fertiges Setup-Paket: **2–3 Befehle
kopieren, einfügen, Enter drücken — und die Webseite läuft mit HTTPS.**

---

## Häufige Fragen

**Muss ich das jetzt sofort kaufen?**
Nein. Das brauchen wir erst bei Meilenstein M7 (Web-Plattform +
Live-Betrieb). Der Bot wird vorher lokal entwickelt und getestet.

**Was, wenn ich etwas falsch mache?**
Kein Problem — beide Anbieter lassen sich monatlich kündigen, und einen
Server kann man jederzeit löschen und neu erstellen.

**Geht auch ein anderer Anbieter?**
Ja. Wichtig ist nur: Linux-Server mit Ubuntu 24.04 (min. 4 GB RAM),
Windows-Server (min. 4 GB RAM), irgendeine Domain.
