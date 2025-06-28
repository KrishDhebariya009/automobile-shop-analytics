-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jun 28, 2025 at 02:10 PM
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
-- Database: `automobile_shop`
--

-- --------------------------------------------------------

--
-- Table structure for table `owners`
--

CREATE TABLE `owners` (
  `id` int(11) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `mobile` varchar(15) DEFAULT NULL,
  `password` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `owners`
--

INSERT INTO `owners` (`id`, `name`, `mobile`, `password`) VALUES
(4, 'bansuri', '9428626419', '8805');

-- --------------------------------------------------------

--
-- Table structure for table `purchases`
--

CREATE TABLE `purchases` (
  `id` int(11) NOT NULL,
  `bill_no` varchar(20) DEFAULT NULL,
  `name` varchar(100) DEFAULT NULL,
  `mobile` varchar(15) DEFAULT NULL,
  `amount` decimal(10,2) DEFAULT NULL,
  `category` varchar(50) DEFAULT NULL,
  `vehicle` varchar(50) DEFAULT NULL,
  `payment` varchar(50) DEFAULT NULL,
  `date` date DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `purchases`
--

INSERT INTO `purchases` (`id`, `bill_no`, `name`, `mobile`, `amount`, `category`, `vehicle`, `payment`, `date`, `user_id`) VALUES
(7, '1', 'Karshan Patel', '7874701001', 1450.00, 'Parts', 'Car', 'Cash', '2025-06-25', 1),
(8, '2', 'Bhargav Thesiya', '9624413978', 850.00, 'Oil', 'Bike', 'UPI', '2025-06-25', 2),
(9, '3', 'Bhargav Thesiya', '9624413978', 560.00, 'Parts', 'Bike', 'UPI', '2025-06-25', 2),
(10, '5', 'Jenish Patoliya', '7383003757', 1263.00, 'Parts', 'AtulShakti', 'Cash', '2025-06-25', 3),
(11, '22', 'Jenish Patoliya', '7383003757', 3020.00, 'Parts', 'Car', 'UPI', '2025-06-25', 3),
(12, '5', 'Nikunj Patoliya', '9574390073', 1560.00, 'Parts', 'Other', 'Online', '2025-06-25', 4),
(13, '7', 'Nikunj Patoliya', '9574390073', 580.00, 'Parts', 'Bike', 'Cash', '2025-06-25', 4),
(14, '2212', 'pareshbhai patoliya', '9909540247', 3540.00, 'Parts', 'Car', 'UPI', '2025-06-26', 5);

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `mobile` varchar(15) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `name`, `mobile`, `password`) VALUES
(1, 'Karshan Patel', '7874701001', 'scrypt:32768:8:1$CmBGjiYTn5lSOJPT$95483a59afb658d16b4a9253ec3b8b91f779528c8a20c0c396ea5eec0fc221332b001757e0e3f3005836a7db995be9809163b39e7efd7e73f41ba3702998e6f7'),
(2, 'Bhargav Thesiya', '9624413978', 'scrypt:32768:8:1$5yflngdxhRf66PHS$806bf241025f35ae1785dbe2eb176e9823e4df087624449dff1b28c0cbce860f6e9a16122dc0e58622d547b075158169cbe7ffedd7d5bb6c1b4f27e4edb33aa4'),
(3, 'Jenish Patoliya', '7383003757', 'scrypt:32768:8:1$ivY14wGUJ1Ikqu9j$4ded95737a67a3b72609c34ab0f38449d7156fffbbc4c0f8236c41fa76700337951ec4349451d9165496b6f6d0e368e66d0a71a17047334dcecc7b0c3b5c31e6'),
(4, 'Nikunj Patoliya', '9574390073', 'scrypt:32768:8:1$LNbrmcQxrkUIdrqh$6ad8891ab93f212c75d30a1c9e7ce7ddbb6e70c0d9b93dbd33a7b71ec0e522f04c285c209158fe18dc9a2ec49c1c7794cca403a3a90931fc3097b942d02d69f4'),
(5, 'pareshbhai patoliya', '9909540247', 'scrypt:32768:8:1$EOuFzjStCNLEG91X$9ccb0b39dfbdecd6e1ff2d54ad59f47b75388506d11f3166cd89fe8964f69d31fc89397867d7def2ef91d16b95d0ef031a083ac7e4480df8c6ecb99dfc6673c7');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `owners`
--
ALTER TABLE `owners`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `mobile` (`mobile`);

--
-- Indexes for table `purchases`
--
ALTER TABLE `purchases`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `mobile` (`mobile`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `owners`
--
ALTER TABLE `owners`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `purchases`
--
ALTER TABLE `purchases`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
