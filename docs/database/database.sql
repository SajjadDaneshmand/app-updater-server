-- create database
CREATE DATABASE IF NOT EXISTS products;


-- use of database
USE products;


-- create tables

CREATE TABLE IF NOT EXISTS applications(
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) UNIQUE NOT NULL,
    author VARCHAR(255) NOT NULL,
    description TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS releases(
    id INT PRIMARY KEY AUTO_INCREMENT,
    app_id INT NOT NULL,
    version VARCHAR(64) NOT NULL,
    changelog TEXT NOT NULL,
    date DATETIME,
    FOREIGN KEY(app_id) REFERENCES applications(id)
);

CREATE TABLE IF NOT EXISTS users(
    id VARCHAR(255) PRIMARY KEY,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    access BOOLEAN NOT NULL DEFAULT false,
    token VARCHAR(255)
);
