import sys
import os
from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize
import nltk

raw_dataset_path = 'raw'
tagged_dataset_path = 'NER_labelled_Corpus_111508041'

count_of_classes = dict()

def calculateProbability():
	print(count_of_classes)
	fw = open('Stat_NER_111508041.txt', 'w')
	total_count = 0
	for classname in count_of_classes.keys():
		total_count += count_of_classes[classname]
	fw.write("{:20} {:20}".format("KEY", "PROBABILITY"))
	fw.write("\n")
	for classname in count_of_classes.keys():
		fw.write("{:20} {:20}".format(classname, count_of_classes[classname]/total_count))
		fw.write("\n")
		fw.flush()
	fw.close()	

def printContextToFile(context, classname):
	fw = open('Pattern/Pattern_' + classname + '_111508041.txt', 'a+')
	#fw.write('{:20} {:30} {:20} {:30} {:20}'.format("CLASS", "PREV_WORD", "PREV_TAG", "NEXT_WORD", "NEXT_TAG"))
	#fw.write("\n")
	#fw.flush()
	count = 0
	for key in context.keys():
		if key == classname:
			for (current_pos, prev_prev_word, prev_prev_tag, prev_word, prev_tag, next_word, next_tag, next_next_word, next_next_tag) in context[key]:
				count += 1
				fw.write('{:15} {:18} {:10} {:18} {:10} {:18} {:10} {:18} {:10}'.format(current_pos, prev_prev_word, prev_prev_tag, prev_word, prev_tag, next_word, next_tag, next_next_word, next_next_tag))
				fw.write('\n')
				fw.flush()
			if key not in count_of_classes.keys():
				count_of_classes[key] = count
			else:
				count_of_classes[key] += count
	fw.close()
			

def create_reference_for_context_computation(ner_tagged_text, pos_tagged_text):
	context = dict()
	for i, (token, tag) in enumerate(ner_tagged_text):
		if tag != 'O':
			if (i-1) >= 0:
				(prev_word, prev_tag) = pos_tagged_text[i-1]
				#if prev_tag == 'NNP':
					#(prev_word, prev_tag) = ner_tagged_text[i-1]
			else:
				prev_word = 'NULL'
				prev_tag = 'NULL'
			if (i-2) >= 0:
				(prev_prev_word, prev_prev_tag) = pos_tagged_text[i-2]
				#if prev_prev_tag == 'NNP':
					#(prev_prev_word, prev_prev_tag) = ner_tagged_text[i-2]		
			else:
				prev_prev_word = 'NULL'
				prev_prev_tag = 'NULL'
			if (i-1) <= (len(pos_tagged_text) - 1):
				(next_word, next_tag) = pos_tagged_text[i+1]
				#if next_tag == 'NNP':
					#(next_word, next_tag) = ner_tagged_text[i+1]
			else:
				next_word = 'NULL'
				next_tag = 'NULL'
			if (i+2) <= (len(pos_tagged_text)-1):
				(next_next_word, next_next_tag) = pos_tagged_text[i+2]
				#if next_next_tag == 'NNP':
					#(next_next_word, next_next_tag) = ner_tagged_text[i+2]					
			else:
				next_next_word = 'NULL'
				next_next_tag = 'NULL'
			if tag not in context.keys():
				context[tag] = list()
			print(pos_tagged_text[i])
			if (pos_tagged_text[i][1], prev_prev_word, prev_prev_tag, prev_word, prev_tag, next_word, next_tag, next_next_word, next_next_tag) not in context[tag]:
				context[tag].append((pos_tagged_text[i][1], prev_prev_word, prev_prev_tag, prev_word, prev_tag, next_word, next_tag, next_next_word, next_next_tag))
	return context

def getOutputAsString(classified_text):
	output_str = ""
	for token in classified_text:
		if token[1] == 'O':
			output_str += token[0] + " "
		else:
			output_str += token[0] + "_" + token[1] + " "
	return output_str


def create_postagged_dataset(raw_dataset_path, tagged_dataset_path):
	files = list()
	for (dirpath, dirnames, filenames) in os.walk(raw_dataset_path):
		files.extend(filenames)
	
	try:
		st = StanfordNERTagger('/home/dell/Practicals/NLP/111508041_Assign5a/stanford-ner-2018-02-27/classifiers/english.muc.7class.distsim.crf.ser.gz', '/home/dell/Practicals/NLP/111508041_Assign5a/stanford-ner-2018-02-27/stanford-ner.jar', encoding="utf-8")
	except LookUpError:
		print("Please change the path to the jar file")
		exit(1)
	
	for classname in ["PERSON", "ORGANIZATION", "DATE", "TIME", "MONEY", "PERCENT", "LOCATION"]:
		fw = open('Pattern/Pattern_' + classname + '_111508041.txt', 'w')
		fw.write('{:15} {:18} {:10} {:18} {:10} {:18} {:10} {:18} {:10}'.format("POS_CURR", "PREV2_WORD", "PREV2_TAG", "PREV_WORD", "PREV_TAG", "NEXT_WORD", "NEXT_TAG", "NEXT2_WORD", "NEXT2_TAG"))
		fw.write("\n")
		fw.flush()
		fw.close()
	
	fw2 = open('Stat_NER_111508041.txt', 'w')
	fw2.write('{:20} {:20}'.format("CLASS", "PROBABILITY"))
			
	for f in files:
		fr = open(raw_dataset_path + "/" + f, 'r')
		fw = open(tagged_dataset_path + "/" + f, 'w')
		for line in fr:
			if ".START" in line:
				continue
			tokenized_line = word_tokenize(line)
			ner_tagged_text = st.tag(tokenized_line)
			pos_tagged_text = nltk.pos_tag(tokenized_line)
			output_str = getOutputAsString(ner_tagged_text)
			fw.write(output_str)
			fw.write('\n')
			fw.flush()
			context = create_reference_for_context_computation(ner_tagged_text, pos_tagged_text)
			if bool(context) != False:
				print(context)
				printContextToFile(context, "PERSON")
				printContextToFile(context, "ORGANIZATION")
				printContextToFile(context, "DATE")
				printContextToFile(context, "TIME")
				printContextToFile(context, "LOCATION")
				printContextToFile(context, "MONEY")
				printContextToFile(context, "PERCENT")
		fw.close()
		fr.close()
	calculateProbability()

def main():
	create_postagged_dataset(raw_dataset_path, tagged_dataset_path)

if __name__ == '__main__':
	main()
