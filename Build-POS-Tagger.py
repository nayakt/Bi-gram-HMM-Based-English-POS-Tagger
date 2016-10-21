import math
import sys

#python build_tagger.py sents.train sents.devt model_file


train_file=sys.argv[1]
model_file=sys.argv[3]

tagset=['<s>', 'PRP$', 'VBG', 'FW', 'VBN', 'POS', "''", 'VBP', 'WDT', 'JJ', 'WP',
            'VBZ', 'DT', '#', 'RP', '$', 'NN', 'VBD', ',', '.', 'TO', 'PRP', 'RB',
            '-LRB-', ':', 'NNS', 'NNP', '``', 'WRB', 'CC', 'LS', 'PDT', 'RBS', 'RBR',
            'CD', 'EX', 'IN', 'WP$', 'MD', 'NNPS', '-RRB-', 'JJS', 'JJR', 'SYM', 'VB', 'UH', '</s>']

suffix_set=['s','ed', 'en', 'ing','ion','al','ive', 'able', 'ize','ful']

log0=-1000.0

# read training file
print "reading training file......"
file_reader=open(train_file)
train_sents=file_reader.readlines()
file_reader.close()

count_tags={"<s>":len(train_sents)}   #C(t)
count_words={}  #C(w)
count_word_tag_pairs={}  #C(w,t)
smoothed_count_word_tag_pairs={}  #C*(w,t)
count_tag_bigrams={}    #C(t(i-1),t(i))
count_tags_singleton={}  # sing(t)=number of unique words for which C(w,t)=1
count_tags_word_type={}  # k(t)=number of unique words tagged with t

count_suffix_tag_pairs={}
count_capital_tag_pairs={}

print "calculating model statistics......"
for sent in train_sents:
    sent=sent.replace('\n','')
    word_tag_pairs=sent.split(' ')
    word_index=0
    prev_tag="<s>"
    for word_tag_pair in word_tag_pairs:
        elements=word_tag_pair.split('/')
        tag=elements[len(elements)-1]
        word=elements[0]
        if(word_index==0):
            if(word[0] >='A' and word[0]<='Z'):
                if(count_capital_tag_pairs.has_key(tag)):
                    count_capital_tag_pairs[tag] +=1
                else:
                    count_capital_tag_pairs[tag]=1

        word_index +=1
        for index in range(1, len(elements) - 1):
            word = word + "/" + elements[index]

        # update word count
        if(count_words.has_key(word)):
            count_words[word]=count_words[word]+1
        else:
            count_words[word]=1

        # update tag count
        if count_tags.has_key(tag):
            count_tags[tag]=count_tags[tag]+1
        else:
            count_tags[tag]=1

        # update word, tag pair count
        word_tag=word +' '+tag
        if(count_word_tag_pairs.has_key(word_tag)):
            count_word_tag_pairs[word_tag]=count_word_tag_pairs[word_tag]+1
        else:
            count_word_tag_pairs[word_tag]=1

        # update tag. tag pair count
        tag_bigram=prev_tag+' '+tag
        if(count_tag_bigrams.has_key(tag_bigram)):
            count_tag_bigrams[tag_bigram]=count_tag_bigrams[tag_bigram]+1
        else:
            count_tag_bigrams[tag_bigram]=1
        prev_tag=tag

    # update sentence end tag bigram
    last_tag_bigram=prev_tag+' '+"</s>"
    if (count_tag_bigrams.has_key(last_tag_bigram)):
        count_tag_bigrams[last_tag_bigram] = count_tag_bigrams[last_tag_bigram] + 1
    else:
        count_tag_bigrams[last_tag_bigram] = 1

token_size=0
for word in count_words.keys():
    token_size +=count_words[word]
for t in range(1,len(tagset)-1):
    tag=tagset[t]
    count_tags_singleton[tag]=0
