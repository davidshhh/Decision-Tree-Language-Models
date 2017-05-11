import cluster
import argparse
from pprint import pprint


def get_mutual_information(i, j, clusters):
	return "hi"

def read_bit_vectors(encodings, text):
	bit_vectors = []
	quadgram = []

	for ch in text:
		quadgram.append(ch)
		if len(quadgram) == 4:
			bit_vector = ""
			for i in range(3):
				bit_vector += encodings[quadgram[i]]
			bit_vectors.append((bit_vector, ch))
			quadgram.pop(0)
	return bit_vectors

def bit_encoding(encodings, train_text):
	# split into dev and heldout data
	train = open(train_text, 'r')
	text = train.read()
	dev = text[0:int(len(text) * 0.8)]
	held = text[int(-len(text) * 0.2):]

	dev_bit_vectors = read_bit_vectors(encodings, dev)
	held_bit_vectors = read_bit_vectors(encodings, held)

	pos = [9 * i for i in range(3)]
	# maximize mutual information

	print dev_bit_vectors



if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("train_text", help="file name of training text")
	args = parser.parse_args()
	train_text = args.train_text
	encodings = cluster.main()
	bit_encoding(encodings, train_text)
