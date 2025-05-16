-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Dec 16, 2024 at 12:32 PM
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
-- Database: `lost_and_found`
--

-- --------------------------------------------------------

--
-- Table structure for table `admin_info`
--

CREATE TABLE `admin_info` (
  `id` int(11) NOT NULL,
  `username` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `admin_info`
--

INSERT INTO `admin_info` (`id`, `username`, `password`) VALUES
(1, 'adminISUCC', 'scrypt:32768:8:1$1yJcPq3R2XStpDW6$d40c892aa527c2518ed78b6feb7a215c0c0235d5e0ea7d4e45dc2eeba0b218f2b4eb555e134e98357d1cfe62dfe24cb3a79dfa5f0202a71ec37b6b7d0af0b3c4');

-- --------------------------------------------------------

--
-- Table structure for table `claims`
--

CREATE TABLE `claims` (
  `id` int(11) NOT NULL,
  `item_id` int(11) NOT NULL,
  `claimer_name` varchar(255) NOT NULL,
  `contact_info` varchar(255) DEFAULT NULL,
  `status` enum('Pending','Confirmed') DEFAULT 'Pending',
  `message` text DEFAULT NULL,
  `date_claimed` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `claims`
--

INSERT INTO `claims` (`id`, `item_id`, `claimer_name`, `contact_info`, `status`, `message`, `date_claimed`) VALUES
(40, 40, 'jeslene culebra', '542452', 'Confirmed', '', '2024-12-16'),
(41, 41, 'Mharian Villamor', 'andy@gmail.com', 'Confirmed', '', '2024-12-16');

-- --------------------------------------------------------

--
-- Table structure for table `items`
--

CREATE TABLE `items` (
  `id` int(11) NOT NULL,
  `item_name` varchar(255) NOT NULL,
  `description` text NOT NULL,
  `status` enum('Published','Claimed') DEFAULT 'Published',
  `location` varchar(255) NOT NULL,
  `date_found` date NOT NULL,
  `image_path` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `items`
--

INSERT INTO `items` (`id`, `item_name`, `description`, `status`, `location`, `date_found`, `image_path`) VALUES
(38, 'Brown Wallet', 'Claimed the item here at the Main Office of ISU-CC', 'Published', 'criminology department', '2024-12-16', 'wallet.jpg'),
(40, 'Flask Tumbler', 'Claimed the item here at the Main Office of ISU-CC', 'Claimed', 'New building 2nd floor stair', '2024-12-16', 'tumbler.jpg'),
(41, 'Umbrella', 'Claimed the item here at the Main Office of ISU-CC', 'Claimed', 'IT building room 302 ', '2024-12-16', 'umbrella.jpg'),
(42, 'Black Sling bag', 'Claimed the item here at the Main Office of ISU-CC', 'Published', 'RBM hallway', '2024-12-16', 'Sling_bag_black.jpeg'),
(43, 'Iphone Black', 'Claimed the item here at the Main Office of ISU-CC', 'Published', 'Gym Cr male', '2024-12-16', 'phone.jpg'),
(44, 'Identification Card', 'Claimed the item here at the Main Office of ISU-CC', 'Published', 'Educ dept', '2024-12-16', 'id.png');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `admin_info`
--
ALTER TABLE `admin_info`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `claims`
--
ALTER TABLE `claims`
  ADD PRIMARY KEY (`id`),
  ADD KEY `item_id` (`item_id`);

--
-- Indexes for table `items`
--
ALTER TABLE `items`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `admin_info`
--
ALTER TABLE `admin_info`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `claims`
--
ALTER TABLE `claims`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=42;

--
-- AUTO_INCREMENT for table `items`
--
ALTER TABLE `items`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=45;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `claims`
--
ALTER TABLE `claims`
  ADD CONSTRAINT `claims_ibfk_1` FOREIGN KEY (`item_id`) REFERENCES `items` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
