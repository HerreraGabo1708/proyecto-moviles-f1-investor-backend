from app import db


class Monoplaza(db.Model):
    __tablename__ = 'monoplazas'

    id = db.Column(db.Integer, primary_key=True)

    # Relaciones internas
    piloto_id = db.Column(db.Integer, db.ForeignKey('pilotos.id'), nullable=True)
    equipo_id = db.Column(db.Integer, db.ForeignKey('equipos.id'), nullable=True)
    temporada_id = db.Column(db.Integer, db.ForeignKey('temporadas.id'), nullable=True)

    # Datos descriptivos del monoplaza
    nombre = db.Column(db.String(100), nullable=True)
    codigo_modelo = db.Column(db.String(50), nullable=True)

    # Atributos de rendimiento simulados
    velocidad_punta = db.Column(db.Float, default=300.0)  # km/h
    aceleracion = db.Column(db.Float, default=50.0)
    aerodinamica = db.Column(db.Float, default=50.0)
    fiabilidad = db.Column(db.Float, default=50.0)
    desgaste_neumaticos = db.Column(db.Float, default=50.0)

    # Valor general calculado
    media = db.Column(db.Float, default=50.0)

    # Estado interno
    activo = db.Column(db.Boolean, default=True)

    # Multimedia
    foto = db.Column(db.String(255), nullable=True)

    # Relaciones
    equipo = db.relationship('Equipo', backref='monoplazas', lazy=True)
    temporada = db.relationship('Temporada', backref='monoplazas', lazy=True)

    def actualizar_media(self):
        self.media = round((
            self.aceleracion +
            self.aerodinamica +
            self.fiabilidad +
            self.desgaste_neumaticos
        ) / 4, 2)

        return self.media

    def aplicar_mejora(self, tipo_mejora, incremento):
        """
        Aplica una mejora simple al monoplaza.
        El incremento se limita para evitar valores mayores a 100.
        """

        if incremento <= 0:
            raise ValueError("El incremento debe ser mayor a cero")

        if tipo_mejora == 'velocidad_punta':
            self.velocidad_punta += incremento

        elif tipo_mejora == 'aceleracion':
            self.aceleracion = min(100.0, self.aceleracion + incremento)

        elif tipo_mejora == 'aerodinamica':
            self.aerodinamica = min(100.0, self.aerodinamica + incremento)

        elif tipo_mejora == 'fiabilidad':
            self.fiabilidad = min(100.0, self.fiabilidad + incremento)

        elif tipo_mejora == 'desgaste_neumaticos':
            self.desgaste_neumaticos = min(100.0, self.desgaste_neumaticos + incremento)

        else:
            raise ValueError("Tipo de mejora no valido")

        self.actualizar_media()
        return self

    def to_dict(self):
        return {
            'id': self.id,

            'piloto_id': self.piloto_id,
            'piloto': self.piloto.nombre if self.piloto else None,
            'equipo_id': self.equipo_id,
            'equipo': self.equipo.nombre if self.equipo else None,
            'temporada_id': self.temporada_id,
            'temporada': self.temporada.anio if self.temporada else None,

            'nombre': self.nombre,
            'codigo_modelo': self.codigo_modelo,

            'velocidad_punta': self.velocidad_punta,
            'aceleracion': self.aceleracion,
            'aerodinamica': self.aerodinamica,
            'fiabilidad': self.fiabilidad,
            'desgaste_neumaticos': self.desgaste_neumaticos,
            'media': self.media,

            'activo': self.activo,
            'foto': self.foto,
        }

    def to_dict_basico(self):
        return {
            'id': self.id,
            'piloto_id': self.piloto_id,
            'piloto': self.piloto.nombre if self.piloto else None,
            'equipo_id': self.equipo_id,
            'equipo': self.equipo.nombre if self.equipo else None,
            'temporada_id': self.temporada_id,
            'nombre': self.nombre,
            'codigo_modelo': self.codigo_modelo,
            'media': self.media,
            'activo': self.activo,
            'foto': self.foto,
        }

    @staticmethod
    def crear_desde_equipo(equipo, temporada_id=None, piloto_id=None):
        """
        Crea un monoplaza base a partir de los atributos de un equipo.
        No guarda automaticamente en la base de datos.
        """

        nombre = f"Monoplaza {equipo.nombre}" if equipo else "Monoplaza"

        monoplaza = Monoplaza(
            piloto_id=piloto_id,
            equipo_id=equipo.id if equipo else None,
            temporada_id=temporada_id,

            nombre=nombre,
            codigo_modelo=None,

            velocidad_punta=300.0,
            aceleracion=equipo.rendimiento_coche if equipo else 50.0,
            aerodinamica=equipo.aerodinamica if equipo else 50.0,
            fiabilidad=equipo.fiabilidad if equipo else 50.0,
            desgaste_neumaticos=50.0,

            media=50.0,
            activo=True,
            foto=None
        )

        monoplaza.actualizar_media()

        return monoplaza