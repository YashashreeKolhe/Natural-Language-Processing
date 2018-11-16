#!/usr/bin/python3
import numpy as np
import sys
import nltk
from sklearn.metrics import precision_recall_fscore_support as score

def compute_statistics(final_sequence, expected_sequence):
    unique_tags = list()
    floatFormat = "{:.2f}"
    
    for tag in final_sequence:
        if tag not in unique_tags:
            unique_tags.append(tag)
    precision, recall, fscore, support = score(expected_sequence, final_sequence)
    
    fw = open("precision_recall_fscore.txt", "w")
    fw.write('{:5} {:10} {:10} {:10}'.format("Tag", "Precision", "Recall", "F-Measure"))
    fw.write("\n")
    
    for (t, p, r, f) in zip(unique_tags, precision, recall, fscore):
        fw.write('{:5} {:10} {:10} {:10}'.format(str(t), str(floatFormat.format(p)), str(floatFormat.format(r)), str(floatFormat.format(f))))
        fw.write("\n")
    
    fw.close()


def print_prob(dictionary, filename):
	fw = open(filename, 'w')
	for (term1, term2) in dictionary:
		fw.write(term1 + "|" + term2 + "=" + str(dictionary[(term1, term2)]))
		fw.write("\n")
		fw.flush()
	fw.close()


def calculate_probabilities(training_set, pos_count, transmission_prob, emission_prob, number_of_sent):
	fr = open(training_set, 'r')
	for line in fr:
		count = 0
		words = line.split()
		for i in range(0, len(words)):
			if words[i].split('_')[1] not in pos_count:
				pos_count[words[i].split('_')[1]] = 1
			else:
				pos_count[words[i].split('_')[1]] += 1
			if (words[i].split('_')[0], words[i].split('_')[1]) not in emission_prob:
				emission_prob[(words[i].split('_')[0], words[i].split('_')[1])] = 1
			else:
				emission_prob[(words[i].split('_')[0], words[i].split('_')[1])] += 1
			if i == 0:
				term = words[0].split('_')[0]
				pos = words[0].split('_')[1]
				if (pos, 'null') not in transmission_prob:
					transmission_prob[(pos, 'null')] = 1
				else:
					transmission_prob[(pos, 'null')] += 1
			else:
				term = words[i].split('_')[0]
				pos = words[i].split('_')[1]
				prev_pos = words[i-1].split('_')[1]
				if (pos, prev_pos) not in transmission_prob:
					transmission_prob[(pos, prev_pos)] = 1
				else:
					transmission_prob[(pos, prev_pos)] += 1
	
	for(pos1, pos2) in transmission_prob:
		if pos2 == 'null':
			transmission_prob[(pos1,pos2)] = float(transmission_prob[(pos1, pos2)]/number_of_sent)
		else:
			transmission_prob[(pos1, pos2)] = float(transmission_prob[(pos1, pos2)]/pos_count[pos2])
	
	print_prob(transmission_prob, 'transmission_prob.txt')
	
	for (word, pos) in emission_prob:
		emission_prob[(word, pos)] = float(emission_prob[(word, pos)]/pos_count[pos])

	print_prob(emission_prob, 'emission_prob.txt')

def input_processing(line):
	observations = line.split()
	return observations

def viterbi_computation(observations, transmission_prob, emission_prob, pos_count):
	list_of_pos = list()
	for key in pos_count:
		list_of_pos.append(key)
	
	 
	viterbi_matrix = [[0 for i in range(0, len(observations))] for j in range(0, len(pos_count) + 1)]
	backpointer = [[0 for i in range(0, len(observations))] for j in range(0, len(pos_count) + 1)]
	
	for i, s in enumerate(pos_count):
		if (s, 'null') not in transmission_prob:
			transmission_prob[(s, 'null')] = 0.0001
		if (observations[0], s) not in emission_prob:
			emission_prob[(observations[0], s)] = 0.0001
		viterbi_matrix[i][0] = transmission_prob[(s, 'null')] * emission_prob[(observations[0], s)]
		backpointer[i][0] = -1
	
	#print(observations[0] + "_" + str(list_of_pos[np.argmax(np.array(viterbi_matrix)[:, 0])]))
	sentences = list()
	tags = list()
	for j, obs in enumerate(observations[1:]):
		for i, s in enumerate(pos_count):
			vals1 = [0 for i in range(0, len(pos_count))]
			vals2 = [0 for i in range(0, len(pos_count))]
			for k, prev_state in enumerate(pos_count):
				if (s, prev_state) not in transmission_prob:
					transmission_prob[(s, prev_state)] = 0.0001
				if (obs, s) not in emission_prob:
					emission_prob[(obs, s)] = 0.0001
					
				vals1[k] = viterbi_matrix[k][j] * transmission_prob[(s, prev_state)] * emission_prob[(obs, s)]
				
				if (s, prev_state) not in transmission_prob:
					transmission_prob[(s, prev_state)] = 0.0001
				
				vals2[k] = viterbi_matrix[k][j] * transmission_prob[(s, prev_state)]
			#print(vals2)
			viterbi_matrix[i][j+1] = max(vals1)
			backpointer[i][j] = np.argmax(vals2)
		#print(np.array(viterbi_matrix)[:, j+1])
		#print(observations[j] + '_' + str(list_of_pos[np.argmax(np.array(viterbi_matrix)[:, j])]))
		sentences.append(observations[j] + '_' + str(list_of_pos[np.argmax(np.array(viterbi_matrix)[:, j])]))
		tags.append(str(list_of_pos[np.argmax(np.array(viterbi_matrix)[:, j])]))
	
	#print(observations[len(observations) - 1] + "_" + str(list_of_pos[np.argmax(np.array(viterbi_matrix)[:, len(observations) - 1])]))
	sentences.append(observations[len(observations) - 1] + '_' + str(list_of_pos[np.argmax(np.array(viterbi_matrix)[:, len(observations) - 1])]))
	tags.append(str(list_of_pos[np.argmax(np.array(viterbi_matrix)[:, len(observations) - 1])]))
	return (sentences, tags)

def compute_expected_tag_sequence(observations):
	pos_tags = nltk.pos_tag(observations)
	tag_sequence = list()
	for (word, tag) in pos_tags:
		tag_sequence.append(tag)
	return tag_sequence

def main():
	if len(sys.argv) < 3 or len(sys.argv) > 3:
		print('Usage: ./run.sh <training_set> <test_set>')
		exit(1)
	
	pos_count = dict()
	transmission_prob = dict()
	emission_prob = dict()

	
	fr = open(sys.argv[1], 'r')
	lines = list()
	for line in fr:
		lines.append(line)
	fr.close()

	calculate_probabilities(sys.argv[1], pos_count, transmission_prob, emission_prob, len(lines))

	#print(pos_count)

	fw = open('output.txt', 'w')
	
	final_tag_sequence = list()
	expected_sequence = list()
	
	fr = open(sys.argv[2], 'r')
	for line in fr:
		observations = input_processing(line.strip())
		sentence, final_sequence = viterbi_computation(observations, transmission_prob, emission_prob, pos_count)
		final_tag_sequence += final_sequence
		expected_sequence += compute_expected_tag_sequence(observations)
		fw.write(" ".join(sentence))
		fw.write('\n')
		fw.flush()

	fw.close()
	
	compute_statistics(final_tag_sequence, expected_sequence)
	
if __name__ == '__main__':
	main()
