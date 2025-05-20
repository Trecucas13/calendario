-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 20-05-2025 a las 19:11:13
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `savia salud`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `calendarios`
--

CREATE TABLE `calendarios` (
  `id_calendario` int(11) NOT NULL,
  `id_usuario` int(11) NOT NULL,
  `nombre_calendario` varchar(100) NOT NULL,
  `id_municipio` int(11) NOT NULL,
  `id_procedimiento` int(11) NOT NULL,
  `fecha_inicio` date NOT NULL,
  `fecha_fin` date NOT NULL,
  `hora_inicio` time NOT NULL,
  `hora_fin` time NOT NULL,
  `espacio_citas` int(11) NOT NULL,
  `tiempo_fuera` varchar(5) NOT NULL,
  `inicio_hora_descanso` time DEFAULT NULL,
  `fin_hora_descanso` time DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `calendarios`
--

INSERT INTO `calendarios` (`id_calendario`, `id_usuario`, `nombre_calendario`, `id_municipio`, `id_procedimiento`, `fecha_inicio`, `fecha_fin`, `hora_inicio`, `hora_fin`, `espacio_citas`, `tiempo_fuera`, `inicio_hora_descanso`, `fin_hora_descanso`, `created_at`) VALUES
(17, 17, 'Hemoglobina', 4, 2, '2025-05-01', '2025-05-23', '08:00:00', '17:00:00', 10, 'si', '12:00:00', '13:00:00', '2025-05-02 13:52:57'),
(18, 17, 'valentina', 4, 1, '2025-05-06', '2025-05-21', '08:00:00', '17:00:00', 10, 'si', '23:00:00', '13:00:00', '2025-05-06 20:52:40'),
(19, 17, 'Ecopetrol', 4, 3, '2025-05-19', '2025-05-24', '08:00:00', '17:00:00', 15, 'si', '12:00:00', '13:00:00', '2025-05-19 21:06:13'),
(20, 18, 'vph sopetran', 4, 4, '2025-05-21', '2025-05-22', '08:00:00', '17:00:00', 10, 'no', NULL, NULL, '2025-05-19 21:36:25');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `citas`
--

CREATE TABLE `citas` (
  `id` int(11) NOT NULL,
  `id_calendario` int(11) NOT NULL,
  `id_usuario` int(11) NOT NULL,
  `id_paciente` int(11) NOT NULL,
  `id_procedimiento` int(11) NOT NULL,
  `fecha` date NOT NULL,
  `hora` time NOT NULL,
  `estado` tinyint(1) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `citas`
--

INSERT INTO `citas` (`id`, `id_calendario`, `id_usuario`, `id_paciente`, `id_procedimiento`, `fecha`, `hora`, `estado`, `created_at`) VALUES
(16, 17, 17, 17, 3, '2025-05-07', '09:00:00', 0, '2025-05-06 20:18:29');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `gestiones`
--

CREATE TABLE `gestiones` (
  `id` int(36) NOT NULL,
  `registro_id` char(36) DEFAULT NULL,
  `tipificacion` varchar(100) DEFAULT NULL,
  `comentario` text DEFAULT NULL,
  `id_llamada` varchar(100) DEFAULT NULL,
  `fecha_gestion` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `usuario` varchar(100) DEFAULT NULL,
  `llave_compuesta` char(36) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `municipios`
--

CREATE TABLE `municipios` (
  `id_municipio` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `municipios`
--

INSERT INTO `municipios` (`id_municipio`, `nombre`) VALUES
(2, 'Bello'),
(4, 'Envigado'),
(3, 'Itagüí'),
(1, 'Medellín'),
(5, 'sopetran');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `pacientes`
--

CREATE TABLE `pacientes` (
  `id` int(11) NOT NULL,
  `nombre` varchar(250) NOT NULL,
  `apellido` varchar(250) NOT NULL,
  `tipo_documento` varchar(25) NOT NULL,
  `numero_documento` int(11) NOT NULL,
  `telefono` int(11) NOT NULL,
  `direccion` varchar(20) NOT NULL,
  `fecha_nacimiento` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `pacientes`
--

INSERT INTO `pacientes` (`id`, `nombre`, `apellido`, `tipo_documento`, `numero_documento`, `telefono`, `direccion`, `fecha_nacimiento`) VALUES
(17, 'Santiago', 'Otalvaro', 'TI', 1040033667, 2147483647, 'Vereda llanadas', '2025-05-02 00:00:00');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `procedimientos`
--

CREATE TABLE `procedimientos` (
  `id_procedimiento` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `procedimientos`
--

INSERT INTO `procedimientos` (`id_procedimiento`, `nombre`) VALUES
(1, 'Consulta General'),
(4, 'Ginecología'),
(2, 'Odontología'),
(3, 'Pediatría'),
(5, 'vph');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `registro_base`
--

CREATE TABLE `registro_base` (
  `id` int(36) NOT NULL,
  `tipo_id` varchar(20) DEFAULT NULL,
  `num_id` varchar(50) DEFAULT NULL,
  `primer_nombre` varchar(50) DEFAULT NULL,
  `segundo_nombre` varchar(50) DEFAULT NULL,
  `primer_apellido` varchar(50) DEFAULT NULL,
  `segundo_apellido` varchar(50) DEFAULT NULL,
  `fecha` date DEFAULT NULL,
  `edad` int(11) DEFAULT NULL,
  `estado_afiliacion` varchar(50) DEFAULT NULL,
  `regimen_afiliacion` varchar(50) DEFAULT NULL,
  `telefonos` varchar(100) DEFAULT NULL,
  `direccion` varchar(100) DEFAULT NULL,
  `municipio` varchar(50) DEFAULT NULL,
  `subregion` varchar(50) DEFAULT NULL,
  `proceso` varchar(50) DEFAULT NULL,
  `fecha_carga` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `mejor_gestion` varchar(100) DEFAULT NULL,
  `asesor` varchar(100) DEFAULT NULL,
  `tipo_gestion` varchar(50) DEFAULT NULL,
  `fecha_gestion` date DEFAULT NULL,
  `mes` varchar(20) DEFAULT NULL,
  `cantidad_gestiones` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `roles`
--

CREATE TABLE `roles` (
  `id` int(11) NOT NULL,
  `rol` varchar(100) NOT NULL,
  `fecha_creacion` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `roles`
--

INSERT INTO `roles` (`id`, `rol`, `fecha_creacion`) VALUES
(1, 'Administrador', '2025-04-23 12:59:11'),
(2, 'Asesor', '2025-04-23 12:59:11');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tipificacion`
--

CREATE TABLE `tipificacion` (
  `id` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `ranking` int(11) DEFAULT NULL,
  `tipo_contacto` varchar(20) DEFAULT NULL CHECK (`tipo_contacto` in ('EFECTIVO','NO EFECTIVO','NO CONTACTADO'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE `usuarios` (
  `id` int(11) NOT NULL,
  `documento` int(11) NOT NULL,
  `nombre` varchar(250) NOT NULL,
  `password` varchar(250) NOT NULL,
  `rol` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `usuarios`
--

INSERT INTO `usuarios` (`id`, `documento`, `nombre`, `password`, `rol`) VALUES
(17, 1234567890, 'hola', 'savia', 1),
(18, 123456789, 'cardona', 'Salud', 2);

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `calendarios`
--
ALTER TABLE `calendarios`
  ADD PRIMARY KEY (`id_calendario`),
  ADD KEY `idx_municipio` (`id_municipio`),
  ADD KEY `idx_procedimiento` (`id_procedimiento`),
  ADD KEY `id_municipio` (`id_municipio`),
  ADD KEY `fk_usuarios_calendario` (`id_usuario`);

--
-- Indices de la tabla `citas`
--
ALTER TABLE `citas`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `id_paciente` (`id`),
  ADD KEY `idx_calendario` (`id_calendario`),
  ADD KEY `idx_fecha` (`fecha`),
  ADD KEY `id_calendario` (`id_calendario`),
  ADD KEY `fk_pacientes_citas` (`id_paciente`),
  ADD KEY `fk_usuarios_citas` (`id_usuario`);

--
-- Indices de la tabla `gestiones`
--
ALTER TABLE `gestiones`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `municipios`
--
ALTER TABLE `municipios`
  ADD PRIMARY KEY (`id_municipio`),
  ADD UNIQUE KEY `unique_nombre` (`nombre`);

--
-- Indices de la tabla `pacientes`
--
ALTER TABLE `pacientes`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `numero_documento` (`numero_documento`);

--
-- Indices de la tabla `procedimientos`
--
ALTER TABLE `procedimientos`
  ADD PRIMARY KEY (`id_procedimiento`),
  ADD UNIQUE KEY `unique_nombre` (`nombre`);

--
-- Indices de la tabla `registro_base`
--
ALTER TABLE `registro_base`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `roles`
--
ALTER TABLE `roles`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `tipificacion`
--
ALTER TABLE `tipificacion`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `documento` (`documento`),
  ADD KEY `fk_rol_usuario` (`rol`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `calendarios`
--
ALTER TABLE `calendarios`
  MODIFY `id_calendario` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=21;

--
-- AUTO_INCREMENT de la tabla `citas`
--
ALTER TABLE `citas`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;

--
-- AUTO_INCREMENT de la tabla `gestiones`
--
ALTER TABLE `gestiones`
  MODIFY `id` int(36) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `municipios`
--
ALTER TABLE `municipios`
  MODIFY `id_municipio` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT de la tabla `pacientes`
--
ALTER TABLE `pacientes`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=18;

--
-- AUTO_INCREMENT de la tabla `procedimientos`
--
ALTER TABLE `procedimientos`
  MODIFY `id_procedimiento` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT de la tabla `registro_base`
--
ALTER TABLE `registro_base`
  MODIFY `id` int(36) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `roles`
--
ALTER TABLE `roles`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `tipificacion`
--
ALTER TABLE `tipificacion`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=20;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `calendarios`
--
ALTER TABLE `calendarios`
  ADD CONSTRAINT `fk_id_municipio` FOREIGN KEY (`id_municipio`) REFERENCES `municipios` (`id_municipio`),
  ADD CONSTRAINT `fk_id_procedimiento` FOREIGN KEY (`id_procedimiento`) REFERENCES `procedimientos` (`id_procedimiento`),
  ADD CONSTRAINT `fk_usuarios_calendario` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id`);

--
-- Filtros para la tabla `citas`
--
ALTER TABLE `citas`
  ADD CONSTRAINT `fk_calendario_citas` FOREIGN KEY (`id_calendario`) REFERENCES `calendarios` (`id_calendario`),
  ADD CONSTRAINT `fk_pacientes_citas` FOREIGN KEY (`id_paciente`) REFERENCES `pacientes` (`id`),
  ADD CONSTRAINT `fk_usuarios_citas` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id`);

--
-- Filtros para la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD CONSTRAINT `fk_rol_usuario` FOREIGN KEY (`rol`) REFERENCES `roles` (`id`) ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
