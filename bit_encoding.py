import cluster
import argparse
from collections import defaultdict
from pprint import pprint
from math import log
from copy import deepcopy
import sys

def get_history_cond_prob(h1, h2, history, dev_bit_vectors):
	return 0


def get_mutual_information(question, node):
	# new histories
	(phi1, w1) = ([], 0)
	(phi2, w2) = ([], 0)

	# collect bigram statistics for the text at this node
	prev = (0,)
	bigram = defaultdict(int)

	# split data by question of frontier
	for (ch, bv) in node:
		if bv[question] ==  "0":
			phi1.append((ch, bv))
			w1 += 1
		else:
			phi2.append((ch, bv))
			w2 += 1
		if len(prev) > 1:
			bigram[(prev, (ch, bv))] += 1
		prev = (ch, bv)

	# normalize bigram of vectors to frequencies for p(w1, w2) calculation
	total_bigram = sum(bigram.values())
	bigram = defaultdict(float, {k : float(v) / total_bigram for k, v in bigram.iteritems()})

	# normalize weights of each split
	w1 = float(w1) / len(node)
	w2 = float(w2) / len(node)

	split = [(phi1, w1), (phi2, w2)]

	# setup look up tables for phi prob amd conditional phi prob
	phi = {}
	for i, (h, w) in enumerate(split):
		for (ch, bv) in h:
			phi[(ch, bv)] = i

	prob_phi = {i : w for i, (_, w) in enumerate(split)}
	con_prob_phi = defaultdict(lambda : defaultdict(int))

	# compute the entropy of the predicted letter for each permissible question
	# based on the development data that reaches that node
	prev = (0,)
	for (w, bv) in node:
		if len(prev) > 1:
			con_prob_phi[phi[prev]][(w, bv)] += 1
		prev = (w, bv)

	con_prob_phi = {phi_w1 : {w2 : (float(count) / sum(w2_counts.values())) for w2, count in w2_counts.iteritems()} for phi_w1, w2_counts in con_prob_phi.iteritems()}

	entropy = 0.0
	prev = (0,)

	visited = set()
	for (w, bv) in node:
		if len(prev) > 1 and (prev, (w, bv)) not in visited:
			visited.add((prev, (w, bv)))
			entropy += bigram[(prev, (w, bv))] * log(con_prob_phi[phi[prev]][(w, bv)], 2)
		prev = (w, bv)

	print entropy
	return (entropy, split)

def read_bit_vectors(encodings, text):
	bit_vectors = []
	quadgram = []
	bigram = defaultdict(int)

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

	return (bigram, bit_vectors)

def bit_encoding(encodings, train_text, f_bigram):
	# split into dev and heldout data
	train = open(train_text, 'r')
	text = train.read()
	dev = text[0:int(len(text) * 0.8)]
	held = text[int(-len(text) * 0.2):]

	(dev_bigram, dev_bit_vectors) = read_bit_vectors(encodings, dev)
	(held_bigram, held_bit_vectors) = read_bit_vectors(encodings, held)

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
		(q_can, mt_can, split_can) = (-1, -1, [])

		# for each of the three questions, check mutual information and find 'candidate'
		for q in range(len(qs)):
			(mt, split) = get_mutual_information(qs[q], node)
			if mt > mt_can:
				(q_can, mt_can, split_can) = (q, mt, split)

		# check the entropy reduction on the held out data by splitting this candidate


		# split node


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
