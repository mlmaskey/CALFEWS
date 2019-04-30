import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from cord import *


######################################################################################
###Plot Simulation Results
######################################################################################
district_results = pd.read_csv('cord/data/results/annual_district_results_simulation.csv')
contract_results = pd.read_csv('cord/data/results/contract_results_annual_simulation.csv')

modelplot = Model('cord/data/input/cord-data.csv', sd='10-01-1996')
modelplot.initialize_water_districts()

cross_valley_list = [modelplot.lowertule, modelplot.kerntulare, modelplot.othercrossvalley]

modelplot.lowertule.price = 60.0
modelplot.kerntulare.price = 120.0
modelplot.othercrossvalley.price = 40.0

modelplot.lowertule.assessment = 35.0
modelplot.othercrossvalley.assessment = 14.0
modelplot.kerntulare.assessment = 0.0

modelplot.arvin.bank_get = 12.33
modelplot.lowertule.bank_get = 0.0
modelplot.kerntulare.bank_get = 0.0
modelplot.othercrossvalley.bank_get = 0.0

modelplot.arvin.bank_give = 86.33
modelplot.lowertule.bank_give = 0.0
modelplot.kerntulare.bank_give = 0.0
modelplot.othercrossvalley.bank_give = 0.0

annual_pumping = district_results['1']
annual_cross_valley = contract_results['CVC_contract'] + contract_results['CVC_carryover'] + contract_results['CVC_turnback']
annual_friant = contract_results['FR1_contract'] + contract_results['FR2_contract']
weighted_friant = modelplot.lowertule.project_contract['friant1']*contract_results['FR1_contract'] + modelplot.lowertule.project_contract['friant2']*contract_results['FR2_contract']
timeseries_revenues = {}
average_revenue = {}
cross_valley_revenues = {}
for type in ['delivery', 'recovery', 'banking']:
  cross_valley_revenues[type] = np.zeros(len(district_results))

key_list = ['LWT', 'KRT', 'OXV']
contract_type = 'SLS'
plotter.show_pumping_pdf(annual_pumping, 'CVP Delta Pumping', 3000.0)
plotter.show_pumping_pdf(annual_cross_valley, 'Cross Valley Deliveries', 150.0)
for x in cross_valley_list:
  timeseries_revenues[x.key] = {}
  average_revenue[x.key] = {}
  for type in ['delivery', 'recovery', 'banking']:
    timeseries_revenues[x.key][type], average_revenue[x.key][type] = plotter.find_district_revenues(district_results, x.key, x.acreage['W'], x.price, x.assessment, x.bank_get, x.bank_give, type)
    cross_valley_revenues[type] += timeseries_revenues[x.key][type]
	
plotter.show_district_revenues(cross_valley_revenues, 0.0, 25.0)
plotter.show_recovery_historic(district_results, timeseries_revenues, average_revenue, key_list, 1976, 1980, -25.0, 0, 5.0, 0.0, 300.0, 60.0, 0)
plotter.show_recovery_historic(district_results, timeseries_revenues, average_revenue, key_list, 1986, 1994, -25.0, 0, 5.0, 0.0, 300.0, 60.0, 0)
plotter.show_recovery_historic(district_results, timeseries_revenues, average_revenue, key_list, 2012, 2017, -25.0, 0, 5.0, 0.0, 300.0, 60.0, 0)

max_volumetric_price = 100.0
max_total_price = 400.0
contingency_increments = 30
insurance_increments = 20
evaluation_length = 30
group_revenues = {}
group_averages = {}
group_value_at_risk = {}
for type in ['delivery', 'recovery', 'banking', 'price']:
  group_revenues[type] = np.zeros(len(annual_pumping))
  group_averages[type] = 0.0
  group_value_at_risk[type] = 0.0
  
