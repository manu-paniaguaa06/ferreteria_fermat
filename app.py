from flask import Flask, render_template, request, jsonify, g
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), 'fermat.db')

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)
    if db: db.close()

def query(sql, args=(), one=False):
    cur = get_db().execute(sql, args)
    rv = cur.fetchall()
    return (rv[0] if rv else None) if one else rv

def mutate(sql, args=()):
    db = get_db()
    cur = db.execute(sql, args)
    db.commit()
    return cur.lastrowid

SCHEMA = """
CREATE TABLE IF NOT EXISTS categoria (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT NOT NULL, icono TEXT DEFAULT '🔧');
CREATE TABLE IF NOT EXISTS proveedor (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT NOT NULL, contacto TEXT, telefono TEXT, email TEXT);
CREATE TABLE IF NOT EXISTS producto (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT NOT NULL, descripcion TEXT, precio REAL NOT NULL, stock INTEGER DEFAULT 0, sku TEXT, categoria_id INTEGER REFERENCES categoria(id), proveedor_id INTEGER REFERENCES proveedor(id), activo INTEGER DEFAULT 1);
CREATE TABLE IF NOT EXISTS cliente (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT NOT NULL, telefono TEXT, email TEXT, direccion TEXT, fecha_registro TEXT DEFAULT (datetime('now')));
CREATE TABLE IF NOT EXISTS pedido (id INTEGER PRIMARY KEY AUTOINCREMENT, cliente_id INTEGER NOT NULL REFERENCES cliente(id), fecha TEXT DEFAULT (datetime('now')), estado TEXT DEFAULT 'pendiente', total REAL DEFAULT 0, notas TEXT);
CREATE TABLE IF NOT EXISTS item_pedido (id INTEGER PRIMARY KEY AUTOINCREMENT, pedido_id INTEGER NOT NULL REFERENCES pedido(id) ON DELETE CASCADE, producto_id INTEGER NOT NULL REFERENCES producto(id), cantidad INTEGER NOT NULL, precio_unitario REAL NOT NULL);
CREATE TABLE IF NOT EXISTS pedido_proveedor (id INTEGER PRIMARY KEY AUTOINCREMENT, proveedor_id INTEGER NOT NULL REFERENCES proveedor(id), fecha TEXT DEFAULT (datetime('now')), estado TEXT DEFAULT 'borrador', total REAL DEFAULT 0, notas TEXT);
CREATE TABLE IF NOT EXISTS item_pedido_proveedor (id INTEGER PRIMARY KEY AUTOINCREMENT, pedido_proveedor_id INTEGER NOT NULL REFERENCES pedido_proveedor(id) ON DELETE CASCADE, producto_id INTEGER NOT NULL REFERENCES producto(id), cantidad INTEGER NOT NULL, precio_unitario REAL NOT NULL);
"""

def init_db():
    db = sqlite3.connect(DB_PATH)
    db.executescript(SCHEMA)
    cur = db.execute("SELECT COUNT(*) FROM categoria")
    if cur.fetchone()[0] == 0:
        db.executemany("INSERT INTO categoria(nombre,icono) VALUES(?,?)", [('Herramientas','🔨'),('Tornillería','🔩'),('Plomería','🚿'),('Electricidad','⚡'),('Pintura','🎨'),('Construcción','🧱')])
        db.executemany("INSERT INTO proveedor(nombre,contacto,telefono,email) VALUES(?,?,?,?)", [('Distribuidora Central','Carlos Méndez','555-1234','ventas@distcentral.mx'),('Herramientas del Norte','Ana Ruiz','555-5678','ana@hdnorte.mx')])
        db.executemany("INSERT INTO producto(nombre,descripcion,precio,stock,sku,categoria_id,proveedor_id) VALUES(?,?,?,?,?,?,?)", [
            ('Martillo de Carpintero 16oz','Martillo profesional mango fibra de vidrio',185.0,24,'HER-001',1,1),
            ('Desarmador Phillips #2','Punta magnética, mango antideslizante',45.0,50,'HER-002',1,1),
            ('Llave Ajustable 12"','Acero forjado, graduación mm y pulgadas',220.0,15,'HER-003',1,2),
            ('Tornillo Hexagonal M8x30','Acero inoxidable, paquete 50 piezas',65.0,200,'TOR-001',2,1),
            ('Tuerca M8 Hexagonal','Paquete de 100 piezas',35.0,300,'TOR-002',2,1),
            ('Codo PVC 3/4"','PVC sanitario 90 grados',12.0,80,'PLO-001',3,2),
            ('Tubo PVC 1/2" x 3m','PVC hidráulico presión',48.0,40,'PLO-002',3,2),
            ('Cinta Aislante 3M','Rollo 18mm x 20m, negro',28.0,60,'ELE-001',4,1),
            ('Pintura Vinílica Blanca 19L','Interior/Exterior, lavable',680.0,12,'PIN-001',5,2),
            ('Cemento Portland 50kg','Uso general, alta resistencia',185.0,3,'CON-001',6,1),
        ])
        db.executemany("INSERT INTO cliente(nombre,telefono,email,direccion) VALUES(?,?,?,?)", [
            ('Roberto Hernández','555-9001','roberto@gmail.com','Av. Juárez 123'),
            ('María González','555-9002','maria@outlook.com','Calle Hidalgo 456'),
            ('Construcciones Pérez SA','555-9003','info@construperez.mx','Blvd. Industrial 789'),
        ])
        db.commit()
    db.close()

