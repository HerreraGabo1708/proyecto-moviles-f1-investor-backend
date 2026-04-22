from app import db
from datetime import datetime


class Mejora(db.Model):
    __tablename__ = 'mejoras'

    id             = db.Column(db.Integer, primary_key=True)
    equipo_id      = db.Column(db.Integer, db.ForeignKey('equipos.id'), nullable=False)
    tipo           = db.Column(db.String(50), nullable=False)   # motor/aerodinamica/fiabilidad/estrategia
    valor_agregado = db.Column(db.Float, default=0.0)
    costo          = db.Column(db.Float, nullable=False)
    fecha          = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id':             self.id,
            'equipo_id':      self.equipo_id,
            'tipo':           self.tipo,
            'valor_agregado': self.valor_agregado,
            'costo':          self.costo,
            'fecha':          self.fecha.isoformat(),
        }
