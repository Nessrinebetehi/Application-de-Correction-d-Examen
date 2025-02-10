--CREATE DATABASE Anonymat;.sql
CREATE DATABASE Anonymat;
USE Anonymat;

CREATE TABLE responsables (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,      
    surname VARCHAR(50) NOT NULL,     
    birthday DATE NOT NULL,           
    username VARCHAR(50) UNIQUE NOT NULL, 
    password VARCHAR(255) NOT NULL    
);

CREATE TABLE correcteurs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,        
    surname VARCHAR(50) NOT NULL,     
    birthday DATE NOT NULL,            
    username VARCHAR(50) UNIQUE NOT NULL, 
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
    candidat_id INT,                   
    module_name VARCHAR(100) NOT NULL,  
    grade1 DECIMAL(5, 2) NOT NULL,
    grade2 DECIMAL(5, 2) NOT NULL,
    grade3 DECIMAL(5, 2) NOT NULL,
    coefficient DECIMAL(3, 2) NOT NULL,
    FOREIGN KEY (candidat_id) REFERENCES candidats(id)
);

CREATE TABLE salles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code_salle VARCHAR(50) UNIQUE NOT NULL,
    capacity INT NOT NULL                  
);
