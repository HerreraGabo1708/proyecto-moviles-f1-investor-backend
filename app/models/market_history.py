from app import db
from datetime import datetime


class MarketHistory(db.Model):
    __tablename__ = 'market_history'

    id = db.Column(db.Integer, primary_key=True)

    tipo_activo = db.Column(db.String(20), nullable=False)  # piloto / equipo
    activo_id = db.Column(db.Integer, nullable=False)

    jolpica_id = db.Column(db.String(100), nullable=True)
    nombre_activo = db.Column(db.String(150), nullable=True)

    temporada_id = db.Column(db.Integer, db.ForeignKey('temporadas.id'), nullable=True)
    carrera_id = db.Column(db.Integer, db.ForeignKey('carreras.id'), nullable=True)

    valor_anterior = db.Column(db.Float, nullable=True)
    valor_nuevo = db.Column(db.Float, nullable=False)
    variacion = db.Column(db.Float, default=0.0)
    porcentaje_variacion = db.Column(db.Float, default=0.0)

    motivo = db.Column(db.String(100), nullable=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    temporada = db.relationship('Temporada', backref='market_history', lazy=True)
    carrera = db.relationship('Carrera', backref='market_history', lazy=True)

    def calcular_variacion(self):
        if self.valor_anterior is None:
            self.variacion = 0.0
            self.porcentaje_variacion = 0.0
            return self

        self.variacion = round(self.valor_nuevo - self.valor_anterior, 2)

        if self.valor_anterior > 0:
            self.porcentaje_variacion = round(
                (self.variacion / self.valor_anterior) * 100,
                2
            )
        else:
            self.porcentaje_variacion = 0.0

        return self

    def to_dict(self):
        return {
            'id': self.id,
            'tipo_activo': self.tipo_activo,
            'activo_id': self.activo_id,
            'jolpica_id': self.jolpica_id,
            'nombre_activo': self.nombre_activo,
            'temporada_id': self.temporada_id,
            'carrera_id': self.carrera_id,
            'valor_anterior': self.valor_anterior,
            'valor_nuevo': self.valor_nuevo,
            'variacion': self.variacion,
            'porcentaje_variacion': self.porcentaje_variacion,
            'motivo': self.motivo,
            'fecha': self.fecha.isoformat() if self.fecha else None,
        }