def fmt_fecha(s):
    if not s: return ''
    try: return datetime.strptime(s[:16], '%Y-%m-%dT%H:%M').strftime('%d/%m/%Y %H:%M')
    except:
        try: return datetime.strptime(s[:16], '%Y-%m-%d %H:%M').strftime('%d/%m/%Y %H:%M')
        except: return s[:16]

def fmt_fecha_short(s):
    if not s: return ''
    try: return datetime.strptime(s[:10], '%Y-%m-%d').strftime('%d/%m/%Y')
    except: return s[:10]

def producto_dict(r):
    return {'id':r['id'],'nombre':r['nombre'],'descripcion':r['descripcion'] or '','precio':r['precio'],'stock':r['stock'],'sku':r['sku'] or '','categoria':r['cat_nombre'] or '','categoria_icono':r['cat_icono'] or '🔧','proveedor':r['prov_nombre'] or '','activo':bool(r['activo'])}

def pedido_dict(p, items):
    return {'id':p['id'],'cliente':p['cliente_nombre'],'cliente_id':p['cliente_id'],'fecha':fmt_fecha(p['fecha']),'estado':p['estado'],'total':p['total'] or 0,'notas':p['notas'] or '','items':[{'id':i['id'],'producto':i['prod_nombre'],'cantidad':i['cantidad'],'precio_unitario':i['precio_unitario'],'subtotal':i['cantidad']*i['precio_unitario']} for i in items]}

def ped_prov_dict(p, items):
    return {'id':p['id'],'proveedor':p['prov_nombre'],'proveedor_id':p['proveedor_id'],'fecha':fmt_fecha(p['fecha']),'estado':p['estado'],'total':p['total'] or 0,'notas':p['notas'] or '','items':[{'id':i['id'],'producto':i['prod_nombre'],'cantidad':i['cantidad'],'precio_unitario':i['precio_unitario'],'subtotal':i['cantidad']*i['precio_unitario']} for i in items]}

@app.route('/')
def index(): return render_template('index.html')
@app.route('/catalogo')
def catalogo(): return render_template('catalogo.html')
@app.route('/pedidos')
def pedidos(): return render_template('pedidos.html')
@app.route('/empleados')
def empleados(): return render_template('empleados.html')

@app.route('/api/productos')
def get_productos():
    cat = request.args.get('categoria'); q = request.args.get('q','')
    sql = "SELECT p.*, c.nombre cat_nombre, c.icono cat_icono, pr.nombre prov_nombre FROM producto p LEFT JOIN categoria c ON p.categoria_id=c.id LEFT JOIN proveedor pr ON p.proveedor_id=pr.id WHERE p.activo=1"
    args = []
    if cat: sql += " AND p.categoria_id=?"; args.append(cat)
    if q: sql += " AND p.nombre LIKE ?"; args.append(f'%{q}%')
    return jsonify([producto_dict(r) for r in query(sql, args)])

@app.route('/api/productos', methods=['POST'])
def create_producto():
    d = request.json
    id = mutate("INSERT INTO producto(nombre,descripcion,precio,stock,sku,categoria_id,proveedor_id) VALUES(?,?,?,?,?,?,?)",(d['nombre'],d.get('descripcion',''),d['precio'],d.get('stock',0),d.get('sku',''),d.get('categoria_id') or None,d.get('proveedor_id') or None))
    r = query("SELECT p.*, c.nombre cat_nombre, c.icono cat_icono, pr.nombre prov_nombre FROM producto p LEFT JOIN categoria c ON p.categoria_id=c.id LEFT JOIN proveedor pr ON p.proveedor_id=pr.id WHERE p.id=?",(id,),one=True)
    return jsonify(producto_dict(r)), 201

