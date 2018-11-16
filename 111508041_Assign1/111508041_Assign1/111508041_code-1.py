# -*- coding: utf-8 -*-

import sys
import re
import datetime
import time
import os

def find_all(a_str, sub):
    start = 0
    while True:
        start = a_str.find(sub, start)
        if start == -1: return
        yield start
        start += len(sub)

def validate_date_format(date_text, date_format):
    try:
        datetime.datetime.strptime(date_text, date_format)
        return True
    except ValueError:
        return False

def validate_time_format(time_text, time_format):
    try:
        datetime.datetime.strptime(time_text, time_format)
        return True
    except ValueError:
        return False

def time_in_24hrs(hour, am_or_pm):
    if not am_or_pm:
        return 12 if int(hour) == 12 else int(hour) + 12
    elif am_or_pm.lower() == 'am':
        return 0 if int(hour) == 12 else int(hour)
    elif am_or_pm.lower() == 'pm':
        return 12 if int(hour) == 12 else int(hour) + 12

def check_if_string_without_symbols(word):
    c = 0
    for char in word:
        if char.isalpha() or char.isdigit():
            c += 1
    if c == len(word):
        return True
    else:
        return False

def resolve_symbols(word, list_of_split_words, counter, list_of_split_words_on_spaces):
    for punctuation_mark in list_of_punctuation_marks:
        if punctuation_mark in word:
            flag = 1
            splits = word.split(punctuation_mark)
            if len(splits) == 2:
                if splits[0] != "" and splits[0] != " ":
                    tokenize(list_of_split_words, splits[0], counter, list_of_split_words_on_spaces, flag_for_single_quote)
                list_of_split_words.append(punctuation_mark)
                if splits[1] != "" and splits[1] != " ":
                    tokenize(list_of_split_words, splits[1], counter, list_of_split_words_on_spaces, flag_for_single_quote)
            else:
                if word[0] == punctuation_mark:
                    list_of_split_words.append(punctuation_mark)
                    if word.split(punctuation_mark)[0] != "" and word.split(punctuation_mark)[0] != " ":
                        tokenize(list_of_split_words, word.split(punctuation_mark)[0], counter, list_of_split_words_on_spaces, flag_for_single_quote)
                else:
                    if word.split(punctuation_mark)[0] != "" and word.split(punctuation_mark)[0] != " ":
                        tokenize(list_of_split_words, word.split(punctuation_mark)[0], counter, list_of_split_words_on_spaces, flag_for_single_quote)
                    list_of_split_words.append(punctuation_mark)

