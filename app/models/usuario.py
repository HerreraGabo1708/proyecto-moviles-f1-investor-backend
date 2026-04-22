from app import db
from datetime import datetime


class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id        = db.Column(db.Integer, primary_key=True)
    nombre    = db.Column(db.String(100), nullable=False)
    correo    = db.Column(db.String(150), unique=True, nullable=False)
    password  = db.Column(db.String(255), nullable=False)
    capital   = db.Column(db.Float, default=1_000_000.0)   # Capital inicial: 1M
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

    inversiones = db.relationship('Inversion', backref='usuario', lazy=True)
    portfolio   = db.relationship('Portfolio', backref='usuario', lazy=True)

    def to_dict(self):
        return {
            'id':        self.id,
            'nombre':    self.nombre,
            'correo':    self.correo,
            'capital':   self.capital,
            'creado_en': self.creado_en.isoformat(),
        }
