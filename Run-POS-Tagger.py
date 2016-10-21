import os
import math
import sys
import datetime

tagset=['<s>', 'PRP$', 'VBG', 'FW', 'VBN', 'POS', "''", 'VBP', 'WDT', 'JJ', 'WP',
            'VBZ', 'DT', '#', 'RP', '$', 'NN', 'VBD', ',', '.', 'TO', 'PRP', 'RB',
            '-LRB-', ':', 'NNS', 'NNP', '``', 'WRB', 'CC', 'LS', 'PDT', 'RBS', 'RBR',
            'CD', 'EX', 'IN', 'WP$', 'MD', 'NNPS', '-RRB-', 'JJS', 'JJR', 'SYM', 'VB', 'UH', '</s>']

tag_counts={}
tag_seen_type_counts={}
tag_unseen_type_counts={}
transition_counts = [[0 for x in range(46)] for y in range(46)] #np.zeros( (46,46) )
transition_probs=[[0.0 for x in range(46)] for y in range(46)] #np.zeros( (46,46) )
emission_probs={}
word_tag_pair_smoothed_counts={}
vocab={}
log0=-1000.0
suffix_tag_probs={}
no_suffix_prob=-100.0
suffix_set=['s','ed', 'en', 'ing','ion','al','ive', 'able', 'ize','ful']
capital_tag_probs={}
no_capital_prob=-100.0

# following method returns p(word |tag)
def get_emission_prob(word):
    emit_vec = [None] * 45
    for t in range(1, 46):
        tag=tagset[t]
        word_tag = word + " " + tag
        if (emission_probs.has_key(word_tag)):
            emit_vec[t - 1] = emission_probs[word_tag]
        elif not (vocab.has_key(word)):
            suffix_prob=no_suffix_prob
            for suffix in suffix_set:
                if word.endswith(suffix) and suffix_tag_probs.has_key(suffix+" "+tag):
                    suffix_prob=suffix_tag_probs[suffix+" "+tag]
                    break;
            capital_prob=no_capital_prob
            if(word[0] >='A' and word[0]<='Z' and capital_tag_probs.has_key(tag)):
                capital_prob=capital_tag_probs[tag]
            word_tag = "<unk>" + " " + tag
            if (emission_probs.has_key(word_tag)):
                emit_vec[t - 1] = emission_probs[word_tag] + suffix_prob + capital_prob
            else:
                emit_vec[t - 1] = log0
        else:
            emit_vec[t - 1] = log0
    return  emit_vec
def remove_blanks(parts):
    modified_parts=[]
    for part in parts:
        if len(part) > 0:
            modified_parts.append(part)
    return modified_parts

def get_tag_sequence(words):
    N = 45
    sent_len = len(words)
    tagset_len = len(tagset)
    viterbi = [[0.0 for x in range(sent_len)] for y in range(N + 2)]
    backpointer = [[0 for x in range(sent_len)] for y in range(N + 2)]
    emit_vec=get_emission_prob(words[0])
    for t in range(1, tagset_len - 1):
        viterbi[t][0] = transition_probs[0][t-1] + emit_vec[t-1]
        backpointer[t][0] = 0

    for w in range(1, sent_len):
        word = words[w]
        emit_vec = get_emission_prob(word)
        for t in range(1, tagset_len - 1):
            max_viterbi_val=viterbi[1][w - 1] + transition_probs[1][t-1]
            max_viterbi_arg = 1
            for t_prev in range(2, tagset_len - 1):
                cur_viterbi = viterbi[t_prev][w - 1] + transition_probs[t_prev][t-1]
                if cur_viterbi > max_viterbi_val:
                    max_viterbi_val = cur_viterbi
                    max_viterbi_arg = t_prev
            viterbi[t][w] = max_viterbi_val + emit_vec[t-1]
            backpointer[t][w] = max_viterbi_arg

    max_viterbi_val=viterbi[1][sent_len - 1] + transition_probs[1][45]
    max_viterbi_arg = 1
    for t_prev in range(2, tagset_len - 1):
        cur_viterbi = viterbi[t_prev][sent_len - 1] + transition_probs[t_prev][45]

        if cur_viterbi > max_viterbi_val:
            max_viterbi_val = cur_viterbi
            max_viterbi_arg = t_prev
    backpointerFinal = max_viterbi_arg

    tags = []
    tag_index = backpointerFinal
    for t in range(sent_len - 1, -1, -1):
        tags.append(tagset[tag_index])
        tag_index = backpointer[tag_index][t]

    tags.reverse()
    return tags

