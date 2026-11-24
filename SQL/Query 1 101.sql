SET SQL_SAFE_UPDATES = 0;
USE CoffeeQuality;
ALTER TABLE coffeesample MODIFY HarvestYear VARCHAR(50);
DELETE FROM qualityassessment; DELETE FROM coffeesample;
DELETE FROM farm; DELETE FROM owner; DELETE FROM country;

-- 1. COUNTRY
INSERT INTO country (CountryName)
SELECT DISTINCT TRIM(Country) FROM raw_coffee
WHERE NULLIF(TRIM(Country), '') IS NOT NULL;

-- 2. OWNER
INSERT INTO owner (OwnerName)
SELECT DISTINCT TRIM(Owner) FROM raw_coffee
WHERE NULLIF(TRIM(Owner), '') IS NOT NULL;

-- 3. FARM
INSERT INTO farm (FarmName, CountryID, OwnerID)
SELECT DISTINCT TRIM(r.FarmName), c.CountryID, o.OwnerID
FROM raw_coffee r
JOIN      country c ON c.CountryName = TRIM(r.Country)
LEFT JOIN owner   o ON o.OwnerName   = TRIM(r.Owner)
WHERE NULLIF(TRIM(r.FarmName), '') IS NOT NULL
  AND LOWER(TRIM(r.FarmName)) NOT IN ('various','several','multiple','-','1');

-- 4. COFFEESAMPLE
INSERT INTO coffeesample (SampleID, FarmID, Species, LotNumber, HarvestYear, Altitude)
SELECT r.SampleID, f.FarmID, TRIM(r.Species),
       NULLIF(TRIM(r.LotNumber), ''), NULLIF(TRIM(r.HarvestYear), ''),
              NULLIF(NULLIF(TRIM(r.AltitudeMean), ''), 'NA')
FROM raw_coffee r
LEFT JOIN country c ON c.CountryName = TRIM(r.Country)
LEFT JOIN owner   o ON o.OwnerName   = TRIM(r.Owner)
LEFT JOIN farm    f ON f.FarmName = TRIM(r.FarmName)
                   AND f.CountryID = c.CountryID
                   AND f.OwnerID <=> o.OwnerID;

-- 5. QUALITYASSESSMENT
INSERT INTO qualityassessment (SampleID, Aroma, Flavor, Acidity, TotalCupPoints)
SELECT SampleID, Aroma, Flavor, Acidity, TotalCupPoints FROM raw_coffee;

-- 6. CHECK
SELECT 'country' AS tbl, COUNT(*) AS n FROM country
UNION ALL SELECT 'owner', COUNT(*) FROM owner
UNION ALL SELECT 'farm', COUNT(*) FROM farm
UNION ALL SELECT 'coffeesample', COUNT(*) FROM coffeesample
UNION ALL SELECT 'qualityassessment', COUNT(*) FROM qualityassessment;