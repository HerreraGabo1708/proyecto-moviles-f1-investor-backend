DROP DATABASE IF EXISTS f1_investment_db;
CREATE DATABASE f1_investment_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE f1_investment_db;

-- ==========================================================
-- TABLA: usuarios
-- ==========================================================

CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    username VARCHAR(80) NULL UNIQUE,
    correo VARCHAR(150) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,

    capital_inicial FLOAT DEFAULT 1000000.0,
    capital FLOAT DEFAULT 1000000.0,

    rol VARCHAR(30) DEFAULT 'jugador',
    activo BOOLEAN DEFAULT TRUE,

    creado_en DATETIME DEFAULT CURRENT_TIMESTAMP,
    ultimo_acceso DATETIME NULL
) ENGINE=InnoDB;


-- ==========================================================
-- TABLA: temporadas
-- ==========================================================

CREATE TABLE temporadas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    anio INT NOT NULL UNIQUE,
    activa BOOLEAN DEFAULT FALSE,

    fecha_inicio DATE NULL,
    fecha_fin DATE NULL,

    jolpica_id VARCHAR(20) NULL UNIQUE,
    sincronizada BOOLEAN DEFAULT FALSE,
    ultima_sincronizacion DATETIME NULL,

    estado VARCHAR(30) DEFAULT 'pendiente'
) ENGINE=InnoDB;


-- ==========================================================
-- TABLA: equipos
-- ==========================================================

CREATE TABLE equipos (
    id INT AUTO_INCREMENT PRIMARY KEY,

    nombre VARCHAR(100) NOT NULL,

    jolpica_id VARCHAR(100) NULL UNIQUE,
    nacionalidad VARCHAR(100) NULL,
    temporada INT NULL,
    activo BOOLEAN DEFAULT TRUE,

    rendimiento_coche FLOAT DEFAULT 50.0,
    aerodinamica FLOAT DEFAULT 50.0,
    motor FLOAT DEFAULT 50.0,
    fiabilidad FLOAT DEFAULT 50.0,
    estrategia FLOAT DEFAULT 50.0,
    desarrollo FLOAT DEFAULT 50.0,
    media FLOAT DEFAULT 50.0,

    valor_mercado FLOAT DEFAULT 100000.0,
    presupuesto FLOAT DEFAULT 500000000.0,

    imagen VARCHAR(255) NULL
) ENGINE=InnoDB;


-- ==========================================================
-- TABLA: pilotos
-- ==========================================================