group_revenues['CF'] = np.zeros((contingency_increments, len(annual_pumping)*evaluation_length))
group_revenues['insurance'] = np.zeros((contingency_increments*insurance_increments, len(annual_pumping)*evaluation_length))
group_averages['CF'] = np.zeros(contingency_increments)
group_averages['insurance'] = np.zeros(contingency_increments*insurance_increments)
group_value_at_risk['CF'] = np.zeros(contingency_increments)
group_value_at_risk['insurance'] = np.zeros(contingency_increments*insurance_increments)

plotter.show_insurance_payouts(annual_friant, timeseries_revenues['LWT']['delivery'], timeseries_revenues['LWT']['recovery'], 875.0, 875.0, 'Friant Division Allocations')


mitigate_list = [modelplot.lowertule, modelplot.kerntulare, modelplot.othercrossvalley]
for x in mitigate_list:
  district_deliveries = district_results[x.key + '_banked_accepted']
  timeseries_revenues[x.key]['price'], average_revenue[x.key]['price'] = find_pricing_mitigation(district_deliveries, x.acreage['W'], average_revenue[x.key]['recovery'], max_volumetric_price, max_total_price, x.price, x.assessment)
  timeseries_revenues[x.key]['CF'] = {}
  timeseries_revenues[x.key]['insurance'] = {}
  average_revenue[x.key]['CF'] = {}
  average_revenue[x.key]['insurance'] = {}
  x.value_at_risk = {}
  insurance_cutoff = {}
  insurance_cutoff['delivery'] = 1.5
  insurance_cutoff['recovery'] = 1.0
  insurance_cutoff['price'] = 0.5
  for start_type in ['delivery', 'recovery', 'price']:
    timeseries_revenues[x.key]['CF'][start_type] = np.zeros((contingency_increments, len(annual_friant)*evaluation_length))
    average_revenue[x.key]['CF'][start_type] = np.zeros(contingency_increments)
    annual_cost = {}
    annual_cost['CF'] = {}
    annual_cost['CF']['contribution'] = np.zeros(contingency_increments)
    annual_cost['CF']['premium'] = np.zeros(contingency_increments)
   
    for contingency_index in range(0,contingency_increments):
      contingency_fund_start = 4.0*contingency_index*average_revenue[x.key][start_type]/contingency_increments
      insurance_strike = 0.0
      insurance_cost = 0.0
      insurance_payout = np.zeros(2)
      timeseries_revenues[x.key]['CF'][start_type][contingency_index][:], average_revenue[x.key]['CF'][start_type][contingency_index] = plotter.find_insurance_mitigation(annual_friant, timeseries_revenues[x.key][start_type], average_revenue[x.key][start_type], evaluation_length, insurance_cost, insurance_strike, insurance_payout, contingency_fund_start,insurance_cutoff[start_type])
      annual_cost['CF']['contribution'][contingency_index] = contingency_fund_start*1.96/30
    
    annual_cost['insurance'] = {}
    annual_cost['insurance']['contribution'] = np.zeros(contingency_increments*insurance_increments)
    annual_cost['insurance']['premium'] = np.zeros(contingency_increments*insurance_increments)
    timeseries_revenues[x.key]['insurance'][start_type] = np.zeros((contingency_increments*insurance_increments, len(annual_friant)*evaluation_length))
    average_revenue[x.key]['insurance'][start_type] = np.zeros(contingency_increments*insurance_increments)    
    insurance_payout = plotter.find_insurance_payment(annual_friant, timeseries_revenues[x.key][start_type], 875.0)
    for contingency_index in range(0,contingency_increments):
      contingency_fund_start = 2.0*contingency_index*average_revenue[x.key][start_type]/contingency_increments
      for insurance_index in range(0, insurance_increments):
        insurance_strike = insurance_index*50.0 + 375.0
        insurance_payout = plotter.find_insurance_payment_constant(annual_friant, timeseries_revenues[x.key][start_type], insurance_strike)
        insurance_cost = plotter.price_insurance(annual_friant, insurance_strike, insurance_payout, 1.2)
        timeseries_revenues[x.key]['insurance'][start_type][contingency_index*insurance_increments + insurance_index][:], average_revenue[x.key]['insurance'][start_type][contingency_index*insurance_increments + insurance_index] = plotter.find_insurance_mitigation(annual_friant, timeseries_revenues[x.key][start_type], average_revenue[x.key][start_type], evaluation_length, insurance_cost, insurance_strike, insurance_payout, contingency_fund_start, insurance_cutoff[start_type]) 
        annual_cost['insurance']['contribution'][contingency_index*insurance_increments + insurance_index] = contingency_fund_start*1.96/30
        annual_cost['insurance']['premium'][contingency_index*insurance_increments + insurance_index] = insurance_cost


  
  
    x.value_at_risk[start_type] = {}
    percentile = 0.99
    for type in [start_type, 'CF', 'insurance']:
      if type == 'CF':
        x.value_at_risk[start_type]['CF'] = np.zeros(contingency_increments)
        print(contingency_index)
        for contingency_index in range(0,contingency_increments):
          x.value_at_risk[start_type]['CF'][contingency_index] = plotter.show_value_at_risk(timeseries_revenues[x.key]['CF'][start_type][contingency_index], average_revenue[x.key]['CF'][start_type][contingency_index], percentile)
      elif type == 'insurance':
        x.value_at_risk[start_type]['insurance'] = np.zeros(contingency_increments*insurance_increments)
        for insurance_index in range(0,contingency_increments*insurance_increments):
          x.value_at_risk[start_type]['insurance'][insurance_index] = plotter.show_value_at_risk(timeseries_revenues[x.key]['insurance'][start_type][insurance_index], average_revenue[x.key]['insurance'][start_type][insurance_index], percentile)
      else:
        x.value_at_risk[start_type]['none'] = 0.0
        x.value_at_risk[start_type]['none'] = plotter.show_value_at_risk(timeseries_revenues[x.key][start_type], average_revenue[x.key][start_type], percentile)

	
    contingency_figure_index = plotter.find_index(modelplot.lowertule.value_at_risk[start_type]['CF'], average_revenue['LWT']['CF'][start_type], insurance_cutoff[start_type])
    insurance_figure_index = plotter.find_index(modelplot.lowertule.value_at_risk[start_type]['insurance'], average_revenue['LWT']['insurance'][start_type], insurance_cutoff[start_type])
	
    bar_shapes = plotter.find_revenue_buckets(timeseries_revenues['LWT'], contingency_figure_index, insurance_figure_index, start_type)
    plotter.show_revenue_variability(bar_shapes, average_revenue['LWT'], contingency_figure_index, insurance_figure_index, start_type, annual_cost, 20.0)

