from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
import random
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)

class Base(DeclarativeBase):
    pass
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
    nombre_estudiante = StringField("Ingrese el nombre del estudiante.", validators=[DataRequired()])
    codigo_estudiante = StringField("Ingrese el código del estudiante.", validators=[DataRequired()])
    correo_estudiante = StringField("Ingrese el correo del estudiante.", validators=[DataRequired()])
    telefono_estudiante = StringField("Ingrese el teléfono del estudiante.", validators=[DataRequired()])
    modelo_carro = StringField("Ingrese el modelo de carro del estudiante.", validators=[DataRequired()])
    placa_carro= StringField("Ingrese la placa del carro correspondiente.", validators=[DataRequired()])
    submit = SubmitField("Ingresar registro.")

@app.route('/')
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
        new_student = StudentForm(
            nombre_estudiante=form.nombre_estudiante.data,
            codigo_estudiante=form.codigo_estudiante.data,
            correo_estudiante= form.correo_estudiante.data,
            telefono_estudiante=form.telefono_estudiante.data,
            modelo_carro= form.modelo_carro.data,
            placa_carro=form.placa_carro.data
        )
        db.session.add(new_student)
        db.session.commit()
        return redirect(url_for("all"))
    return render_template("make-student.html", form=form)


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
    app.run(debug=True)
