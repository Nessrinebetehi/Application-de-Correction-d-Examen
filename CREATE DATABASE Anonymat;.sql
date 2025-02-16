--CREATE DATABASE Anonymat;.sql
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
    birthday DATE NOT NULL,            
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL    
);


CREATE TABLE candidats (
    id INT AUTO_INCREMENT PRIMARY KEY, 
    name VARCHAR(50) NOT NULL,        
    surname VARCHAR(50) NOT NULL,      
    birthday DATE NOT NULL,            
    sex ENUM('Male', 'Female') NOT NULL, 
    anonymous_id VARCHAR(255) UNIQUE NOT NULL,
    moyen DECIMAL(5, 2) NOT NULL,      
    decision VARCHAR(50) NOT NULL,
    absence INT DEFAULT 0
);

CREATE TABLE modules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    candidat_id INT NOT NULL,
    module_name VARCHAR(100) NOT NULL,  
    grade1 DECIMAL(5, 2) NOT NULL,
    grade2 DECIMAL(5, 2) NOT NULL,
    grade3 DECIMAL(5, 2) NOT NULL,
    coefficient DECIMAL(4, 2) NOT NULL,
    FOREIGN KEY (candidat_id) REFERENCES candidats(id) ON DELETE CASCADE
);

CREATE TABLE exam (
    id INT AUTO_INCREMENT PRIMARY KEY,
    institue_name VARCHAR(50) NOT NULL,
    exam_option VARCHAR(50) NOT NULL,
    nbr_salles INT NOT NULL, 
    nbr_module INT NOT NULL, 
    name_post VARCHAR(50) NOT NULL
);

CREATE TABLE salles (
    code_salle VARCHAR(50) PRIMARY KEY,
    name_salle VARCHAR(10) UNIQUE NOT NULL,
    capacity INT NOT NULL
);

