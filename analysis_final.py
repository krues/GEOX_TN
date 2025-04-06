

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from glob import glob
import scipy.stats as st
from scipy.optimize import minimize
import pprint
from plots_lc import stacked_bar, bar_plot, tornado_plot, cmap_lcoh

def read_csv_files(folder):
    """
    Read all CSV files from the folder and return a list of DataFrames.
    """
    #glob is used to read all files in a folder with a specific extension. In this case, all files with extension .csv are read.
    files=glob(folder+"/*.csv") 
    dfs = pd.read_csv(files[0],index_col=0)
    dfs.index.name = 'index'
    return dfs

def extract_data(dfs):
    """
    Extract the demand centre data, the location of Min LCOH and Max LCOH.
    """
    # The input to the function is a list of DataFrames. Each DataFrame contains data for a specific scenario.
    # First find the row where the value for "SPIC trucking state" is not equal to 'NH3'
    filtered_rows = dfs[dfs['SPIC trucking state'] != 'NH3']
    demand_centre=filtered_rows.T
    min_lcoh=(dfs[dfs['SPIC lowest cost'] ==min(dfs['SPIC lowest cost'])]).T
    max_lcoh=(dfs[dfs['SPIC lowest cost'] ==max(dfs['SPIC lowest cost'])]).T
    
    return demand_centre,min_lcoh,max_lcoh

def plot_bars(lcdict):
    """
    Plot the data from the list of DataFrames.
    """
    
     
    

    # First for the three locations we only take the LC component values, transportation and conversion costs 
    # and the minimum costs for both trucking and pipeline
    plot_df=[]
    for key, dfs in lcdict.items():
        demand_centre, min_lcoh, max_lcoh = dfs.iloc[:,0], dfs.iloc[:,1], dfs.iloc[:,2]
        
        mask = demand_centre.index.str.contains('SPIC LC') | demand_centre.index.str.contains('SPIC lowest cost') | \
            demand_centre.index.str.contains('conversion costs') | demand_centre.index.str.contains('total cost')
        temp1=demand_centre[mask]

        mask = min_lcoh.index.str.contains('SPIC LC') | min_lcoh.index.str.contains('SPIC lowest cost') | \
            min_lcoh.index.str.contains('conversion costs') | min_lcoh.index.str.contains('total cost')
        temp2=min_lcoh[mask]

        mask = max_lcoh.index.str.contains('SPIC LC') | max_lcoh.index.str.contains('SPIC lowest cost') | \
            max_lcoh.index.str.contains('conversion costs') | max_lcoh.index.str.contains('total cost')
        temp3=max_lcoh[mask]
         
        # Append the data to the lisr
        plot_df.append([temp1,temp2,temp3])
    
    #convert list to dataframe

    final_df=pd.DataFrame(plot_df,index=lcdict.keys())
    final_df.columns=['Demand Centre','Min LCOH','Max LCOH']
    fdf=final_df.T
    
    # For each scenario, the lowest LCOH cost was plotted as bar chart for the 3 locations and stored as PNG spearately
    temp=[]
    for index, row in fdf.iterrows():
        row_df = row.to_frame().T
        
        t=[row_df.loc[index][col].loc['SPIC lowest cost'] for col in row_df.columns]

        temp.append(t)
    
    tarray=np.array(temp)

    # Plot LCOH bars for each scenario

    bar_plot(tarray,fdf)
    

    # To plot stacked bar chart, first we have to extract the stacks and store as trucking and pipeline separately
    # We have to extract SPIC LC* values from fdf for each  element
    ttruck=[]
    tpipe=[]
    mytrans=[]
    temp=[]
    for index, row in fdf.iterrows():
        row_df = row.to_frame().T
        trucking = [row_df.loc[index][col].filter(like='trucking', axis=0) for col in row_df.columns]
        pipeline = [row_df.loc[index][col].filter(like='pipeline', axis=0) for col in row_df.columns]
        ttemp=[]
        # st=[] # COMMENT when using only base scenario
        for col in row_df.columns:
            if row_df.loc[index][col]['SPIC trucking total cost']<row_df.loc[index][col]['SPIC pipeline total cost']:
                ttemp.append(row_df.loc[index][col].filter(like='trucking', axis=0))
                # st.append(' Trucking')
                st=' Trucking'
            else:
                ttemp.append(row_df.loc[index][col].filter(like='pipeline', axis=0))
                # st.append(' Pipeline')
                st=' Pipeline'
        mytrans.append(ttemp)    
        ttruck.append(trucking)#.values.flatten())
        tpipe.append(pipeline)#.values.flatten())
        comp_trans=[s.replace('trucking', '') for s in trucking[0].index]
        # xx=[str(x) + str(y) for x, y in zip(comp_trans, st)] # COMMENT whe using only base scenario
        xx=[str(x) + str(y) for x, y in zip(comp_trans, np.repeat(st,len(comp_trans)))]
        temp.append(xx)
    
    
    
    
    # Convert lists to numpy arrays for plotting
    temptruck = np.array(ttruck)
    temppipe = np.array(tpipe)
    transport=np.array(mytrans)
    
    comp_trucking=trucking[0].index
    comp_pipeline=pipeline[0].index 
    
    # stacked_bar('Trucking',temptruck,comp_trucking,fdf.index,fdf.columns)
    # stacked_bar('Pipeline',temppipe,comp_pipeline,fdf.index,fdf.columns)
    stacked_bar('Transport',transport,temp,fdf.index,fdf.columns)


