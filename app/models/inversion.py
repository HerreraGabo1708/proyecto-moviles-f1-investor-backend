from app import db
from datetime import datetime


class Inversion(db.Model):
    __tablename__ = 'inversiones'

    id = db.Column(db.Integer, primary_key=True)

    # Usuario que realiza la operacion
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

    # Activo comprado o vendido
    tipo_activo = db.Column(db.String(20), nullable=False)  # piloto / equipo
    activo_id = db.Column(db.Integer, nullable=False)

    # Datos externos opcionales
    jolpica_id = db.Column(db.String(100), nullable=True)
    nombre_activo = db.Column(db.String(150), nullable=True)

    # Operacion
    tipo_operacion = db.Column(db.String(10), nullable=False)  # compra / venta
    cantidad = db.Column(db.Float, default=1.0)

    # Valores financieros
    precio_unitario = db.Column(db.Float, nullable=False, default=0.0)
    monto = db.Column(db.Float, nullable=False)
    comision = db.Column(db.Float, default=0.0)

    # Valor del activo en el momento de la operacion
    valor_mercado_momento = db.Column(db.Float, nullable=True)

    # Estado de la inversion
    estado = db.Column(db.String(20), default='completada')  # completada / cancelada / pendiente

    # Fecha de la transaccion
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    def calcular_monto_total(self):
        self.monto = round((self.precio_unitario * self.cantidad) + self.comision, 2)
        return self.monto

    def es_compra(self):
        return self.tipo_operacion == 'compra'

    def es_venta(self):
        return self.tipo_operacion == 'venta'

    def to_dict(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,

            'tipo_activo': self.tipo_activo,
            'activo_id': self.activo_id,
            'jolpica_id': self.jolpica_id,
            'nombre_activo': self.nombre_activo,

            'tipo_operacion': self.tipo_operacion,
            'cantidad': self.cantidad,

            'precio_unitario': self.precio_unitario,
            'monto': self.monto,
            'comision': self.comision,
            'valor_mercado_momento': self.valor_mercado_momento,

            'estado': self.estado,
            'fecha': self.fecha.isoformat() if self.fecha else None,
        }

    def to_dict_basico(self):
        return {
            'id': self.id,
            'tipo_activo': self.tipo_activo,
            'activo_id': self.activo_id,
            'nombre_activo': self.nombre_activo,
            'tipo_operacion': self.tipo_operacion,
            'cantidad': self.cantidad,
            'monto': self.monto,
            'fecha': self.fecha.isoformat() if self.fecha else None,
        }

    @staticmethod
    def crear_compra(usuario_id, tipo_activo, activo_id, nombre_activo, precio_unitario, cantidad=1.0, jolpica_id=None):
        """
        Crea una inversion de tipo compra.
        No guarda automaticamente en la base de datos.
        """

        inversion = Inversion(
            usuario_id=usuario_id,
            tipo_activo=tipo_activo,
            activo_id=activo_id,
            jolpica_id=jolpica_id,
            nombre_activo=nombre_activo,
            tipo_operacion='compra',
            cantidad=cantidad,
            precio_unitario=precio_unitario,
            monto=0.0,
            comision=0.0,
            valor_mercado_momento=precio_unitario,
            estado='completada'
        )

        inversion.calcular_monto_total()

        return inversion

    @staticmethod
    def crear_venta(usuario_id, tipo_activo, activo_id, nombre_activo, precio_unitario, cantidad=1.0, jolpica_id=None):
        """
        Crea una inversion de tipo venta.
        No guarda automaticamente en la base de datos.
        """

        inversion = Inversion(
            usuario_id=usuario_id,
            tipo_activo=tipo_activo,
            activo_id=activo_id,
            jolpica_id=jolpica_id,
            nombre_activo=nombre_activo,
            tipo_operacion='venta',
            cantidad=cantidad,
            precio_unitario=precio_unitario,
            monto=0.0,
            comision=0.0,
            valor_mercado_momento=precio_unitario,
            estado='completada'
        )

        inversion.calcular_monto_total()

        return inversion