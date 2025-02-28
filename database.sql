CREATE DATABASE Anonymat;
USE Anonymat;

-- جدول المسؤولين
CREATE TABLE responsables (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,      
    surname VARCHAR(50) NOT NULL,     
    birthday DATE NOT NULL,           
    email VARCHAR(100) UNIQUE NOT NULL, 
    password VARCHAR(255) NOT NULL 
);

-- جدول الأساتذة
CREATE TABLE professors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,        
    surname VARCHAR(50) NOT NULL,     
    birthday DATE NOT NULL,            
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL    
);

-- جدول المترشحين
CREATE TABLE candidats (
    id INT AUTO_INCREMENT PRIMARY KEY, 
    name VARCHAR(50) NOT NULL,        
    surname VARCHAR(50) NOT NULL,      
    birthday DATE NOT NULL,            
    sex ENUM('Male', 'Female') NOT NULL, 
    anonymous_id VARCHAR(255) UNIQUE NOT NULL,
    moyen DECIMAL(5, 2) NOT NULL CHECK (moyen BETWEEN 0 AND 20),  -- المعدل يجب أن يكون بين 0 و 20
    decision ENUM('Accepted', 'Rejected', 'Pending') NOT NULL,  -- قرارات محددة مسبقًا
    absence INT DEFAULT 0 CHECK (absence >= 0)  -- يجب ألا يكون عدد الغيابات سالبًا
);

-- جدول المعاهد (Institutes)
CREATE TABLE institutes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    institute_name VARCHAR(50) UNIQUE NOT NULL,
    exam_option VARCHAR(50) NOT NULL,
    name_post VARCHAR(50) NOT NULL
);

-- جدول القاعات (Salles) مع ربطه بالمعاهد
CREATE TABLE salles (
    code_salle VARCHAR(50) PRIMARY KEY,
    name_salle VARCHAR(30) UNIQUE NOT NULL,
    capacity INT NOT NULL CHECK (capacity > 0),
    institute_id INT NOT NULL,
    FOREIGN KEY (institute_id) REFERENCES institutes(id) ON DELETE CASCADE
);

-- جدول المواد الدراسية
CREATE TABLE modules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    candidat_id INT NOT NULL,
    module_name VARCHAR(100) NOT NULL,  
    coefficient DECIMAL(4, 2) NOT NULL CHECK (coefficient > 0),
    FOREIGN KEY (candidat_id) REFERENCES candidats(id) ON DELETE CASCADE
);

-- جدول الدرجات لكل مادة (تحسين لتخزين الدرجات بشكل أكثر مرونة)
CREATE TABLE grades (
    id INT AUTO_INCREMENT PRIMARY KEY,
    module_id INT NOT NULL,
    grade DECIMAL(5, 2) NOT NULL CHECK (grade BETWEEN 0 AND 20),
    FOREIGN KEY (module_id) REFERENCES modules(id) ON DELETE CASCADE
);