def calc_stats(fsample,lc_dc):
    
    sample_eff=fsample.loc['Electrolyser_efficiency (%)'].dropna().astype(int) #[0.55,0.6,0.65,0.7,0.75,0.8]
    sample_elec_capex=fsample.loc['Electrolyser_capex (INR Lakhs/MW)'].dropna().astype(int) #[300,400,500,600,700,800]
    sample_solar_capex=fsample.loc['Solar_capex (INR Lakhs/MW)'].dropna().astype(int)
    sample_wind_capex=fsample.loc['Wind_capex (INR Lakhs/MW)'].dropna().astype(int)
    sample_h2=fsample.loc['H2_storage (Euros/MW)'].dropna().astype(int)
    sample_grid=fsample.loc['Electricity (Euros/kwh)'].dropna().astype(int)
    sample_demand=fsample.loc['Demand (ktpa)'].dropna().astype(int)
    
    samples=fsample.fillna(-123).astype(int)
    
    base_values=fsample.loc[:,'Base'].astype(int)
    
    df_eff,xx_eff=get_regression(sample_eff,base_values,lc_dc,'efficiency')
    df_elec_capex,xx_elec_capex=get_regression(sample_elec_capex,base_values,lc_dc,'electrolyser_capex')
    df_solar,xx_solar=get_regression(sample_solar_capex,base_values,lc_dc,'solar')
    df_wind,xx_wind=get_regression(sample_wind_capex,base_values,lc_dc,'wind')
    # df_grid=get_regression(sample_grid,base_values,lc_dc,'electricity')
    df_hyd,xx_hyd=get_regression(sample_h2,base_values,lc_dc,'h2')
    # df_demand=get_regression(sample_demand,base_values,lc_dc,'demand')

    df_param=pd.concat([df_eff,df_elec_capex,df_solar,df_wind,df_hyd])
    xx_param=pd.concat([xx_eff,xx_elec_capex,xx_solar,xx_wind,xx_hyd])
    # xx_param=[xx_eff,xx_elec_capex,xx_solar,xx_wind,xx_hyd]
    newdf = ([(xx_param.iloc[i:i+3]) for i in range(0,15,3)])
    # ## transpose dataframe to 3 columns dataframe
    # newdf = newdf.T
    
    df_sorted = df_param.reindex(df_param[f'% change from base LCOH'].abs().sort_values(ascending=True).index)
    df_sorted=df_sorted.rename(index={'H2_storage (Euros/MW)':'H2_storage (INR Lakhs/MW)'})
    # print(df_sorted)
    text1=[':'.join(map(str,i)) for i in df_sorted.index.tolist()]
    text2=[' from '+str(j) for j in df_sorted['Base Values']]
    texts=[str(x) + str(y) for x, y in zip(text1,text2)]

    # # ----- Tornado Chart -----

    tornado_plot(df_param,df_sorted,texts)
    
    
    # #Colormap of electrolyser efficiency, capex and lc - ONLY use electrolyser folder

    cmap_lcoh(sample_eff,sample_elec_capex,lc_dc)

    # # Waterfall chart
    df_sorted1 = df_param.reindex(df_param['Absolute Impact (INR/kg H2)'].abs().sort_values(ascending=False).index)
    df_sorted1=df_sorted1.rename(index={'H2_storage (Euros/MW)':'H2_storage (INR Lakhs/MW)'})
    baselc=round(df_sorted1.iloc[0].loc['Base LCOH']*95,2)
    neg_lc=df_sorted1[df_sorted1['Absolute Impact (INR/kg H2)']<0]
    wtext1=[':'.join(map(str,i)) for i in neg_lc.index.tolist()]
    wtext2=[' from '+str(j) for j in neg_lc['Base Values']]
    wtexts=[str(x) + str(y) for x, y in zip(wtext1,wtext2)]
    running_totals = [baselc]
    for inc in neg_lc['Absolute Impact (INR/kg H2)']:
        running_totals.append(running_totals[-1] + inc)
        
    # The final total
    final_value = round(running_totals[-1],2)
    wtexts.insert(0,'Base')
    wtexts.append('Final LCOH')
    print(list(enumerate(neg_lc.iloc[:]['Absolute Impact (INR/kg H2)'], start=1)))
    print(f'Optimistic Scenario LCOH: {final_value} INR/kg H2')

    # # Create figure
    # fig, ax = plt.subplots(figsize=(10, 5))

    # # We'll plot bars in a loop:
    # #   - For the baseline, it's just a single bar at index 0
    # #   - For each increment, we plot a bar that starts where the previous total ended
    # #   - For negative increments, the bar goes downward
    # #   - For the final, we can optionally highlight it
    # bar_positions = range(len(wtexts))
    # # Baseline bar
    # ax.bar(0, baselc, color='skyblue')
    # # Increment bars
    # for i, inc in enumerate(neg_lc.iloc[:]['Absolute Impact (INR/kg H2)'], start=1):
    #     # if inc is positive, bar extends upward from running_totals[i-1]
    #     # if negative, bar extends downward
    #     if inc >= 0:
    #         # bar bottom is running_totals[i-1], height is inc
    #         ax.bar(i, inc, bottom=running_totals[i-1], color='coral')
    #     else:
    #         # bar bottom is running_totals[i], height is abs(inc)
    #         # because running_totals[i] is already (running_totals[i-1] + inc)
    #         ax.bar(i, abs(inc), bottom=running_totals[i], color='lightgreen')

    # # Final bar
    # ax.bar(len(wtexts) - 1, final_value, color='skyblue')

    # # Label the x-axis with category names
    # ax.set_xticks(bar_positions)
    # ax.set_xticklabels(wtexts, rotation=30, ha='right')
    # ax.set_ylabel("LCOH (INR/kg)")
    # ax.set_ylim(0,600)
    # ax.set_xlabel('Scenarios')

    # # Add value labels
    # for i, val in enumerate(running_totals):
    #     ax.text(i, val + (5 if val >= 0 else -15), f"{val:.1f}",
    #             ha='center', va='bottom' if val >= 0 else 'top')

    # # Also label the final bar
    # ax.text(len(wtexts)-1, final_value + 5, f"{final_value:.1f}",
    #         ha='center', va='bottom')

    # plt.title("LCOH at the Demand Centre from Baseline to Final in an Optimistic Scenario")
    # plt.tight_layout()
    # plt.savefig('Waterfall_LCOH_optmistic.png',dpi=200)
    # plt.close()
    # # plt.show()

    calc_lcoa(df_param)

    return df_param,texts
    

