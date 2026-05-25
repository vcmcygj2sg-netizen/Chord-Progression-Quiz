# Auralingo

Eine Streamlit-App fuer Gehoerbildung im LMS-Kurs. Die App ist als kurze Trainingsroutine gedacht: hoeren, Aufmerksamkeit fokussieren, Muster erkennen und erst danach benennen.

## Uebungsablauf

Die App hat ein Menue mit zwei Uebungsarten:

- `4-Chord-Loops`: Vier-Akkord-Muster werden als Stufenfolgen erkannt.
- `Kadenzmuster`: Vier-Akkord-Muster werden als Kadenzverlaeufe erkannt. Die Antwortmoeglichkeiten sind Kadenznamen, keine Stufensymbole.

In beiden Uebungen spielt die App zuerst ein vollstimmiges Vier-Akkord-Muster. Danach kann der Bass als Hoerhilfe genutzt werden:

- Bass hervorgehoben, waehrend die Akkorde weiterhin hoerbar bleiben.
- Bass in Sopranlage, erst nach Klick auf eine unauffaellige Zusatz-Schaltflaeche.

Die App wechselt in zufaelligen kleinen Bloecken zwischen zwei Aufgabentypen:

- Ein Soundfile hoeren und aus vier Antwortmoeglichkeiten waehlen.
- Ein Akkordmuster beziehungsweise Kadenzmuster sehen und aus zwei Soundfiles das passende auswaehlen.

Beim ersten Aufgabentyp bleibt Bass-Hoeren eine Strategie zum Erkennen des Patterns. Beim zweiten Aufgabentyp steht der Vergleich zweier Soundfiles im Vordergrund.

Am unteren Rand stehen drei einfache Zaehler: richtig geloeste Antworten, falsche Antworten und die Trefferquote in Prozent.

Die Progressionen bleiben harmonisch unveraendert. Die Bassnoten werden beim Abspielen aber dynamisch oktaviert, damit zwischen zwei Basstoenen kein Sprung groesser als eine Quinte entsteht. Kommt `I` beziehungsweise `Im` mehrfach in einer Progression vor, bleibt der Tonika-Basston jedes Mal im selben Register.

Die Klangfarbe wird pro Mission zufaellig aus `Orgel`, `E-Piano` und `Synth` gewaehlt. Die Orgel entspricht dem bisherigen Grundklang.

Die Stufen werden mit Grossbuchstaben notiert. Mollstufen tragen ein `m`, zum Beispiel `VIm`.

## Level

- `Level 1: Dur`: diatonische Dur-Folgen, Pop-Patterns und kadenznahe Muster.
- `Level 2: Moll`: Vier-Akkord-Muster in natuerlich Moll.
- `Level 3: Borrowed Chords`: Durkontexte mit geliehenen Akkorden wie `bVII`, `bVI`, `bIII` und `IVm`.

Die Kadenz-Uebung nutzt einen gemeinsamen Pool aus Dur- und Mollkadenzen.

## Didaktische Idee

Die App orientiert sich an Timothy Chenettes Artikel [What Are the Truly Aural Skills?](https://mtosmt.org/issues/mto.21.27.2/mto.21.27.2.chenette.html). Die Uebungen fragen daher nicht nur Theorie-Labels ab, sondern trainieren zuerst aufmerksamkeitsnahe Hoerleistungen: Basslinien verfolgen und musikalische Muster als Chunks erkennen.

## Starten

Einfachster Start:

```powershell
.\start_app.bat
```

Falls du PowerShell-Skripte auf deinem Rechner erlaubt hast, geht auch:

```powershell
.\start_app.ps1
```

Oder Schritt fuer Schritt:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py --server.address 127.0.0.1
```

## LMS

Fuer den LMS-Kurs muss die App online laufen, zum Beispiel auf Streamlit Community Cloud. Die lokale Adresse `http://127.0.0.1:8501` funktioniert nur auf deinem eigenen Rechner.

Eine genaue Anleitung steht in [LMS_EINBETTUNG.md](LMS_EINBETTUNG.md).

## GitHub und Streamlit Community Cloud

Fuer GitHub braucht die App mindestens diese Dateien:

- `app.py`
- `midi_engine.py`
- `requirements.txt`

Diese Dateien sind sinnvoll, aber nicht zwingend noetig:

- `.streamlit/config.toml`
- `README.md`
- `LMS_EINBETTUNG.md`
- `GITHUB_STREAMLIT_CHECKLIST.md`
- `.gitignore`

In Streamlit Community Cloud ist die Startdatei:

```text
app.py
```

Weitere Systempakete oder Zugangsdaten sind fuer diese App nicht noetig. Wenn Streamlit nach einer Python-Version fragt, waehle Python 3.12.

Wenn `python` bei dir nicht gefunden wird, nutze stattdessen den vollen Pfad:

```powershell
& "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py --server.address 127.0.0.1
```