def tokenize(list_of_split_words, word, index_of_word, list_of_split_words_on_spaces, flag_for_single_quote):
    if word == '':
        return True
    if word == ' ':
        return True
    if word.startswith("CF:D:"):
        list_of_split_words.append(word)
        return True
    if word.startswith("CF:T:"):
        list_of_split_words.append(word)
        return True

    if len(word) == 1 and word[0] in list_of_punctuation_marks:
        list_of_split_words.append(word)
        return True

    match_for_url = re.findall(regex_for_url, word)
    if match_for_url:
        list_of_split_words.append(match_for_url[0])
        return True

    match_for_username = re.findall(regex_for_username, word)
    if match_for_username:
        list_of_split_words.append(word.strip())
        return True

    match_for_email = re.findall(regex_for_email, word)
    if match_for_email:
        list_of_split_words.append(word)
        return True

    flag = 0
    for emoticon in list_of_emoticons:
        if emoticon in word:
            flag = 1
            for index in list(find_all(word, emoticon)):
                occurence_dict[index] =  emoticon
    last_index = -1
    for index in sorted(occurence_dict.iterkeys()):
        if last_index == -1 and index != 0:
            list_of_split_words.append(word[0:index])
            list_of_split_words.append(occurence_dict[index])
            last_index = index + len(occurence_dict[index])
        elif last_index == -1 and index == 0:
            list_of_split_words.append(occurence_dict[index])
            last_index = index + len(occurence_dict[index])
        elif last_index != -1 and last_index != index:
            list_of_split_words.append(word[last_index:index])
            list_of_split_words.append(occurence_dict[index])
            last_index = index + len(occurence_dict[index])
        elif last_index != -1 and last_index == index:
            list_of_split_words.append(occurence_dict[index])
            last_index = index + len(occurence_dict[index])
        if index == max(occurence_dict.keys()) and last_index != len(word):
            list_of_split_words.append(word[last_index:])
    occurence_dict.clear()
    if flag == 1:
        return True

    if word.startswith("(") and word.endswith(")"):
        list_of_split_words.append("(")
        tokenize(list_of_split_words, word[1:len(word)-1].strip(), index_of_word, list_of_split_words_on_spaces, flag_for_single_quote)
        list_of_split_words.append(")")
        return True

    if word.startswith("("):
        list_of_split_words.append("(")
        tokenize(list_of_split_words, word[1:len(word)].strip(), index_of_word, list_of_split_words_on_spaces, flag_for_single_quote)
        return True

    if word.endswith(")"):
        tokenize(list_of_split_words, word[0:len(word)-1].strip(), index_of_word, list_of_split_words_on_spaces, flag_for_single_quote)
        list_of_split_words.append(")")
        return True

    if ellipsis in word:
        if word[0:word.index(ellipsis)] != "" or word[0:word.index(ellipsis)] != " ":
            tokenize(list_of_split_words, word[0:word.index(ellipsis)], index_of_word, list_of_split_words_on_spaces, flag_for_single_quote)
        list_of_split_words.append(ellipsis)

        if word[word.index(ellipsis)+len(ellipsis):] != '' or word[word.index(ellipsis)+len(ellipsis):] != " ":
            tokenize(list_of_split_words, word[word.index(ellipsis)+len(ellipsis):], index_of_word, list_of_split_words_on_spaces, flag_for_single_quote)
        return True

    if word.startswith("'"):
        flag_for_single_quote[0] = 1
        list_of_split_words.append("'")
        tokenize(list_of_split_words, word[1:], index_of_word, list_of_split_words_on_spaces, flag_for_single_quote)
        return True

    if word.endswith(".") or word.endswith(","):
        tokenize(list_of_split_words, word[0:len(word)-1], index_of_word, list_of_split_words_on_spaces, flag_for_single_quote)
        list_of_split_words.append(word[len(word)-1])
        return True

    if "-" in word:
        if word.startswith("-"):
            return False
        split_hyphenated = word.split('-')
        res = split_hyphenated[0]
        for split in split_hyphenated[1:]:
            if split:
                if not split[0].isupper():
                    res += "-" + split
                else:
                    break
            else:
                break
        if res == split_hyphenated[0]:
            for split in split_hyphenated:
                if check_if_string_without_symbols(split) == True:
                    list_of_split_words.append(split)
                else:
                    resolve_symbols(split, list_of_split_words, index_of_word, list_of_split_words_on_spaces)
                list_of_split_words.append("-")
            list_of_split_words.pop()
        else:
            list_of_split_words.append(res)

        return True

    if word.endswith("'d"):
        flag_for_d = 0
        for word_ahead in list_of_split_words_on_spaces[index_of_word+1:index_of_word+3]:
            if len(re.findall(r"""[a-zA-Z]+ed([^a-zA-Z]|$)""", word_ahead)) > 0 or word_ahead in list_of_irregular_verb_participles:
                list_of_split_words.append(word.split("'d")[0])
                list_of_split_words.append("had")
                flag_for_d = 1
                break
        if flag_for_d == 0:
            if word.split("'d")[0] == "I" or word.split("'d")[0] == "i" or word.split("'d")[0] == "We" or word.split("'d")[0] == "we":
                list_of_split_words.append(word.split("'d")[0])
                list_of_split_words.append("should")
            else:
                list_of_split_words.append(word.split("'d")[0])
                list_of_split_words.append("would")
        return True

    if word.endswith("n't"):
        flag_for_nt = 0
        for option in list_of_nt:
            if option == word:
                list_of_split_words.append(list_of_nt[option])
                list_of_split_words.append('not')
                flag_for_nt = 1
                break
        if flag_for_nt == 0:
            list_of_split_words.append(word.split("n'")[0])
            list_of_split_words.append('not')
        return True
    if word.endswith("'ve"):
        list_of_split_words.append(word.split("'ve")[0])
        list_of_split_words.append('have')
        return True
    if word.endswith("'re"):
        list_of_split_words.append(word.split("'re")[0])
        list_of_split_words.append('are')
        return True
    if word.endswith("'m"):
        list_of_split_words.append(word.split("'m")[0])
        list_of_split_words.append('am')
        return True
    if "'n" in word:
        splitted_words = word.split("'n")
        if len(splitted_words) >= 1 and (splitted_words[0] != '' and splitted_words[0] != ' '):
            list_of_split_words.append(splitted_words[0])
        list_of_split_words.append('and')
        if len(splitted_words) == 2 and (splitted_words[1] != '' and splitted_words[1] != ' '):
            list_of_split_words.append(splitted_words[1])
        return True

    if word.startswith("y'"):
        list_of_split_words.append('you')
        splitted_words = word.split("y'")
        if splitted_words[1] != '' and splitted_words[1] != ' ':
            list_of_split_words.append(splitted_words[1])
        return True
    if word.startswith("Y'"):
        list_of_split_words.append('You')
        splitted_words = word.split("Y'")
        if splitted_words[1] != '' and splitted_words[1] != ' ':
            list_of_split_words.append(splitted_words[1])
        return True

    if word.endswith("'s"):
        if word == "Let's":
            list_of_split_words.append("Let")
            list_of_split_words.append("us")
        else:
            flag_for_s = 0
            for word_ahead in list_of_split_words_on_spaces[index_of_word+1:index_of_word+3]:
                if "ing" in word_ahead:
                    list_of_split_words.append(word.split("'s")[0])
                    list_of_split_words.append("is")
                    flag_for_s = 1
                    break
            if flag_for_s == 0:
                for word_ahead in list_of_split_words_on_spaces[index_of_word+1:index_of_word+3]:
                    if word_ahead.endswith("ed") or word_ahead in list_of_irregular_verb_participles:
                        list_of_split_words.append(word.split("'s")[0])
                        list_of_split_words.append("has")
                        flag_for_s = 2
                        break
            if flag_for_s == 0:
                list_of_split_words.append(word.split("'s")[0])
                if word.split("'s")[0] in list_of_pronouns or not word.split("'s'")[0].istitle():
                    list_of_split_words.append("is")
                else:
                    list_of_split_words.append("'s")
        return True

    if word.endswith("'"):
        if flag_for_single_quote[0] == 1 or not flag_for_single_quote:
            flag_for_single_quote[0] = 0
            list_of_split_words.append(word.split("'")[0])
            list_of_split_words.append("'")
        else:
            list_of_split_words.append(word.split("'")[0])
            list_of_split_words.append("'s")
        return True

    if word.endswith("'ll"):
        list_of_split_words.append(word.split("'")[0])
        if word.split("'")[0] == "I" or word.split("'")[0] == "i" or word.split("'")[0] == "We" or word.split("'")[0] == "we":
            list_of_split_words.append("shall")
        else:
            list_of_split_words.append("will")
        return True

    c = 0
    for char in word:
        if char.isalpha() or char.isdigit():
            c += 1
    if c == len(word):
        if word.isupper():
            list_of_split_words.append(word)
            return True
        subwords = re.findall('[A-Z][^A-Z]*', word)
        if not subwords:
            list_of_split_words.append(word)
        else:
            if not word.startswith(subwords[0]):
                list_of_split_words.append(word[0:word.find(subwords[0])])
            for subword in subwords:
                list_of_split_words.append(subword)
        return True
    return False

