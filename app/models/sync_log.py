from app import db
from datetime import datetime


class SyncLog(db.Model):
    __tablename__ = 'sync_logs'

    id = db.Column(db.Integer, primary_key=True)

    fuente = db.Column(db.String(50), default='jolpica')
    endpoint = db.Column(db.String(255), nullable=False)
    temporada = db.Column(db.Integer, nullable=True)

    estado = db.Column(db.String(30), default='exitoso')  # exitoso / error
    mensaje = db.Column(db.Text, nullable=True)

    registros_procesados = db.Column(db.Integer, default=0)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'fuente': self.fuente,
            'endpoint': self.endpoint,
            'temporada': self.temporada,
            'estado': self.estado,
            'mensaje': self.mensaje,
            'registros_procesados': self.registros_procesados,
            'fecha': self.fecha.isoformat() if self.fecha else None,
        }