from app import db


class Portfolio(db.Model):
    __tablename__ = 'portfolio'

    id = db.Column(db.Integer, primary_key=True)

    # Usuario propietario del activo
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

    # Activo dentro del juego
    tipo_activo = db.Column(db.String(20), nullable=False)  # piloto / equipo
    activo_id = db.Column(db.Integer, nullable=False)

    # Datos externos opcionales
    jolpica_id = db.Column(db.String(100), nullable=True)
    nombre_activo = db.Column(db.String(150), nullable=True)

    # Cantidad actual en posesion
    cantidad = db.Column(db.Float, default=0.0)

    # Precio promedio al que el usuario compro este activo
    valor_promedio_compra = db.Column(db.Float, default=0.0)

    # Valor actual del activo en el mercado
    valor_actual = db.Column(db.Float, default=0.0)

    # Estado del item del portfolio
    activo = db.Column(db.Boolean, default=True)

    def valor_invertido_total(self):
        return round(self.cantidad * self.valor_promedio_compra, 2)

    def valor_actual_total(self):
        return round(self.cantidad * self.valor_actual, 2)

    def ganancia_perdida(self):
        return round(self.valor_actual_total() - self.valor_invertido_total(), 2)

    def porcentaje_rendimiento(self):
        invertido = self.valor_invertido_total()

        if invertido <= 0:
            return 0.0

        return round((self.ganancia_perdida() / invertido) * 100, 2)

    def actualizar_por_compra(self, cantidad_comprada, precio_unitario):
        """
        Actualiza la cantidad y el valor promedio cuando el usuario compra mas.
        """

        if cantidad_comprada <= 0:
            raise ValueError("La cantidad comprada debe ser mayor a cero")

        if precio_unitario <= 0:
            raise ValueError("El precio unitario debe ser mayor a cero")

        valor_actual_invertido = self.cantidad * self.valor_promedio_compra
        nuevo_valor_invertido = cantidad_comprada * precio_unitario

        nueva_cantidad = self.cantidad + cantidad_comprada

        if nueva_cantidad <= 0:
            self.cantidad = 0.0
            self.valor_promedio_compra = 0.0
            return self

        self.valor_promedio_compra = round(
            (valor_actual_invertido + nuevo_valor_invertido) / nueva_cantidad,
            2
        )

        self.cantidad = nueva_cantidad
        self.valor_actual = precio_unitario
        self.activo = self.cantidad > 0

        return self

    def actualizar_por_venta(self, cantidad_vendida):
        """
        Resta cantidad cuando el usuario vende.
        """

        if cantidad_vendida <= 0:
            raise ValueError("La cantidad vendida debe ser mayor a cero")

        if cantidad_vendida > self.cantidad:
            raise ValueError("No hay suficiente cantidad disponible para vender")

        self.cantidad -= cantidad_vendida

        if self.cantidad <= 0:
            self.cantidad = 0.0
            self.activo = False

        return self

    def actualizar_valor_actual(self, nuevo_valor):
        if nuevo_valor < 0:
            raise ValueError("El valor actual no puede ser negativo")

        self.valor_actual = nuevo_valor
        return self

    def to_dict(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,

            'tipo_activo': self.tipo_activo,
            'activo_id': self.activo_id,
            'jolpica_id': self.jolpica_id,
            'nombre_activo': self.nombre_activo,

            'cantidad': self.cantidad,
            'valor_promedio_compra': self.valor_promedio_compra,
            'valor_actual': self.valor_actual,

            'valor_invertido_total': self.valor_invertido_total(),
            'valor_actual_total': self.valor_actual_total(),
            'ganancia_perdida': self.ganancia_perdida(),
            'porcentaje_rendimiento': self.porcentaje_rendimiento(),

            'activo': self.activo,
        }

    def to_dict_basico(self):
        return {
            'id': self.id,
            'tipo_activo': self.tipo_activo,
            'activo_id': self.activo_id,
            'nombre_activo': self.nombre_activo,
            'cantidad': self.cantidad,
            'valor_promedio_compra': self.valor_promedio_compra,
            'valor_actual': self.valor_actual,
            'ganancia_perdida': self.ganancia_perdida(),
            'porcentaje_rendimiento': self.porcentaje_rendimiento(),
            'activo': self.activo,
        }

    @staticmethod
    def crear_item(usuario_id, tipo_activo, activo_id, nombre_activo, cantidad, precio_unitario, jolpica_id=None):
        """
        Crea un nuevo item de portfolio.
        No guarda automaticamente en la base de datos.
        """

        item = Portfolio(
            usuario_id=usuario_id,
            tipo_activo=tipo_activo,
            activo_id=activo_id,
            jolpica_id=jolpica_id,
            nombre_activo=nombre_activo,
            cantidad=cantidad,
            valor_promedio_compra=precio_unitario,
            valor_actual=precio_unitario,
            activo=True
        )

        return item