def get_regression(sample,base_values,lc,forwhat):

    sort_values=sample.sort_values()
    temp_base=base_values
    base_values=base_values.astype(object)
    base_values['H2_storage (Euros/MW)']=str(int(base_values['H2_storage (Euros/MW)']/1000))+'k'
    base_values.pop('Battery2h (Euros/MW)')
    # base_values.pop('Electrolyser_efficiency (%)')
    # base_values.pop('Electrolyser_capex (INR Lakhs/MW)')
    base_other={}
    base_needed={}
    for i,v in base_values.items():
        if forwhat not in i.lower():
            base_other[i]=v
        else:
            base_needed[i]=v
    
    temps=[]
    temps1=[]
    for key,val in lc.items():
        mask=([str(v) in key for k,v in base_other.items()])
        #print(key," : ",mask," : ",base_other.values())
        mask1=([str(v) in key for k,v in base_values.items()])
        temps.append(mask)
        temps1.append(mask1)
    
    temp=np.array(temps)
    temp1=np.array(temps1)
    tobeused=dict(zip(lc.keys(),np.all(temp==True, axis=1)))   
    baselc=dict(zip(lc.keys(),np.all(temp1==True, axis=1)))   
    pts_eff={}
    base_lc={}
    for key,val in lc.items():
        
        if(tobeused[key]==True):
            pts_eff[key]=val
        if(baselc[key]==True):
            base_lc[key]=val
    
    plot_values=list(pts_eff.values())
    lreg=st.linregress(sort_values,plot_values)
    print(f"LCOH = {forwhat.upper()}x{round(lreg.slope,3)} + {round(lreg.intercept,1)}")
    
    percent_var={}
    basex=[]
    valuesx=sample[sample.index!='Base']
    valuebase=sample[sample.index=='Base']
    valall=sample
    x=list(base_lc.values())
    for key,val in pts_eff.items():
        if(val!=x[0]):
            percent_var[key]=((val-x[0])*100/x[0])
            basex.append(pts_eff[key])
            
    all_values=pd.DataFrame()      
    df_lc=pd.DataFrame()
    
    # title={}
    if forwhat=='electricity':
        df_lc.index=valuesx/100  
        valuebase/=100  
        all_values.index=valall/100
        # for k,v in base_needed.items():
        #     title[k]=v/100
    elif forwhat=='h2':
        df_lc.index=valuesx*95/100000  
        valuebase=valuebase*95/100000 
        all_values.index=valall*95/100000
    else:
        df_lc.index=valuesx
        all_values.index=valall
        
        # title=base_needed
    
    idx=df_lc.index
    idx1=all_values.index
    iterables=[[df_lc.index.name],idx.tolist()]
    iterables1=[[all_values.index.name],idx1.tolist()]
    xx=pd.MultiIndex.from_product(iterables, names=["Parameter", "Values"])
    df_lc.index=xx

    xx1=pd.MultiIndex.from_product(iterables1, names=["Parameter", "Values"])
    all_values.index=xx1
    
    df_lc['Base Values']=list(valuebase)*len(basex)
    df_lc['Base LCOH']=[x[0]]*len(basex)
    df_lc['LCOH']=basex
    df_lc['Absolute Impact (INR/kg H2)']=(df_lc['LCOH']-df_lc['Base LCOH'])*95
    df_lc[f'% change in parameter']=(idx.tolist()-df_lc['Base Values'])*100/df_lc['Base Values']
    df_lc[f'% change from base LCOH']=percent_var.values()
    df_lc['Sensitivity of LCOH to parameter']=round(df_lc[f'% change from base LCOH']/df_lc[f'% change in parameter'],2)
    # df_lc=df_lc.rename(columns={df_lc.columns[1]:'Base LCOH'})
    final_df_lc=pd.DataFrame(df_lc,columns=['Base Values','Base LCOH','Absolute Impact (INR/kg H2)',\
                                            f'% change in parameter',f'% change from base LCOH','Sensitivity of LCOH to parameter'])
    # pd.set_option('display.max_columns', None)
    return final_df_lc,pd.DataFrame(xx1) #xx1.tolist()


