import cluster
import argparse
from collections import defaultdict
from pprint import pprint
from math import log
from copy import deepcopy
import sys

def compute_entropy(node, bigram, phi, con_prob_phi):
	entropy = 0.0
	prev = (0,)

	visited = set()
	for (w, bv) in node:
		if len(prev) > 1 and (prev, (w, bv)) not in visited:
			visited.add((prev, (w, bv)))
			entropy -= bigram[(prev, (w, bv))] * log(con_prob_phi[phi[prev]][(w, bv)], 2)
		prev = (w, bv)
	return entropy

def build_con_prob(node, phi):
	prev = (0,)
	con_prob_phi = defaultdict(lambda: defaultdict(int))
	for (w, bv) in node:
		if len(prev) > 1:
			con_prob_phi[phi[prev]][(w, bv)] += 1
		prev = (w, bv)
	con_prob_phi = {phi_w1 : {w2 : (float(count) / sum(w2_counts.values())) for w2, count in w2_counts.iteritems()} for phi_w1, w2_counts in con_prob_phi.iteritems()}
	return con_prob_phi

def build_phi(history):
	phi = {}
	for i, (h, _) in enumerate(history):
		for (ch, bv) in h:
			phi[(ch, bv)] = i
	# SMOOTH
	return defaultdict(int, phi)

def get_entropy_text(text, history):
	phi = build_phi(history)
	con_prob = build_con_prob(text, phi)
	bigram = get_bigram(text)
	entropy = compute_entropy(text, bigram, phi, con_prob)

	return entropy

def get_bigram(text):
	bigram = defaultdict(int)
	prev = (0,)

	# collect bigram statistics
	for (ch, bv) in text:

		if len(prev) > 1:
			bigram[(prev, (ch, bv))] += 1
		prev = (ch, bv)
	
	# normalize bigram of vectors to frequencies for p(w1, w2) calculation
	total_bigram = sum(bigram.values())
	bigram = defaultdict(float, {k : float(v) / total_bigram for k, v in bigram.iteritems()})
	
	return bigram


def get_entropy(question, node):
	# new histories
	(phi1, w1) = ([], 0)
	(phi2, w2) = ([], 0)

	prev = (0,)
	# split data by question of frontier
	for (ch, bv) in node:
		if bv[question] ==  "0":
			phi1.append((ch, bv))
			w1 += 1
		else:
			phi2.append((ch, bv))
			w2 += 1

		prev = (ch, bv)

	# count bigrams for p(w1, w2)
	bigram = get_bigram(node)

	# normalize weights of each split
	w1 = float(w1) / len(node)
	w2 = float(w2) / len(node)

	split = [(phi1, w1), (phi2, w2)]

	# setup look up tables for phi prob amd conditional phi prob
	#phi = build_phi(split)

	phi = build_phi(split)

	con_prob_phi = build_con_prob(node, phi)

	# compute the entropy of the predicted letter for each permissible question
	# based on the development data that reaches that node

	entropy = compute_entropy(node, bigram, phi, con_prob_phi)

	return (entropy, split)

def read_bit_vectors(encodings, text):
	bit_vectors = []
	quadgram = []

	# load (l1, l2, l3) into bit vectors
	prev = ""
	for ch in text:
		quadgram.append(ch)
		if len(quadgram) == 4:

			# construct vector base on previous three words
			bit_vector = ""
			for i in range(3):
				bit_vector += encodings[quadgram[i]]
			bit_vectors.append((ch, bit_vector))

			quadgram.pop(0)

	return bit_vectors

def bit_encoding(encodings, train_text, f_bigram):
	# split into dev and heldout data
	train = open(train_text, 'r')
	text = train.read()
	dev = text[0:int(len(text) * 0.8)]
	held = text[int(-len(text) * 0.2):]

	dev_bit_vectors = read_bit_vectors(encodings, dev)
	held_bit_vectors = read_bit_vectors(encodings, held)

	# starting positions of each question
	questions = [9 * i for i in range(3)]

	# starting from the root of the tree, includes frequencies for computing new cluster weight
	frontiers = [(dev_bit_vectors, questions)]
	# Phi, starting with just one clustering represented by all words and the weight of cluster
	history = [(dev_bit_vectors, 1.0)]


	# conitnue splitting until all nodes are terminal
	while frontiers:

		(node, qs) = frontiers.pop(0)
		# maximize mutual information asked by question and choose the question as 'candidate'
		(q_can, en_can, split_can) = (-1, -1, [])

		# for each of the three questions, check mutual information and find 'candidate'
		for q in range(len(qs)):
			(en, split) = get_entropy(qs[q], node)
			if en > en_can:
				(q_can, en_can, split_can) = (q, en, split)

		# check the entropy reduction on the held out data by splitting this candidate
		(entropy, _) = get_entropy(q_can, held_bit_vectors)
		entropy_ori = get_entropy_text(held_bit_vectors, history)

		entropy_reduction = entropy_ori - entropy
		print entropy
		print entropy_ori
		print entropy_reduction

		# split node
		if entropy_reduction > 0.005:

		 	# locate frontier in history and create new history
		 #	for i, (h, w) in enumerate(history):
		 #		if node == h:
		 #			del new_history[i]
	 
	 	#	history = history + [(phi1, w1), (phi2, w2)]


		# declare node terminal


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("train_text", help="file name of training text")
	args = parser.parse_args()
	train_text = args.train_text

	(encodings, f_bigram) = cluster.main()

	print "\nBit-Encoding Based Decision-Tree Language Model:"
	print "------------------------------------------------"

	bit_encoding(encodings, train_text, f_bigram)
