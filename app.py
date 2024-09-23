from flask import Flask, render_template, request, redirect, url_for, g
import sqlite3
import datetime

app = Flask(__name__)

# Configuración de la base de datos SQLite
DATABASE = DATABASE = 'C:/Users/sysadmin/OneDrive/Escritorio/ProyectoXUBA/database.db'



def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row  # Permite que las filas se comporten como diccionarios
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Rutas para la página principal
@app.route('/')
def index():
    return render_template('index.html')

# Rutas para manejar personas
@app.route('/personas')
def personas():
    db = get_db()
    cursor = db.execute('SELECT * FROM personas')
    personas = cursor.fetchall()
    return render_template('personas.html', personas=personas)

@app.route('/add_persona', methods=['GET', 'POST'])
def add_persona():
    if request.method == 'POST':
        db = get_db()
        db.execute(
            'INSERT INTO personas (nombre, apellido, mail, telefono) VALUES (?, ?, ?, ?)',
            (request.form['nombre'], request.form['apellido'], request.form['mail'], request.form['telefono'])
        )
        db.commit()
        return redirect(url_for('personas'))
    return render_template('form_persona.html')

@app.route('/edit_persona/<int:id>', methods=['GET', 'POST'])
def edit_persona(id):
    db = get_db()
    if request.method == 'POST':
        db.execute(
            'UPDATE personas SET nombre = ?, apellido = ?, mail = ?, telefono = ? WHERE id_persona = ?',
            (request.form['nombre'], request.form['apellido'], request.form['mail'], request.form['telefono'], id)
        )
        db.commit()
        return redirect(url_for('personas'))
    
    cursor = db.execute('SELECT * FROM personas WHERE id_persona = ?', (id,))
    persona = cursor.fetchone()
    return render_template('form_persona.html', persona=persona)

@app.route('/delete_persona/<int:id>')
def delete_persona(id):
    db = get_db()
    db.execute('DELETE FROM personas WHERE id_persona = ?', (id,))
    db.commit()
    return redirect(url_for('personas'))

@app.route('/proveedores')
def proveedores():
    db = get_db()
    # Obtener todos los proveedores
    cursor = db.execute('SELECT * FROM proveedores')
    proveedores = cursor.fetchall()

    # Obtener localidades únicas
    cursor_localidades = db.execute('SELECT DISTINCT localidad FROM proveedores')
    localidades = [row['localidad'] for row in cursor_localidades.fetchall()]

    return render_template('proveedores.html', proveedores=proveedores, localidades=localidades)

@app.route('/add_proveedor', methods=['GET', 'POST'])
def add_proveedor():
    if request.method == 'POST':
        db = get_db()
        db.execute(
            'INSERT INTO proveedores (nombre, telefono, mail, localidad) VALUES (?, ?, ?, ?)',
            (request.form['nombre'], request.form['telefono'], request.form['mail'], request.form['localidad'])
        )
        db.commit()
        return redirect(url_for('proveedores'))
    return render_template('form_proveedor.html')

@app.route('/edit_proveedor/<int:id>', methods=['GET', 'POST'])
def edit_proveedor(id):
    db = get_db()
    if request.method == 'POST':
        db.execute(
            'UPDATE proveedores SET nombre = ?, telefono = ?, mail = ?, localidad = ? WHERE id_proveedor = ?',
            (request.form['nombre'], request.form['telefono'], request.form['mail'], request.form['localidad'], id)
        )
        db.commit()
        return redirect(url_for('proveedores'))
    
    cursor = db.execute('SELECT * FROM proveedores WHERE id_proveedor = ?', (id,))
    proveedor = cursor.fetchone()
    return render_template('form_proveedor.html', proveedor=proveedor)

@app.route('/delete_proveedor/<int:id>')
def delete_proveedor(id):
    db = get_db()
    db.execute('DELETE FROM proveedores WHERE id_proveedor = ?', (id,))
    db.commit()
    return redirect(url_for('proveedores'))

# Rutas para manejar mercaderías
@app.route('/mercaderias')
def mercaderias():
    db = get_db()
    cursor = db.execute('SELECT * FROM mercaderias')
    mercaderias = cursor.fetchall()
    return render_template('mercaderias.html', mercaderias=mercaderias)