#list of punctuation marks and some commonly used emoticons
list_of_punctuation_marks = ['.',',', '?', '!', '"', ':', ';', '$', '%', '&', '*', '{', '}', '!', '-']
list_of_emoticons = [":)", ":-)", ":D", ":-D", ":]", ":-]", ":-))", ":(", ":-(", ":'-(", ":'(", ":'-)", ":')", ";)", ";-)", ":-/", ":/", ":-P", ":P", "XD", "X-D", "XP", "X-P"]
ellipsis = "..."

#list of n't suffixed exceptional splitted_words
list_of_nt = {"ain't" : "are", "won't" : "will", "can't" : "can", "shan't" : "shall"}

#list of past participles of irregular verbs
list_of_irregular_verb_participles = ['gone', 'been', 'beaten', 'become', 'begun', 'brought', 'built', 'bet', 'blown', 'broken', 'burst', 'bought', 'caught', 'chosen', 'come', 'come', 'cost', 'cut', 'dealt', 'done', 'drawn', 'drunk', 'driven', 'eaten', 'fallen', 'fed', 'felt', 'fought', 'found', 'flown', 'forgotten', 'got', 'gotten', 'given', 'gone', 'grown', 'hung', 'had', 'heard', 'hidden', 'hit', 'held', 'hurt', 'kept', 'known', 'laid', 'led', 'left', 'lent', 'let', 'lain', 'lit', 'lost', 'made', 'meant', 'met', 'paid', 'put', 'read', 'ridden', 'rung', 'risen', 'run', 'said', 'seen', 'sold', 'sent', 'set', 'shaken', 'stolen', 'shone', 'shot', 'shown', 'shut', 'sung', 'sunk', 'sat', 'slept', 'slid', 'spoken', 'spent', 'sprung', 'stood', 'stuck', 'sworn', 'swept', 'swum', 'swung', 'taken', 'taught', 'torn', 'told', 'thought', 'thrown', 'understood', 'woken', 'worn', 'woven', 'won', 'written', 'burnt', 'dreamt', 'learnt', 'smelt', 'spelt']

