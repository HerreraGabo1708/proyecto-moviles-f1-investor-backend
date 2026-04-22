from app import db


class Neumatico(db.Model):
    __tablename__ = 'neumaticos'

    id                  = db.Column(db.Integer, primary_key=True)
    tipo                = db.Column(db.String(30), nullable=False)   # blando/medio/duro/intermedio/lluvia
    velocidad_base      = db.Column(db.Float, default=1.0)           # multiplicador
    desgaste_por_vuelta = db.Column(db.Float, default=1.0)
    temp_min            = db.Column(db.Float, default=70.0)
    temp_max            = db.Column(db.Float, default=100.0)
    tipo_pista          = db.Column(db.String(30), default='seco')   # seco/mojado/mixto

    def to_dict(self):
        return {
            'id':                  self.id,
            'tipo':                self.tipo,
            'velocidad_base':      self.velocidad_base,
            'desgaste_por_vuelta': self.desgaste_por_vuelta,
            'temp_min':            self.temp_min,
            'temp_max':            self.temp_max,
            'tipo_pista':          self.tipo_pista,
        }