@app.route('/api/productos/<int:id>', methods=['PUT'])
def update_producto(id):
    d = request.json; fields=[]; vals=[]
    for k in ('nombre','descripcion','precio','stock','sku','categoria_id','proveedor_id','activo'):
        if k in d: fields.append(f"{k}=?"); vals.append(d[k])
    if fields: vals.append(id); mutate(f"UPDATE producto SET {','.join(fields)} WHERE id=?",vals)
    r = query("SELECT p.*, c.nombre cat_nombre, c.icono cat_icono, pr.nombre prov_nombre FROM producto p LEFT JOIN categoria c ON p.categoria_id=c.id LEFT JOIN proveedor pr ON p.proveedor_id=pr.id WHERE p.id=?",(id,),one=True)
    return jsonify(producto_dict(r))

@app.route('/api/productos/<int:id>', methods=['DELETE'])
def delete_producto(id): mutate("UPDATE producto SET activo=0 WHERE id=?",(id,)); return jsonify({'ok':True})

@app.route('/api/categorias')
def get_categorias(): return jsonify([dict(r) for r in query("SELECT * FROM categoria")])

@app.route('/api/categorias', methods=['POST'])
def create_categoria():
    d = request.json; id = mutate("INSERT INTO categoria(nombre,icono) VALUES(?,?)",(d['nombre'],d.get('icono','🔧')))
    return jsonify(dict(query("SELECT * FROM categoria WHERE id=?",(id,),one=True))), 201

@app.route('/api/clientes')
def get_clientes():
    q = request.args.get('q','')
    rows = query("SELECT * FROM cliente WHERE nombre LIKE ? ORDER BY id DESC",(f'%{q}%',))
    return jsonify([{**dict(r),'fecha_registro':fmt_fecha_short(r['fecha_registro'])} for r in rows])

@app.route('/api/clientes', methods=['POST'])
def create_cliente():
    d = request.json; id = mutate("INSERT INTO cliente(nombre,telefono,email,direccion) VALUES(?,?,?,?)",(d['nombre'],d.get('telefono',''),d.get('email',''),d.get('direccion','')))
    r = query("SELECT * FROM cliente WHERE id=?",(id,),one=True)
    return jsonify({**dict(r),'fecha_registro':fmt_fecha_short(r['fecha_registro'])}), 201

@app.route('/api/clientes/<int:id>', methods=['PUT'])
def update_cliente(id):
    d = request.json; fields=[]; vals=[]
    for k in ('nombre','telefono','email','direccion'):
        if k in d: fields.append(f"{k}=?"); vals.append(d[k])
    if fields: vals.append(id); mutate(f"UPDATE cliente SET {','.join(fields)} WHERE id=?",vals)
    r = query("SELECT * FROM cliente WHERE id=?",(id,),one=True)
    return jsonify({**dict(r),'fecha_registro':fmt_fecha_short(r['fecha_registro'])})

@app.route('/api/pedidos')
def get_pedidos():
    estado = request.args.get('estado'); args=[]
    sql = "SELECT p.*, c.nombre cliente_nombre FROM pedido p JOIN cliente c ON p.cliente_id=c.id"
    if estado: sql += " WHERE p.estado=?"; args.append(estado)
    sql += " ORDER BY p.fecha DESC"
    rows = query(sql, args); result=[]
    for p in rows:
        items = query("SELECT ip.*, pr.nombre prod_nombre FROM item_pedido ip JOIN producto pr ON ip.producto_id=pr.id WHERE ip.pedido_id=?",(p['id'],))
        result.append(pedido_dict(p,items))
    return jsonify(result)

@app.route('/api/pedidos', methods=['POST'])
def create_pedido():
    d = request.json
    pid = mutate("INSERT INTO pedido(cliente_id,notas,estado,total) VALUES(?,?,'pendiente',0)",(d['cliente_id'],d.get('notas','')))
    total=0
    for item in d.get('items',[]):
        prod = query("SELECT precio FROM producto WHERE id=?",(item['producto_id'],),one=True)
        if prod:
            mutate("INSERT INTO item_pedido(pedido_id,producto_id,cantidad,precio_unitario) VALUES(?,?,?,?)",(pid,item['producto_id'],item['cantidad'],prod['precio']))
            total += item['cantidad']*prod['precio']
    mutate("UPDATE pedido SET total=? WHERE id=?",(total,pid))
    p = query("SELECT p.*, c.nombre cliente_nombre FROM pedido p JOIN cliente c ON p.cliente_id=c.id WHERE p.id=?",(pid,),one=True)
    items = query("SELECT ip.*, pr.nombre prod_nombre FROM item_pedido ip JOIN producto pr ON ip.producto_id=pr.id WHERE ip.pedido_id=?",(pid,))
    return jsonify(pedido_dict(p,items)), 201

@app.route('/api/pedidos/<int:id>/estado', methods=['PUT'])
def update_pedido_estado(id):
    mutate("UPDATE pedido SET estado=? WHERE id=?",(request.json.get('estado'),id))
    p = query("SELECT p.*, c.nombre cliente_nombre FROM pedido p JOIN cliente c ON p.cliente_id=c.id WHERE p.id=?",(id,),one=True)
    items = query("SELECT ip.*, pr.nombre prod_nombre FROM item_pedido ip JOIN producto pr ON ip.producto_id=pr.id WHERE ip.pedido_id=?",(id,))
    return jsonify(pedido_dict(p,items))

