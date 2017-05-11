import argparse

def cluster(train_text):
	train = open(train_text, 'r')
	prev = ""
	for line in train:
		for ch in line:
			if prev != '':
				
			prev = ch


parser = argparse.ArgumentParser()
parser.add_argument("train_text", help="file name of training text")
args = parser.parse_args()

train_text = args.train_text
cluster(train_text)