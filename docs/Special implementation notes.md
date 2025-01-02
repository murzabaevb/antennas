## Rec. ITU-R S.465-6 (model `ITUS465`)
The Rec. ITU-R S.465-6 does not define the antenna gain for off-the-axis angles less than φ<sub>min</sub>. Therefore, the gain() method returns None for such cases. The maximum antenna gain in the radiation pattern and as well as in the export files is the antenna gain at this critical angle φ<sub>min</sub> but not the actual maximum antenna gain.   

## Rec. ITU-R S.580-6 (model `ITUS580`)
The Rec. ITU-R S.580-6 does not define the antenna gain for off-the-axis angles less than max(1, 100*lambda/diameter). Therefore, the gain() method returns None for such cases. The maximum antenna gain in the radiation pattern and as well as in the export files is the antenna gain calculated at this critical angle but not the actual maximum antenna gain.

