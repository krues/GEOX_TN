


import os
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from glob import glob
import scipy.stats as st
import pprint


def bar_plot(tarray,fdf):
    print('Function bar_plot disabled')

    # ylabels=[f'Efficiency 60% from 70%',f'Electrolyser Capex (INR Lakhs/MW) 300 from 500',f'Solar Capex (INR Lakhs/MW) 350 from 450',\
    #          f'Wind Capex (INR Lakhs/MW) 500 from 600',f'H2 Storage (INR Lakhs/MW) 14.25 from 23.75',f'Base',f'H2 Storage (INR Lakhs/MW) 33.25 from 23.75',\
    #             f'Wind Capex (INR Lakhs/MW) 700 from 600',f'Solar Capex (INR Lakhs/MW) 550 from 450',f'Electrolyser Capex (INR Lakhs/MW) 700 from 500',\
    #                 f'Efficiency 80% from 70%']
    # xaxis=fdf.columns
    # xfigs=fdf.index
    # ct=0
    # for x in tarray:
    #     fig,ax=plt.subplots()
    #     fig.set_size_inches(14.5, 8.5)
    #     g=plt.barh(xaxis,np.round(x,2)*95)
    #     plt.title(f'LCOH for {xfigs[ct]}')
    #     plt.yticks(range(0,len(ylabels)),labels=ylabels)
    #     plt.xlabel('LCOH (INR/kg H2)')
    #     plt.ylabel('Scenarios')
    #     ax.bar_label(g,padding=3)
    #     plt.tight_layout()
    #     plt.savefig(f'LCOH_{xfigs[ct]}.png',dpi=200)
    #     ct+=1
    #     plt.close()
    #     # plt.show()

    # # For only Base scenatio
    # fig,ax=plt.subplots()
    # fig.set_size_inches(18.5,10.5)
    # plt.rcParams['font.size']=16
    # # Set tick font size
    # for label in (ax.get_xticklabels() + ax.get_yticklabels()):
    #     label.set_fontsize(16)
    
    # tdf=pd.DataFrame(np.squeeze(tarray))
    # tdf.index=xfigs
    # tdf=(tdf*95).astype(float).round(0)
    # print(tdf)
    # tdf.plot(kind='barh',ax=ax)
    # for c in ax.containers:
    #     ax.bar_label(c, label_type='center')
    # # g=plt.barh(xfigs.tolist(),np.round(tarray.flatten(),0)*95)
    # plt.title(f'LCOH for Base Scenario',fontsize=20)
    # # plt.yticks(range(0,len(ylabels)),labels=ylabels)
    # plt.xlabel('LCOH (INR/kg H2)',fontsize=20)
    # plt.ylabel('Locations',fontsize=20)
    # # ax.bar_label(g,padding=3)
    # ax.get_legend().remove()
    # ax.set_xlim([0,900])
    # plt.tight_layout()
    # plt.savefig(f'LCOH_base.png',dpi=200)
    # ct+=1
    # plt.close()
    # # plt.show()


