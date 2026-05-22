from app import db
from datetime import datetime


class Mejora(db.Model):
    __tablename__ = 'mejoras'

    id = db.Column(db.Integer, primary_key=True)

    # Relaciones internas
    equipo_id = db.Column(db.Integer, db.ForeignKey('equipos.id'), nullable=False)
    temporada_id = db.Column(db.Integer, db.ForeignKey('temporadas.id'), nullable=True)

    # Datos descriptivos
    nombre = db.Column(db.String(100), nullable=True)
    descripcion = db.Column(db.String(255), nullable=True)

    # Tipo de mejora
    tipo = db.Column(db.String(50), nullable=False)
    # motor / aerodinamica / fiabilidad / estrategia / desarrollo / rendimiento_coche

    # Impacto de la mejora
    valor_agregado = db.Column(db.Float, default=0.0)
    impacto_valor_mercado = db.Column(db.Float, default=0.0)

    # Costo de la mejora
    costo = db.Column(db.Float, nullable=False)

    # Estado de la mejora
    estado = db.Column(db.String(30), default='pendiente')
    # pendiente / aplicada / cancelada

    aplicada = db.Column(db.Boolean, default=False)

    # Fecha
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_aplicacion = db.Column(db.DateTime, nullable=True)

    # Relaciones
    temporada = db.relationship('Temporada', backref='mejoras', lazy=True)

    def aplicar(self):
        """
        Aplica la mejora al equipo relacionado.
        Aumenta el atributo indicado en el equipo y actualiza su media.
        """

        if self.aplicada:
            raise ValueError("La mejora ya fue aplicada")

        if not self.equipo:
            raise ValueError("La mejora no tiene equipo asociado")

        if self.valor_agregado <= 0:
            raise ValueError("El valor agregado debe ser mayor a cero")

        if self.tipo == 'motor':
            self.equipo.motor = min(100.0, self.equipo.motor + self.valor_agregado)

        elif self.tipo == 'aerodinamica':
            self.equipo.aerodinamica = min(100.0, self.equipo.aerodinamica + self.valor_agregado)

        elif self.tipo == 'fiabilidad':
            self.equipo.fiabilidad = min(100.0, self.equipo.fiabilidad + self.valor_agregado)

        elif self.tipo == 'estrategia':
            self.equipo.estrategia = min(100.0, self.equipo.estrategia + self.valor_agregado)

        elif self.tipo == 'desarrollo':
            self.equipo.desarrollo = min(100.0, self.equipo.desarrollo + self.valor_agregado)

        elif self.tipo == 'rendimiento_coche':
            self.equipo.rendimiento_coche = min(
                100.0,
                self.equipo.rendimiento_coche + self.valor_agregado
            )

        else:
            raise ValueError("Tipo de mejora no valido")

        if hasattr(self.equipo, 'actualizar_media'):
            self.equipo.actualizar_media()

        if self.impacto_valor_mercado > 0:
            self.equipo.valor_mercado += self.impacto_valor_mercado

        self.aplicada = True
        self.estado = 'aplicada'
        self.fecha_aplicacion = datetime.utcnow()

        return self

    def cancelar(self):
        if self.aplicada:
            raise ValueError("No se puede cancelar una mejora ya aplicada")

        self.estado = 'cancelada'
        return self

    def to_dict(self):
        return {
            'id': self.id,

            'equipo_id': self.equipo_id,
            'equipo': self.equipo.nombre if self.equipo else None,
            'temporada_id': self.temporada_id,
            'temporada': self.temporada.anio if self.temporada else None,

            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'tipo': self.tipo,

            'valor_agregado': self.valor_agregado,
            'impacto_valor_mercado': self.impacto_valor_mercado,
            'costo': self.costo,

            'estado': self.estado,
            'aplicada': self.aplicada,

            'fecha': self.fecha.isoformat() if self.fecha else None,
            'fecha_aplicacion': self.fecha_aplicacion.isoformat() if self.fecha_aplicacion else None,
        }

    def to_dict_basico(self):
        return {
            'id': self.id,
            'equipo_id': self.equipo_id,
            'equipo': self.equipo.nombre if self.equipo else None,
            'tipo': self.tipo,
            'valor_agregado': self.valor_agregado,
            'costo': self.costo,
            'estado': self.estado,
            'aplicada': self.aplicada,
        }

    @staticmethod
    def crear_mejora(equipo_id, tipo, valor_agregado, costo, temporada_id=None, nombre=None, descripcion=None):
        """
        Crea una mejora interna para un equipo.
        No guarda automaticamente en la base de datos.
        """

        mejora = Mejora(
            equipo_id=equipo_id,
            temporada_id=temporada_id,
            nombre=nombre,
            descripcion=descripcion,
            tipo=tipo,
            valor_agregado=valor_agregado,
            impacto_valor_mercado=valor_agregado * 1000,
            costo=costo,
            estado='pendiente',
            aplicada=False
        )

        return mejora