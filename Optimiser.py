"""
South African Utility-Scale Hybrid Asset Dispatch Optimiser
Author: BSc Mathematics & Applied Mathematics Graduate Portfolio Project
Language: Python 3
"""

import numpy as np
import pandas as pd

def get_megaflex_tariffs():
    """Defines a standard 24-hour Eskom Megaflex Time-of-Use tariff profile (ZAR/MWh)."""
    tariffs = np.zeros(24)
    # Off-Peak hours (Late night/early morning)
    tariffs[0:6] = 750.0
    tariffs[22:24] = 750.0
    # Standard hours (Midday and shoulder periods)
    tariffs[6:7] = 1500.0
    tariffs[10:18] = 1500.0
    tariffs[20:22] = 1500.0
    # Peak hours (Morning and evening grid strain)
    tariffs[7:10] = 3600.0
    tariffs[18:20] = 3600.0
    return tariffs

def run_dispatch_simulation():
    # Asset Engineering & Boundary Constraints
    pv_capacity_mw = 50.0
    mec_limit_mw = 40.0             # Grid export ceiling
    bess_capacity_mwh = 40.0        # Max energy reservoir
    bess_power_limit_mw = 20.0      # Max instantaneous charge/discharge rate
    round_trip_efficiency = 0.85
    one_way_efficiency = np.sqrt(round_trip_efficiency)
    
    # Safety Buffers (10% Minimum SoC to prevent deep degradation)
    min_soc_mwh = 0.10 * bess_capacity_mwh
    current_soc = min_soc_mwh # Initial state at midnight
    
    # Structural Arrays
    hours = np.arange(24)
    tariffs = get_megaflex_tariffs()
    
    # Modelling a standard bell-curve clear-sky solar generation profile (6 AM to 6 PM)
    pv_generation = pv_capacity_mw * np.sin(np.pi * (hours - 5) / 13)
    pv_generation = np.where((hours >= 6) & (hours <= 18), pv_generation, 0.0)
    
    # Pre-allocating results arrays
    bess_charge = np.zeros(24)
    bess_discharge = np.zeros(24)
    soc_tracker = np.zeros(24)
    grid_export = np.zeros(24)
    clipped_energy_reclaimed = np.zeros(24)
    
    # Discrete-time simulation loop
    for t in hours:
        tariff = tariffs[t]
        pv_avail = pv_generation[t]
        
        # Identify baseline clipping before any battery intervention
        raw_clipping = max(0.0, pv_avail - mec_limit_mw)
        
        p_charge = 0.0
        p_discharge = 0.0
        
        # STRATEGY 1: Prioritise charging using clipped solar energy (Free energy recovery)
        if raw_clipping > 0.0 and current_soc < bess_capacity_mwh:
            max_charge_possible = min(raw_clipping, bess_power_limit_mw, (bess_capacity_mwh - current_soc) / one_way_efficiency)
            p_charge = max_charge_possible
            clipped_energy_reclaimed[t] = p_charge
            current_soc += p_charge * one_way_efficiency
            
        # STRATEGY 2: If the battery isn't full, top up during cheap, standard midday hours
        elif tariff <= 1500.0 and pv_avail > 0.0 and current_soc < bess_capacity_mwh:
            max_charge_possible = min(pv_avail, bess_power_limit_mw, (bess_capacity_mwh - current_soc) / one_way_efficiency)
            p_charge = max_charge_possible
            current_soc += p_charge * one_way_efficiency
            
        # STRATEGY 3: Dispatch battery storage during peak, high-value tariff hours
        elif tariff == 3600.0 and current_soc > min_soc_mwh:
            max_discharge_possible = min(bess_power_limit_mw, (current_soc - min_soc_mwh) * one_way_efficiency)
            grid_headroom = max(0.0, mec_limit_mw - pv_avail)
            p_discharge = min(max_discharge_possible, grid_headroom)
            current_soc -= (p_discharge / one_way_efficiency)
            
        # Finalise asset states for hour t
        bess_charge[t] = p_charge
        bess_discharge[t] = p_discharge
        soc_tracker[t] = current_soc
        grid_export[t] = min(mec_limit_mw, pv_avail - p_charge + p_discharge)
        
    # Vectorised financial calculation
    hourly_revenue_zar = grid_export * tariffs
    
    # Structuring data into a clean DataFrame matrix
    df = pd.DataFrame({
        'Hour': hours,
        'Tariff_ZAR_MWh': tariffs,
        'Solar_PV_Generation_MW': pv_generation,
        'BESS_Charge_MW': bess_charge,
        'BESS_Discharge_MW': bess_discharge,
        'BESS_State_of_Charge_MWh': soc_tracker,
        'Reclaimed_Clipping_MW': clipped_energy_reclaimed,
        'Actual_Grid_Export_MW': grid_export,
        'Hourly_Revenue_ZAR': hourly_revenue_zar
    })
    
    return df

if __name__ == '__main__':
    results_df = run_dispatch_simulation()
    
    print("="*60)
    print("HYBRID DISPATCH OPTIMISATION SEQUENCE COMPLETE")
    print("="*60)
    print(f"Total Theoretical Solar Generated : {results_df['Solar_PV_Generation_MW'].sum():.2f} MWh")
    print(f"Total Midday Clipping Reclaimed   : {results_df['Reclaimed_Clipping_MW'].sum():.2f} MWh")
    print(f"Total Energy Exported to Grid     : {results_df['Actual_Grid_Export_MW'].sum():.2f} MWh")
    print(f"Total Projected Asset Revenue     : R{results_df['Hourly_Revenue_ZAR'].sum():,.2f}")
    print("="*60)
    
    # Exporting data matrix
    results_df.to_csv('simulation_output.csv', index=False)
    print("Successfully exported 'simulation_output.csv' to directory.")
