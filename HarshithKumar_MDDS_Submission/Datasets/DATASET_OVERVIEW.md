# MDDS Dataset Overview & Schema Specification

The dataset is derived from the Ministry of Drinking Water and Sanitation (MDDS) standardization catalog for administrative divisions in India.

## Administrative Hierarchy Scale
- Countries: 1 (India)
- States / UTs: 36
- Districts: 700+
- Sub-Districts (Talukas / Tehsils): 6,000+
- Revenue Villages: 600,000+
- Total Raw Rows: ~650,000

## Column Mapping
1. MDDS STC: State Code (numeric string, e.g. '27' for Maharashtra)
2. STATE NAME: Name of the State/UT
3. MDDS DTC: District Code (e.g. '497' for Nandurbar)
4. DISTRICT NAME: Name of the District
5. MDDS Sub_DT: Sub-District / Taluka Code (e.g. '03950' for Akkalkuwa)
6. SUB-DISTRICT NAME: Name of the Sub-District
7. MDDS PLCN: Primary Locality / Village Code (e.g. '525002' for Manibeli)
8. Area Name: Revenue Village / Area Name

Note: All code attributes must be ingested strictly as VARCHAR to avoid dropping leading zeroes (such as '03950').