def calc_lcoa(df_param):
    
    df_sorted1 = df_param.reindex(df_param['Absolute Impact (INR/kg H2)'].abs().sort_values(ascending=False).index)
    df_sorted1=df_sorted1.rename(index={'H2_storage (Euros/MW)':'H2_storage (INR Lakhs/MW)'})
    baselc=round(df_sorted1.iloc[0].loc['Base LCOH']*95,2)
    wtext1=[':'.join(map(str,i)) for i in df_sorted1.index.tolist()]
    wtext2=[' from '+str(j) for j in df_sorted1['Base Values']]
    wtexts=[str(x) + str(y) for x, y in zip(wtext1,wtext2)]
    wtexts.insert(0,'Base')
    
    # # Ammonia plant values
    
    # h2_per_nh3=177 # kg h2 per ton NH3
    # nh3_syn_capex=44000
    # nh3_syn_opex=0.05*nh3_syn_capex
    # disc_rate=0.03
    # nh3_demand=100
    # nh3_asu_capex=4400
    # nh3_asu_opex=0.05*nh3_asu_capex
    # nh3_storage_capex=54824
    # nh3_storage_opex=0.04*nh3_storage_capex

    # # Calculations for base scenario (INR/ton)
    # hyd_cost=baselc*h2_per_nh3

    # Initial guess: all adjustment factors are 1 (no change)
    x0 = [1.0, 1.0, 1.0,1.0,1.0,1.0,1.0]

    # Set bounds (for example, each factor can vary by ±20%) bounds=[(0.8,1.2)]
    bounds = [(0.6,1.4), (0.6,1.4), (0.6,1.4),(0.6,1.4),(0.6,1.4),(0.6,1.4),(0.6,1.4)]

    res = minimize(LCOA_objective, x0, bounds=bounds)
    print("Optimal adjustment factors:", res.x)
    print("Minimum LCOA (INR/tonne NH3):", res.fun)


    # res1 = minimize(LCOU_objective, x0, bounds=bounds)
    # print("Optimal adjustment factors:", res1.x)
    # print("Minimum LCOU (INR/tonne Urea):", res1.fun)

    blend=[0,0.2,0.4,0.6,0.8,1]
    cost=[]
    for i in blend:
        print(i)
        cost.append(LCOU_objective(res.fun,i))
    
    lcou=dict(zip([str(j*100)+'%' for j in blend],cost))
    print(lcou)

