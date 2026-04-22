from app import db
from datetime import datetime


class Inversion(db.Model):
    __tablename__ = 'inversiones'

    id             = db.Column(db.Integer, primary_key=True)
    usuario_id     = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    tipo_activo    = db.Column(db.String(20), nullable=False)   # piloto / equipo
    activo_id      = db.Column(db.Integer,   nullable=False)
    tipo_operacion = db.Column(db.String(10), nullable=False)   # compra / venta
    monto          = db.Column(db.Float, nullable=False)
    cantidad       = db.Column(db.Float, default=1.0)
    fecha          = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id':             self.id,
            'usuario_id':     self.usuario_id,
            'tipo_activo':    self.tipo_activo,
            'activo_id':      self.activo_id,
            'tipo_operacion': self.tipo_operacion,
            'monto':          self.monto,
            'cantidad':       self.cantidad,
            'fecha':          self.fecha.isoformat(),
        }
