# -*- coding: utf-8 -*-


import math

from operator import itemgetter

import operator

#################################################
# recommender class does user-based filtering and recommends items 
class UserBasedFilteringRecommender:
    
    # class variables:    
    # none
    
    ##################################
    # class instantiation method - initializes instance variables
    #
    # usersItemRatings:
    # users item ratings data is in the form of a nested dictionary:
    # at the top level, we have User Names as keys, and their Item Ratings as values;
    # and Item Ratings are themselves dictionaries with Item Names as keys, and Ratings as values
    # Example: 
    #     {"Angelica":{"Blues Traveler": 3.5, "Broken Bells": 2.0, "Norah Jones": 4.5, "Phoenix": 5.0, "Slightly Stoopid": 1.5, "The Strokes": 2.5, "Vampire Weekend": 2.0},
    #      "Bill":{"Blues Traveler": 2.0, "Broken Bells": 3.5, "Deadmau5": 4.0, "Phoenix": 2.0, "Slightly Stoopid": 3.5, "Vampire Weekend": 3.0}}
    #
    # k:
    # the number of nearest neighbors
    # defaults to 1
    #
    # m:
    # the number of recommedations to return
    # defaults to 10
    #
    def __init__(self, usersItemRatings, metric='pearson', k=1, m=10):
        
        # set self.usersItemRatings
        self.usersItemRatings = usersItemRatings
            
        # set self.k
        if k > 0:   
            self.k = k
        else:
            print ("    (FYI - invalid value of k (must be > 0) - defaulting to 1)")
            self.k = 1
         
        # set self.m
        if m > 0:   
            self.m = m
        else:
            print ("    (FYI - invalid value of m (must be > 0) - defaulting to 10)")
            self.m = 10
            

    #################################################
    # pearson correlation similarity
    # notation: if UserX is Angelica and UserY is Bill, then:
    # userXItemRatings = {"Blues Traveler": 3.5, "Broken Bells": 2.0, "Norah Jones": 4.5, "Phoenix": 5.0, "Slightly Stoopid": 1.5, "The Strokes": 2.5, "Vampire Weekend": 2.0}
    # userYItemRatings = {"Blues Traveler": 2.0, "Broken Bells": 3.5, "Deadmau5": 4.0, "Phoenix": 2.0, "Slightly Stoopid": 3.5, "Vampire Weekend": 3.0}
    def pearsonFn(self, userXItemRatings, userYItemRatings):
        
        sum_xy = 0
        sum_x = 0
        sum_y = 0
        sum_x2 = 0
        sum_y2 = 0
        
        n = len(userXItemRatings.keys() & userYItemRatings.keys())
        
        for item in userXItemRatings.keys() & userYItemRatings.keys():
            x = userXItemRatings[item]
            y = userYItemRatings[item]
            sum_xy += x * y
            sum_x += x
            sum_y += y
            sum_x2 += pow(x, 2)
            sum_y2 += pow(y, 2)
       
        if n == 0:
            print ("    (FYI - personFn n==0; returning -2)")
            return -2
        
        denominator = math.sqrt(sum_x2 - pow(sum_x, 2) / n) * math.sqrt(sum_y2 - pow(sum_y, 2) / n)
        if denominator == 0:
            print ("    (FYI - personFn denominator==0; returning -2)")
            return -2
        else:
            return round((sum_xy - (sum_x * sum_y) / n) / denominator, 2)
            

    #################################################
    # make recommendations for userX from the most similar k nearest neigibors (NNs)
    def recommendKNN(self, userX):
        
        listofusers = {}
        # for given userX, get the sorted list of users - by most similar to least similar   
        for user in self.usersItemRatings.keys():
            pearsonCorrelation = UserBasedFilteringRecommender.pearsonFn(self,self.usersItemRatings[userX], self.usersItemRatings[user])
            
         #writing them to a dictionary by validating if pearson correlation is defined and both users are not same   
            if ((user!=userX) & (pearsonCorrelation != -2)):
                normalisedPearsonCorrelation=(pearsonCorrelation+1)/2
                listofusers[user] = normalisedPearsonCorrelation
        
        #sorting the dictionary in decreasing order of values
        temp = sorted(listofusers.items(), key=operator.itemgetter(1),reverse=True)
        sorted_list = dict(temp) 

        # calcualte the weighted average item recommendations for userX from userX's k NNs
        ratingsSum = 0
        NN = self.k
        
        #Calculating the total of all pearson correlations for k nearest neighbors
        for users in sorted_list.keys():
           if NN==0:
               break
           ratingsSum+=sorted_list[users]
           NN-=1
        ratingsMultiplier = {}
        
        #calculating the corresponding weights to make summation = 1. So that cumulative rating is in range 1-5
        NN = self.k
        for users in sorted_list.keys():
           if NN==0:
               break
           ratingsMultiplier[users] = sorted_list[users]/ratingsSum
           NN-=1   
        #making a master list of all songs       
        masterItemSet = set()
        for nearestneighbor in self.usersItemRatings.keys():
            masterItemSet = set(self.usersItemRatings[nearestneighbor].keys()) | masterItemSet
        masterItemList = list(masterItemSet)
        
        #calculating the effective suggested rating for k nearest neighbor for each song per user
        suggestedRatingsMatrix = {}
        for songs in masterItemList:
            suggestedRating = 0
            for nearestneighbor in ratingsMultiplier.keys():  
                if (songs in self.usersItemRatings[nearestneighbor].keys()):
                    suggestedRating += ratingsMultiplier[nearestneighbor]*self.usersItemRatings[nearestneighbor][songs]
            suggestedRatingsMatrix[songs]=suggestedRating
        
        #suggesting only songs that songs that have not been previously rated by a user
        finalSuggestedDict = {}
        for suggestedSongs in suggestedRatingsMatrix.keys():
            if ((suggestedSongs not in self.usersItemRatings[userX].keys())&(suggestedRatingsMatrix[suggestedSongs]!=0)):
                  finalSuggestedDict[suggestedSongs] = round(suggestedRatingsMatrix[suggestedSongs],2)
       
        
        # return sorted list of recommendations (sorted highest to lowest ratings)
        temp = sorted(finalSuggestedDict.items(), key=operator.itemgetter(1),reverse=True)
        finalSuggestedD = dict(temp) 
        return finalSuggestedD