def LCOA_objective(x):
    """
    x is a vector containing:
      x[0]: CAPEX adjustment factor for NH3 synthesis unit (multiplicative factor)
      x[1]: CAPEX adjustment factor for ASU
      x[2]: CAPEX adjustment factor for storage
      # You can add more parameters (like OPEX adjustments) if needed.
    """
    baselc=458.54
    # Ammonia plant values
    hydrogen_to_NH3 = 177  # 178 kg H2 per tonne of NH3
    annual_NH3_production = 100000 *1000/ hydrogen_to_NH3  # ~562,000 tonnes NH3 per year (100,000 tonnes H2/year)

    # Electricity cost and specific energy consumption (SEC) for NH3 and ASU, in kWh/kg
    # SEC_NH3 = 0.648 #0.55  # kWh/kg NH3 for ammonia synthesis
    # SEC_ASU = 0.09 #0.23  # kWh/kg NH3 for air separation
    SEC_total=0.738
    electricity_cost = 4 #4 # INR per kWh (example value)

    # # Assume OPEX rates
    # OPEX_rate_NH3 = 0.02
    # OPEX_rate_ASU = 0.02
    # OPEX_rate_storage = 0.04
    all_opex_rate=0.04 #0.04

    # # Baseline CAPEX values (INR per tonne NH3) # GIZ 2024 ammonia india modelling tool
    # CAPEX_NH3 = 44000 #650*86 #44000     # ammonia synthesis unit
    # CAPEX_ASU = 4400 #3466*1000000/((48/0.8235)*8760) #4400      # air separation unit
    # CAPEX_storage = 54824 #0.086*1000000 #54824 # ammonia storage
    all_capex=631*95 # Faisihi et al., 2021

    # CRF using a discount rate of 9% and plant lifetime of 50 years for the combined N2-NH3 complex
    # Alternatively, you might use a depreciation rate of 2% per year.
    discount_rate = 0.09
    plant_lifetime = 50
    CRF = (discount_rate * (1 + discount_rate) ** plant_lifetime) / ((1 + discount_rate) ** plant_lifetime - 1)
    # For 9% and 50 years, CRF ~ 0.0913
    
    # # Adjusted CAPEX values
    # capex_NH3_adj = CAPEX_NH3 #* x[0]
    # capex_ASU_adj = CAPEX_ASU #* x[1]
    # capex_storage_adj = CAPEX_storage #* x[2]
    all_capex_adj=all_capex
    
    # # Annualized costs using CRF:
    # annualized_NH3 = capex_NH3_adj * CRF
    # annualized_ASU = capex_ASU_adj * CRF
    # annualized_storage = capex_storage_adj * CRF
    all_annualized=all_capex_adj*CRF

    # # OPEX components (per tonne of NH3)
    # OPEX_NH3 = capex_NH3_adj * OPEX_rate_NH3
    # OPEX_ASU = capex_ASU_adj * OPEX_rate_ASU
    # OPEX_storage = capex_storage_adj * OPEX_rate_storage
    all_opex=all_capex_adj*all_opex_rate

    # Electricity costs per tonne NH3 (convert SEC from kWh/kg to kWh/tonne)
    # elec_cost_NH3 = SEC_NH3 * 1000 * electricity_cost
    # elec_cost_ASU = SEC_ASU * 1000 * electricity_cost
    all_elec_cost=SEC_total * 1000 * electricity_cost

    # Hydrogen feed cost (per tonne NH3)
    H2_feed_cost = hydrogen_to_NH3 * baselc  # 178 * LCOH INR per tonne NH3
    # print(H2_feed_cost,',',annualized_ASU+OPEX_ASU,',',annualized_NH3+OPEX_NH3,',',annualized_storage+OPEX_storage,',',elec_cost_ASU,',',elec_cost_NH3)
    
    # Sum up all costs per tonne NH3
    # cost_per_ton = (H2_feed_cost +
    #                 annualized_NH3 + OPEX_NH3 +
    #                 annualized_ASU + OPEX_ASU +
    #                 annualized_storage + OPEX_storage +
    #                 elec_cost_NH3 + elec_cost_ASU)
    cost_per_ton = (H2_feed_cost +
                    all_annualized + all_opex +
                    all_elec_cost)
    # print(cost_per_ton)
    return cost_per_ton


