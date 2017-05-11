import cluster
import argparse
from pprint import pprint

def bit_encoding(encodings):

	return "hi"

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("train_text", help="file name of training text")
	args = parser.parse_args()
	train_text = args.train_text

	encodings = cluster.main()
	bit_encoding(encodings)
