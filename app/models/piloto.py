from app import db


class Piloto(db.Model):
    __tablename__ = 'pilotos'

    id            = db.Column(db.Integer, primary_key=True)
    nombre        = db.Column(db.String(100), nullable=False)
    numero        = db.Column(db.Integer, nullable=False)
    edad          = db.Column(db.Integer, default=20)
    equipo_id     = db.Column(db.Integer, db.ForeignKey('equipos.id'), nullable=True)
    skill         = db.Column(db.Float, default=50.0)
    consistencia  = db.Column(db.Float, default=50.0)
    racecraft     = db.Column(db.Float, default=50.0)
    experiencia   = db.Column(db.Float, default=50.0)
    potencial     = db.Column(db.Float, default=50.0)
    media         = db.Column(db.Float, default=50.0)
    valor_mercado = db.Column(db.Float, default=50_000.0)
    forma_actual  = db.Column(db.Float, default=50.0)   # 0-100
    foto          = db.Column(db.String(255), nullable=True)

    monoplaza  = db.relationship('Monoplaza', backref='piloto', uselist=False, lazy=True)
    resultados = db.relationship('Resultado', backref='piloto', lazy=True)

    def to_dict(self):
        return {
            'id':            self.id,
            'nombre':        self.nombre,
            'numero':        self.numero,
            'edad':          self.edad,
            'equipo_id':     self.equipo_id,
            'equipo':        self.equipo.nombre if self.equipo else None,
            'skill':         self.skill,
            'consistencia':  self.consistencia,
            'racecraft':     self.racecraft,
            'experiencia':   self.experiencia,
            'potencial':     self.potencial,
            'media':         self.media,
            'valor_mercado': self.valor_mercado,
            'forma_actual':  self.forma_actual,
            'foto':          self.foto,
        }