def LCOU_objective(lcoa_green,x):
    """
    x is a vector containing:
      x[0]: CAPEX adjustment factor for NH3 synthesis unit (multiplicative factor)
      x[1]: CAPEX adjustment factor for ASU
      x[2]: CAPEX adjustment factor for storage
      # You can add more parameters (like OPEX adjustments) if needed.
    """
    baselcoa=lcoa_green #INR /ton NH3
    lcoa_grey=280*86 #usd to inr
    blending=x
    lcoa_blend=(blending*baselcoa)+((1-blending)*lcoa_grey)
    # Ammonia plant values
    nh3_to_urea = 0.57  # tonne NH3 per tonne of Urea
    # NH3 feed cost (per tonne urea)
    nh3_feed_cost = nh3_to_urea * lcoa_blend  # 178 * LCOH INR per tonne NH3
    # print(H2_feed_cost,',',annualized_ASU+OPEX_ASU,',',annualized_NH3+OPEX_NH3,',',annualized_storage+OPEX_storage,',',elec_cost_ASU,',',elec_cost_NH3)
    co2_to_urea = 0.73  # tonne co2 per tonne of Urea
    co2_onsite=4800
    co2_external=6400
    # CO2 feed cost (per tonne urea)
    co2_feed_cost = co2_to_urea * co2_external
    
    # urea_production_green = 58*8670 #tph * hours in year -- tpa
    urea_production_grey = 94*8670
    # capex_green = 1440*(10**7) #INR
    capex_grey = 7600*(10**7)
    # opex_green= 2100*(10**7)
    opex_grey= 1540*(10**7)

    # CRF using a discount rate of 9% and plant lifetime of 50 years for the combined N2-NH3 complex
    # Alternatively, you might use a depreciation rate of 2% per year.
    discount_rate = 0.09
    plant_lifetime = 50
    CRF = (discount_rate * (1 + discount_rate) ** plant_lifetime) / ((1 + discount_rate) ** plant_lifetime - 1)
    # For 9% and 50 years, CRF ~ 0.0913
    
    # # Adjusted CAPEX values
    # capex_NH3_adj = CAPEX_NH3 #* x[0]
    # capex_ASU_adj = CAPEX_ASU #* x[1]
    # capex_storage_adj = CAPEX_storage #* x[2]
    all_capex_adj=capex_grey
    

    all_annualized=all_capex_adj*CRF/urea_production_grey


    all_opex=opex_grey/urea_production_grey


     

    cost_per_ton = (nh3_feed_cost +
                    all_annualized + all_opex +
                    co2_feed_cost)
    return cost_per_ton    

