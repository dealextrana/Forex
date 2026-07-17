# Anleitung: Telegram-Bot erstellen (dauert ca. 3 Minuten)

Der Bot schickt dir später bei jedem Trade eine Nachricht aufs Handy.
Damit das geht, brauchst du einen eigenen Telegram-Bot. So erstellst du
ihn — Schritt für Schritt:

## Schritt 1: Telegram öffnen

Öffne die Telegram-App auf deinem Handy (oder Telegram am Computer).

## Schritt 2: Den „BotFather" finden

1. Tippe oben auf die **Lupe** (Suche).
2. Schreibe: `BotFather`
3. Tippe auf das Ergebnis **@BotFather** — das ist der offizielle
   Telegram-Roboter mit einem **blauen Haken** ✔️.
   (Achtung: Nur der mit dem blauen Haken ist echt!)

## Schritt 3: Neuen Bot bauen

1. Tippe unten auf **Start**.
2. Schreibe ihm diese Nachricht: `/newbot`
3. Er fragt nach einem **Namen**. Schreibe z. B.: `Mein Trading Bot`
4. Er fragt nach einem **Benutzernamen**. Der muss mit `bot` enden und
   darf noch nicht vergeben sein. Schreibe z. B.:
   `alex_mechmodel_bot`
   (Wenn er sagt, der Name ist vergeben: einfach einen anderen
   probieren, z. B. mit Zahlen: `alex_mechmodel_2026_bot`)

## Schritt 4: Den geheimen Schlüssel kopieren

Der BotFather schickt dir jetzt eine Nachricht mit einem langen Code,
der so ähnlich aussieht:

```
1234567890:AAHrX2example-example_exampleXYZ
```

Das ist der **Token** — der geheime Schlüssel deines Bots.

1. Tippe auf den Code, um ihn zu **kopieren**.
2. Speichere ihn an einem sicheren Ort (z. B. Passwort-Manager oder
   Notizen-App mit Sperre).

## ⚠️ Ganz wichtig

- Der Token ist wie ein **Passwort**. Gib ihn **niemandem** weiter und
  poste ihn nirgendwo öffentlich.
- Falls er doch mal öffentlich wird: beim BotFather `/revoke` schreiben,
  dann bekommst du einen neuen und der alte wird ungültig.

## Schritt 5: Fertig!

Mehr musst du jetzt nicht tun. Den Token trägst du später (wenn die
Webseite fertig ist) einmal in den Einstellungen ein. Danach verbindest
du dein Telegram mit deinem Account:

1. Im Web-Dashboard auf „Telegram verbinden" klicken → du bekommst
   einen kurzen Code angezeigt.
2. Deinem Bot in Telegram `/start DEIN-CODE` schreiben.
3. Ab jetzt bekommst du alle Trade-Nachrichten automatisch. ✅