plotter.show_insurance_payouts(annual_pumping, timeseries_revenues['LWT']['delivery'], timeseries_revenues['LWT']['recovery'], 875.0)

type_list = ['delivery', 'recovery', 'banking', 'price']
certain_revenues = np.zeros(5)
var1_revenues = np.zeros(5)
var2_revenues = np.zeros(5)
for i,v in enumerate(type_list):
  certain_revenues[i] = wonderful_averages[v] - wonderful_var['99%'][v]
  var1_revenues[i] = wonderful_var['95%'][v]
  var2_revenues[i] = wonderful_var['99%'][v] - wonderful_var['95%'][v]
for x in wonderful_list:
  for contingency_index in range(0, contingency_increments):
    if x.value_at_risk['CF'][contingency_index] < 0.5:
      x.index_use = contingency_index
      break
  max_revenue = 0.0
  for insurance_index in range(0, contingency_increments*insurance_increments):
    if x.value_at_risk['insurance'][insurance_index] < 0.45 and x.average_revenue['insurance'][insurance_index] > max_revenue:
      x.index_use_2 = insurance_index
      max_revenue = x.average_revenue['insurance'][insurance_index]
	
  certain_revenues[3] += (x.average_revenue['CF'][int(x.index_use)] - x.value_at_risk2['CF'][int(x.index_use)])
  var1_revenues[3] += (x.value_at_risk['CF'][int(x.index_use)])
  var2_revenues[3] += (x.value_at_risk2['CF'][int(x.index_use)] - x.value_at_risk['CF'][int(x.index_use)])

  certain_revenues[4] += (x.average_revenue['insurance'][int(x.index_use_2)] - x.value_at_risk2['insurance'][int(x.index_use_2)])
  var1_revenues[4] += (x.value_at_risk['insurance'][int(x.index_use_2)])
  var2_revenues[4] += (x.value_at_risk2['insurance'][int(x.index_use_2)] - x.value_at_risk['insurance'][int(x.index_use_2)])



