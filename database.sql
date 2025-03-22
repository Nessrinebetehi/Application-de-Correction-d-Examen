CREATE DATABASE Anonymat;
USE Anonymat;


CREATE TABLE responsables (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,      
    surname VARCHAR(50) NOT NULL,     
    birthday DATE NOT NULL,           
    email VARCHAR(100) UNIQUE NOT NULL, 
    password VARCHAR(255) NOT NULL 
);


CREATE TABLE professors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,        
    surname VARCHAR(50) NOT NULL,             
    email VARCHAR(100) UNIQUE NOT NULL,
    correction integer NOT NULL,
    module VARCHAR(50) NOT NULL,
    password VARCHAR(255) NOT NULL  
);


CREATE TABLE institutes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    institute_name VARCHAR(50) UNIQUE NOT NULL,
    exam_option VARCHAR(50) NOT NULL,
    name_post VARCHAR(50) NOT NULL,
    nbr_exams integer
);
CREATE TABLE salles (
    code_salle VARCHAR(50) PRIMARY KEY,
    name_salle VARCHAR(30) UNIQUE NOT NULL,
    capacity INT NOT NULL CHECK (capacity > 0),
    institute_id INT NOT NULL
);

CREATE TABLE candidats (
    id INT AUTO_INCREMENT PRIMARY KEY, 
    name VARCHAR(50) NOT NULL,        
    surname VARCHAR(50) NOT NULL,      
    birthday DATE NOT NULL,           
    anonymous_id VARCHAR(255) UNIQUE NOT NULL,
    moyen DECIMAL(5, 2) NOT NULL DEFAULT 10.00 CHECK (moyen BETWEEN 0 AND 20),
    decision ENUM('Accepted', 'Rejected', 'Pending') NOT NULL DEFAULT 'Pending', 
    absence INT DEFAULT 0 CHECK (absence >= 0),
    salle_name VARCHAR(50), 
    FOREIGN KEY (salle_name) REFERENCES salles(name_salle) ON DELETE SET NULL
);


CREATE TABLE exams (
    id INT AUTO_INCREMENT PRIMARY KEY,
    candidat_id INT NULL, 
    module_name VARCHAR(100) NOT NULL,  
    coefficient DECIMAL(4, 2) NOT NULL CHECK (coefficient >= 1),
    grade_1 DECIMAL(5, 2) CHECK (grade_1 BETWEEN 0 AND 20),
    grade_2 DECIMAL(5, 2) CHECK (grade_2 BETWEEN 0 AND 20),
    grade_3 DECIMAL(5, 2) CHECK (grade_3 BETWEEN 0 AND 20),
    finale_g DECIMAL(5, 2) CHECK (finale_g BETWEEN 0 AND 20),
    FOREIGN KEY (candidat_id) REFERENCES candidats(id) ON DELETE CASCADE
);