def stacked_bar(strtrans,temptrans,comp_trans,fdf_index,fdf_columns):
    # Plot stacked bar chart for Trucking

    print(f'Temporarily stacked bar plot disabled {strtrans}')
    # ylabels=[f'Efficiency 60% from 70%',f'Electrolyser Capex (INR Lakhs/MW) 300 from 500',f'Solar Capex (INR Lakhs/MW) 350 from 450',\
    #          f'Wind Capex (INR Lakhs/MW) 500 from 600',f'H2 Storage (INR Lakhs/MW) 14.25 from 23.75',f'Base',f'H2 Storage (INR Lakhs/MW) 33.25 from 23.75',\
    #             f'Wind Capex (INR Lakhs/MW) 700 from 600',f'Solar Capex (INR Lakhs/MW) 550 from 450',f'Electrolyser Capex (INR Lakhs/MW) 700 from 500',\
    #                 f'Efficiency 80% from 70%']
    # xaxis=fdf_columns
    # xfigs=fdf_index
    # width=0.5
    # ct=0
    # for x in temptrans:
    #     fig, ax = plt.subplots()
    #     bottom = np.zeros(len(xaxis))
    #     tempdict=dict(zip(comp_trans[ct],x.T))
    #     tempdict.pop(comp_trans[ct][1])
    #     for components,costs in tempdict.items():
    #         costs=costs.astype(float)
    #         p = ax.barh(xaxis, (costs*95).astype(int), label=components,left=bottom)
    #         np.add(bottom,(costs*95).astype(int),out=bottom,casting='unsafe')
    #         ax.bar_label(p,label_type='center')

    #     ax.set_title(f'Cost of Components for {strtrans} at {xfigs[ct]}', fontsize=20)
    #     ax.legend(loc="upper right", fontsize=14)
    #     ax.set_xlim(0,900)
    #     fig.set_size_inches(18.5, 10.5)
    #     ax.set_yticks(range(0,len(xaxis)))
    #     ax.set_yticklabels(ylabels, fontsize=14)#,rotation=45, ha="right", rotation_mode="anchor")
    #     ax.set_xticks(range(0,900,100))
    #     ax.set_xticklabels(range(0,900,100),fontsize=14)
    #     plt.xlabel('Cost (INR/kg H2)', fontsize=20)
    #     plt.ylabel('Scenario', fontsize=20)
    #     plt.tight_layout()
    #     plt.savefig(f'Cost_by_components_{strtrans}_{xfigs[ct]}.png',dpi=200)
    #     plt.close()
    #     ct+=1

    # # For only Base scenatio
    # fig,ax=plt.subplots()
    # fig.set_size_inches(18.5, 10.5)
    # plt.rcParams['font.size']=16
    # # Set tick font size
    # for label in (ax.get_xticklabels() + ax.get_yticklabels()):
    #     label.set_fontsize(16)
    # tdf=pd.DataFrame(np.squeeze(temptrans),columns=comp_trans[0])
    # tdf.index=xfigs
    # # tdf=tdf.columns.set_names(comp_trans[0])
    # tdf=tdf.drop(tdf.columns[1],axis=1)
    # tdf=(tdf*95).astype(float).round(0)
    # print(tdf)
    
    # tdf.plot(kind='barh',stacked=True,ax=ax)
    # for c in ax.containers:
    #     ax.bar_label(c, label_type='center')    
    
    
    # plt.title(f'LCOH breakdown for Base Scenario', fontsize=20)
    # ax.set_xlim([0,900])
    # plt.xlabel('LCOH (INR/kg H2)',fontsize=20)
    # plt.ylabel('Locations',fontsize=20)
    # plt.tight_layout()
    # plt.savefig(f'LCOH_breakdown_base.png',dpi=200)
    # plt.close()
    # # plt.show()

def tornado_plot(df_param,df_sorted,texts):
    print('Tornado disabled')
    # fig, ax = plt.subplots(figsize=(10,6))

    # ax.barh(range(0,len(df_param)),df_sorted[f'% change from base LCOH'], color='skyblue')
    # ax.set_yticks(range(0,len(df_param)))
    # ax.set_yticklabels(texts)
    # ax.set_xlabel(f'% Change in LCOH from base scenario of ~ 459 INR/kg H2')
    # ax.set_title('Impact of various parameters on LCOH at demand centre')

    # plt.grid(axis='x', linestyle='--', alpha=0.7)
    # plt.tight_layout()
    # plt.savefig('Demand_centre_LCOH_parameters_percent.png',dpi=200)
    # plt.close() 
    # # plt.show()

def cmap_lcoh(sample_eff,sample_elec_capex,lc_dc):

    print('CMAP plot disabled')

    # sort_eff=sample_eff.sort_values()
    # sort_elec_capex=sample_elec_capex.sort_values()


    # lc_2d=np.zeros(shape=(len(sort_eff),len(sort_elec_capex)))
     
    # for i in range(0,len(sort_eff)):
    #     for j in range(0,len(sort_elec_capex)):
    #         for key,val in lc_dc.items():
    #             if((('eff'+str(sort_eff.iloc[i])) in key) and ((str(sort_elec_capex.iloc[j])+'capex') in key)):
    #                 lc_2d[i,j]=val
    
    # # pprint.pprint(lc_2d)

    # # Converting Currency 1 Euro = 95 INR
    # lc_2d=lc_2d*95
    # fig, ax = plt.subplots()
    # im = ax.imshow(lc_2d,interpolation='none',cmap=plt.cm.coolwarm,origin='lower')

    # # Show all ticks and label them with the respective list entries
    # ax.set_xticks(range(len(sort_elec_capex)))
    # ax.set_yticks(range(len(sort_eff)))    
    # ax.set_xticklabels(sort_elec_capex,fontsize=14,rotation=45, ha="right", rotation_mode="anchor")
    # ax.set_yticklabels(sort_eff,fontsize=14)  
    # cbar=fig.colorbar(im,ax=ax)
    # cbar.ax.tick_params(labelsize=14)
    # # plt.show()
    # fig.set_size_inches(18.5, 10.5)
    # ax.set_title('LCOH (INR/kg H2) vs Electrolyser at Demand Centre', fontsize=20)
    # plt.xlabel('Electrolyser Capex (INR Lakhs/MW)', fontsize=20)
    # plt.ylabel('Electrolyser Efficiency (%)', fontsize=20)
    # plt.savefig('Demand_centre_LCOH_electrolyser.png',dpi=200)
    # plt.close()
    # # plt.imshow(lc_2d,interpolation='none',cmap=plt.cm.jet,origin='lower')  
    # # many other colormaps can be seen here: http://matplotlib.org/examples/color/colormaps_reference.html
    
