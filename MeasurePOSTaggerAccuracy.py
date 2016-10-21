import os
import sys

#python MeasurePOSTaggerAccuracy.py output_file ref_file

#my_pos_file=os.path.join(data_folder,"sents.devt.out")
my_pos_file=sys.argv[1]
file_reader=open(my_pos_file)
my_pos_tags=file_reader.readlines()
file_reader.close()

#gold_pos_file=os.path.join(data_folder,"sents.devt")
gold_pos_file=sys.argv[2]
file_reader=open(gold_pos_file)
gold_pos_tags=file_reader.readlines()
file_reader.close()
tag_total=0
tag_match=0
for i in range(0,len(my_pos_tags)):
    my_pos_tags[i]=my_pos_tags[i].replace('\n','')
    my_parts=my_pos_tags[i].split(' ')
    gold_pos_tags[i]=gold_pos_tags[i].replace('\n','')
    gold_parts=gold_pos_tags[i].split(' ')
    tag_total += len(gold_parts)

    for j in range(0,len(gold_parts)):
        if(my_parts[j]==gold_parts[j]):
            tag_match +=1

print "Accuracy=", float(tag_match)/tag_total
