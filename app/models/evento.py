from app import db


class Evento(db.Model):
    __tablename__ = 'eventos_adversos'   # era 'eventos'

    id           = db.Column(db.Integer, primary_key=True)
    nombre       = db.Column(db.String(100), nullable=False)
    probabilidad = db.Column(db.Float, default=0.1)           # 0.0 – 1.0
    tipo         = db.Column(db.String(50), nullable=False)   # clima/accidente/fallo_mecanico/safety_car/penalizacion
    descripcion  = db.Column(db.Text, nullable=True)
    efecto_valor = db.Column(db.Float, default=-5.0)          # modificador de puntuación

    def to_dict(self):
        return {
            'id':           self.id,
            'nombre':       self.nombre,
            'probabilidad': self.probabilidad,
            'tipo':         self.tipo,
            'descripcion':  self.descripcion,
            'efecto_valor': self.efecto_valor,
        }
