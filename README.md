# ⚙ Fermat — Sistema de Gestión Interna

Aplicación web interna para **Ferretería Fermat**, construida con Flask + SQLite.
Optimizada para **iPad y celular**.

---

## 🚀 Instalación rápida

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Ejecutar
python app.py
```

Luego abre **http://localhost:5000** en tu navegador o tablet.

---

## 📱 Vistas

| Vista | Ruta | Descripción |
|-------|------|-------------|
| Inicio | `/` | Dashboard con estadísticas y accesos rápidos |
| Catálogo | `/catalogo` | Ver productos por categoría, agregar al carrito y hacer pedidos |
| Pedidos | `/pedidos` | Ver y gestionar pedidos de clientes |
| Empleados | `/empleados` | Panel completo: pedidos, proveedores, inventario, clientes |

---

## 🔌 API Endpoints

### Productos
- `GET /api/productos?q=busqueda&categoria=1` — Listar/buscar
- `POST /api/productos` — Crear
- `PUT /api/productos/<id>` — Editar
- `DELETE /api/productos/<id>` — Desactivar

### Categorías
- `GET /api/categorias`
- `POST /api/categorias`

### Clientes
- `GET /api/clientes?q=busqueda`
- `POST /api/clientes`
- `PUT /api/clientes/<id>`

### Pedidos de Clientes
- `GET /api/pedidos?estado=pendiente`
- `POST /api/pedidos`
- `PUT /api/pedidos/<id>/estado`

### Proveedores
- `GET /api/proveedores`
- `POST /api/proveedores`

### Pedidos a Proveedores
- `GET /api/pedidos-proveedor`
- `POST /api/pedidos-proveedor`
- `PUT /api/pedidos-proveedor/<id>/estado`

### Dashboard
- `GET /api/dashboard`

---

## 🗄 Base de datos

SQLite (`fermat.db`), auto-generada en el primer arranque con datos de ejemplo:
- 6 categorías
- 10 productos
- 2 proveedores
- 3 clientes de ejemplo

Para producción, cambia `SQLALCHEMY_DATABASE_URI` a PostgreSQL o MySQL.

---

## 🏗 Estructura

```
fermat/
├── app.py              # Flask app + modelos + rutas API
├── requirements.txt
├── templates/
│   ├── base.html       # Layout base con navbar
│   ├── index.html      # Dashboard
│   ├── catalogo.html   # Catálogo + carrito
│   ├── pedidos.html    # Pedidos clientes
│   └── empleados.html  # Panel empleados
└── static/
    ├── css/main.css    # Estilos (dark theme industrial)
    └── js/main.js      # Utilidades JS
```
