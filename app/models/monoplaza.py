from app import db


class Monoplaza(db.Model):
    __tablename__ = 'monoplazas'

    id                   = db.Column(db.Integer, primary_key=True)
    piloto_id            = db.Column(db.Integer, db.ForeignKey('pilotos.id'), nullable=True)
    equipo_id            = db.Column(db.Integer, db.ForeignKey('equipos.id'), nullable=True)
    velocidad_punta      = db.Column(db.Float, default=300.0)   # km/h
    aceleracion          = db.Column(db.Float, default=50.0)
    aerodinamica         = db.Column(db.Float, default=50.0)
    fiabilidad           = db.Column(db.Float, default=50.0)
    desgaste_neumaticos  = db.Column(db.Float, default=50.0)
    foto                 = db.Column(db.String(255), nullable=True)

    equipo = db.relationship('Equipo', backref='monoplazas', lazy=True)

    def to_dict(self):
        return {
            'id':                  self.id,
            'piloto_id':           self.piloto_id,
            'piloto':              self.piloto.nombre if self.piloto else None,
            'equipo_id':           self.equipo_id,
            'equipo':              self.equipo.nombre if self.equipo else None,
            'velocidad_punta':     self.velocidad_punta,
            'aceleracion':         self.aceleracion,
            'aerodinamica':        self.aerodinamica,
            'fiabilidad':          self.fiabilidad,
            'desgaste_neumaticos': self.desgaste_neumaticos,
            'foto':                self.foto,
        }
