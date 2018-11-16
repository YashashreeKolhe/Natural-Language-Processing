# -*- coding: utf-8 -*-

import sys
from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize
from sklearn.metrics import precision_recall_fscore_support as score



def computeStatistics(expected_tags, generated_tags):
	unique_tags = list()
	floatFormat = "{:.2f}"
	
	for tag in generated_tags:
		if tag not in unique_tags:
			unique_tags.append(tag)
	
	precision, recall, fscore, support = score(expected_tags, generated_tags)
			
	fw = open("precision_recall_fscore.txt", "w")
	fw.write('{:20} {:10} {:10} {:10}'.format("Tag", "Precision", "Recall", "F-Measure"))
	fw.write("\n")
			
	for (t, p, r, f) in zip(unique_tags, precision, recall, fscore):
		fw.write('{:20} {:10} {:10} {:10}'.format(str(t), str(floatFormat.format(p)), str(floatFormat.format(r)), str(floatFormat.format(f))))
		fw.write("\n")
	fw.close()

def getTags(filename):
	tag_sequence = list()
	fr = open(filename, 'r')
	for line in fr:
		tokenized_line = word_tokenize(line)
		for token in tokenized_line:
			if '_' in token:
				tag_sequence.append(token.split('_')[1])
			else:
				tag_sequence.append('O')
	fr.close()
	return tag_sequence

def getOutputAsString(classified_text):
	output_str = ""
	for token in classified_text:
		if token[1] == 'O':
			output_str += token[0] + " "
		else:
			output_str += token[0] + "_" + token[1] + " "
	return output_str
	
def main():
	if len(sys.argv) < 3 or len(sys.argv) > 3:
		print("Usage: python3 111508041_Assign5-Code.py <pretrained_file> <test_file>")
		exit(1)
	
	expected_tags = getTags(sys.argv[1])
	print(expected_tags)
	try:
		st = StanfordNERTagger('/home/dell/Practicals/NLP/111508041_Assign5/stanford-ner-2018-02-27/classifiers/english.muc.7class.distsim.crf.ser.gz', '/home/dell/Practicals/NLP/111508041_Assign5/stanford-ner-2018-02-27/stanford-ner.jar', encoding="utf-8")
	except LookUpError:
		print("Please change the path to the jar file")
		exit(1)
	
	fr = open(sys.argv[2], 'r')
	fw = open('NER_labelled_Corpus_111508041.txt', 'w')

	for lines in fr:
		tokenized_text = word_tokenize(lines)
		classified_text = st.tag(tokenized_text)
		output_str = getOutputAsString(classified_text)
		fw.write(output_str)
		fw.write('\n')
		fw.flush()
	fw.close()
	fr.close()

	generated_tags = getTags('output.txt')
	print(generated_tags)
	computeStatistics(expected_tags, generated_tags)
		

if __name__ == '__main__':
	main()