for x in wonderful_list:
  fig = plt.figure()
  ax1 = fig.add_subplot(111)
  for contingency_index in range(0,contingency_increments):
    zero_counter = 0
    for insurance_index in range(0,insurance_increments):
      xxx = contingency_index*insurance_increments + insurance_index
      if zero_counter == 0 or x.value_at_risk['insurance'][xxx] > 0.001:  
        print(zero_counter, end = " ")
        print(x.value_at_risk['insurance'][xxx])
        ax1.scatter(x.average_revenue['insurance'][xxx], x.value_at_risk['insurance'][xxx], s=50, c='orange', edgecolor='none', alpha=0.7)
      if x.value_at_risk['insurance'][xxx] < 0.001:
        zero_counter = 1
      else:
        zero_counter = 0
  zero_counter = 0
  for xx in range(0,contingency_increments):
    if zero_counter == 0 or x.value_at_risk['CF'][xx] > 0.001:  
      ax1.scatter(x.average_revenue['CF'][xx], x.value_at_risk['CF'][xx], s=50, c='purple', edgecolor='none', alpha=0.7)
    if x.value_at_risk['CF'][xx] < 0.001:
      zero_counter = 1
    else:
      zero_counter = 0
  ax1.scatter(x.average_revenue['price'], x.value_at_risk['price'], s=50, c='green', edgecolor='none', alpha=0.7)
  ax1.scatter(x.average_revenue['banking'], x.value_at_risk['banking'], s=50, c='red', edgecolor='none', alpha=0.7) 
  ax1.scatter(x.average_revenue['delivery'], x.value_at_risk['delivery'], s=50, c='steelblue', edgecolor='none', alpha=0.7)


  connectorX = {}
  connectorY = {}
  connectorX['banking'] = np.zeros(2)
  connectorY['banking'] = np.zeros(2)
  connectorX['price'] = np.zeros(3)
  connectorY['price'] = np.zeros(3)
  connectorX['CF'] = np.zeros(contingency_increments+1)
  connectorY['CF'] = np.zeros(contingency_increments+1)
  connectorX['insurance'] = np.zeros((contingency_increments,insurance_increments+1))
  connectorY['insurance'] = np.zeros((contingency_increments,insurance_increments+1))

  connectorX['banking'][0] = x.average_revenue['delivery']
  connectorY['banking'][0] = x.value_at_risk['delivery']
  connectorX['price'][0] = x.average_revenue['delivery']
  connectorY['price'][0] = x.value_at_risk['delivery']
  connectorX['banking'][1] = x.average_revenue['banking']
  connectorY['banking'][1] = x.value_at_risk['banking']
  connectorX['price'][1] = x.average_revenue['banking']
  connectorY['price'][1] = x.value_at_risk['banking']
  connectorX['price'][2] = x.average_revenue['price']
  connectorY['price'][2] = x.value_at_risk['price']
  connectorX['CF'][0] = x.average_revenue['banking']
  connectorY['CF'][0] = x.value_at_risk['banking']
  ins_breakpoint = np.zeros(contingency_increments)
  for xx in range(0,contingency_increments):
    connectorX['CF'][1+xx] = x.average_revenue['CF'][xx]
    connectorY['CF'][1+xx] = x.value_at_risk['CF'][xx]
    connectorX['insurance'][xx][0] = x.average_revenue['CF'][xx]
    connectorY['insurance'][xx][0] = x.value_at_risk['CF'][xx]
    for xxx in range(0,insurance_increments):
      connectorX['insurance'][xx][1+xxx] = x.average_revenue['insurance'][xx*insurance_increments+xxx]
      connectorY['insurance'][xx][1+xxx] = x.value_at_risk['insurance'][xx*insurance_increments+xxx]	
      if x.value_at_risk['insurance'][xx*insurance_increments+xxx] < 0.001:
        ins_breakpoint[xx] = xxx + 1
      elif xxx == insurance_increments - 1:
        ins_breakpoint[xx] = insurance_increments
		
    if x.value_at_risk['CF'][xx] < 0.001:
      breakpoint = xx + 1
    elif xx == contingency_increments - 1:
      breakpoint = contingency_increments
	  
  for xxx in range(0,breakpoint):
    ax1.plot(connectorX['insurance'][xxx][0:int(ins_breakpoint[xxx]+1)], connectorY['insurance'][xxx][0:int(ins_breakpoint[xxx]+1)], color = 'orange')
  ax1.plot(connectorX['CF'][0:(breakpoint+1)], connectorY['CF'][0:(breakpoint+1)], color = 'purple')
  ax1.plot(connectorX['price'], connectorY['price'], color = 'green')
  ax1.plot(connectorX['banking'], connectorY['banking'], color = 'red')
  
  ax1.set_ylabel('95% Value-at-Risk')
  ax1.set_xlabel('Average District Revenue')
  plt.tight_layout()
  plt.show()




  #timeseries_pumping = {}
  #timeseries_pumping['single'] = np.zeros(len(district_deliveries)*30)
  #timeseries_pumping['double'] = np.zeros(len(district_deliveries)*30)
  #timeseries_pumping['triple'] = np.zeros(len(district_deliveries)*30)
  #timeseries_pumping['four'] = np.zeros(len(district_deliveries)*30)
      #for year_duration in ['single', 'double', 'triple', 'four']:
        #timeseries_pumping[year_duration][(yy-y)+(y-1)*30] = annual_pumping[yy-y_adjust]
		
      #if yy - y > 0:
        #if yy - y_adjust > 0:
          #for year_duration in ['double', 'triple', 'four']:
            #timeseries_pumping[year_duration][(yy-y)+(y-1)*30] += annual_pumping[yy-y_adjust-1]
        #else:
          #for year_duration in ['double', 'triple', 'four']:
            #timeseries_pumping[year_duration][(yy-y)+(y-1)*30] += annual_pumping[yy-1]
      #if yy - y > 1:
        #if yy - y_adjust > 1:
          #for year_duration in ['triple', 'four']:
            #timeseries_pumping[year_duration][(yy-y)+(y-1)*30] += annual_pumping[yy-y_adjust-2]
        #else:
          #for year_duration in ['triple', 'four']:
            #timeseries_pumping[year_duration][(yy-y)+(y-1)*30] += annual_pumping[yy-2]
      #if yy - y > 2:
        #if yy - y_adjust > 2:
          #timeseries_pumping['four'][(yy-y)+(y-1)*30] += annual_pumping[yy-y_adjust-3]
        #else:
          #timeseries_pumping['four'][(yy-y)+(y-1)*30] += annual_pumping[yy-3]
  #fig = plt.figure()
  #ax1 = fig.add_subplot(221)
  #ax1.scatter(timeseries_pumping['single'], timeseries_revenues[x.key]['CF'], s=50, c='steelblue', edgecolor='none', alpha=0.7)
  #ax1 = fig.add_subplot(222)
  #ax1.scatter(timeseries_pumping['double'], timeseries_revenues[x.key]['CF'], s=50, c='steelblue', edgecolor='none', alpha=0.7)
  #ax1 = fig.add_subplot(223)
  #ax1.scatter(timeseries_pumping['triple'], timeseries_revenues[x.key]['CF'], s=50, c='steelblue', edgecolor='none', alpha=0.7)
  #ax1 = fig.add_subplot(224)
  #ax1.scatter(timeseries_pumping['four'], timeseries_revenues[x.key]['CF'], s=50, c='steelblue', edgecolor='none', alpha=0.7)
  ##plt.tight_layout()
  #plt.show()  