CREATE TABLE pilotos (
    id INT AUTO_INCREMENT PRIMARY KEY,

    nombre VARCHAR(100) NOT NULL,
    numero INT NULL,
    edad INT DEFAULT 20,

    equipo_id INT NULL,

    jolpica_id VARCHAR(100) NULL UNIQUE,
    codigo VARCHAR(10) NULL,
    nacionalidad VARCHAR(100) NULL,
    fecha_nacimiento DATE NULL,
    temporada INT NULL,
    activo BOOLEAN DEFAULT TRUE,

    skill FLOAT DEFAULT 50.0,
    consistencia FLOAT DEFAULT 50.0,
    racecraft FLOAT DEFAULT 50.0,
    experiencia FLOAT DEFAULT 50.0,
    potencial FLOAT DEFAULT 50.0,
    media FLOAT DEFAULT 50.0,

    valor_mercado FLOAT DEFAULT 50000.0,
    forma_actual FLOAT DEFAULT 50.0,

    foto VARCHAR(255) NULL,

    CONSTRAINT fk_pilotos_equipo
        FOREIGN KEY (equipo_id) REFERENCES equipos(id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
) ENGINE=InnoDB;


-- ==========================================================
-- TABLA: circuitos
-- ==========================================================

CREATE TABLE circuitos (
    id INT AUTO_INCREMENT PRIMARY KEY,

    nombre_gp VARCHAR(100) NOT NULL,
    nombre_circuito VARCHAR(100) NOT NULL,
    pais VARCHAR(80) NOT NULL,

    jolpica_id VARCHAR(100) NULL UNIQUE,
    localidad VARCHAR(100) NULL,
    latitud FLOAT NULL,
    longitud_geo FLOAT NULL,
    activo BOOLEAN DEFAULT TRUE,

    longitud FLOAT DEFAULT 5.0,
    num_curvas INT DEFAULT 15,
    tipo_pista VARCHAR(50) DEFAULT 'mixto',
    zonas_drs INT DEFAULT 2,
    nivel_tecnico FLOAT DEFAULT 50.0,
    nivel_desgaste FLOAT DEFAULT 50.0,
    nivel_sobrepaso FLOAT DEFAULT 50.0,

    imagen VARCHAR(255) NULL
) ENGINE=InnoDB;


-- ==========================================================
-- TABLA: carreras
-- ==========================================================

CREATE TABLE carreras (
    id INT AUTO_INCREMENT PRIMARY KEY,

    temporada_id INT NOT NULL,
    circuito_id INT NOT NULL,

    jolpica_id VARCHAR(100) NULL UNIQUE,
    temporada_anio INT NULL,
    round_number INT NULL,
    nombre_gp VARCHAR(150) NULL,

    fecha DATE NULL,
    hora TIME NULL,

    estado VARCHAR(20) DEFAULT 'pendiente',

    CONSTRAINT fk_carreras_temporada
        FOREIGN KEY (temporada_id) REFERENCES temporadas(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_carreras_circuito
        FOREIGN KEY (circuito_id) REFERENCES circuitos(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
) ENGINE=InnoDB;


-- ==========================================================
-- TABLA: resultados
-- ==========================================================

CREATE TABLE resultados (
    id INT AUTO_INCREMENT PRIMARY KEY,

    carrera_id INT NOT NULL,
    piloto_id INT NOT NULL,
    equipo_id INT NULL,

    posicion INT NOT NULL,
    puntos FLOAT DEFAULT 0.0,

    jolpica_id VARCHAR(150) NULL UNIQUE,
    posicion_texto VARCHAR(20) NULL,
    posicion_salida INT NULL,
    vueltas INT NULL,
    estado_jolpica VARCHAR(100) NULL,

    tiempo FLOAT NULL,
    estado_final VARCHAR(30) DEFAULT 'finalizado',

    CONSTRAINT fk_resultados_carrera
        FOREIGN KEY (carrera_id) REFERENCES carreras(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_resultados_piloto
        FOREIGN KEY (piloto_id) REFERENCES pilotos(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_resultados_equipo
        FOREIGN KEY (equipo_id) REFERENCES equipos(id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
) ENGINE=InnoDB;


-- ==========================================================
-- TABLA: inversiones
-- ==========================================================

CREATE TABLE inversiones (
    id INT AUTO_INCREMENT PRIMARY KEY,

    usuario_id INT NOT NULL,

    tipo_activo VARCHAR(20) NOT NULL,
    activo_id INT NOT NULL,

    jolpica_id VARCHAR(100) NULL,
    nombre_activo VARCHAR(150) NULL,

    tipo_operacion VARCHAR(10) NOT NULL,
    cantidad FLOAT DEFAULT 1.0,

    precio_unitario FLOAT NOT NULL DEFAULT 0.0,
    monto FLOAT NOT NULL,
    comision FLOAT DEFAULT 0.0,
    valor_mercado_momento FLOAT NULL,

    estado VARCHAR(20) DEFAULT 'completada',

    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_inversiones_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;


-- ==========================================================
-- TABLA: portfolio
-- ==========================================================

CREATE TABLE portfolio (
    id INT AUTO_INCREMENT PRIMARY KEY,

    usuario_id INT NOT NULL,

    tipo_activo VARCHAR(20) NOT NULL,
    activo_id INT NOT NULL,

    jolpica_id VARCHAR(100) NULL,
    nombre_activo VARCHAR(150) NULL,

    cantidad FLOAT DEFAULT 0.0,
    valor_promedio_compra FLOAT DEFAULT 0.0,
    valor_actual FLOAT DEFAULT 0.0,

    activo BOOLEAN DEFAULT TRUE,

    CONSTRAINT fk_portfolio_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT uq_portfolio_usuario_activo
        UNIQUE (usuario_id, tipo_activo, activo_id)
) ENGINE=InnoDB;


-- ==========================================================
-- TABLA: monoplazas
-- ==========================================================

CREATE TABLE monoplazas (
    id INT AUTO_INCREMENT PRIMARY KEY,

    piloto_id INT NULL,
    equipo_id INT NULL,
    temporada_id INT NULL,

    nombre VARCHAR(100) NULL,
    codigo_modelo VARCHAR(50) NULL,

    velocidad_punta FLOAT DEFAULT 300.0,
    aceleracion FLOAT DEFAULT 50.0,
    aerodinamica FLOAT DEFAULT 50.0,
    fiabilidad FLOAT DEFAULT 50.0,
    desgaste_neumaticos FLOAT DEFAULT 50.0,

    media FLOAT DEFAULT 50.0,
    activo BOOLEAN DEFAULT TRUE,

    foto VARCHAR(255) NULL,

    CONSTRAINT fk_monoplazas_piloto
        FOREIGN KEY (piloto_id) REFERENCES pilotos(id)
        ON DELETE SET NULL
        ON UPDATE CASCADE,

    CONSTRAINT fk_monoplazas_equipo
        FOREIGN KEY (equipo_id) REFERENCES equipos(id)
        ON DELETE SET NULL
        ON UPDATE CASCADE,

    CONSTRAINT fk_monoplazas_temporada
        FOREIGN KEY (temporada_id) REFERENCES temporadas(id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
) ENGINE=InnoDB;


-- ==========================================================
-- TABLA: mejoras
-- ==========================================================

CREATE TABLE mejoras (
    id INT AUTO_INCREMENT PRIMARY KEY,

    equipo_id INT NOT NULL,
    temporada_id INT NULL,

    nombre VARCHAR(100) NULL,
    descripcion VARCHAR(255) NULL,

    tipo VARCHAR(50) NOT NULL,

    valor_agregado FLOAT DEFAULT 0.0,
    impacto_valor_mercado FLOAT DEFAULT 0.0,

    costo FLOAT NOT NULL,

    estado VARCHAR(30) DEFAULT 'pendiente',
    aplicada BOOLEAN DEFAULT FALSE,

    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_aplicacion DATETIME NULL,

    CONSTRAINT fk_mejoras_equipo
        FOREIGN KEY (equipo_id) REFERENCES equipos(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_mejoras_temporada
        FOREIGN KEY (temporada_id) REFERENCES temporadas(id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
) ENGINE=InnoDB;


-- ==========================================================
-- TABLA: neumaticos
-- ==========================================================

CREATE TABLE neumaticos (
    id INT AUTO_INCREMENT PRIMARY KEY,

    tipo VARCHAR(30) NOT NULL,
    nombre VARCHAR(80) NULL,
    descripcion VARCHAR(255) NULL,

    velocidad_base FLOAT DEFAULT 1.0,
    desgaste_por_vuelta FLOAT DEFAULT 1.0,

    agarre_base FLOAT DEFAULT 50.0,
    durabilidad_base FLOAT DEFAULT 50.0,

    temp_min FLOAT DEFAULT 70.0,
    temp_max FLOAT DEFAULT 100.0,

    tipo_pista VARCHAR(30) DEFAULT 'seco',

    color VARCHAR(30) NULL,
    activo BOOLEAN DEFAULT TRUE
) ENGINE=InnoDB;


-- ==========================================================
-- TABLA: eventos_adversos
-- ==========================================================

CREATE TABLE eventos_adversos (
    id INT AUTO_INCREMENT PRIMARY KEY,

    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT NULL,

    probabilidad FLOAT DEFAULT 0.1,
    tipo VARCHAR(50) NOT NULL,

    afecta_a VARCHAR(30) DEFAULT 'piloto',

    efecto_valor FLOAT DEFAULT -5.0,
    efecto_rendimiento FLOAT DEFAULT 0.0,
    efecto_fiabilidad FLOAT DEFAULT 0.0,
    efecto_forma FLOAT DEFAULT 0.0,
    efecto_mercado FLOAT DEFAULT 0.0,

    tipo_pista VARCHAR(30) NULL,
    clima VARCHAR(30) NULL,

    activo BOOLEAN DEFAULT TRUE
) ENGINE=InnoDB;


-- ==========================================================
-- TABLA: equipos_f2
-- ==========================================================

CREATE TABLE equipos_f2 (
    id INT AUTO_INCREMENT PRIMARY KEY,

    nombre VARCHAR(100) NOT NULL,
    nacionalidad VARCHAR(100) NULL,

    rendimiento_coche FLOAT DEFAULT 50.0,
    aerodinamica FLOAT DEFAULT 50.0,
    motor FLOAT DEFAULT 50.0,
    fiabilidad FLOAT DEFAULT 50.0,
    estrategia FLOAT DEFAULT 50.0,
    desarrollo FLOAT DEFAULT 50.0,
    media FLOAT DEFAULT 50.0,

    valor_mercado FLOAT DEFAULT 50000.0,
    presupuesto FLOAT DEFAULT 100000000.0,

    temporada_id INT NULL,
    activo BOOLEAN DEFAULT TRUE,

    imagen VARCHAR(255) NULL,

    CONSTRAINT fk_equipos_f2_temporada
        FOREIGN KEY (temporada_id) REFERENCES temporadas(id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
) ENGINE=InnoDB;


-- ==========================================================
-- TABLA: market_history
-- ==========================================================

CREATE TABLE market_history (
    id INT AUTO_INCREMENT PRIMARY KEY,

    tipo_activo VARCHAR(20) NOT NULL,
    activo_id INT NOT NULL,

    jolpica_id VARCHAR(100) NULL,
    nombre_activo VARCHAR(150) NULL,

    temporada_id INT NULL,
    carrera_id INT NULL,

    valor_anterior FLOAT NULL,
    valor_nuevo FLOAT NOT NULL,
    variacion FLOAT DEFAULT 0.0,
    porcentaje_variacion FLOAT DEFAULT 0.0,

    motivo VARCHAR(100) NULL,

    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_market_history_temporada
        FOREIGN KEY (temporada_id) REFERENCES temporadas(id)
        ON DELETE SET NULL
        ON UPDATE CASCADE,

    CONSTRAINT fk_market_history_carrera
        FOREIGN KEY (carrera_id) REFERENCES carreras(id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
) ENGINE=InnoDB;


-- ==========================================================
-- TABLA: sync_logs
-- ==========================================================

CREATE TABLE sync_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,

    fuente VARCHAR(50) DEFAULT 'jolpica',
    endpoint VARCHAR(255) NOT NULL,
    temporada INT NULL,

    estado VARCHAR(30) DEFAULT 'exitoso',
    mensaje TEXT NULL,

    registros_procesados INT DEFAULT 0,

    fecha DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;


-- ==========================================================
-- INDICES RECOMENDADOS
-- ==========================================================

CREATE INDEX idx_pilotos_equipo_id ON pilotos(equipo_id);
CREATE INDEX idx_pilotos_jolpica_id ON pilotos(jolpica_id);
CREATE INDEX idx_pilotos_temporada ON pilotos(temporada);
CREATE INDEX idx_pilotos_activo ON pilotos(activo);

CREATE INDEX idx_equipos_jolpica_id ON equipos(jolpica_id);
CREATE INDEX idx_equipos_temporada ON equipos(temporada);
CREATE INDEX idx_equipos_activo ON equipos(activo);

CREATE INDEX idx_circuitos_jolpica_id ON circuitos(jolpica_id);
CREATE INDEX idx_carreras_temporada_id ON carreras(temporada_id);
CREATE INDEX idx_carreras_circuito_id ON carreras(circuito_id);
CREATE INDEX idx_carreras_jolpica_id ON carreras(jolpica_id);
CREATE INDEX idx_carreras_temporada_anio ON carreras(temporada_anio);
CREATE INDEX idx_carreras_estado ON carreras(estado);

CREATE INDEX idx_resultados_carrera_id ON resultados(carrera_id);
CREATE INDEX idx_resultados_piloto_id ON resultados(piloto_id);
CREATE INDEX idx_resultados_equipo_id ON resultados(equipo_id);
CREATE INDEX idx_resultados_jolpica_id ON resultados(jolpica_id);

CREATE INDEX idx_inversiones_usuario_id ON inversiones(usuario_id);
CREATE INDEX idx_inversiones_tipo_activo ON inversiones(tipo_activo, activo_id);
CREATE INDEX idx_inversiones_fecha ON inversiones(fecha);

CREATE INDEX idx_portfolio_usuario_id ON portfolio(usuario_id);
CREATE INDEX idx_portfolio_activo ON portfolio(tipo_activo, activo_id);

CREATE INDEX idx_monoplazas_piloto_id ON monoplazas(piloto_id);
CREATE INDEX idx_monoplazas_equipo_id ON monoplazas(equipo_id);
CREATE INDEX idx_monoplazas_temporada_id ON monoplazas(temporada_id);

CREATE INDEX idx_mejoras_equipo_id ON mejoras(equipo_id);
CREATE INDEX idx_mejoras_temporada_id ON mejoras(temporada_id);

CREATE INDEX idx_market_history_activo ON market_history(tipo_activo, activo_id);
CREATE INDEX idx_market_history_temporada ON market_history(temporada_id);
CREATE INDEX idx_market_history_carrera ON market_history(carrera_id);
CREATE INDEX idx_market_history_fecha ON market_history(fecha);

CREATE INDEX idx_sync_logs_estado ON sync_logs(estado);
CREATE INDEX idx_sync_logs_fuente ON sync_logs(fuente);
CREATE INDEX idx_sync_logs_temporada ON sync_logs(temporada);


-- ==========================================================
-- SEED: NEUMATICOS BASE
-- ==========================================================

INSERT INTO neumaticos (
    tipo,
    nombre,
    descripcion,
    velocidad_base,
    desgaste_por_vuelta,
    agarre_base,
    durabilidad_base,
    temp_min,
    temp_max,
    tipo_pista,
    color,
    activo
) VALUES
('blando', 'Blando', 'Neumatico rapido con alto desgaste', 1.08, 1.35, 90.0, 40.0, 85.0, 110.0, 'seco', 'rojo', TRUE),
('medio', 'Medio', 'Neumatico balanceado para condiciones secas', 1.03, 1.00, 75.0, 65.0, 80.0, 105.0, 'seco', 'amarillo', TRUE),
('duro', 'Duro', 'Neumatico resistente con menor velocidad', 0.98, 0.70, 60.0, 90.0, 75.0, 100.0, 'seco', 'blanco', TRUE),
('intermedio', 'Intermedio', 'Neumatico para pista mixta o ligeramente mojada', 0.95, 1.10, 70.0, 60.0, 60.0, 90.0, 'mixto', 'verde', TRUE),
('lluvia', 'Lluvia', 'Neumatico para condiciones de lluvia intensa', 0.90, 1.20, 85.0, 55.0, 50.0, 85.0, 'mojado', 'azul', TRUE);


-- ==========================================================
-- SEED: EVENTOS ADVERSOS BASE
-- ==========================================================

INSERT INTO eventos_adversos (
    nombre,
    probabilidad,
    tipo,
    descripcion,
    efecto_valor,
    afecta_a,
    efecto_rendimiento,
    efecto_fiabilidad,
    efecto_forma,
    efecto_mercado,
    tipo_pista,
    clima,
    activo
) VALUES
('Lluvia intensa', 0.12, 'clima', 'La lluvia cambia las condiciones de carrera y aumenta el riesgo de errores.', -3.0, 'carrera', -2.0, 0.0, 0.0, -1000.0, 'mojado', 'lluvia', TRUE),
('Accidente leve', 0.08, 'accidente', 'Un piloto sufre un incidente menor durante la carrera.', -6.0, 'piloto', -4.0, 0.0, -5.0, -5000.0, NULL, NULL, TRUE),
('Fallo mecanico', 0.07, 'fallo_mecanico', 'El monoplaza presenta problemas de fiabilidad.', -8.0, 'monoplaza', -3.0, -8.0, 0.0, -8000.0, NULL, NULL, TRUE),
('Safety Car', 0.15, 'safety_car', 'La carrera se neutraliza temporalmente por un incidente.', -2.0, 'carrera', 0.0, 0.0, 0.0, -1000.0, NULL, NULL, TRUE),
('Penalizacion', 0.06, 'penalizacion', 'Un piloto recibe una penalizacion que afecta su resultado.', -5.0, 'piloto', -3.0, 0.0, -2.0, -3000.0, NULL, NULL, TRUE);


-- ==========================================================
-- FIN DEL SCRIPT
-- ==========================================================