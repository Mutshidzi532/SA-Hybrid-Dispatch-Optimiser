# SA-Hybrid-Dispatch-Optimiser
A mathematical optimisation model for a South African 50MW Solar PV + 40MWh BESS hybrid plant. Utilises Pandas and NumPy array vectorisation to reclaim midday inverter clipping losses and execute peak-period energy arbitrage matching Eskom Megaflex Time of Use tariff # South African Utility-Scale Hybrid Asset Dispatch Optimiser

An applied mathematics and data analysis framework designed to optimise the operational dispatch strategy of a co-located **50 MW Solar PV plant** and a **20 MW / 40 MWh Battery Energy Storage System (BESS)** operating under South Africa's utility grid constraints.

---

## 📋 Problem Statement

In South Africa, large-scale independent power producers (IPPs) face severe structural and financial inefficiencies due to two main factors:
1. **Grid Interconnection Constraints:** IPPs are bound by a strict Maximum Export Capacity (MEC) limit at the grid connection point. During peak solar hours, generation regularly exceeds this limit, resulting in **midday inverter clipping (curtailment)** where free green energy is permanently wasted.
2. **Volatile Time-of-Use (ToU) Tariffs:** Under networks like the Eskom Megaflex tariff structure, the financial value of energy fluctuates drastically between Peak, Standard, and Off-Peak windows. Discharging power blindly as it is generated misses high-revenue windows.

### The Objective
To design a deterministic mathematical dispatch framework that treats the battery State of Charge (SoC) as a bounded discrete-time variable. The algorithm must automatically capture midday solar clipping losses to charge the battery and strategically shift energy export to high-tariff peak windows, thereby maximising asset revenue and improving the plant's capacity factor.

---

##  Mathematical Formulation & Logic

The simulator runs a discrete-time sequence (\(t = 0, 1, \dots, 23\)) across a 24-hour cycle using the following parameters:

*   **Solar PV Capacity:** 50 MW
*   **Maximum Export Capacity (MEC Limit):** 40 MW
*   **BESS Energy Capacity:** 40 MWh (with a 10% lower safety buffer)
*   **BESS Power Limit:** 20 MW
*   **Round-Trip Efficiency (\(\eta_{\text{rt}}\)):** 85% (\(\eta_{\text{in}} = \eta_{\text{out}} = \sqrt{0.85} \approx 92.2\%\))

### Governing SoC Equation:
\[SoC_{t} = SoC_{t-1} + \left(P_{t}^{\text{charge}} \cdot \eta_{\text{in}}\right) - \left(\frac{P_{t}^{\text{discharge}}}{\eta_{\text{out}}}\right)\]

### Operational Boundaries:
*   \(0.10 \cdot BESS_{\text{capacity}} \le SoC_{t} \le BESS_{\text{capacity}}\)
*   \(P_{t}^{\text{grid}} = P_{t}^{\text{PV}} - P_{t}^{\text{charge}} + P_{t}^{\text{discharge}} \le MEC\)

---

##  Repository Structure

*   optimiser.py – Core script utilising prioritised array logic in Pandas and NumPy to handle the system constraints.
*   `simulation_output.csv` – The generated data matrix containing hourly operational logs (produced upon execution).

---

##  Eskom Megaflex Tariff Structure Matrix
The model implements the standard high-demand season tariff pricing tiers to determine optimal arbitrage actions:
*   **Peak Windows (R3,600 / MWh):** 07:00–10:00 and 18:00–20:00
*   **Standard Windows (R1,500 / MWh):** 06:00–07:00, 10:00–18:00, and 20:00–22:00
*   **Off-Peak Windows (R750 / MWh):** 22:00–06:00