if __name__ == "__main__":

    # python run_tagger.py sents.test model_file sents.out

    test_file = sys.argv[1]
    model_file=sys.argv[2]
    out_file=sys.argv[3]
    print "reading model statistics......"
    file_reader=open(model_file)
    line=file_reader.readline()
    line=line.replace('\n','')
    parts=line.split('\t')
    parts=remove_blanks(parts)

    for line_num in range(0,46):
        line=file_reader.readline().replace('\n','')
        parts = line.split('\t')
        parts = remove_blanks(parts)
        tag=parts[0]
        tag_counts[tag]=int(parts[1])
        tag_seen_type_counts[tag]=int(parts[2])
        tag_unseen_type_counts[tag]=int(parts[3])
        for index in range(4,len(parts)):
            transition_counts[line_num][index-4]=int(parts[index])

    for i in range(0,len(tagset)-1):
        ptag=tagset[i]
        for j in range(1,len(tagset)):
            ctag=tagset[j]
            C_ptag = tag_counts[ptag]
            T = tag_seen_type_counts[ptag]
            Z = tag_unseen_type_counts[ptag]
            tran_count = transition_counts[i][j-1]
            prob = 0.0
            if (tran_count > 0):
                prob = float(tran_count) / (C_ptag + T)
            else:
                prob = float(T) / (Z * (C_ptag + T))
            if (prob == 0.0):
                transition_probs[i][j-1]=log0
            else:
                transition_probs[i][j-1]=math.log1p(prob-1)

    file_reader.readline()

    while(1==1):
        word_tag_count_line=file_reader.readline()
        word_tag_count_line=word_tag_count_line.replace('\n','').strip()
        if (len(word_tag_count_line)==0):
            break;
        parts=word_tag_count_line.split(' ')
        word=parts[0]
        tag=parts[1]
        word_tag=word+" "+tag
        emission_probs[word_tag]=float(parts[2])

        if vocab.has_key(word):
            vocab[word] +=1
        else:
            vocab[word]=1


    while(1==1):
        suffix_line = file_reader.readline()
        suffix_line=suffix_line.replace('\n','').strip()
        if(len(suffix_line)==0):
            break;
        suffix=suffix_line.split(' ')[0]
        tag=suffix_line.split(' ')[1]
        suffix_tag_probs[suffix+" "+tag]=float(suffix_line.split(' ')[2])
        if(suffix_tag_probs[suffix+" "+tag] < no_suffix_prob):
            no_suffix_prob=suffix_tag_probs[suffix+" "+tag]
    no_suffix_prob -=1
    capital_lines=file_reader.readlines()
    for capital_line in capital_lines:
        capital_line=capital_line.replace('\n','').strip()
        capital_tag_probs[capital_line.split(' ')[0]]=float(capital_line.split(' ')[1])
        if(capital_tag_probs[capital_line.split(' ')[0]] < no_capital_prob):
            no_capital_prob=capital_tag_probs[capital_line.split(' ')[0]]
    no_capital_prob -=1

    file_reader.close()

    print "reading test sentences......"

    file_reader=open(test_file)
    test_sents=file_reader.readlines()
    file_reader.close()

    file_writer=open(out_file,'w')

    print "Viterbi starts......"
    a=datetime.datetime.now()
    sent_count=1
    for test_sent in test_sents:
        test_sent=test_sent.replace('\n','')
        words=test_sent.split(' ')

        tag_seq=get_tag_sequence(words)

        result=""
        for i in range(0,len(words)):
            result = result + words[i]+"/"+tag_seq[i]+" "
        result=result.strip()
        file_writer.write(result+"\n")
        print "processed "+str(sent_count)+" sentences out of "+str(len(test_sents))+"......"
        sent_count +=1

    file_writer.close()
    b=datetime.datetime.now()
    print b-a
    print "Finished......"

