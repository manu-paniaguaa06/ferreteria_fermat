# ⚙ Fermat — Sistema de Gestión Interna

App web interna para **Ferretería Fermat** · Flask + PostgreSQL (Railway) / SQLite (local)

---

## 🖥 Correr en local (desarrollo)

```bash
python app.py
# Abre → http://localhost:5000
```

Sin instalar nada extra — usa SQLite automáticamente si no hay DATABASE_URL.

---

## 🚀 Deploy en Railway

### 1 — Subir a GitHub

```bash
git init && git add . && git commit -m "Fermat init"
git remote add origin https://github.com/TU_USUARIO/fermat.git
git push -u origin main
```

### 2 — Crear proyecto en Railway

1. [railway.app](https://railway.app) → New Project → Deploy from GitHub repo
2. Selecciona el repo — Railway detecta el Procfile automáticamente

### 3 — Agregar PostgreSQL

1. En el proyecto → "+ New" → Database → PostgreSQL
2. Railway agrega DATABASE_URL automáticamente a tu servicio
3. Haz Redeploy — las tablas se crean solas

### 4 — Obtener URL pública

Settings → Domains → Generate Domain  
Ejemplo: https://fermat-production.up.railway.app

---

## Variables de entorno

| Variable | Descripción |
|----------|-------------|
| DATABASE_URL | URL de PostgreSQL (Railway la asigna automáticamente) |
| PORT | Puerto (Railway lo asigna automáticamente) |

---

## Estructura

```
fermat/
├── app.py              # Flask — compatible PG y SQLite
├── Procfile            # gunicorn para Railway
├── railway.json        # Config Railway
├── requirements.txt    # flask, gunicorn, psycopg2-binary
├── templates/          # index, catalogo, pedidos, empleados
└── static/css+js
```
