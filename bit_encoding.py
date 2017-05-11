import cluster
import argparse
from pprint import pprint


def bit_encoding(encodings, train_text):
	# split into dev and heldout data
	train = open(train_text, 'r')
	text = train.read()
	dev = text[0:int(len(text) * 0.8)]
	held = text[int(-len(text) * 0.2):]

	quadgram = []
	for c in dev:
		if len(quadgram) == 4:
			quadgram.pop(0)

		quadgram.append(c)

	return "hi"

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("train_text", help="file name of training text")
	args = parser.parse_args()
	train_text = args.train_text
	encodings = ""
	#encodings = cluster.main()
	bit_encoding(encodings, train_text)
