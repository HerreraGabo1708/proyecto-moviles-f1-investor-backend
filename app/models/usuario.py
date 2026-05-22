from app import db
from datetime import datetime


class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)

    # Datos de cuenta
    nombre = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=True)
    correo = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    # Datos del juego / inversion
    capital_inicial = db.Column(db.Float, default=1_000_000.0)
    capital = db.Column(db.Float, default=1_000_000.0)

    # Estado de cuenta
    rol = db.Column(db.String(30), default='jugador')  # jugador / admin
    activo = db.Column(db.Boolean, default=True)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_acceso = db.Column(db.DateTime, nullable=True)

    # Relaciones
    inversiones = db.relationship('Inversion', backref='usuario', lazy=True)
    portfolio = db.relationship('Portfolio', backref='usuario', lazy=True)

    def actualizar_ultimo_acceso(self):
        self.ultimo_acceso = datetime.utcnow()
        return self.ultimo_acceso

    def tiene_capital_suficiente(self, monto):
        return self.capital >= monto

    def debitar_capital(self, monto):
        if monto <= 0:
            raise ValueError("El monto debe ser mayor a cero")

        if not self.tiene_capital_suficiente(monto):
            raise ValueError("Capital insuficiente")

        self.capital -= monto
        return self.capital

    def acreditar_capital(self, monto):
        if monto <= 0:
            raise ValueError("El monto debe ser mayor a cero")

        self.capital += monto
        return self.capital

    def calcular_valor_portfolio(self):
        total = 0.0

        for item in self.portfolio:
            if hasattr(item, 'valor_actual_total'):
                total += item.valor_actual_total()

        return round(total, 2)

    def calcular_patrimonio_total(self):
        return round(self.capital + self.calcular_valor_portfolio(), 2)

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'username': self.username,
            'correo': self.correo,

            'capital_inicial': self.capital_inicial,
            'capital': self.capital,
            'valor_portfolio': self.calcular_valor_portfolio(),
            'patrimonio_total': self.calcular_patrimonio_total(),

            'rol': self.rol,
            'activo': self.activo,
            'creado_en': self.creado_en.isoformat() if self.creado_en else None,
            'ultimo_acceso': self.ultimo_acceso.isoformat() if self.ultimo_acceso else None,
        }

    def to_dict_basico(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'username': self.username,
            'correo': self.correo,
            'capital': self.capital,
            'rol': self.rol,
            'activo': self.activo,
        }