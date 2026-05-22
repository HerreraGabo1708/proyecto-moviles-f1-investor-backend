from app import db


class Resultado(db.Model):
    __tablename__ = 'resultados'

    id = db.Column(db.Integer, primary_key=True)

    # Relaciones internas
    carrera_id = db.Column(db.Integer, db.ForeignKey('carreras.id'), nullable=False)
    piloto_id = db.Column(db.Integer, db.ForeignKey('pilotos.id'), nullable=False)
    equipo_id = db.Column(db.Integer, db.ForeignKey('equipos.id'), nullable=True)

    # Datos principales del resultado
    posicion = db.Column(db.Integer, nullable=False)
    puntos = db.Column(db.Float, default=0.0)

    # Datos provenientes de Jolpica
    jolpica_id = db.Column(db.String(150), nullable=True, unique=True)
    posicion_texto = db.Column(db.String(20), nullable=True)
    posicion_salida = db.Column(db.Integer, nullable=True)
    vueltas = db.Column(db.Integer, nullable=True)
    estado_jolpica = db.Column(db.String(100), nullable=True)

    # Datos internos / simulados
    tiempo = db.Column(db.Float, nullable=True)  # segundos simulados
    estado_final = db.Column(db.String(30), default='finalizado')  # finalizado / abandono / dsq

    # Relacion opcional con equipo
    equipo = db.relationship('Equipo', backref='resultados', lazy=True)

    def normalizar_estado_final(self):
        """
        Convierte el estado de Jolpica a un estado interno del juego.
        """

        if not self.estado_jolpica:
            self.estado_final = 'finalizado'
            return self.estado_final

        estado = self.estado_jolpica.lower()

        if estado == 'finished' or 'lap' in estado:
            self.estado_final = 'finalizado'
        elif 'accident' in estado or 'collision' in estado or 'engine' in estado or 'gearbox' in estado:
            self.estado_final = 'abandono'
        elif 'disqualified' in estado:
            self.estado_final = 'dsq'
        else:
            self.estado_final = 'finalizado'

        return self.estado_final

    def to_dict(self):
        return {
            'id': self.id,
            'carrera_id': self.carrera_id,
            'piloto_id': self.piloto_id,
            'piloto': self.piloto.nombre if self.piloto else None,
            'equipo_id': self.equipo_id,
            'equipo': self.equipo.nombre if self.equipo else None,

            'posicion': self.posicion,
            'puntos': self.puntos,

            'jolpica_id': self.jolpica_id,
            'posicion_texto': self.posicion_texto,
            'posicion_salida': self.posicion_salida,
            'vueltas': self.vueltas,
            'estado_jolpica': self.estado_jolpica,

            'tiempo': self.tiempo,
            'estado_final': self.estado_final,
        }

    def to_dict_basico(self):
        return {
            'id': self.id,
            'carrera_id': self.carrera_id,
            'piloto_id': self.piloto_id,
            'piloto': self.piloto.nombre if self.piloto else None,
            'equipo_id': self.equipo_id,
            'equipo': self.equipo.nombre if self.equipo else None,
            'posicion': self.posicion,
            'puntos': self.puntos,
            'estado_final': self.estado_final,
        }

    @staticmethod
    def from_jolpica(result_data, carrera_id, piloto_id, equipo_id=None):
        """
        Convierte un resultado de Jolpica en una instancia de Resultado.
        No guarda automaticamente en la base de datos.
        """

        driver_data = result_data.get('Driver', {})
        constructor_data = result_data.get('Constructor', {})

        driver_id = driver_data.get('driverId')
        constructor_id = constructor_data.get('constructorId')

        position_value = result_data.get('position')
        grid_value = result_data.get('grid')
        laps_value = result_data.get('laps')
        points_value = result_data.get('points')

        try:
            posicion = int(position_value) if position_value else 0
        except ValueError:
            posicion = 0

        try:
            posicion_salida = int(grid_value) if grid_value else None
        except ValueError:
            posicion_salida = None

        try:
            vueltas = int(laps_value) if laps_value else None
        except ValueError:
            vueltas = None

        try:
            puntos = float(points_value) if points_value else 0.0
        except ValueError:
            puntos = 0.0

        jolpica_id = None

        if carrera_id and driver_id:
            jolpica_id = f"race_{carrera_id}_driver_{driver_id}"

        resultado = Resultado(
            carrera_id=carrera_id,
            piloto_id=piloto_id,
            equipo_id=equipo_id,

            posicion=posicion,
            puntos=puntos,

            jolpica_id=jolpica_id,
            posicion_texto=result_data.get('positionText'),
            posicion_salida=posicion_salida,
            vueltas=vueltas,
            estado_jolpica=result_data.get('status'),

            tiempo=None,
            estado_final='finalizado'
        )

        resultado.normalizar_estado_final()

        return resultado