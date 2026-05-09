import pandas as pd
import numpy as np
from itertools import combinations
from collections import defaultdict

class Apriori:
    def __init__(self, min_support=0.1, min_confidence=0.5):
        self.min_support = min_support
        self.min_confidence = min_confidence
    
    def fit(self, transactions):
        """
        拟合模型，生成频繁项集和关联规则
        """
        # 计算单个项目的支持度
        item_counts = defaultdict(int)
        for transaction in transactions:
            for item in transaction:
                item_counts[item] += 1
        
        n_transactions = len(transactions)
        
        # 生成1-项集
        frequent_itemsets = {}
        current_itemsets = []
        for item, count in item_counts.items():
            support = count / n_transactions
            if support >= self.min_support:
                current_itemsets.append(frozenset([item]))
                frequent_itemsets[frozenset([item])] = support
        
        k = 2
        while current_itemsets:
            # 生成候选k-项集
            candidate_itemsets = self._generate_candidates(current_itemsets, k)
            
            # 计算候选k-项集的支持度
            candidate_counts = defaultdict(int)
            for transaction in transactions:
                transaction_set = set(transaction)
                for candidate in candidate_itemsets:
                    if candidate.issubset(transaction_set):
                        candidate_counts[candidate] += 1
            
            # 筛选频繁k-项集
            current_itemsets = []
            for candidate, count in candidate_counts.items():
                support = count / n_transactions
                if support >= self.min_support:
                    current_itemsets.append(candidate)
                    frequent_itemsets[candidate] = support
            
            k += 1
        
        self.frequent_itemsets = frequent_itemsets
        self.rules = self._generate_rules()
        return self
    
    def _generate_candidates(self, itemsets, k):
        """
        生成候选k-项集
        """
        candidates = set()
        n = len(itemsets)
        for i in range(n):
            for j in range(i + 1, n):
                itemset1 = itemsets[i]
                itemset2 = itemsets[j]
                union = itemset1.union(itemset2)
                if len(union) == k:
                    candidates.add(union)
        return candidates
    
    def _generate_rules(self):
        """
        生成关联规则
        """
        rules = []
        for itemset in self.frequent_itemsets:
            if len(itemset) < 2:
                continue
            
            # 生成所有可能的前件和后件组合
            for i in range(1, len(itemset)):
                for antecedent in combinations(itemset, i):
                    antecedent = frozenset(antecedent)
                    consequent = itemset - antecedent
                    
                    # 计算置信度
                    support_itemset = self.frequent_itemsets[itemset]
                    support_antecedent = self.frequent_itemsets[antecedent]
                    confidence = support_itemset / support_antecedent
                    
                    if confidence >= self.min_confidence:
                        # 计算提升度
                        if consequent in self.frequent_itemsets:
                            support_consequent = self.frequent_itemsets[consequent]
                            lift = confidence / support_consequent
                        else:
                            lift = 0
                        
                        rules.append({
                            'antecedent': set(antecedent),
                            'consequent': set(consequent),
                            'support': support_itemset,
                            'confidence': confidence,
                            'lift': lift
                        })
        return rules
    
    def get_frequent_itemsets(self):
        """
        获取频繁项集
        """
        return self.frequent_itemsets
    
    def get_rules(self):
        """
        获取关联规则
        """
        return self.rules