def main():
    # Read the samples for different parameters from samples.xlsx
    fname = "/samples_new.xlsx"
    fs=pd.read_excel(fname, index_col=0)#, na_values='NaN').fillna(0)
    fsample=fs.iloc[:,0:6]
    

     
    folder = "" #FOLDER PATH
    f= os.listdir(folder)
    f1=[i for i in f if 'IN_2023_hydrogen_' in i]
    
    # Extract the characters from filenames after "IN_2023_hydrogen_"
    s=[i.split("IN_2023_hydrogen_")[1] for i in f1]

    # Read csv files in the folders and subfolder and store the dataframes in a list  
    filedf=[]
    for i in f1:
        fullpath = os.path.join(folder, i)
        dfs = read_csv_files(fullpath)
        filedf.append(dfs)
    
    # Convert the list of dataframes to a dictionary with the filename substrings as keys
    var_dict=dict(zip(s,filedf))
    all_dfs=[]
    lc_dc=[]

    # Run thruogh the dictionary and perform location extraction for demand centre, min lcoh and max lcoh
    for key in var_dict:
        dc,minl,maxl=extract_data(var_dict[key])
        # Only the column of SPIC Lowest Cost i.e Final LCOH is considered
        x=dc.loc['SPIC lowest cost'].iloc[0]
        # The values associated with the lowest cost are stored in list 
        lc_dc.append(x)
        
        #The 3 location dataframes are aggregated into a list
        all_dfs.append(pd.concat([dc,minl,maxl],axis=1))
    
    # The list of the 3 locations and their various values are stored as dictionary
    lcoh_dict=dict(zip(s,all_dfs))
    plot_bars(lcoh_dict)
    
    # The lowest cost in the demand centre is stored as a dictionary
    lc_dc_dict=dict(zip(s,lc_dc))
    # Calling function to check relationships between lowest cost at demand centre and other parameters
    df_param,texts=calc_stats(fsample,lc_dc_dict)
    valtext=[df_param.index[i][1] for i in range(0,len(texts)-1)]


if __name__ == "__main__":
    main()


