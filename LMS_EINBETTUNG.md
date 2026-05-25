# LMS-Einbettung

Diese App ist als Uebetool gedacht. Sie speichert keine Namen, keine Noten und keine personenbezogenen Daten.

## 1. Online stellen

Der einfachste Weg ist Streamlit Community Cloud:

1. Erstelle ein GitHub-Repository fuer diese App.
2. Lade die Dateien aus `GITHUB_STREAMLIT_CHECKLIST.md` hoch.
3. Oeffne Streamlit Community Cloud.
4. Waehle dein Repository aus.
5. Setze als Startdatei `app.py`.
6. Deploy.

Danach bekommst du eine Adresse wie:

```text
https://dein-app-name.streamlit.app
```

Deine aktuelle App-Adresse ist:

```text
https://chord-progression-quiz-5pwtf3a4wzrk8gzs7dejdp.streamlit.app/
```

## 2. In den LMS-Kurs einbetten

Nutze fuer Streamlit-Apps den Embed-Parameter `?embed=true`.

Wichtig: Verwende nicht die alte Adresse `share.streamlit.io/...`, sondern die neue App-Adresse mit der Endung `.streamlit.app`.

Richtig:

```text
https://chord-progression-quiz-5pwtf3a4wzrk8gzs7dejdp.streamlit.app/?embed=true
```

Falsch:

```text
https://share.streamlit.io/...
```

```html
<iframe
  src="https://chord-progression-quiz-5pwtf3a4wzrk8gzs7dejdp.streamlit.app/?embed=true"
  width="100%"
  height="760"
  style="border: 0;"
  loading="lazy"
  allow="autoplay">
</iframe>
```

Wenn dein LMS iframes blockiert, verlinke stattdessen direkt:

```text
https://chord-progression-quiz-5pwtf3a4wzrk8gzs7dejdp.streamlit.app/?embed=true
```

## 3. Moodle / HMTMH-LMS

Wenn dein LMS auf Moodle basiert, nutze fuer diese App nicht die Aktivitaet `Externes Tool`.

`Externes Tool` ist in Moodle fuer LTI-Anbindungen gedacht. Streamlit Community Cloud ist aber kein LTI-Tool, sondern eine normale Webseite.

Nutze stattdessen eine dieser Varianten:

1. `Text- und Medienfeld` oder `Textseite`
   - HTML-Ansicht im Editor oeffnen.
   - Den iframe-Code einfuegen.
   - Speichern.

2. `URL`
   - Als URL die Adresse `https://chord-progression-quiz-5pwtf3a4wzrk8gzs7dejdp.streamlit.app/?embed=true` eintragen.
   - Bei Darstellung, falls vorhanden, `Einbetten` oder `Oeffnen` waehlen.

Wenn der iframe nach dem Speichern verschwindet oder blockiert wird, muss die LMS-Administration iframes bzw. die Domain `streamlit.app` erlauben.

## 4. Hinweis fuer den Kurs

Die App ist ein freiwilliges Uebetool. Der Fortschritt gilt nur fuer die aktuelle Browser-Sitzung und wird nicht ins LMS-Notenbuch uebertragen.
