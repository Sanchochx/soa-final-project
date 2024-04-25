from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
import random

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

@app.route('/')
def data():
    result = db.session.execute(db.select(ParkingUsta))
    data = result.scalars().all()
    return render_template("index.html", all_data=data)

@app.route("/data/<int:data_id>")
def show_data_by_id(data_id):
    requested_data = db.get_or_404(ParkingUsta, data_id)
    return render_template("data.html", data=requested_data)

@app.route("/obtener_registro")
def registro_aleatorio():
    result = db.session.execute(db.select(ParkingUsta))
    all_data = result.scalars().all()
    registro_aleatorio = random.choice(all_data)
    return jsonify(registro=registro_aleatorio.to_dict())

@app.route("/todos_los_registros")
def todos_los_registros():
    result = db.session.execute(db.select(ParkingUsta).order_by(ParkingUsta.nombre_estudiante))
    all_data = result.scalars().all()
    return jsonify(registro=[registro.to_dict() for registro in all_data])

@app.route("/anadir", methods=["POST"])
def anadir_registro():
    nuevo_registro = ParkingUsta(
        nombre_estudiante=request.form.get("nombre_estudiante"),
        codigo_estudiante=request.form.get("codigo_estudiante"),
        correo_estudiante=request.form.get("correo_estudiante"),
        telefono_estudiante=request.form.get("telefono_estudiante"),
        modelo_carro=request.form.get("modelo_carro"),
        placa_carro=request.form.get("placa_carro"),
    )
    db.session.add(nuevo_registro)
    db.session.commit()
    return jsonify(response={"success": "Registro nuevo agregado satisfactoriamente."})


@app.route("/actualizar-telefono/<int:telefono_id>", methods=["PATCH"])
def actualizar_registro_telefono(telefono_id):
    nuevo_telefono = request.args.get("nuevo_telefono")
    registro = db.get_or_404(ParkingUsta, telefono_id)
    if registro:
        registro.telefono_estudiante = nuevo_telefono
        db.session.commit()
        return jsonify(response={"success": "Satisfactoriamente actualizado el número de teléfono."}), 200
    else:
        return jsonify(error={"Not Found": "Lastimosamente un registro con ese id no fue encontrado en la base de datos."}), 404

@app.route("/report-closed/<int:registro_id>", methods=["DELETE"])
def borrar_registro(registro_id):
    api_key = request.args.get("api-key")
    if api_key == "TopSecretAPIKey":
        registro = db.get_or_404(ParkingUsta, registro_id)
        if registro:
            db.session.delete(registro)
            db.session.commit()
            return jsonify(response={"success": "Registro eliminado satisfactoriamente."}), 200
        else:
            return jsonify(error={"Not Found": "Lastimosamente un registro con ese id no fue encontrado en la base de datos."}), 404
    else:
        return jsonify(error={"Forbidden": "Lo lamento, eso no es permitido. Verifica haber ingresado la api_key correcta."}), 403

if __name__ == '__main__':
    app.run(debug=True)
