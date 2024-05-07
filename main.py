from random import random
from flask import Flask, render_template, redirect, url_for, jsonify, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_bootstrap import Bootstrap5
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String
from flask_wtf import FlaskForm
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = True
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)
Session(app)

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'sql_inyeccion_db'
}

class Base(DeclarativeBase):
    pass

#-------STUDENTS DATABASE---------#
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking-usta.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

class ParkingUsta(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre_estudiante: Mapped[str] = mapped_column(String(250), unique=False, nullable=False)
    codigo_estudiante: Mapped[str] = mapped_column(String(250), unique=False, nullable=False)
    correo_estudiante: Mapped[str] = mapped_column(String(250), unique=False, nullable=False)
    telefono_estudiante: Mapped[str] = mapped_column(String(250), unique=False, nullable=False)
    modelo_carro: Mapped[str] = mapped_column(String(250), unique=False, nullable=False)
    placa_carro: Mapped[str] = mapped_column(String(250), unique=False, nullable=False)


    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

with app.app_context():
    db.create_all()

class StudentForm(FlaskForm):
    nombre_estudiante = StringField("Ingrese el nombre del estudiante:", validators=[DataRequired()])
    codigo_estudiante = StringField("Ingrese el código del estudiante:", validators=[DataRequired()])
    correo_estudiante = StringField("Ingrese el correo del estudiante:", validators=[DataRequired()])
    telefono_estudiante = StringField("Ingrese el teléfono del estudiante:", validators=[DataRequired()])
    modelo_carro = StringField("Ingrese el modelo de carro del estudiante:", validators=[DataRequired()])
    placa_carro= StringField("Ingrese la placa del carro correspondiente:", validators=[DataRequired()])
    submit = SubmitField("Ingresar registro.")

def autenticar_usuario(username, password):
    try:
        conexion = mysql.connector.connect(**db_config)
        cursor = conexion.cursor()
        consulta = "SELECT * FROM usuarios WHERE username = %s"
        cursor.execute(consulta, (username,))
        usuario = cursor.fetchone()

        if usuario and check_password_hash(usuario[2], password):
            return True
        else:
            return False

    except mysql.connector.Error as error:
        print(f"Error al conectarse a la base de datos: {error}")
        return False

def crear_usuario_db(username, password):
    try:
        conexion = mysql.connector.connect(**db_config)
        cursor = conexion.cursor()
        consulta = "SELECT * FROM usuarios WHERE username = %s"
        cursor.execute(consulta, (username,))
        resultado = cursor.fetchone()

        if resultado:
            flash("El nombre de usuario ya existe. Elija otro.", "danger")
            conexion.close()
            return False

        hashed_password = generate_password_hash(password, method='scrypt')
        consulta = "INSERT INTO usuarios (username, password) VALUES (%s, %s)"
        cursor.execute(consulta, (username, hashed_password))

        conexion.commit()
        conexion.close()

        return True

    except mysql.connector.Error as error:
        print(f"Error al crear el usuario: {error}")
        return False

def obtener_usuarios():
    try:
        conexion = mysql.connector.connect(**db_config)
        cursor = conexion.cursor()
        consulta = "SELECT id, username FROM usuarios"
        cursor.execute(consulta)
        usuarios = cursor.fetchall()
        conexion.close()
        return usuarios

    except mysql.connector.Error as error:
        print(f"Error al obtener la lista de usuarios: {error}")
        return []

def eliminar_usuario_db(usuario_id):
    try:
        conexion = mysql.connector.connect(**db_config)
        cursor = conexion.cursor()

        # Verificar si el usuario que se va a eliminar es el mismo que está en sesión
        usuario_en_sesion = obtener_usuario_por_username(session['username'])
        if usuario_en_sesion and usuario_en_sesion[0] == usuario_id:
            flash("No puedes eliminar tu propia cuenta mientras estás en sesión", "warning")
            return False

        consulta = "DELETE FROM usuarios WHERE id = %s"
        cursor.execute(consulta, (usuario_id,))
        conexion.commit()
        conexion.close()
        return True

    except mysql.connector.Error as error:
        print(f"Error al eliminar el usuario: {error}")
        return False


def obtener_usuario_por_id(usuario_id):
    try:
        conexion = mysql.connector.connect(**db_config)
        cursor = conexion.cursor()
        consulta = "SELECT * FROM usuarios WHERE id = %s"
        cursor.execute(consulta, (usuario_id,))
        usuario = cursor.fetchone()
        conexion.close()
        return usuario

    except mysql.connector.Error as error:
        print(f"Error al obtener el usuario por ID: {error}")
        return None


def obtener_usuario_por_username(username):
    try:
        conexion = mysql.connector.connect(**db_config)
        cursor = conexion.cursor()
        consulta = "SELECT * FROM usuarios WHERE username = %s"
        cursor.execute(consulta, (username,))
        usuario = cursor.fetchone()
        conexion.close()
        return usuario

    except mysql.connector.Error as error:
        print(f"Error al obtener el usuario por nombre de usuario: {error}")
        return None



@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if autenticar_usuario(username, password):
            session['username'] = username
            flash("Inicio de sesión exitoso", "success")
            return redirect(url_for('students'))
        else:
            flash("Autenticación fallida", "danger")

    return render_template('login.html')

@app.route('/registrarse', methods=['GET', 'POST'])
def registrarse():
    if request.method == 'POST':
        nuevo_username = request.form['nuevo_username']
        nuevo_password = request.form['nuevo_password']

        if crear_usuario_db(nuevo_username, nuevo_password):
            flash("Usuario creado con éxito", "success")
            return redirect(url_for('login'))
        else:
            flash("Error al crear el usuario", "danger")

    return render_template('registrarse.html')

@app.route('/menu_principal')
def menu_principal():
    if 'username' in session:
        usuarios = obtener_usuarios()
        # Aquí obtienes la información del usuario específico que deseas mostrar
        usuario = obtener_usuario_por_username(session['username'])
        return render_template('menu_principal.html', username=session['username'], usuario=usuario, usuarios=usuarios)
    else:
        flash("Debes iniciar sesión primero", "warning")
        return redirect(url_for('login'))


@app.route('/cerrar_sesion')
def cerrar_sesion():
    session.pop('username', None)
    flash("Sesión cerrada", "info")
    return redirect(url_for('login'))

@app.route('/crear_usuario', methods=['GET', 'POST'])
def crear_usuario():
    if 'username' not in session:
        flash("Debes iniciar sesión primero", "warning")
        return redirect(url_for('login'))

    if request.method == 'POST':
        nuevo_username = request.form['nuevo_username']
        nuevo_password = request.form['nuevo_password']

        if crear_usuario_db(nuevo_username, nuevo_password):
            flash("Usuario creado con éxito", "success")
            return redirect(url_for('menu_principal'))
        else:
            flash("Error al crear el usuario", "danger")

    return render_template('crear_usuario.html')

@app.route('/eliminar_usuario/<int:usuario_id>', methods=['GET', 'POST'])
def eliminar_usuario(usuario_id):
    if 'username' not in session:
        flash("Debes iniciar sesión primero", "warning")
        return redirect(url_for('login'))

    if eliminar_usuario_db(usuario_id):
        flash("Usuario eliminado con éxito", "success")
    else:
        flash("Error al eliminar el usuario", "danger")

    return redirect(url_for('menu_principal'))

@app.route('/students')
def students():
    result = db.session.execute(db.select(ParkingUsta))
    student = result.scalars().all()
    return render_template("index.html", all_students=student)

@app.route("/student/<int:student_id>")
def show_student(student_id):
    requested_student = db.get_or_404(ParkingUsta, student_id)
    return render_template("student.html", student=requested_student)

@app.route("/new-student", methods=["GET", "POST"])
def add_student():
    form = StudentForm()
    if form.validate_on_submit():
        new_student = ParkingUsta(
            nombre_estudiante=form.nombre_estudiante.data,
            codigo_estudiante=form.codigo_estudiante.data,
            correo_estudiante= form.correo_estudiante.data,
            telefono_estudiante=form.telefono_estudiante.data,
            modelo_carro= form.modelo_carro.data,
            placa_carro=form.placa_carro.data
        )
        db.session.add(new_student)
        db.session.commit()
        return redirect(url_for("students"))
    return render_template("make-student.html", form=form)

@app.route("/edit-student/<int:student_id>", methods=["GET", "POST"])
def edit_student(student_id):
    student = db.get_or_404(ParkingUsta, student_id)
    edit_form = StudentForm(
        nombre_estudiante=student.nombre_estudiante,
        codigo_estudiante=student.codigo_estudiante,
        correo_estudiante=student.correo_estudiante,
        telefono_estudiante=student.telefono_estudiante,
        modelo_carro=student.modelo_carro,
        placa_carro=student.placa_carro
    )
    if edit_form.validate_on_submit():
        student.nombre_estudiante = edit_form.nombre_estudiante.data
        student.codigo_estudiante = edit_form.codigo_estudiante.data
        student.correo_estudiante = edit_form.correo_estudiante.data
        student.telefono_estudiante = edit_form.telefono_estudiante.data
        student.modelo_carro = edit_form.modelo_carro.data
        student.placa_carro = edit_form.placa_carro.data
        db.session.commit()
        return redirect(url_for("show_student", student_id=student.id))
    return render_template("make-student.html", form=edit_form, is_edit=True)

@app.route("/delete/<int:student_id>")
def delete_student_f(student_id):
    student_to_delete = db.get_or_404(ParkingUsta, student_id)
    db.session.delete(student_to_delete)
    db.session.commit()
    return redirect(url_for('students'))

@app.route("/documentacion_api/")
def doc_api():
    return render_template("api.html")

# *-----------------POSTMAN -------------------*

@app.route("/all_students")
def all():
    result = db.session.execute(db.select(ParkingUsta).order_by(ParkingUsta.nombre_estudiante))
    all_data = result.scalars().all()
    return jsonify(registro=[registro.to_dict() for registro in all_data])

@app.route("/student")
def student():
    result = db.session.execute(db.select(ParkingUsta))
    all_data = result.scalars().all()
    random_student = random.choice(all_data)
    return jsonify(registro=random_student.to_dict())


@app.route("/update_phone/<int:phone_id>", methods=["PATCH"])
def update_student_phone(phone_id):
    new_phone = request.args.get("new_phone")
    data_phone = db.get_or_404(ParkingUsta, phone_id)
    if data_phone:
        data_phone.telefono_estudiante = new_phone
        db.session.commit()
        return jsonify(response={"success": "Satisfactoriamente actualizado el número de teléfono."}), 200
    else:
        return jsonify(error={"Not Found": "Lastimosamente un registro con ese id no fue encontrado en la base de datos."}), 404

@app.route("/add_student", methods=["POST"])
def new_student():
    new_student = ParkingUsta(
        nombre_estudiante=request.form.get("nombre_estudiante"),
        codigo_estudiante=request.form.get("codigo_estudiante"),
        correo_estudiante=request.form.get("correo_estudiante"),
        telefono_estudiante=request.form.get("telefono_estudiante"),
        modelo_carro=(request.form.get("modelo_carro")),
        placa_carro=(request.form.get("placa_carro")),
    )
    db.session.add(new_student)
    db.session.commit()
    return jsonify(response={"success": "Satisfactoriamente agregado el nuevo estudiante."})

@app.route("/report-closed/<int:registro_id>", methods=["DELETE"])
def delete_student(student_id):
    api_key = request.args.get("api-key")
    if api_key == "TopSecretAPIKey":
        student = db.get_or_404(ParkingUsta, student_id)
        if student:
            db.session.delete(student)
            db.session.commit()
            return jsonify(response={"success": "Registro eliminado satisfactoriamente."}), 200
        else:
            return jsonify(error={"Not Found": "Lastimosamente un registro con ese id no fue encontrado en la base de datos."}), 404
    else:
        return jsonify(error={"Forbidden": "Lo lamento, eso no es permitido. Verifica haber ingresado la api_key correcta."}), 403

if __name__ == '__main__':
    app.run(debug=True, port=8001)