@app.route('/add_mercaderia', methods=['GET', 'POST'])
def add_mercaderia():
    db = get_db()
    if request.method == 'POST':
        mercaderia = {
            'nombre': request.form['nombre'],
            'detalle': request.form['detalle'],
            'unidad': request.form['unidad'],
            'id_proveedor': request.form['id_proveedor']
        }
        db.execute('INSERT INTO mercaderias (nombre, detalle, unidad, id_proveedor) VALUES (?, ?, ?, ?)', 
                   (mercaderia['nombre'], mercaderia['detalle'], mercaderia['unidad'], mercaderia['id_proveedor']))
        db.commit()
        return redirect(url_for('mercaderias'))

    # Obtener proveedores para la lista desplegable
    proveedores = db.execute('SELECT id_proveedor, nombre FROM proveedores').fetchall()
    
    return render_template('form_mercaderia.html', proveedores=proveedores)


@app.route('/edit_mercaderia/<int:id>', methods=['GET', 'POST'])
def edit_mercaderia(id):
    db = get_db()
    if request.method == 'POST':
        db.execute(
            'UPDATE mercaderias SET nombre = ?, detalle = ?, unidad = ?, id_proveedor = ? WHERE id_mercaderia = ?',
            (request.form['nombre'], request.form['detalle'], request.form['unidad'], request.form['id_proveedor'], id)
        )
        db.commit()
        return redirect(url_for('mercaderias'))

    cursor = db.execute('SELECT * FROM mercaderias WHERE id_mercaderia = ?', (id,))
    mercaderia = cursor.fetchone()
    return render_template('form_mercaderia.html', mercaderia=mercaderia)

@app.route('/delete_mercaderia/<int:id>')
def delete_mercaderia(id):
    db = get_db()
    db.execute('DELETE FROM mercaderias WHERE id_mercaderia = ?', (id,))
    db.commit()
    return redirect(url_for('mercaderias'))

# Rutas para manejar almacén
@app.route('/almacen')
def almacen():
    db = get_db()

    # Obtener todas las mercaderías del almacén, incluyendo su nombre y detalles desde la tabla de mercaderías
    cursor_almacen = db.execute('''
        SELECT a.id_mercaderia, m.nombre, m.detalle, m.unidad, a.cantidad, a.ultimo_movimiento, a.tipo_movimiento
        FROM almacen a
        JOIN mercaderias m ON a.id_mercaderia = m.id_mercaderia
    ''')
    almacen = cursor_almacen.fetchall()

    # Obtener todas las mercaderías disponibles para registrar una entrada (en otra tabla "mercaderias")
    cursor_mercaderias = db.execute('SELECT id_mercaderia, nombre FROM mercaderias')
    mercaderias = cursor_mercaderias.fetchall()

    return render_template('almacen.html', almacen=almacen, mercaderias=mercaderias)


@app.route('/add_almacen', methods=['GET', 'POST'])
def add_almacen():
    db = get_db()
    if request.method == 'POST':
        item = {
            'id_mercaderia': request.form['id_mercaderia'],
            'cantidad': int(request.form['cantidad']),
            'ultimo_movimiento': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'tipo_movimiento': 'entrada'
        }
        db.execute('INSERT INTO almacen (id_mercaderia, cantidad, ultimo_movimiento, tipo_movimiento) VALUES (?, ?, ?, ?)',
                   (item['id_mercaderia'], item['cantidad'], item['ultimo_movimiento'], item['tipo_movimiento']))
        db.commit()
        return redirect(url_for('almacen'))

    # Obtener mercaderías para la lista desplegable
    mercaderias = db.execute('SELECT id_mercaderia, nombre FROM mercaderias').fetchall()
    
    return render_template('form_almacen.html', mercaderias=mercaderias)

@app.route('/salida_almacen', methods=['GET', 'POST'])
def salida_almacen():
    if request.method == 'POST':
        db = get_db()
        db.execute(
            'UPDATE almacen SET cantidad = cantidad - ?, ultimo_movimiento = ?, tipo_movimiento = ? WHERE id_mercaderia = ?',
            (request.form['cantidad'], datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'salida', request.form['id_mercaderia'])
        )
        db.commit()
        return redirect(url_for('almacen'))
    return render_template('form_salida_almacen.html')

if __name__ == '__main__':
    app.run(debug=True)
