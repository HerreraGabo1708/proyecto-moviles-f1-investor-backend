from app import db


class Evento(db.Model):
    __tablename__ = 'eventos_adversos'

    id = db.Column(db.Integer, primary_key=True)

    # Datos principales del evento
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)

    # Probabilidad de ocurrencia
    probabilidad = db.Column(db.Float, default=0.1)  # 0.0 - 1.0

    # Tipo de evento
    tipo = db.Column(db.String(50), nullable=False)
    # clima / accidente / fallo_mecanico / safety_car / penalizacion / mercado / rendimiento

    # A quien afecta principalmente
    afecta_a = db.Column(db.String(30), default='piloto')
    # piloto / equipo / carrera / monoplaza / mercado

    # Impacto general
    efecto_valor = db.Column(db.Float, default=-5.0)

    # Impactos especificos de simulacion
    efecto_rendimiento = db.Column(db.Float, default=0.0)
    efecto_fiabilidad = db.Column(db.Float, default=0.0)
    efecto_forma = db.Column(db.Float, default=0.0)
    efecto_mercado = db.Column(db.Float, default=0.0)

    # Condiciones donde aplica mejor
    tipo_pista = db.Column(db.String(30), nullable=True)
    # seco / mojado / mixto / cualquiera

    clima = db.Column(db.String(30), nullable=True)
    # seco / lluvia / nublado / extremo / cualquiera

    # Estado
    activo = db.Column(db.Boolean, default=True)

    def ocurre(self, random_value):
        """
        Determina si el evento ocurre segun un valor aleatorio entre 0 y 1.
        """

        return random_value <= self.probabilidad

    def aplicar_a_piloto(self, piloto):
        """
        Aplica el efecto del evento sobre un piloto.
        No guarda automaticamente en la base de datos.
        """

        if not piloto:
            raise ValueError("Debe indicar un piloto")

        if self.efecto_forma != 0:
            piloto.forma_actual = max(
                0.0,
                min(100.0, piloto.forma_actual + self.efecto_forma)
            )

        if self.efecto_rendimiento != 0:
            piloto.skill = max(
                0.0,
                min(100.0, piloto.skill + self.efecto_rendimiento)
            )

        if self.efecto_mercado != 0:
            piloto.valor_mercado = max(
                0.0,
                piloto.valor_mercado + self.efecto_mercado
            )

        if hasattr(piloto, 'actualizar_media'):
            piloto.actualizar_media()

        return piloto

    def aplicar_a_equipo(self, equipo):
        """
        Aplica el efecto del evento sobre un equipo.
        No guarda automaticamente en la base de datos.
        """

        if not equipo:
            raise ValueError("Debe indicar un equipo")

        if self.efecto_rendimiento != 0:
            equipo.rendimiento_coche = max(
                0.0,
                min(100.0, equipo.rendimiento_coche + self.efecto_rendimiento)
            )

        if self.efecto_fiabilidad != 0:
            equipo.fiabilidad = max(
                0.0,
                min(100.0, equipo.fiabilidad + self.efecto_fiabilidad)
            )

        if self.efecto_mercado != 0:
            equipo.valor_mercado = max(
                0.0,
                equipo.valor_mercado + self.efecto_mercado
            )

        if hasattr(equipo, 'actualizar_media'):
            equipo.actualizar_media()

        return equipo

    def aplicar_a_monoplaza(self, monoplaza):
        """
        Aplica el efecto del evento sobre un monoplaza.
        No guarda automaticamente en la base de datos.
        """

        if not monoplaza:
            raise ValueError("Debe indicar un monoplaza")

        if self.efecto_rendimiento != 0:
            monoplaza.aceleracion = max(
                0.0,
                min(100.0, monoplaza.aceleracion + self.efecto_rendimiento)
            )

        if self.efecto_fiabilidad != 0:
            monoplaza.fiabilidad = max(
                0.0,
                min(100.0, monoplaza.fiabilidad + self.efecto_fiabilidad)
            )

        if hasattr(monoplaza, 'actualizar_media'):
            monoplaza.actualizar_media()

        return monoplaza

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,

            'probabilidad': self.probabilidad,
            'tipo': self.tipo,
            'afecta_a': self.afecta_a,

            'efecto_valor': self.efecto_valor,
            'efecto_rendimiento': self.efecto_rendimiento,
            'efecto_fiabilidad': self.efecto_fiabilidad,
            'efecto_forma': self.efecto_forma,
            'efecto_mercado': self.efecto_mercado,

            'tipo_pista': self.tipo_pista,
            'clima': self.clima,
            'activo': self.activo,
        }

    def to_dict_basico(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'probabilidad': self.probabilidad,
            'tipo': self.tipo,
            'afecta_a': self.afecta_a,
            'efecto_valor': self.efecto_valor,
            'activo': self.activo,
        }

    @staticmethod
    def crear_evento_base(nombre, tipo, probabilidad, efecto_valor, afecta_a='piloto', descripcion=None):
        """
        Crea un evento adverso base.
        No guarda automaticamente en la base de datos.
        """

        evento = Evento(
            nombre=nombre,
            tipo=tipo,
            probabilidad=probabilidad,
            efecto_valor=efecto_valor,
            afecta_a=afecta_a,
            descripcion=descripcion,
            activo=True
        )

        return evento