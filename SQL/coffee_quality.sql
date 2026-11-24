-- Coffee Quality Database: logical model (DDL)
-- Import in MySQL Workbench 8.0: File > Import > Reverse Engineer MySQL Create Script...

CREATE SCHEMA IF NOT EXISTS CoffeeQuality;
USE CoffeeQuality;

CREATE TABLE Country (
  CountryID   INT AUTO_INCREMENT PRIMARY KEY,
  CountryName VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE Owner (
  OwnerID   INT AUTO_INCREMENT PRIMARY KEY,
  OwnerName VARCHAR(200) NOT NULL
);

CREATE TABLE Farm (
  FarmID    INT AUTO_INCREMENT PRIMARY KEY,
  FarmName  VARCHAR(200) NOT NULL,
  CountryID INT NOT NULL,
  OwnerID   INT NULL,
  CONSTRAINT fk_farm_country FOREIGN KEY (CountryID) REFERENCES Country(CountryID)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_farm_owner FOREIGN KEY (OwnerID) REFERENCES Owner(OwnerID)
    ON UPDATE CASCADE ON DELETE SET NULL
);

CREATE TABLE CoffeeSample (
  SampleID    INT PRIMARY KEY,
  FarmID      INT NULL,
  Species     VARCHAR(50),
  LotNumber   VARCHAR(100),
  HarvestYear VARCHAR(20),
  Altitude    DECIMAL(7,1),
  CONSTRAINT fk_sample_farm FOREIGN KEY (FarmID) REFERENCES Farm(FarmID)
    ON UPDATE CASCADE ON DELETE SET NULL
);

CREATE TABLE QualityAssessment (
  AssessmentID   INT AUTO_INCREMENT PRIMARY KEY,
  SampleID       INT NOT NULL UNIQUE,
  Aroma          DECIMAL(4,2),
  Flavor         DECIMAL(4,2),
  Acidity        DECIMAL(4,2),
  TotalCupPoints DECIMAL(5,2),
  CONSTRAINT fk_assessment_sample FOREIGN KEY (SampleID) REFERENCES CoffeeSample(SampleID)
    ON UPDATE CASCADE ON DELETE CASCADE
);