@app.route('/api/proveedores')
def get_proveedores(): return jsonify([dict(r) for r in query("SELECT * FROM proveedor")])

@app.route('/api/proveedores', methods=['POST'])
def create_proveedor():
    d = request.json; id = mutate("INSERT INTO proveedor(nombre,contacto,telefono,email) VALUES(?,?,?,?)",(d['nombre'],d.get('contacto',''),d.get('telefono',''),d.get('email','')))
    return jsonify(dict(query("SELECT * FROM proveedor WHERE id=?",(id,),one=True))), 201

@app.route('/api/pedidos-proveedor')
def get_pedidos_proveedor():
    rows = query("SELECT pp.*, p.nombre prov_nombre FROM pedido_proveedor pp JOIN proveedor p ON pp.proveedor_id=p.id ORDER BY pp.fecha DESC")
    result=[]
    for pp in rows:
        items = query("SELECT ip.*, pr.nombre prod_nombre FROM item_pedido_proveedor ip JOIN producto pr ON ip.producto_id=pr.id WHERE ip.pedido_proveedor_id=?",(pp['id'],))
        result.append(ped_prov_dict(pp,items))
    return jsonify(result)

@app.route('/api/pedidos-proveedor', methods=['POST'])
def create_pedido_proveedor():
    d = request.json
    pid = mutate("INSERT INTO pedido_proveedor(proveedor_id,notas,estado,total) VALUES(?,?,'borrador',0)",(d['proveedor_id'],d.get('notas','')))
    total=0
    for item in d.get('items',[]):
        mutate("INSERT INTO item_pedido_proveedor(pedido_proveedor_id,producto_id,cantidad,precio_unitario) VALUES(?,?,?,?)",(pid,item['producto_id'],item['cantidad'],item.get('precio_unitario',0)))
        total += item['cantidad']*item.get('precio_unitario',0)
    mutate("UPDATE pedido_proveedor SET total=? WHERE id=?",(total,pid))
    pp = query("SELECT pp.*, p.nombre prov_nombre FROM pedido_proveedor pp JOIN proveedor p ON pp.proveedor_id=p.id WHERE pp.id=?",(pid,),one=True)
    items = query("SELECT ip.*, pr.nombre prod_nombre FROM item_pedido_proveedor ip JOIN producto pr ON ip.producto_id=pr.id WHERE ip.pedido_proveedor_id=?",(pid,))
    return jsonify(ped_prov_dict(pp,items)), 201

@app.route('/api/pedidos-proveedor/<int:id>/estado', methods=['PUT'])
def update_pedido_proveedor_estado(id):
    mutate("UPDATE pedido_proveedor SET estado=? WHERE id=?",(request.json.get('estado'),id))
    pp = query("SELECT pp.*, p.nombre prov_nombre FROM pedido_proveedor pp JOIN proveedor p ON pp.proveedor_id=p.id WHERE pp.id=?",(id,),one=True)
    items = query("SELECT ip.*, pr.nombre prod_nombre FROM item_pedido_proveedor ip JOIN producto pr ON ip.producto_id=pr.id WHERE ip.pedido_proveedor_id=?",(id,))
    return jsonify(ped_prov_dict(pp,items))

@app.route('/api/dashboard')
def dashboard():
    hoy = datetime.utcnow().strftime('%Y-%m-%d')
    recientes_rows = query("SELECT p.*, c.nombre cliente_nombre FROM pedido p JOIN cliente c ON p.cliente_id=c.id ORDER BY p.fecha DESC LIMIT 5")
    recientes=[]
    for p in recientes_rows:
        items = query("SELECT ip.*, pr.nombre prod_nombre FROM item_pedido ip JOIN producto pr ON ip.producto_id=pr.id WHERE ip.pedido_id=?",(p['id'],))
        recientes.append(pedido_dict(p,items))
    return jsonify({'total_productos':query("SELECT COUNT(*) c FROM producto WHERE activo=1",one=True)['c'],'total_clientes':query("SELECT COUNT(*) c FROM cliente",one=True)['c'],'pedidos_pendientes':query("SELECT COUNT(*) c FROM pedido WHERE estado='pendiente'",one=True)['c'],'pedidos_hoy':query("SELECT COUNT(*) c FROM pedido WHERE date(fecha)=?",(hoy,),one=True)['c'],'stock_bajo':query("SELECT COUNT(*) c FROM producto WHERE stock<5 AND activo=1",one=True)['c'],'pedidos_recientes':recientes})

init_db()
if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
