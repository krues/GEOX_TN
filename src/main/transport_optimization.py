#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 26 16:52:59 2023

@author: Claire Halloran, University of Oxford
Contains code originally written by Leander MÃ¼ller, RWTH Aachen University

Calculates the cost-optimal commodity transportation strategy to the nearest demand center.

Calculate cost of pipeline transport and demand profile based on optimal size



"""

import geopandas as gpd
import numpy as np
import pandas as pd
from functions import CRF, cheapest_trucking_strategy, h2_conversion_stand, \
                            cheapest_pipeline_strategy, calculate_trucking_costs, \
                            calculate_nh3_pipeline_costs
from shapely.geometry import Point
import shapely.wkt
import geopy.distance
from utils import check_folder_exists

def calculate_dist_to_demand(hex_geometry, demand_center_lat, demand_center_lon):
    """
    Calculates distance to demand.

    Parameters
    ----------
    hex_geometry : geodataframe
        A specific hexagon geometry pulled from the full hexagon GeoJSON file
    demand_center_lat : 
        Latitude of the demand centre
    demand_center_lon : 
        Longitude of the demand centre
    
    Returns
    -------
    dist : float
        Distance between demand center coordinates and hexagon coordinates in km
    """
    poly = shapely.wkt.loads(str(hex_geometry))
    center = poly.centroid
    demand_coords = (demand_center_lat, demand_center_lon)
    hexagon_coords = (center.y, center.x)
    dist = geopy.distance.geodesic(demand_coords, hexagon_coords).km

    return dist

def calculate_road_construction_cost(distance_to_road, road_capex, 
                                     infrastructure_interest_rate, 
                                     infrastructure_lifetime_years, road_opex):
    """
    Calculates the cost of constructing a road from a hexagon to the nearest road.

    Parameters
    ----------
    distance_to_road : float
        Distance from the hexagon to the nearest road in km.
    road_capex : 
        Cost to construct road (per unit?)
    infrastructure_interest_rate : 
        Interest rate on infrastructure costs
    infrastructure_lifetime_years :
        Lifetime in years of the constructed infrastructure
    road_opex :
        Operating costs of the road (per unit?)
    
    Returns
    -------
    cost : float
        Cost to construct a road
    """
    cost = distance_to_road * road_capex * CRF(
                                            infrastructure_interest_rate, 
                                            infrastructure_lifetime_years
                                            ) + distance_to_road * road_opex

    return cost

def main():
    plant_type = str(snakemake.wildcards.plant_type)
    tech_params_filepath = str(snakemake.input.technology_parameters)
    demand_params_filepath = str(snakemake.input.demand_parameters)
    country_params_filepath = str(snakemake.input.country_parameters)
    transport_params_filepath = str(snakemake.input.transport_parameters)
    pipeline_params_filepath = str(snakemake.input.pipeline_parameters)
    if plant_type == "hydrogen":
        conversion_params_filepath = f'parameters/{snakemake.wildcards.country}/{snakemake.wildcards.plant_type}/conversion_parameters.xlsx'
    hexagons = gpd.read_file(str(snakemake.input.hexagons))

    infra_data = pd.read_excel(tech_params_filepath,
                           sheet_name='Infra',
                           index_col='Infrastructure')
    
    demand_center_list = pd.read_excel(demand_params_filepath,
                                    sheet_name='Demand centers',
                                    index_col='Demand center',
                                    )
    demand_centers = demand_center_list.index
    country_params = pd.read_excel(country_params_filepath,
                                        index_col='Country')
    

    needs_pipeline_construction = bool(snakemake.config["transport"]["pipeline_construction"])
    needs_road_construction = bool(snakemake.config["transport"]["road_construction"])

    long_road_capex = infra_data.at['Long road','CAPEX']
    short_road_capex = infra_data.at['Short road','CAPEX']
    road_opex = infra_data.at['Short road','OPEX']

    # Prices from the country excel file
    elec_price = country_params['Electricity price (euros/kWh)'].iloc[0]
    heat_price = country_params['Heat price (euros/kWh)'].iloc[0]
    plant_interest_rate = country_params['Plant interest rate'].iloc[0]
    infrastructure_interest_rate = country_params['Infrastructure interest rate'].iloc[0]
    infrastructure_lifetime = country_params['Infrastructure lifetime (years)'].iloc[0]

    check_folder_exists("resources")
    
    # calculate cost of hydrogen state conversion and transportation for demand
    # loop through all demand centers-- limit this on continential scale
    for demand_center in demand_centers:
        print(f"\nOptimisation for {demand_center} begins...\n")
        # Demand location based variables
        demand_center_lat = demand_center_list.loc[demand_center,'Lat [deg]']
        demand_center_lon = demand_center_list.loc[demand_center,'Lon [deg]']
        demand_location = Point(demand_center_lon, demand_center_lat)
        annual_demand_quantity = demand_center_list.loc[demand_center,'Annual demand [kg/a]']
        demand_state = demand_center_list.loc[demand_center,'Demand state']

        # Storage hexagons for costs calculated in the next for loop
        road_construction_costs = np.empty(len(hexagons))
        trucking_states = np.empty(len(hexagons),dtype='<U10')
        trucking_costs = np.empty(len(hexagons))
        pipeline_costs = np.empty(len(hexagons))

        if demand_state not in ['500 bar','LH2','NH3']:
            raise NotImplementedError(f'{demand_state} demand not supported.')
        
        # Loop through all hexagons
        for i in range(len(hexagons)):
            print(f"Currently optimising {i+1} of {len(hexagons)} hexagons...")
            dist_to_road = hexagons['road_dist'][i]
            hex_geometry = hexagons['geometry'][i]
            dist_to_demand = calculate_dist_to_demand(hex_geometry, demand_center_lat, demand_center_lon)

            #!!! maybe this is the place to set a restriction based on distance to demand center-- for all hexagons with a distance below some cutoff point
            # label demand location under consideration
            # Different calculations dependent if in demand location or not
            # If the hexagon contains the demand location
            if hex_geometry.contains(demand_location) == True:
                # Calculate cost of converting hydrogen to a demand state for local demand (i.e. no transport)
                if plant_type == "hydrogen":
                    if demand_state == 'NH3':
                        trucking_costs[i]=pipeline_costs[i]=h2_conversion_stand(demand_state+'_load',
                                                annual_demand_quantity,
                                                elec_price,
                                                heat_price,
                                                plant_interest_rate,
                                                conversion_params_filepath
                                                )[2]/annual_demand_quantity
                        trucking_states[i] = "None"
                        road_construction_costs[i] = 0.
                    else:
                        trucking_costs[i]=pipeline_costs[i]=h2_conversion_stand(demand_state,
                                                annual_demand_quantity,
                                                elec_price,
                                                heat_price,
                                                plant_interest_rate,
                                                conversion_params_filepath
                                                )[2]/annual_demand_quantity
                        trucking_states[i] = "None"
                        road_construction_costs[i] = 0.
                elif plant_type == "ammonia":
                    trucking_costs[i] = pipeline_costs[i] = 0.
                    trucking_states[i] = "None"
            
            # Otherwise, if the hexagon does not contain the demand center
            else:
                # Calculate the cost of constructing a road to the hexagon if needed
                if needs_road_construction == True:
                    # If there 0 distance to road, there is no road construction cost
                    if dist_to_road==0:
                        road_construction_costs[i] = 0.
                    # If the distance is more than 0 and less than 10, use short road costs
                    elif dist_to_road!=0 and dist_to_road<10:
                        road_construction_costs[i] = \
                            calculate_road_construction_cost(dist_to_road, 
                                                            short_road_capex, 
                                                            infrastructure_interest_rate, 
                                                            infrastructure_lifetime, 
                                                            road_opex)/annual_demand_quantity
                    # Otherwise (i.e., if distance is more than 10), use long road costs
                    else:
                        road_construction_costs[i] = \
                            calculate_road_construction_cost(dist_to_road, 
                                                            long_road_capex, 
                                                            infrastructure_interest_rate, 
                                                            infrastructure_lifetime, 
                                                            road_opex)/annual_demand_quantity

                    # Then find cheapest trucking strategy
                    if plant_type == "hydrogen":
                        trucking_costs[i], trucking_states[i] =\
                            cheapest_trucking_strategy(demand_state,
                                                        annual_demand_quantity,
                                                        dist_to_demand,
                                                        elec_price,
                                                        heat_price,
                                                        infrastructure_interest_rate,
                                                        conversion_params_filepath,
                                                        transport_params_filepath,
                                                        )
                    elif plant_type == "ammonia":
                        trucking_costs[i] = calculate_trucking_costs(demand_state,
                                                           dist_to_demand, 
                                                           annual_demand_quantity,
                                                           infrastructure_interest_rate, 
                                                           transport_params_filepath)/annual_demand_quantity
                        trucking_states[i] = "NH3"
                # Otherwise, if road construction not allowed
                else:
                    # No road construction is needed
                    road_construction_costs[i] = 0.
                    # If distance to road is 0, just get cheapest trucking strategy
                    if dist_to_road==0:
                        if plant_type == "hydrogen":
                            trucking_costs[i], trucking_states[i] =\
                                cheapest_trucking_strategy(demand_state,
                                                            annual_demand_quantity,
                                                            dist_to_demand,
                                                            elec_price,
                                                            heat_price,
                                                            infrastructure_interest_rate,
                                                            conversion_params_filepath,
                                                            transport_params_filepath,
                                                            )
                        elif plant_type == "ammonia":
                            trucking_costs[i] = calculate_trucking_costs(demand_state,
                                                           dist_to_demand, 
                                                           annual_demand_quantity,
                                                           infrastructure_interest_rate, 
                                                           transport_params_filepath)/annual_demand_quantity
                            trucking_states[i] = "NH3"
                    # And if road construction is not allowed and distance to road is > 0, trucking states are nan
                    # -- Sam to confirm whether assigning nan will cause future issues in code
                    elif dist_to_road>0: 
                        trucking_costs[i]=trucking_states[i] = np.nan

                # Calculate costs of constructing a pipeline to the hexagon if allowed
                if needs_pipeline_construction== True:
                    if plant_type == "hydrogen":
                        pipeline_costs[i], pipeline_type =\
                            cheapest_pipeline_strategy(demand_state,
                                                    annual_demand_quantity,
                                                    dist_to_demand,
                                                    elec_price,
                                                    heat_price,
                                                    infrastructure_interest_rate,
                                                    conversion_params_filepath,
                                                    pipeline_params_filepath,
                                                    )
                    elif plant_type == "ammonia":
                        pipeline_costs[i], pipeline_type =\
                            calculate_nh3_pipeline_costs(dist_to_demand,
                                                        annual_demand_quantity,
                                                        elec_price,
                                                        pipeline_params_filepath,
                                                        infrastructure_interest_rate
                                                        )
                        print(pipeline_costs[i],pipeline_type)
                else:
                    pipeline_costs[i] = np.nan

        print("\nOptimisation complete.\n")
        # Hexagon file updated with each demand center's costs and states
        hexagons[f'{demand_center} road construction costs'] = road_construction_costs # cost of road construction
        if plant_type == "hydrogen":
            hexagons[f'{demand_center} trucking transport and conversion costs'] = trucking_costs # supply conversion, trucking transport, and demand conversion
            hexagons[f'{demand_center} pipeline transport and conversion costs'] = pipeline_costs # cost of supply conversion, pipeline transport, and demand conversion
        elif plant_type == "ammonia":
            hexagons[f'{demand_center} trucking transport costs'] = trucking_costs # cost of trucking transport
            hexagons[f'{demand_center} pipeline transport costs'] = pipeline_costs # cost of supply conversion, pipeline transport, and demand conversion
        hexagons[f'{demand_center} trucking state'] = trucking_states

    hexagons.to_file(str(snakemake.output), driver='GeoJSON', encoding='utf-8') # SNAKEMAKE OUTPUT

if __name__ == "__main__":
    main()