list_of_pronouns = ['He', 'She', 'It', 'Who', 'Where', 'What', 'Which', 'This', 'That', 'Whatever', 'Whoever', 'Whomever', 'Whichever', 'Anything', 'Everybody', 'Anybody', 'Anyone', 'Everyone', 'Everything', 'Nobody', 'Nothing', 'Somebody', 'Someone', 'Something', 'There', 'there', 'here', 'Here', 'he', 'she', 'it', 'who', 'where', 'what', 'which', 'whis', 'what', 'whatever', 'whoever', 'whomever', 'whichever', 'anything', 'everybody', 'anybody', 'anyone', 'everyone', 'everything', 'nobody', 'nothing', 'somebody', 'someone', 'something']

list_of_timezones_abbreviation = ['ACDT','ACST','ACT','ACT','ACWST','ADT','AEDT','AEST','AFT','AKDT','AKST','AMST','AMT','AMT','ART','AST','AST','AWST','AZOST','AZOT','AZT','BDT','BIOT','BIT','BOT','BRST','BRT','BST','BST','BST','BTT','CAT','CCT','CDT','CDT','CEST','CET','CHADT','CHAST','CHOST','CHOT','CHST','CHUT','CIST','CIT','CKT','CLST','CLT','COST','COT','CST','CST','CST','CT','CVT','CWST','CXT','DAVT','DDUT','DFT','EASST','EAST','EAT','ECT','ECT','EDT','EEST','EET','EGST','EGT','EIT','EST','FET','FJT','FKST','FKT','FNT','GALT','GAMT','GET','GFT','GILT','GIT','GMT','GST','GST','GYT','HAEC','HDT','HKT','HMT','HOVST','HOVT','HST','ICT','IDLW','IDT','IOT','IRDT','IRKT','IRST','IST','IST','IST','JST','KALT','KGT','KOST','KRAT','KST','LHST','LHST','LINT','MAGT','MART','MAWT','MDT','MEST','MET','MHT','MIST','MIT','MMT','MSK','MST','MST','MUT','MVT','MYT','NCT','NDT','NFT','NPT','NST','NT','NUT','NZDT','NZST','OMST','ORAT','PDT','PET','PETT','PGT','PHOT','PHT','PKT','PMDT','PMST','PONT','PST','PST','PYST','PYT','RET','ROTT','SAKT','SAMT','SAST','SBT','SCT','SDT','SGT','SLST','SRET','SRT','SST','SST','SYOT','TAHT','TFT','THA','TJT','TKT','TLT','TMT','TOT','TRT','TVT','ULAST','ULAT','UTC','UYST','UYT','UZT','VET','VLAT','VOLT','VOST','VUT','WAKT','WAST','WAT','WEST','WET','WIT','WST','YAKT','YEKT']


#declaration of variables

match_for_date = []
list_of_split_words = []
occurence_dict ={}
flag_for_single_quote = []


#regex for username
regex_for_username = r"@[a-zA-Z0-9-_']+[\.]{0,1}[a-zA-Z0-9_-]+"
regex_for_email = r"[^@\s]+@[^@\s]+\.[^@\s]+"

#regex for URL

