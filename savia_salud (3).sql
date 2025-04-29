-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 25-04-2025 a las 18:39:30
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
(16, 17, 'Hemoglobina', 4, 4, '2025-04-11', '2025-04-29', '08:00:00', '17:00:00', 30, 'si', '12:00:00', '13:00:00', '2025-04-25 16:10:16');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `citas`
--

CREATE TABLE `citas` (
  `id` int(11) NOT NULL,
  `id_calendario` int(11) NOT NULL,
  `id_usuario` int(11) NOT NULL,
  `id_paciente` int(11) NOT NULL,
  `fecha` date NOT NULL,
  `hora` time NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `citas`
--

INSERT INTO `citas` (`id`, `id_calendario`, `id_usuario`, `id_paciente`, `fecha`, `hora`, `created_at`) VALUES
(3, 16, 17, 4, '2025-04-30', '09:30:00', '2025-04-25 16:10:47'),
(4, 16, 17, 5, '2025-04-30', '08:30:00', '2025-04-25 16:36:06');

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
(1, 'Medellín');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `pacientes`
--

CREATE TABLE `pacientes` (
  `id` int(11) NOT NULL,
  `tipo_documento` varchar(25) NOT NULL,
  `numero_documento` int(11) NOT NULL,
  `telefono` int(11) NOT NULL,
  `direccion` varchar(20) NOT NULL,
  `fecha_nacimiento` datetime NOT NULL,
  `examen_realizar` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `pacientes`
--

INSERT INTO `pacientes` (`id`, `tipo_documento`, `numero_documento`, `telefono`, `direccion`, `fecha_nacimiento`, `examen_realizar`) VALUES
(4, 'CC', 1040033667, 2147483647, 'Vereda llanadas', '2025-04-29 00:00:00', 'Otorrinonaringologo'),
(5, 'TI', 1040033669, 2147483647, 'Vereda llanadas', '2008-05-07 00:00:00', 'Otorrinonaringologo');

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
(3, 'Pediatría');

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
(18, 132456789, 'cardona', 'saviaSalud*2025_', 2),
(19, 1011394242, 'valentina Tobón', 'saviaSalud*2025_', 1);

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
-- Indices de la tabla `municipios`
--
ALTER TABLE `municipios`
  ADD PRIMARY KEY (`id_municipio`),
  ADD UNIQUE KEY `unique_nombre` (`nombre`);

--
-- Indices de la tabla `pacientes`
--
ALTER TABLE `pacientes`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `procedimientos`
--
ALTER TABLE `procedimientos`
  ADD PRIMARY KEY (`id_procedimiento`),
  ADD UNIQUE KEY `unique_nombre` (`nombre`);

--
-- Indices de la tabla `roles`
--
ALTER TABLE `roles`
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
  MODIFY `id_calendario` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;

--
-- AUTO_INCREMENT de la tabla `citas`
--
ALTER TABLE `citas`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `municipios`
--
ALTER TABLE `municipios`
  MODIFY `id_municipio` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `pacientes`
--
ALTER TABLE `pacientes`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT de la tabla `procedimientos`
--
ALTER TABLE `procedimientos`
  MODIFY `id_procedimiento` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `roles`
--
ALTER TABLE `roles`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

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
