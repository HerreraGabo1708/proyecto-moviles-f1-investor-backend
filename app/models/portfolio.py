from app import db


class Portfolio(db.Model):
    __tablename__ = 'portfolio'

    id                    = db.Column(db.Integer, primary_key=True)
    usuario_id            = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    tipo_activo           = db.Column(db.String(20), nullable=False)   # piloto / equipo
    activo_id             = db.Column(db.Integer,   nullable=False)
    cantidad              = db.Column(db.Float, default=0.0)
    valor_promedio_compra = db.Column(db.Float, default=0.0)

    def to_dict(self):
        return {
            'id':                    self.id,
            'usuario_id':            self.usuario_id,
            'tipo_activo':           self.tipo_activo,
            'activo_id':             self.activo_id,
            'cantidad':              self.cantidad,
            'valor_promedio_compra': self.valor_promedio_compra,
        }