regex_for_url = r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"""

#regex for dates
regex_for_yymmdd = r'\d\d\d\d[-/]\d?\d[-/]\d?\d'
regex_for_ddmmyy = r'[^\d]\d?\d[-/]\d?\d[-/]\d\d\d?\d?'
regex_for_ddmonthyear = r'([^\d](([0-9])|(([0-2][0-9])|([3][01])))([\s]*(st|nd|rd|th))?)?[\s]*([Jj]anurary|[Ff]ebruary|[Mm]arch|[Aa]pril|[Ma]ay|[Jj]une|[Jj]uly|[Aa]ugust|[Ss]eptember|[Oo]ctober|[Nn]ovember|[Dd]ecember)[\s]*((\d\d\d?\d?)|(\'\d\d))?'
regex_for_year1 = r'(in|from)[\s]+(the[\s]+)?\d\d\d\d'
regex_for_year2 = r"(in|from)[\s]+(the[\s]+)?'\d\d(\d\d)?s?"

#regex for time
time_abbreviations = r'(ACDT|ACST|ACT|ACT|ACWST|ADT|AEDT|AEST|AFT|AKDT|AKST|AMST|AMT|AMT|ART|AST|AST|AWST|AZOST|AZOT|AZT|BDT|BIOT|BIT|BOT|BRST|BRT|BST|BST|BST|BTT|CAT|CCT|CDT|CDT|CEST|CET|CHADT|CHAST|CHOST|CHOT|CHST|CHUT|CIST|CIT|CKT|CLST|CLT|COST|COT|CST|CST|CST|CT|CVT|CWST|CXT|DAVT|DDUT|DFT|EASST|EAST|EAT|ECT|ECT|EDT|EEST|EET|EGST|EGT|EIT|EST|FET|FJT|FKST|FKT|FNT|GALT|GAMT|GET|GFT|GILT|GIT|GMT|GST|GST|GYT|HAEC|HDT|HKT|HMT|HOVST|HOVT|HST|ICT|IDLW|IDT|IOT|IRDT|IRKT|IRST|IST|IST|IST|JST|KALT|KGT|KOST|KRAT|KST|LHST|LHST|LINT|MAGT|MART|MAWT|MDT|MEST|MET|MHT|MIST|MIT|MMT|MSK|MST|MST|MUT|MVT|MYT|NCT|NDT|NFT|NPT|NST|NT|NUT|NZDT|NZST|OMST|ORAT|PDT|PET|PETT|PGT|PHOT|PHT|PKT|PMDT|PMST|PONT|PST|PST|PYST|PYT|RET|ROTT|SAKT|SAMT|SAST|SBT|SCT|SDT|SGT|SLST|SRET|SRT|SST|SST|SYOT|TAHT|TFT|THA|TJT|TKT|TLT|TMT|TOT|TRT|TVT|ULAST|ULAT|UTC|UYST|UYT|UZT|VET|VLAT|VOLT|VOST|VUT|WAKT|WAST|WAT|WEST|WET|WIT|WST|YAKT|YEKT)'
regex_for_oclock =  time_abbreviations+r"?[\s]*" + r"""[^\d](([0]?[0-9])|([1][0-2]))[\s]*o'clock""" + r"[\s]*" +time_abbreviations+r"?"
regex_for_ampm = time_abbreviations+r"?"+ r'[\s]*(([0]?[0-9])|([1][0-2]))(:[0-5]?[0-9])?(:[0-5]?[0-9])?[\s]*(am|pm|AM|PM)[\s]*' + time_abbreviations+"?"

