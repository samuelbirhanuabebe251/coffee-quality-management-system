-- =====================================================================
-- Coffee Quality Management System - Phase 3: analysis queries
-- Database: CoffeeQuality (country, owner, farm, coffeesample, qualityassessment)
-- Run each query separately: click inside it and press Cmd + Enter
-- =====================================================================

USE CoffeeQuality;


-- ---------------------------------------------------------------------
-- Q1: Top 10 coffees with country, farm and owner
--     Technique: JOIN across 5 tables, ORDER BY, LIMIT
-- ---------------------------------------------------------------------
SELECT C.CountryName, F.FarmName, O.OwnerName, S.SampleID, Q.TotalCupPoints
FROM qualityassessment Q
JOIN coffeesample S ON Q.SampleID  = S.SampleID
JOIN farm F         ON S.FarmID    = F.FarmID
JOIN country C      ON F.CountryID = C.CountryID
LEFT JOIN owner O   ON F.OwnerID   = O.OwnerID
ORDER BY Q.TotalCupPoints DESC
LIMIT 10;


-- ---------------------------------------------------------------------
-- Q2: Countries with at least 10 samples, ranked by average score
--     Technique: COUNT, AVG, GROUP BY, HAVING
-- ---------------------------------------------------------------------
SELECT C.CountryName,
       COUNT(*)                        AS NumSamples,
       ROUND(AVG(Q.TotalCupPoints), 2) AS AvgScore
FROM qualityassessment Q
JOIN coffeesample S ON Q.SampleID  = S.SampleID
JOIN farm F         ON S.FarmID    = F.FarmID
JOIN country C      ON F.CountryID = C.CountryID
GROUP BY C.CountryName
HAVING COUNT(*) >= 10
ORDER BY AvgScore DESC;


-- ---------------------------------------------------------------------
-- Q3: Does altitude affect quality? Average score by altitude band
--     Technique: CASE, GROUP BY, WHERE BETWEEN
-- ---------------------------------------------------------------------
SELECT CASE
         WHEN S.Altitude < 1000  THEN '1. Low (<1000 m)'
         WHEN S.Altitude <= 1500 THEN '2. Medium (1000-1500 m)'
         ELSE '3. High (>1500 m)'
       END                             AS AltitudeBand,
       COUNT(*)                        AS NumSamples,
       ROUND(AVG(Q.TotalCupPoints), 2) AS AvgScore
FROM coffeesample S
JOIN qualityassessment Q ON Q.SampleID = S.SampleID
WHERE S.Altitude BETWEEN 1 AND 5000          -- exclude missing and impossible altitudes
GROUP BY AltitudeBand
ORDER BY AltitudeBand;


-- ---------------------------------------------------------------------
-- Q4: How many samples score above the overall average?
--     Technique: subquery
-- ---------------------------------------------------------------------
SELECT COUNT(*) AS SamplesAboveAverage,
       (SELECT ROUND(AVG(TotalCupPoints), 2) FROM qualityassessment) AS OverallAverage
FROM qualityassessment
WHERE TotalCupPoints > (SELECT AVG(TotalCupPoints) FROM qualityassessment);


-- ---------------------------------------------------------------------
-- Q5: Samples grown above 1500 m with a score above 85
--     Technique: multi-condition WHERE (AND)
-- ---------------------------------------------------------------------
SELECT C.CountryName, F.FarmName, S.Altitude, Q.TotalCupPoints
FROM coffeesample S
JOIN qualityassessment Q ON Q.SampleID  = S.SampleID
JOIN farm F              ON S.FarmID    = F.FarmID
JOIN country C           ON F.CountryID = C.CountryID
WHERE S.Altitude > 1500
  AND S.Altitude <= 5000                      -- exclude impossible altitudes
  AND Q.TotalCupPoints > 85
ORDER BY Q.TotalCupPoints DESC;


-- ---------------------------------------------------------------------
-- Q6: Consistently excellent farms (at least 3 samples, average above 85)
--     Technique: GROUP BY + HAVING with two conditions
-- ---------------------------------------------------------------------
SELECT F.FarmName, C.CountryName,
       COUNT(*)                        AS NumSamples,
       ROUND(AVG(Q.TotalCupPoints), 2) AS AvgScore
FROM farm F
JOIN country C           ON C.CountryID = F.CountryID
JOIN coffeesample S      ON S.FarmID    = F.FarmID
JOIN qualityassessment Q ON Q.SampleID  = S.SampleID
GROUP BY F.FarmID, F.FarmName, C.CountryName
HAVING COUNT(*) >= 3 AND AVG(Q.TotalCupPoints) > 85
ORDER BY AvgScore DESC;


-- ---------------------------------------------------------------------
-- Q7: The highest-scoring sample in each country
--     Technique: correlated subquery
-- ---------------------------------------------------------------------
SELECT C.CountryName, F.FarmName, S.SampleID, Q.TotalCupPoints
FROM qualityassessment Q
JOIN coffeesample S ON Q.SampleID  = S.SampleID
JOIN farm F         ON S.FarmID    = F.FarmID
JOIN country C      ON F.CountryID = C.CountryID
WHERE Q.TotalCupPoints = (
        SELECT MAX(Q2.TotalCupPoints)
        FROM qualityassessment Q2
        JOIN coffeesample S2 ON Q2.SampleID = S2.SampleID
        JOIN farm F2         ON S2.FarmID   = F2.FarmID
        WHERE F2.CountryID = F.CountryID      -- same country as the outer row
      )
ORDER BY Q.TotalCupPoints DESC;


-- ---------------------------------------------------------------------
-- Q8: View joining all 5 tables (reused for reports and Python, Phase 4)
--     Technique: CREATE VIEW, LEFT JOIN (keeps samples without a farm)
-- ---------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_sample_details AS
SELECT S.SampleID, C.CountryName, F.FarmName, O.OwnerName,
       S.HarvestYear, S.Altitude,
       Q.Aroma, Q.Flavor, Q.Acidity, Q.TotalCupPoints
FROM coffeesample S
JOIN qualityassessment Q ON Q.SampleID  = S.SampleID
LEFT JOIN farm F         ON S.FarmID    = F.FarmID
LEFT JOIN country C      ON F.CountryID = C.CountryID
LEFT JOIN owner O        ON F.OwnerID   = O.OwnerID;

-- use the view like a normal table
SELECT * FROM vw_sample_details ORDER BY TotalCupPoints DESC LIMIT 10;


-- ---------------------------------------------------------------------
-- Q9: Data-quality check: missing and impossible values
--     Technique: SUM of conditions, NULL checks, subquery
-- ---------------------------------------------------------------------
SELECT COUNT(*)                 AS TotalSamples,
       SUM(FarmID IS NULL)      AS NoFarm,
       SUM(Altitude IS NULL)    AS NoAltitude,
       SUM(HarvestYear IS NULL) AS NoHarvestYear,
       SUM(Altitude > 5000)     AS ImpossibleAltitude,
       (SELECT SUM(TotalCupPoints = 0) FROM qualityassessment) AS ZeroScore
FROM coffeesample;

