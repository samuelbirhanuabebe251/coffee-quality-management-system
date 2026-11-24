SELECT C.CountryName, F.FarmName, O.OwnerName, S.SampleID, Q.TotalCupPoints
FROM qualityassessment Q
JOIN coffeesample S ON Q.SampleID  = S.SampleID
JOIN farm F         ON S.FarmID    = F.FarmID
JOIN country C      ON F.CountryID = C.CountryID
LEFT JOIN owner O   ON F.OwnerID   = O.OwnerID
ORDER BY Q.TotalCupPoints DESC
LIMIT 10;