def main():
    fw = open('output.txt', 'w')
    f = open(sys.argv[1], 'r')

    #tokenizing dates
    for line in f:
        line = line.strip()

        fw.write(line + "\n")
        fw.flush()


        flag_for_single_quote.append(0)

        line = line.replace(",", " , ")
        line = line.replace("$", " $ ")
        line = line.replace("%", " % ")
        line = line.replace("*", " * ")
        line = line.replace("!", " ! ")
        line = line.replace("{", " { ")
        line = line.replace("}", " } ")
        line = line.replace("=", " = ")
        line = line.replace("<", " < ")
        line = line.replace(">", " > ")
        line = line.replace("&", " & ")
        line = line.replace("\"", " \" ")
        line = re.sub(' +', ' ', line)
        line = line.strip()



        results = re.finditer(regex_for_oclock, line)
        match_for_time = [match.group().strip() for match in results]
        print match_for_time
        for match in match_for_time:
            match.replace(" o'clock", "o'clock")
            if validate_time_format(match, "%Io'clock"):
                line = line.replace(match, " CF:T:" + datetime.datetime.strptime(match, "%Io'clock").strftime('%H') + "00|" + str(time_in_24hrs(datetime.datetime.strptime(match, "%Io'clock").strftime('%I'), '')) + "00" + " ")
            elif validate_time_format(match, "%Io'clock %Z"):
                line = line.replace(match, " CF:T:" + datetime.datetime.strptime(match, "%Io'clock %Z").strftime('%H') + "00|" + str(time_in_24hrs(datetime.datetime.strptime(match, "%Io'clock %Z").strftime('%I'), '')) + "00" + ":" + match.split(' ')[len(match.split(' ')) - 1] + " ")
            elif validate_time_format(match, "%Z %Io'clock"):
                line = line.replace(match, " CF:T:" + datetime.datetime.strptime(match, "%Z %Io'clock").strftime('%H') + "00|" + str(time_in_24hrs(datetime.datetime.strptime(match, "%Z %Io'clock").strftime('%I'), '')) + "00" + ":" + match.split(' ')[0] + " ")
        line = re.sub(' +', ' ', line)
        results = re.finditer(regex_for_ampm, line)
        match_for_time = [match.group().strip() for match in results]
        print match_for_time
        for match in match_for_time:
            if validate_time_format(match, '%H %p'):
                line = line.replace(match, " CF:T:" + datetime.datetime.strptime(match, "%I %p").strftime('%H%M') + " ")
            elif validate_time_format(match, '%H %p %Z'):
                line = line.replace(match, " CF:T:" + datetime.datetime.strptime(match, "%I %p %Z").strftime('%H%M:') + match.split(" ")[len(match.split(" ")) - 1].strip() + " ")
            elif validate_time_format(match, '%I:%M %p'):
                line = line.replace(match, " CF:T:" + datetime.datetime.strptime(match, "%I:%M %p").strftime('%H%M') + " ")
            elif validate_time_format(match, '%I:%M %p %Z'):
                line = line.replace(match, " CF:T:" + datetime.datetime.strptime(match, "%I:%M %p %Z").strftime('%H%M:') + match.split(" ")[len(match.split(" ")) - 1].strip() + " ")
            elif validate_time_format(match, '%I %p %Z'):
                line = line.replace(match, " CF:T:" + datetime.datetime.strptime(match, "%I %p %Z").strftime('%H00:') + match.split(" ")[len(match.split(" ")) - 1].strip() + " ")
            elif validate_time_format(match, '%I:%M:%S %p'):
                line = line.replace(match, " CF:T:" + datetime.datetime.strptime(match, "%I:%M:%S %p").strftime('%H%M') + " ")
            elif validate_time_format(match, '%I:%M:%S %p %Z'):
                line = line.replace(match, " CF:T:" + datetime.datetime.strptime(match, "%I:%M:%S %p %Z").strftime('%H%M:') + match.split(" ")[len(match.split(" ")) - 1].strip() + " ")
            elif validate_time_format(match, '%I %Z'):
                line = line.replace(match, " CF:T:" + datetime.datetime.strptime(match, "%I %Z").strftime('%H%M:') + match.split(" ")[len(match.split(" ")) - 1].strip() + " ")
            elif validate_time_format(match, '%I:%M'):
                line = line.replace(match, " CF:T:" + datetime.datetime.strptime(match, "%I:%M").strftime('%H%M')+ " ")
            elif validate_time_format(match, '%I:%M %Z'):
                line = line.replace(match, " CF:T:" + datetime.datetime.strptime(match, "%I:%M %Z").strftime('%H%M:') + match.split(" ")[len(match.split(" ")) - 1].strip() + " ")
            elif validate_time_format(match, '%I:%M:%S %Z'):
                line = line.replace(match, " CF:T:" + datetime.datetime.strptime(match, "%I:%M:%S %Z").strftime('%H%M:') + match.split(" ")[len(match.split(" ")) - 1].strip() + " ")
            elif validate_time_format(match, '%Z %H %p'):
                line = line.replace(match, " CF:T:" + datetime.datetime.strptime(match, '%Z %H %p').strftime('%H%M:') + match.split(" ")[0].strip() + " ")
            elif validate_time_format(match, '%Z %I:%M %p'):
                line = line.replace(match, " CF:T:" + datetime.datetime.strptime(match, '%Z %I:%M %p').strftime('%H%M:') + match.split(" ")[0].strip() + " ")
            elif validate_time_format(match, '%Z %I %p'):
                line = line.replace(match, " CF:T:" + datetime.datetime.strptime(match, '%Z %I %p').strftime('%H00:') + match.split(" ")[0].strip() + " ")
            elif validate_time_format(match, '%Z %I:%M:%S %p'):
                line = line.replace(match, " CF:T:" + datetime.datetime.strptime(match, '%Z %I:%M:%S %p').strftime('%H%M:') + match.split(" ")[0].strip() + " ")
            elif validate_time_format(match, '%Z %I'):
                line = line.replace(match, " CF:T:" + datetime.datetime.strptime(match, '%Z %I').strftime('%H%M:') + match.split(" ")[0].strip() + " ")
            elif validate_time_format(match, '%Z %I:%M'):
                line = line.replace(match, " CF:T:" + datetime.datetime.strptime(match, '%Z %I:%M').strftime('%H%M:') + match.split(" ")[0].strip() + " ")
            elif validate_time_format(match, '%Z %I:%M:%S'):
                line = line.replace(match, " CF:T:" + datetime.datetime.strptime(match, '%Z %I:%M:%S').strftime('%H%M:') + match.split(" ")[0].strip() + " ")
        line = re.sub(' +', ' ', line)

        # match_for_year = re.findall(regex_for_year1, line.strip())
        # for match in match_for_year:
        #     if "in" in match and "the" in match:
        #         line = line.replace(match, "in the CF:D:" + datetime.datetime.strptime(match, "in the '%ys").strftime('%Y')+ ":??:??" + " " )
        #     elif "from" in match and "the" in match:
        #         line = line.replace(match, "from the CF:D:" + datetime.datetime.strptime(match, "from the '%ys").strftime('%Y')+ ":??:??" + " " )
        #     elif "in" in match:
        #         line = line.replace(match, "from the CF:D:" + datetime.datetime.strptime(match, "in '%ys").strftime('%Y')+ ":??:??" + " " )
        #     elif "from" in match:
        #         line = line.replace(match, "from the CF:D:" + datetime.datetime.strptime(match, "from '%ys").strftime('%Y')+ ":??:??" + " " )
        # line = re.sub(' +', ' ', line)

        results = re.finditer(regex_for_year1, line)
        match_for_year = [match.group().strip() for match in results]
        for match in match_for_year:
            if "in" in match and "the" in match:
                line = line.replace(match, "in the CF:D:" + datetime.datetime.strptime(match, 'in the %Y').strftime('%Y')+ ":??:??" + " " )
            elif "from" in match and "the" in match:
                line = line.replace(match, "from the CF:D:" + datetime.datetime.strptime(match, 'from the %Y').strftime('%Y')+ ":??:??" + " " )
            elif "in" in match:
                line = line.replace(match, "in CF:D:" + datetime.datetime.strptime(match, 'in %Y').strftime('%Y')+ ":??:??" + " ")
            elif "from" in match:
                line = line.replace(match, "from CF:D:" + datetime.datetime.strptime(match, 'from %Y').strftime('%Y')+ ":??:??" + " " )
        line = re.sub(' +', ' ', line)

        match_for_date = re.findall(regex_for_yymmdd, line.strip())
        for match in match_for_date:
            if validate_date_format(match, '%Y-%m-%d'):
                line = line.replace(match, " CF:D:" + datetime.datetime.strptime(match, '%Y-%m-%d').strftime('%Y-%m-%d')+ " ")
            else:
                line = line.replace(match, " CF:D:" + datetime.datetime.strptime(match, '%Y/%m/%d').strftime('%Y-%m-%d')+ " ")
        line = re.sub(' +', ' ', line)
        results = re.finditer(regex_for_ddmmyy, line)
        match_for_date = [match.group().strip() for match in results]
        for match in match_for_date:
            if validate_date_format(match, '%d-%m-%Y'):
                line = line.replace(match, " CF:D:" + datetime.datetime.strptime(match, '%d-%m-%Y').strftime('%Y-%m-%d')+ " ")
            elif validate_date_format(match, '%d-%m-%y'):
                line = line.replace(match, " CF:D:" + datetime.datetime.strptime(match, '%d-%m-%y').strftime('%Y-%m-%d')+ " ")
            elif validate_date_format(match, '%d/%m/%Y'):
                line = line.replace(match, " CF:D:" + datetime.datetime.strptime(match, '%d/%m/%Y').strftime('%Y-%m-%d')+ " ")
            else:
                line = line.replace(match, " CF:D:" + datetime.datetime.strptime(match, '%d/%m/%y').strftime('%Y-%m-%d')+ " ")
        line = re.sub(' +',' ',line)
        results = re.finditer(regex_for_ddmonthyear, line)
        match_for_date = [match.group().strip() for match in results]
        for match in match_for_date:
            if validate_date_format(match, '%d %B %y'):
                line = line.replace(match, " CF:D:" + datetime.datetime.strptime(match, '%d %B %y').strftime('%Y-%m-%d')+ " ")
            elif validate_date_format(match, '%d %B %Y'):
                line = line.replace(match, " CF:D:" + datetime.datetime.strptime(match, '%d %B %Y').strftime('%Y-%m-%d')+ " ")
            elif validate_date_format(match, '%dth %B %Y'):
                line = line.replace(match, " CF:D:" + datetime.datetime.strptime(match, '%dth %B %Y').strftime('%Y-%m-%d')+ " ")
            elif validate_date_format(match, '%dth %B %y'):
                line = line.replace(match, " CF:D:" + datetime.datetime.strptime(match, '%dth %B %y').strftime('%Y-%m-%d')+ " ")
            elif validate_date_format(match, '%d %B'):
                line = line.replace(match, " CF:D:" + datetime.datetime.strptime(match, '%d %B').strftime('%Y-%m-%d')+ " ")
            elif validate_date_format(match, '%B %y'):
                line = line.replace(match, " CF:D:" + datetime.datetime.strptime(match, '%d %B').strftime('%Y-%m-%??')+ " ")
            elif validate_date_format(match, '%B %Y'):
                line = line.replace(match, " CF:D:" + datetime.datetime.strptime(match, '%B %Y').strftime('%Y-%m-??')+ " ")
            elif validate_date_format(match, '%B\'%y'):
                line = line.replace(match, " CF:D:" + datetime.datetime.strptime(match, '%B\'%y').strftime('%Y-%m-??')+ " ")
            elif validate_date_format(match, '%B\'%Y'):
                line = line.replace(match, " CF:D:" + datetime.datetime.strptime(match, '%B\'%Y').strftime('%Y-%m-??')+ " ")
            elif validate_date_format(match, '%d %B\'%Y'):
                line = line.replace(match, " CF:D:" + datetime.datetime.strptime(match, '%d %B\'%Y').strftime('%Y-%m-%d')+ " ")
            elif validate_date_format(match, '%d %B\'%y'):
                line = line.replace(match, " CF:D:" + datetime.datetime.strptime(match, '%d %B\'%y').strftime('%Y-%m-%d')+ " ")
            elif validate_date_format(match, '%d %B\'%Y'):
                line = line.replace(match, " CF:D:" + datetime.datetime.strptime(match, '%d %B\'%Y').strftime('%Y-%m-%d')+ " ")
            elif validate_date_format(match, '%B'):
                line = line.replace(match, " CF:D:" + datetime.datetime.strptime(match, '%B').strftime('????-%m-??')+ " ")
        line = re.sub(' +',' ',line)

        match_for_email = re.findall(regex_for_email, line)
        for match in match_for_email:
            print match
            line = line.replace(match, " "+match+" ")

        line = re.sub(' +',' ',line)

        match_for_username = re.findall(regex_for_username, line)
        for match in match_for_username:
            line = line.replace(match, " "+match+" ")

        line = re.sub(' +',' ',line)

        indices = find_all(line, "-")
        for index in indices:
            if index != 0 and index != len(line)-1:
                if not line[index - 1].isalpha() or not line[index+1].isalpha():
                    line = line[0:index] + line[index:index+1].replace("-", " - ") + line[index+1:]
            if index == 0:
                line = line[0:index] + line[index:index+1].replace("-", " - ") + line[index+1:]
            if index == len(line)-1:
                line = line[0:index] + line[index:index+1].replace("-", " - ") + line[index+1:]

        list_of_split_words_on_spaces = line.replace('\n', '').split(' ')
        counter = 0

        for word in list_of_split_words_on_spaces:
            counter += 1

            value = tokenize(list_of_split_words, word, counter-1, list_of_split_words_on_spaces, flag_for_single_quote)
            if value == False:
                flag = 0
                for punctuation_mark in list_of_punctuation_marks:
                    if punctuation_mark in word:
                        flag = 1
                        splits = word.split(punctuation_mark)
                        if len(splits) == 2:
                            if splits[0] != "" and splits[0] != " ":
                                tokenize(list_of_split_words, splits[0], counter - 1, list_of_split_words_on_spaces, flag_for_single_quote)
                            list_of_split_words.append(punctuation_mark)
                            if splits[1] != "" and splits[1] != " ":
                                tokenize(list_of_split_words, splits[1], counter - 1, list_of_split_words_on_spaces, flag_for_single_quote)
                        else:
                            if word[0] == punctuation_mark:
                                list_of_split_words.append(punctuation_mark)
                                if word.split(punctuation_mark)[0] != "" and word.split(punctuation_mark)[0] != " ":
                                    tokenize(list_of_split_words, word.split(punctuation_mark)[0], counter - 1, list_of_split_words_on_spaces, flag_for_single_quote)
                            else:
                                if word.split(punctuation_mark)[0] != "" and word.split(punctuation_mark)[0] != " ":
                                    tokenize(list_of_split_words, word.split(punctuation_mark)[0], counter - 1, list_of_split_words_on_spaces, flag_for_single_quote)
                                list_of_split_words.append(punctuation_mark)
                if flag == 0:
                    list_of_split_words.append(word)
        print list_of_split_words
        for token in list_of_split_words:
            fw.write(token + "\n")
            fw.flush()
        list_of_split_words[:] = []
    fw.close()

if __name__ == '__main__':
    main()
