import sys
import math
import random
import numpy as np
import requests

AVAILABLE_CHOICES = [0, 1, 2, 3, 4]
AVAILABLE_CHOICE_NUMBER = 8

class Node(object):
	def __init__(self):
		self.parent = None
		self.children=[]
		self.visit_times=0
		self.quality_value = 0.0
		self.state=None
	def set_state(self,state):
		self.state = state
	def get_state(self):
		return self.state
	def set_parent(self,parent):
		self.parent = parent
	def get_parent(self):
		return self.parent
	def set_children(self,children):
		self.children = children
	def get_children(self):
		return self.children
	def get_visit_times(self):
		return self.visit_times
	def set_visit_times(self, times):
		self.visit_times = times
	def visit_times_add_one(self):
		self.visit_times +=1
	def get_quality_value(self):
		return self.quality_value
	def set_quality_value(self, value):
		self.quality_value = value
	def quality_value_add_n(self,n):
		self.quality_value +=n
	def is_all_expand(self):
		if len(self.children)==AVAILABLE_CHOICE_NUMBER :
			return True
		else:
			return False
	def add_child(self,sub_node):
		sub_node.set_parent(self)
		self.children.append(sub_node)
	def __repr__(self):
		return "Node:{},Q/N:{}/{},state:{}".format(hash(self),self.quality_value,self,visit_times,self.state)

class State:#游戏过程中的状态
    def __init__(self):
        self.a=[0,0,0,0]#自己的四个花色牌数
        self.b=[0,0,0,0]#对手的四个花色牌数
        self.pile=[0,0,0,0]#放置区的四个花色牌数
        self.color=4#放置区顶的卡牌花色，4表示没有,0~3表示四种花色
        self.deck=[13,13,13,13]#卡组中四个花色牌数
        self.choices=[]#选择过程记录
        self.op=0#标识这一回合是谁操作
    def is_end(self):
        if self.deck==[0,0,0,0] :
            return True
        else:
            return False
    def result(self):
        sum=0;
        for x in a:
            sum+=x
        for x in b:
            sum-=x
        return sum
    def set_a(self,aa):
        self.a=aa
    def set_b(self,bb):
        self.b=bb
    def set_pile(self,Pile,Color):
        self.pile=Pile
        self.color=Color
    def set_deck(self,Deck):
        self.deck=Deck
    def set_choices(self,Choices,Op):
        self.choices=Choices
        self.op=Op
    def next_state(self):
        random_choice=random.choice([choice for choice in AVAILABLE_CHOICES])
        next=State()
        if random_choice<4:
            if op==1:
                next.set_a(self.a)
                next.a[random_choice]-=1
                next.set_b(self.b)
                next.set_deck(self.deck)
                if random_choice==self.color:
                    next.set_deck([0,0,0,0],4)
                    for x in range(0,3):
                        next.a[x]+=self.pile[x]
                    next.a[random_choice]+=1
                else:
                    next.set_pile(self.pile,random_choice)
                    next.pile[random_choice]+=1
                next.set_choices(self.choices+[random_choice],self.op^1)
            else:
                next.set_a(self.a)
                next.set_b(self.b)
                next.b[random_choice]-=1
                next.set_deck(self.deck)
                if random_choice==self.color:
                    next.set_deck([0,0,0,0],4)
                    for x in range(0,3):
                        next.b[x]+=self.pile[x]
                    next.b[random_choice]+=1
                else:
                    next.set_pile(self.pile,random_choice)
                    next.pile[random_choice]+=1
                next.set_choices(self.choices+[random_choice],self.op^1)
        else:
            next.set_a(self.a)
            next.set_b(self.b)
            next.set_deck(self.deck)
            sum=0.0
            temp=0.0
            for x in range(0,3):
                sum+=next.deck[x]
            sum=sum*random.random()
            draw=4
            for x in range(0,3):
                temp+=next.deck[x]
                if temp>=sum:
                    draw=x
                    break
            if draw==self.color:
                if op==1:
                    for x in range(0,3):
                        next.a[x]+=self.pile[x]
                    next.a[draw]+=1
                else:
                    for x in range(0,3):
                        next.b[x]+=self.pile[x]
                    next.a[draw]+=1
                next.set_pile([0,0,0,0],4)
            else:
                next.set_pile(self.pile,draw)
                next.pile[draw]+=1
            return next

def mcts(node):#蒙特卡洛树搜索
    budget=100
    for i in range(budget):
        expand_node=tree_policy(node)
        reward = default_policy(expand_node)
        backup(expand_node,reward)
    return best_child(node,False)
def best_child(node,is_exploration):#若子节点都扩展完了，求UCB值最大的子节点
	best_score=-sys.maxsize
	best_sub_node = None
	for sub_node in node.get_children():
		if is_exploration:
			C=1/math.sqrt(2.0)
		else:
			C=0.0
		left=sub_node.get_quality_value()/sub_node.get_visit_times()
		right=2.0*math.log(node.get_visit_times())/sub_node.get_visit_times()
		score=left+C*math.sqrt(right)
		if score>best_score:
			best_sub_node = sub_node
	return best_sub_node
def tree_policy(node):#选择子节点的策略
	while node.get_state().is_terminal()==False:
		if node.is_all_expand():
			node=best_child(node,True)
		else:
			sub_node = expand(node)
			return sub_node
	return node
def default_policy(node):
	current_state = node.get_state()
	while current_state.is_terminal==False:
		current_state = current_state.get_next_state_with_random_choice()
	final_state_reward=current_state.compute_reward()
	return final_state_reward
def backup(node,reward):
	while node != None:
		node.visit_times_add_one()
		node.quality_value_add_n(reward)
		node = node.parent
