# Upgrade & Run Guide (Django 5 / Python 3.14)

This document summarizes what has been done so far to modernize the project, and provides the exact steps to run it in the current environment.

---

## ✅ What Has Been Done (So Far)

### 1) Dependency Updates
- Upgraded core dependencies to current safe versions for Django 5 + Python 3.14.
- Updated `requirements.txt` with:
  - `Django==5.0.6`
  - `numpy==2.0.0` (2026-compatible)
  - `pandas==2.2.2`
  - Added missing packages required by the app (`cryptography`, `heartpy`, `pyhrv`, `peakutils`, etc.)

> ✅ `python manage.py check` now succeeds with **no errors** after these changes.

### 2) Django Compatibility Fixes
- Updated `app_config/settings.py` to include:
  - `DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"` (removes auto-field warnings)
- Updated `app_config/urls.py` to keep legacy `url(...)` patterns working by aliasing `url = re_path`.

### 3) Model Fixes
- Fixed `GENDER` fields that were too small for the longest `GENDER_CHOICES` value (e.g., `TRANSGENDER`).

### 4) Python 3 / Library Compatibility Fixes
- Patched compatibility issues in `kodys/app_api.py` for modern SciPy/NumPy:
  - Added a shim to alias `scipy.integrate.simps` → `scipy.integrate.simpson` for older code paths.
  - Added a local `trapz` implementation to avoid `numpy.trapz` being missing in NumPy 2.0.
- Fixed relative imports to ensure Django can load app modules (e.g. `from . import bwr`).

---

## 🏁 How to Run This Project (macOS)

### 1) Create/Activate Python Environment (recommended)
```bash
cd "$(pwd)/p232/p232/appsource"
python -m venv .venv
source .venv/bin/activate
```

> If you already have `.venv` and it’s activated, skip this step.

### 2) Install Dependencies
```bash
pip install -U pip
pip install -r requirements.txt
```

### 3) Run Django System Check
```bash
python app_config/manage.py check
```

If this reports `System check identified no issues`, you’re good.

### 4) Apply (or Create) Database Migrations
```bash
python app_config/manage.py makemigrations
python app_config/manage.py migrate
```

### 5) Run the Development Server
```bash
python app_config/manage.py runserver
```

Then visit: `http://127.0.0.1:8000/`

---

## 🧪 Notes / Next Manual Verifications

- Verify any custom reporting pages and file-handling features (PDF generation, image processing, etc.) still work as expected.
- If you see runtime import errors in places other than `manage.py check`, rerun `python manage.py check` and inspect the exception trace.

---

## 📌 Where to Look Next (if you want to continue modernization)

- `kodys/app_api.py` – contains heavy processing logic with external libs (PDF, ECG, etc.)
- `app_config/urls.py` – contains many legacy, regex-based routes (potential refactor target)
- `kodys/models.py` – large schema with many legacy patterns (could be simplified over time)

---

If you'd like, I can also generate a **simplified `README.md`** with these steps or help convert the app to use a more modern dependency manager (Poetry/Poetry lock, pip-tools, etc.).
