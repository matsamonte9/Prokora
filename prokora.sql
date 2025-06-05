-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: May 17, 2025 at 11:49 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `prokora`
--

-- --------------------------------------------------------

--
-- Table structure for table `alembic_version`
--

CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `alembic_version`
--

INSERT INTO `alembic_version` (`version_num`) VALUES
('96a418eeb147');

-- --------------------------------------------------------

--
-- Table structure for table `module`
--

CREATE TABLE `module` (
  `id` int(11) NOT NULL,
  `name` varchar(50) NOT NULL,
  `display_name` varchar(100) NOT NULL,
  `icon` varchar(100) NOT NULL,
  `url` varchar(255) DEFAULT NULL,
  `sequence` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `module`
--

INSERT INTO `module` (`id`, `name`, `display_name`, `icon`, `url`, `sequence`) VALUES
(1, 'dashboard', 'Dashboard', 'grid_view', '/load_module/dashboard', 1),
(2, 'projects', 'Project', 'receipt_long', '/load_module/projects', 2),
(3, 'crm', 'Customers', 'groups', '/load_module/crm', 3),
(4, 'marketing', 'Marketing', 'monitoring', '/load_module/marketing', 4),
(5, 'leads', 'Leads', 'work', '/load_module/leads', 5),
(6, 'employees', 'Employees', 'badge', '/load_module/employees', 6),
(7, 'user_management', 'User Management', 'manage_accounts', '/load_module/user_management', 7);

-- --------------------------------------------------------

--
-- Table structure for table `module_roles`
--

CREATE TABLE `module_roles` (
  `module_id` int(11) NOT NULL,
  `role_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `module_roles`
--

INSERT INTO `module_roles` (`module_id`, `role_id`) VALUES
(2, 1),
(2, 2),
(3, 1),
(3, 3),
(4, 1),
(4, 4),
(5, 1),
(5, 5),
(6, 1),
(7, 1);

-- --------------------------------------------------------

--
-- Table structure for table `permission`
--

CREATE TABLE `permission` (
  `id` int(11) NOT NULL,
  `name` varchar(80) NOT NULL,
  `description` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `permission`
--

INSERT INTO `permission` (`id`, `name`, `description`) VALUES
(1, 'add', NULL),
(2, 'edit', NULL),
(3, 'delete', NULL),
(4, 'view', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `project`
--

CREATE TABLE `project` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `description` text DEFAULT NULL,
  `status` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `project`
--

INSERT INTO `project` (`id`, `name`, `description`, `status`) VALUES
(1, 'Website Redesign', 'Revamp the company\'s main website.', 'ongoing'),
(2, 'Mobile App Development', 'Create a cross-platform mobile application.', 'finished'),
(3, 'Marketing Campaign', 'Launch a new digital marketing strategy.', 'ongoing'),
(4, 'CRM System Upgrade', 'Upgrade the existing CRM software.', 'finished'),
(5, 'Employee Training Program', 'Develop a new training curriculum for employees.', 'ongoing'),
(93, 'Ricky Boy Dulay', 'adsdad', 'finished'),
(94, '123344', 'dasdada', 'ongoing'),
(96, 'Brunzkie Dulay', 'dasdas', 'ongoing'),
(98, 'adds', 'dsds', 'ongoing'),
(99, 'dasdad', 'dasdasd', 'ongoing'),
(104, '123', 'eqweqweqwe', 'ongoing'),
(109, 'fdsfdf', 'ddd', 'finished'),
(110, 'dsaddsaddd', 'dasdas', 'ongoing');

-- --------------------------------------------------------

--
-- Table structure for table `role`
--

CREATE TABLE `role` (
  `id` int(11) NOT NULL,
  `name` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `role`
--

INSERT INTO `role` (`id`, `name`) VALUES
(1, 'admin'),
(5, 'leads'),
(4, 'marketing'),
(2, 'project'),
(3, 'sales');

-- --------------------------------------------------------

--
-- Table structure for table `role_permissions`
--

CREATE TABLE `role_permissions` (
  `role_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `role_permissions`
--

INSERT INTO `role_permissions` (`role_id`, `permission_id`) VALUES
(1, 1),
(1, 2),
(1, 3),
(1, 4),
(2, 1),
(2, 2),
(2, 3),
(2, 4),
(3, 1),
(3, 2),
(3, 4),
(4, 4),
(5, 2),
(5, 4);

-- --------------------------------------------------------

--
-- Table structure for table `submodule`
--

CREATE TABLE `submodule` (
  `id` int(11) NOT NULL,
  `name` varchar(50) NOT NULL,
  `display_name` varchar(100) NOT NULL,
  `url` varchar(255) DEFAULT NULL,
  `sequence` int(11) NOT NULL,
  `module_id` int(11) NOT NULL,
  `icon` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `submodule`
--

INSERT INTO `submodule` (`id`, `name`, `display_name`, `url`, `sequence`, `module_id`, `icon`) VALUES
(1, 'user_list', 'User List', '/load_module/user_list', 1, 7, 'list_alt'),
(2, 'user_profile', 'User Profile', '/load_module/user_profile', 2, 7, 'person'),
(3, 'ongoing', 'Ongoing', '/load_module/ongoing', 1, 2, 'event_repeat'),
(4, 'finished', 'Finished', '/load_module/finished', 2, 2, 'task_alt');

-- --------------------------------------------------------

--
-- Table structure for table `submodule_roles`
--

CREATE TABLE `submodule_roles` (
  `submodule_id` int(11) NOT NULL,
  `role_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `submodule_roles`
--

INSERT INTO `submodule_roles` (`submodule_id`, `role_id`) VALUES
(1, 1),
(2, 1),
(3, 1),
(3, 2),
(4, 1),
(4, 2);

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

CREATE TABLE `user` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `email` varchar(120) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `fs_uniquifier` varchar(255) NOT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `activation_token` varchar(64) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `user`
--

INSERT INTO `user` (`id`, `name`, `email`, `password_hash`, `fs_uniquifier`, `is_active`, `activation_token`) VALUES
(1, 'Admin User', 'admin@example.com', 'scrypt:32768:8:1$r2v1YgndxoNfTdKd$60f9d3a1281715c11400a83eb0c9c8763d960f498a89a906109951b398e2d041036afaf9140db0354aa9977a010720e23be5f6331bfd286b1ba17a267f243f52', '6fd800ba-2cb0-4519-be4d-0092ce0847aa', 1, NULL),
(2, 'Project User', 'project@example.com', 'scrypt:32768:8:1$LkAhzpqlPbYaA1V6$5eaff1de8c6418d65bcc99494d2cea1532e7eaba86f200c7a5e36d1ca3df55c5f4db5424d6167045ef011bc4afa77b750ba852c4cfa16905b55f32229e5a783e', 'e49af65e-c4c2-41ed-8fc5-499943189d76', 1, NULL),
(3, 'Sales User', 'sales@example.com', 'scrypt:32768:8:1$65p04YEVOzwNRxMu$af4786c032680e925b12999ff44626dbc04e9a0602de8fc7267faefa037aa445ffaba39f45277f52b1319fcfba5186239e2d6c114f1ee7087bb2589af729e75a', 'bb4502f0-b986-4560-aa50-4aba33207d98', 1, NULL),
(4, 'Marketing User', 'marketing@example.com', 'scrypt:32768:8:1$oTH1w6cuWqHsSD0L$8c6797f026464ea3ba81b323c86c53757c59712b2a71eee1ea8d7316ed6345e182c305cea8a49d783c22cac194b409c33527822a2b809b6708f416309372811b', '5a4e977a-343a-4e82-a6a7-0bd0559e7278', 1, NULL),
(5, 'Leads User', 'leads@example.com', 'scrypt:32768:8:1$vujIheV6JvPAfYUH$932a0eec949ae69fe46ad0e3e964d705694b7a93984437748c2140eed420006b3739d7c724f08b835b05094dd96b52bb34dbe0b144b25eaadd7328fe959a3eff', 'a4070f03-0283-49c5-be01-57b41af8b764', 1, NULL),
(49, 'Paolo Louis Dumayas', 'paoskidumayas@hotmail.com', 'scrypt:32768:8:1$PcjMqwKzr2dDWmNr$e39256a05aafca9b2c3c951edf5527de3c0a304a7f776d9a209778d4461575df3b62d9df52471edca829d4af2422907fc28dfceb47ea1b1c9d417c14646cc772', '182a4cc2-4050-4a19-8d87-212f02267b04', 1, NULL),
(62, 'Brunzkie Dulay', 'Brunzkie@example.com', 'scrypt:32768:8:1$sagPkUhv8qn0U04Y$79667501f0c5602da0aa92c37349781c60d1eb4eabd3f4e4f3902d74e92868420afbc0adf7df832e2b543ae0a71343896125c714a414f0dced2c388a309639e6', 'ae00ee99025a85e62b3f2b0260ebff59', 1, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `user_roles`
--

CREATE TABLE `user_roles` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `role_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `user_roles`
--

INSERT INTO `user_roles` (`id`, `user_id`, `role_id`) VALUES
(1, 1, 1),
(2, 2, 2),
(3, 3, 3),
(4, 4, 4),
(5, 5, 5),
(48, 49, 1),
(81, 62, 2);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `alembic_version`
--
ALTER TABLE `alembic_version`
  ADD PRIMARY KEY (`version_num`);

--
-- Indexes for table `module`
--
ALTER TABLE `module`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`);

--
-- Indexes for table `module_roles`
--
ALTER TABLE `module_roles`
  ADD PRIMARY KEY (`module_id`,`role_id`),
  ADD KEY `role_id` (`role_id`);

--
-- Indexes for table `permission`
--
ALTER TABLE `permission`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`);

--
-- Indexes for table `project`
--
ALTER TABLE `project`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `role`
--
ALTER TABLE `role`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`);

--
-- Indexes for table `role_permissions`
--
ALTER TABLE `role_permissions`
  ADD PRIMARY KEY (`role_id`,`permission_id`),
  ADD KEY `permission_id` (`permission_id`);

--
-- Indexes for table `submodule`
--
ALTER TABLE `submodule`
  ADD PRIMARY KEY (`id`),
  ADD KEY `module_id` (`module_id`);

--
-- Indexes for table `submodule_roles`
--
ALTER TABLE `submodule_roles`
  ADD PRIMARY KEY (`submodule_id`,`role_id`),
  ADD KEY `role_id` (`role_id`);

--
-- Indexes for table `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`),
  ADD UNIQUE KEY `fs_uniquifier` (`fs_uniquifier`),
  ADD UNIQUE KEY `activation_token` (`activation_token`);

--
-- Indexes for table `user_roles`
--
ALTER TABLE `user_roles`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `role_id` (`role_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `module`
--
ALTER TABLE `module`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT for table `permission`
--
ALTER TABLE `permission`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `project`
--
ALTER TABLE `project`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=111;

--
-- AUTO_INCREMENT for table `role`
--
ALTER TABLE `role`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `submodule`
--
ALTER TABLE `submodule`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT for table `user`
--
ALTER TABLE `user`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=65;

--
-- AUTO_INCREMENT for table `user_roles`
--
ALTER TABLE `user_roles`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=82;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `module_roles`
--
ALTER TABLE `module_roles`
  ADD CONSTRAINT `module_roles_ibfk_1` FOREIGN KEY (`module_id`) REFERENCES `module` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `module_roles_ibfk_2` FOREIGN KEY (`role_id`) REFERENCES `role` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `role_permissions`
--
ALTER TABLE `role_permissions`
  ADD CONSTRAINT `role_permissions_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `role` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `role_permissions_ibfk_2` FOREIGN KEY (`permission_id`) REFERENCES `permission` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `submodule`
--
ALTER TABLE `submodule`
  ADD CONSTRAINT `submodule_ibfk_1` FOREIGN KEY (`module_id`) REFERENCES `module` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `submodule_roles`
--
ALTER TABLE `submodule_roles`
  ADD CONSTRAINT `submodule_roles_ibfk_1` FOREIGN KEY (`submodule_id`) REFERENCES `submodule` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `submodule_roles_ibfk_2` FOREIGN KEY (`role_id`) REFERENCES `role` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `user_roles`
--
ALTER TABLE `user_roles`
  ADD CONSTRAINT `user_roles_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `user_roles_ibfk_2` FOREIGN KEY (`role_id`) REFERENCES `role` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
