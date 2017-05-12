import argparse
from pprint import pprint
from collections import defaultdict
from math import log
import sys

def print_clusters(clusters):
	print "{} clusters:".format(len(clusters))

	# format and print each cluster
	for c in clusters:
		str_c = "("
		for l in c:
			str_c += l + ","
		print str_c.replace(" ", "''")[:-1] + ")"

def get_unigramfreq(cluster, f_unigram):
	f = 0.0
	for l in cluster:
		f += f_unigram[l]
	return f

def get_bigramfreq(cluster_1, cluster_2, f_bigram):
	f = 0.0
	for l1 in cluster_1:
		for l2 in cluster_2:
			f += f_bigram[l1 + l2]
	return f

def get_mutual_information(i, j, clusters, (f_unigram, f_bigram)):
	ij = [i, j]

	mt = 0.0
	# first summation term
	for k in range(len(clusters)):
		for m in range(len(clusters)):
			if k in ij or m in ij:
				continue
			f_km = get_bigramfreq(clusters[k], clusters[m], f_bigram)
			if f_km:
				mt += f_km * log(f_km / (get_unigramfreq(clusters[k], f_unigram) * get_unigramfreq(clusters[m], f_unigram)))

	c_ij = clusters[i] + clusters[j]

	# second summation term
	for k in range(len(clusters)):
		if k in ij:
			continue
		f_kij = get_bigramfreq(clusters[k], c_ij, f_bigram)
		if f_kij:
			mt += f_kij * log(f_kij / (get_unigramfreq(clusters[k], f_unigram) * get_unigramfreq(c_ij, f_unigram)))

	# third summation term
	for m in range(len(clusters)):
		if m in ij:
			continue
		f_jim = get_bigramfreq(c_ij, clusters[m], f_bigram)
		if f_jim:
			mt += f_jim * log(f_jim / (get_unigramfreq(c_ij, f_unigram) * get_unigramfreq(clusters[m], f_unigram)))

	# fourth summation term
	f_ijij = get_bigramfreq(c_ij, c_ij, f_bigram)
	if f_ijij:
		mt += f_ijij * log(f_ijij / (get_unigramfreq(c_ij, f_unigram) * get_unigramfreq(c_ij, f_unigram)))

	return mt

def aggl_cluster(f_unigram, f_bigram):
	# clustres C_1, ..., C_n, init as L the 27 characters
	clusters = [[chr(i)] for i in range(ord('a'), ord('z')+1)] + [[" "]]
 	encodings = defaultdict(str)

	# repeat clustering until all clusters are clustered into one
	while len(clusters) > 1:
		(max_i, max_j, max_mt) = (0, 0, -1)

		# for each n(n-1)/2 (i,j) pairs such that i!=j, find the pair that maximizes mutual information
		for i in range(len(clusters)):
			for j in range(i+1, len(clusters)):

				mt = get_mutual_information(i, j, clusters, (f_unigram, f_bigram))
				if mt > max_mt:
					(max_i, max_j, max_mt) = (i, j, mt)
		
		# update encodings
		for l in clusters[max_i]:
			encodings[l] = "0" + encodings[l]
		for l in clusters[max_j]:
			encodings[l] = "1" + encodings[l]

		# merge the i and j clusters
		merge = clusters[max_i] + clusters[max_j]
		del clusters[max_i]
		del clusters[max_j-1]
		clusters.append(merge)

		if len(clusters) == 2 or len(clusters) == 4:
			print_clusters(clusters)
		

	# find the depth of Tree (K), and pad zeros in the least significant bits
	K = max([len(e) for e in encodings.values()])
	for l in encodings:
		encodings[l] = encodings[l] + "0" * (K - len(encodings[l]))

	return encodings

def read_bigram(train_text):
	# read bigram statistics from training text
	train = open(train_text, 'r')

	# count number of unigrams and bigrams in training text
	unigram_count = defaultdict(int)
	bigram_count = defaultdict(int)
	prev = ""

	for line in train:
		for ch in line:
			unigram_count[ch] += 1
			if prev != '':
				bigram_count[prev + ch] += 1
			prev = ch

	# normalize by total counts to get frequency
	total_unigram = sum(unigram_count.values())
	total_bigram = sum(bigram_count.values())
	f_unigram = defaultdict(float, {k: float(v) / total_unigram for k, v in unigram_count.iteritems()})
	f_bigram = defaultdict(float, {k: float(v) / total_bigram for k, v in bigram_count.iteritems()})

	return (f_unigram, f_bigram)


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("train_text", help="file name of training text")
	args = parser.parse_args()

	train_text = args.train_text

	print "\nAgglomerative Clustering of the Vocabulary: "
	print "--------------------------------------------"
	(f_unigram, f_bigram) = read_bigram(train_text)
	encodings = aggl_cluster(f_unigram, f_bigram)
	return (encodings, f_bigram)

if __name__ == '__main__':
	main()
