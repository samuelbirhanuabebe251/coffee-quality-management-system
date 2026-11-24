SELECT CASE
         WHEN S.Altitude < 1000 THEN '1. Low (<1000 m)'
         WHEN S.Altitude <= 1500 THEN '2. Medium (1000-1500 m)'
         ELSE '3. High (>1500 m)'
       END AS AltitudeBand,
       COUNT(*)                       AS NumSamples,
       ROUND(AVG(Q.TotalCupPoints),2) AS AvgScore
FROM coffeesample S
JOIN qualityassessment Q ON Q.SampleID = S.SampleID
WHERE S.Altitude BETWEEN 1 AND 5000      -- exclude missing and impossible altitudes
GROUP BY AltitudeBand
ORDER BY AltitudeBand;