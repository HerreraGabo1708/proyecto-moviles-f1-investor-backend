from app import db


class Neumatico(db.Model):
    __tablename__ = 'neumaticos'

    id = db.Column(db.Integer, primary_key=True)

    # Datos principales
    tipo = db.Column(db.String(30), nullable=False)
    # blando / medio / duro / intermedio / lluvia

    nombre = db.Column(db.String(80), nullable=True)
    descripcion = db.Column(db.String(255), nullable=True)

    # Rendimiento base
    velocidad_base = db.Column(db.Float, default=1.0)
    desgaste_por_vuelta = db.Column(db.Float, default=1.0)

    # Nuevos atributos de simulacion
    agarre_base = db.Column(db.Float, default=50.0)
    durabilidad_base = db.Column(db.Float, default=50.0)

    # Temperatura ideal
    temp_min = db.Column(db.Float, default=70.0)
    temp_max = db.Column(db.Float, default=100.0)

    # Condicion recomendada de pista
    tipo_pista = db.Column(db.String(30), default='seco')
    # seco / mojado / mixto

    # Visual / estado
    color = db.Column(db.String(30), nullable=True)
    activo = db.Column(db.Boolean, default=True)

    def esta_en_temperatura_optima(self, temperatura):
        """
        Verifica si el neumatico esta dentro de su rango ideal de temperatura.
        """

        return self.temp_min <= temperatura <= self.temp_max

    def calcular_rendimiento(self, temperatura_pista, tipo_pista_actual):
        """
        Calcula un multiplicador simple de rendimiento segun temperatura y pista.
        """

        rendimiento = self.velocidad_base

        if not self.esta_en_temperatura_optima(temperatura_pista):
            rendimiento -= 0.05

        if self.tipo_pista != tipo_pista_actual:
            rendimiento -= 0.10

        return round(max(0.5, rendimiento), 2)

    def calcular_desgaste_total(self, vueltas):
        """
        Calcula el desgaste estimado del neumatico despues de cierta cantidad de vueltas.
        """

        if vueltas <= 0:
            return 0.0

        desgaste = vueltas * self.desgaste_por_vuelta
        return round(desgaste, 2)

    def to_dict(self):
        return {
            'id': self.id,
            'tipo': self.tipo,
            'nombre': self.nombre,
            'descripcion': self.descripcion,

            'velocidad_base': self.velocidad_base,
            'desgaste_por_vuelta': self.desgaste_por_vuelta,
            'agarre_base': self.agarre_base,
            'durabilidad_base': self.durabilidad_base,

            'temp_min': self.temp_min,
            'temp_max': self.temp_max,
            'tipo_pista': self.tipo_pista,

            'color': self.color,
            'activo': self.activo,
        }

    def to_dict_basico(self):
        return {
            'id': self.id,
            'tipo': self.tipo,
            'nombre': self.nombre,
            'velocidad_base': self.velocidad_base,
            'desgaste_por_vuelta': self.desgaste_por_vuelta,
            'tipo_pista': self.tipo_pista,
            'color': self.color,
            'activo': self.activo,
        }

    @staticmethod
    def crear_neumatico_base(tipo):
        """
        Crea un neumatico con valores base segun el tipo.
        No guarda automaticamente en la base de datos.
        """

        tipo = tipo.lower()

        configuraciones = {
            'blando': {
                'nombre': 'Blando',
                'velocidad_base': 1.08,
                'desgaste_por_vuelta': 1.35,
                'agarre_base': 90.0,
                'durabilidad_base': 40.0,
                'temp_min': 85.0,
                'temp_max': 110.0,
                'tipo_pista': 'seco',
                'color': 'rojo'
            },
            'medio': {
                'nombre': 'Medio',
                'velocidad_base': 1.03,
                'desgaste_por_vuelta': 1.00,
                'agarre_base': 75.0,
                'durabilidad_base': 65.0,
                'temp_min': 80.0,
                'temp_max': 105.0,
                'tipo_pista': 'seco',
                'color': 'amarillo'
            },
            'duro': {
                'nombre': 'Duro',
                'velocidad_base': 0.98,
                'desgaste_por_vuelta': 0.70,
                'agarre_base': 60.0,
                'durabilidad_base': 90.0,
                'temp_min': 75.0,
                'temp_max': 100.0,
                'tipo_pista': 'seco',
                'color': 'blanco'
            },
            'intermedio': {
                'nombre': 'Intermedio',
                'velocidad_base': 0.95,
                'desgaste_por_vuelta': 1.10,
                'agarre_base': 70.0,
                'durabilidad_base': 60.0,
                'temp_min': 60.0,
                'temp_max': 90.0,
                'tipo_pista': 'mixto',
                'color': 'verde'
            },
            'lluvia': {
                'nombre': 'Lluvia',
                'velocidad_base': 0.90,
                'desgaste_por_vuelta': 1.20,
                'agarre_base': 85.0,
                'durabilidad_base': 55.0,
                'temp_min': 50.0,
                'temp_max': 85.0,
                'tipo_pista': 'mojado',
                'color': 'azul'
            }
        }

        config = configuraciones.get(tipo)

        if not config:
            raise ValueError("Tipo de neumatico no valido")

        return Neumatico(
            tipo=tipo,
            nombre=config['nombre'],
            descripcion=f"Neumatico tipo {config['nombre']}",
            velocidad_base=config['velocidad_base'],
            desgaste_por_vuelta=config['desgaste_por_vuelta'],
            agarre_base=config['agarre_base'],
            durabilidad_base=config['durabilidad_base'],
            temp_min=config['temp_min'],
            temp_max=config['temp_max'],
            tipo_pista=config['tipo_pista'],
            color=config['color'],
            activo=True
        )