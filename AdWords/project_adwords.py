# Name: Alisha Shahane
# StudentId: 200311941
# UnityId: asshahan

# ---------- Imports ----------
import pandas as pd
import sys
import math
import random
import numpy as np
import copy
random.seed(0)

# ---------- Greedy algo ----------
def getGreedy(queries, advertiser_budget, edges):
    
    advertiser_budget_left = copy.deepcopy(advertiser_budget)

    # Sort on highest bid
    for key, bids in edges.items():
        edges[key] = sorted(bids, key = lambda k: k[1], reverse = True)

    rev = 0.0

    # For every query, assign the highest bidder and increase revenue accordingly
    for q in queries:
        for bidder in edges[q]:
            if advertiser_budget_left[int(bidder[0])] >= bidder[1]:
                advertiser_budget_left[bidder[0]] -= bidder[1]
                rev += bidder[1]
                break

    return rev

# ---------- msvv algo ----------
def getMSVV(queries, advertiser_budget, edges):    
    
    advertiser_budget_left = copy.deepcopy(advertiser_budget)
    advertiser_budget_original = copy.deepcopy(advertiser_budget_left)
    rev = 0.0
    for q in queries:

        max_adjusted_bid, final_bid = 0.0, 0.0
        final_adv = None
        
        for bidder in edges[q]:
            
            advertiser, bid = int(bidder[0]), bidder[1]
            
            if advertiser_budget_left[advertiser] < bid:
                continue
            
            # Calculate fraction of budget spent
            adv_budget_fraction = (advertiser_budget_original[advertiser] - advertiser_budget_left[advertiser])/advertiser_budget_original[advertiser]
            # Calculate adjusted bid for comparison
            psi = (1 - math.exp(adv_budget_fraction - 1))
            adjusted_bid = bid * psi
            
            if adjusted_bid > max_adjusted_bid:
                max_adjusted_bid = adjusted_bid
                final_bid = bid
                final_adv = advertiser
        
        if final_adv != None:
            advertiser_budget_left[final_adv] -= final_bid
            rev += final_bid
                    
    return rev

# ---------- Balance algo ----------
def getBalance(queries, advertiser_budget, edges):    
    
    advertiser_budget_left = copy.deepcopy(advertiser_budget)
    rev = 0.0

    for q in queries:

        max_unspent_budget, final_bid = 0.0, 0.0
        final_adv = None
        
        for bidder in edges[q]:
            
            advertiser, bid = int(bidder[0]), bidder[1]
            
            if advertiser_budget_left[advertiser] < bid:
                continue
            
            # Assign the slot to sdvertiser with maximum unspent budget
            if advertiser_budget_left[advertiser] > max_unspent_budget:
                max_unspent_budget = advertiser_budget_left[advertiser]
                final_bid = bid
                final_adv = advertiser
        
        if final_adv != None:
            advertiser_budget_left[final_adv] -= final_bid
            rev += final_bid
                    
    return rev


# ---------- main ----------
# Check input choice of algorithm
if len(sys.argv) != 2:
    print("Input algorithm not specified (greedy or msvv or balance)")
    exit(0)

# Data Preprocessing
bidding_data = pd.read_csv("./bidder_dataset.csv", header = 0)
queries = [line.split('\n')[0] for line in open("./queries.txt", 'r').readlines()]

# Advertiser - Budget dictionary
advertiser_budget = bidding_data.groupby(['Advertiser'])['Budget'].first().to_dict()

# Create edges
bidding_data['AdvBid'] = bidding_data[['Advertiser', 'Bid Value']].apply(tuple, axis=1)
keyword_bids = bidding_data.groupby('Keyword')['AdvBid']
edges = {keyword : list(bid) for keyword, bid in keyword_bids}

# Perform appropriate algorithm
algo = sys.argv[1]
average_revenue, optimal_revenue = 0.0, 0.0

# Calculate optimal revenue for competitive ratio
for adv in advertiser_budget:
    optimal_revenue += advertiser_budget[adv]

# Greedy algo
if algo == 'greedy':
    
    print("Revenue for Greedy: ", format(getGreedy(queries, advertiser_budget, edges), '.2f'))
    
    for i in range(100):
        random.shuffle(queries)
        average_revenue += getGreedy(queries, advertiser_budget, edges)

    average_revenue /= 100
    print("Competitive Ratio: ", format(average_revenue/optimal_revenue, '.2f'))

# msvv algo
elif algo == 'msvv':
    
    print("Revenue for MSVV: ", format(getMSVV(queries, advertiser_budget, edges), '.2f'))
    
    for i in range(100):
        random.shuffle(queries)
        average_revenue += getMSVV(queries, advertiser_budget, edges)

    average_revenue /= 100
    print("Competitive Ratio: ", format(average_revenue/optimal_revenue, '.2f'))

# Balance algo
elif algo == 'balance':
    
    print("Revenue for Balance: ", format(getBalance(queries, advertiser_budget, edges), '.2f'))
    
    for i in range(100):
        random.shuffle(queries)
        average_revenue += getBalance(queries, advertiser_budget, edges)

    average_revenue /= 100
    print("Competitive Ratio: ", format(average_revenue/optimal_revenue, '.2f'))

else:
    print("Invalid Input (greedy or msvv or balance)")
    exit(0)


