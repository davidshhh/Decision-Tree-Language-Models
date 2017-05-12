import cluster
import argparse
from collections import defaultdict
from pprint import pprint
from math import log
from copy import deepcopy
import sys

def get_history_cond_prob(h1, h2, history, dev_bit_vectors):
	return 0


def get_mutual_information(question, node, history, dev_bigram, dev_bit_vectors):
	# new histories
	(phi1, w1) = ([], 0)
	(phi2, w2) = ([], 0)

	# split data by question of frontier
	for (ch, bv) in node:
		if bv[question] ==  "0":
			phi1.append((ch, bv))
			w1 += 1
		else:
			phi2.append((ch, bv))
			w2 += 1

	# normalize weights of new clusters
	w1 = float(w1) / len(dev_bit_vectors)
	w2 = float(w2) / len(dev_bit_vectors)

	# locate frontier in history and create new history
	new_history = deepcopy(history)
	for i, (h, w) in enumerate(new_history):
		if node == h:
			del new_history[i]

	new_history = new_history + [(phi1, w1), (phi2, w2)]

	# calculate mutual information
	# setup look up tables for phi prob amd conditional phi prob
	phi = {}
	for i, (h, w) in enumerate(new_history):
		for (ch, bv) in h:
			phi[(ch, bv)] = i

	prob_phi = {i : w for i, (_, w) in enumerate(new_history)}
	con_prob_phi = defaultdict(lambda : defaultdict(int))

	prev = (0,)
	for (w, bv) in dev_bit_vectors:
		if len(prev) > 1:
			con_prob_phi[phi[prev]][phi[(w, bv)]] += 1
		prev = (w, bv)

	con_prob_phi = {w1 : {w2 : (float(count) / sum(w2_counts.values())) for w2, count in w2_counts.iteritems()} for w1, w2_counts in con_prob_phi.iteritems()}

	#print con_prob_phi
	#print prob_phi

	mt = 0.0
	prev = (0,)
	for (w, bv) in dev_bit_vectors:
		if len(prev) > 1:

			#if log(con_prob_phi[phi[prev]][phi[(w, bv)]] / prob_phi[phi[(w, bv)]]) < 0:
			#	print log(con_prob_phi[phi[prev]][phi[(w, bv)]] / prob_phi[phi[(w, bv)]])
			mt += dev_bigram[(prev, (w, bv))] * log(con_prob_phi[phi[prev]][phi[(w, bv)]] / prob_phi[phi[(w, bv)]])
			#print mt
		prev = (w, bv)

	print mt
	return (mt, new_history)

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

			# store bigram count of encoding vector and letter
			if (prev != ""):
				bigram[(prev, (ch, bit_vector))] += 1
			prev = (ch, bit_vector)

			quadgram.pop(0)


	# normalize bigram of vectors to frequencies for p(w1, w2) calculation
	total_bigram = sum(bigram.values())
	bigram = defaultdict(float, {k : float(v) / total_bigram for k, v in bigram.iteritems()})

	#total_count = sum(bit_vectors.values())
	#bit_vectors = {k: float(v) / total_count for k, v in bit_vectors.iteritems()}

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
		q_can = -1
		mt_can = -1

		# for each of the three questions, check mutual information and find 'candidate'
		for q in range(len(qs)):
			(mt, new_history) = get_mutual_information(qs[q], node, history, dev_bigram, dev_bit_vectors)
			if mt > mt_can:
				(q_can, mt_can) = (q, mt)

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
