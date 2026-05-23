[README.md](https://github.com/user-attachments/files/28172644/README.md)
# Gehoerbildung

Eine kleine Streamlit-App fuer Gehoerbildung im LMS-Kurs. Die App spielt eine Folge aus vier Akkorden ab und bietet vier Antwortmoeglichkeiten an.

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

Wenn `python` bei dir nicht gefunden wird, nutze stattdessen den vollen Pfad:

```powershell
& "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py --server.address 127.0.0.1
```