for word_tag_pair in count_word_tag_pairs:
    word=word_tag_pair.split(' ')[0]
    tag=word_tag_pair.split(' ')[1]
    for suffix in suffix_set:
        if(word.endswith(suffix)):
            if(count_suffix_tag_pairs.has_key(suffix+" "+tag)):
                count_suffix_tag_pairs[suffix+" "+tag] +=1
            else:
                count_suffix_tag_pairs[suffix+" "+tag]=1
    if(count_tags_word_type.has_key(tag)):
        count_tags_word_type[tag] +=1
    else:
        count_tags_word_type[tag]=1
    if(count_word_tag_pairs[word_tag_pair]==1):
        count_tags_singleton[tag] +=1

for word_tag_pair in count_word_tag_pairs:
    word = word_tag_pair.split(' ')[0]
    tag = word_tag_pair.split(' ')[1]
    smoothed_count_word_tag_pairs[word_tag_pair]=float(count_word_tag_pairs[word_tag_pair]) - float(count_tags[tag]) * count_tags_singleton[tag]/(token_size * count_tags_word_type[tag])
for t in range(1,len(tagset)-1):
    tag=tagset[t]
    smoothed_count_word_tag_pairs["<unk> "+tag]=float(count_tags[tag]) * count_tags_singleton[tag]/token_size


print "writing tag transition statistics......"

file_writer=open(model_file,'w')
file_writer.write("\tTotal(C)\tSeen_Tag_Type(T)\tUnseen_Tag_Type(Z)\t")
for index in range(1,len(tagset)):
    file_writer.write(tagset[index]+"\t")
file_writer.write("\n")

for r in range(0,len(tagset)-1):
    ptag=tagset[r]
    zero_count=0
    for c in range(1,len(tagset)):
        ctag=tagset[c]
        if not(count_tag_bigrams.has_key(ptag + ' ' + ctag)):
            zero_count +=1
    file_writer.write(ptag+"\t"+str(count_tags[ptag])+"\t\t"+str(46-zero_count)+"\t\t\t"+str(zero_count)+"\t\t\t")
    for c in range(1,len(tagset)):
        ctag=tagset[c]
        tag_bigram_count=0
        if(count_tag_bigrams.has_key(ptag+' '+ctag)):
            tag_bigram_count=count_tag_bigrams[ptag+' '+ctag]
        file_writer.write(str(tag_bigram_count)+"\t")

    file_writer.write("\n")

print "writing word emission transition statistics......"
file_writer.write("\n")
for word in count_words.keys():
    for t in range(1,len(tagset)-1):
        tag=tagset[t]
        word_tag = word + ' ' + tag
        if smoothed_count_word_tag_pairs.has_key(word_tag):
            word_tag_count=smoothed_count_word_tag_pairs[word_tag]
            prob=float(word_tag_count)/count_tags[tag]
            log_prob=0.0
            if(prob==0.0):
                log_prob=log0
            else:
                log_prob=math.log1p(prob-1)
            file_writer.write(word_tag+' '+str(log_prob))
            file_writer.write("\n")

print "writing unknown words statistics......"
for t in range(1,len(tagset)-1):
    tag=tagset[t]
    word_tag = "<unk>" + ' ' + tag
    prob=float(smoothed_count_word_tag_pairs[word_tag])/count_tags[tag]
    log_prob = 0.0
    if (prob == 0.0):
        log_prob = log0
    else:
        log_prob = math.log1p(prob - 1)
    file_writer.write(word_tag + ' ' + str(log_prob))
    file_writer.write("\n")

file_writer.write("\n")

for suffix_tag_pair in count_suffix_tag_pairs:
    tag=suffix_tag_pair.split(' ')[1]
    prob=float(count_suffix_tag_pairs[suffix_tag_pair])/count_tags[tag]
    log_prob=log0
    if(prob > 0.0):
        log_prob=math.log1p(prob-1)
    file_writer.write(suffix_tag_pair+" "+str(log_prob))
    file_writer.write("\n")

file_writer.write("\n")
for tag in count_capital_tag_pairs.keys():
    prob=float(count_capital_tag_pairs[tag])/count_tags[tag]
    log_prob=log0
    if(prob>0.0):
        log_prob = math.log1p(prob - 1)
        file_writer.write(tag + " " + str(log_prob))
        file_writer.write("\n")
file_writer.close()

print "Finished......"
