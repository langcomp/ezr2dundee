# Change the format of EZ Reader 'fixation' output to a format similar to the Dundee corpus
# Input: EZ Reader 'fixation' simulation
# Output: Dundee corpus-like fixation data, txt file
# For current purpose, the corpus used for EZ Reader simulation is 'schilling98Corpus' 
# Current problems: 1. Punctuations are not considered, so always olen == wlen, wdlp == oblp
#                   2. Corpus cnt files do not contain words, so 'word' is always 'unknown'
#                   3. Not ready to take Input/Output filenames as arguments in command line
#                   4. To continue...
# Version 1. Written by Yunyan Duan, 02/29/2016

import re

class Fixation:
    def __init__(self):
        self.ppt = 'unknown'
        self.text = 'unknown'
        self.word = 'unknown'
        self.screennum = -1
        self.linenum = -1
        self.olen = -1
        self.wlen = -1
        self.xpos = -1
        self.wordnum = -1
        self.fdur = -1
        self.oblp = -1
        self.wdlp = -1
        self.laun = -99
    def pretty_print(self):
        return(' '.join([str(self.ppt), str(self.text),
                         str(self.word), str(self.screennum), str(self.linenum), 
                         str(self.olen), str(self.wlen), str(self.xpos), 
                         str(self.wordnum), str(self.fdur), str(self.oblp), 
                         str(self.wdlp), str(self.laun)]))

class SimFix:
    def __init__(self, line):
        self.FixDur = int(line[0])
        self.FixLoc = int(line[1])
        self.WordNum = int(line[2])
        self.FixNum = int(line[3])
        self.sent = 'unknown'
        self.subj = 'unknown'
    def pretty_print(self):
        return(' '.join([str(self.FixDur), str(self.FixLoc), 
                         str(self.WordNum), str(self.FixNum), 
                         str(self.sent), str(self.subj)]))

# Step 1: Read data
## Data1: EZ Reader simulation
filename = 'SimulationResults1_fixs.txt'
rf = open(filename)
simfixes = []

for line in rf:
    if line != '\n' and line[1:7] != 'FixDur':
        if line[1:9] == 'Sentence':
            s = filter(None,re.split(':|;|\s|\n',line))
            sentn = int(s[1])
            subjn = int(s[3])
            continue
        else:
            fix = SimFix(line.strip().split('\t'))
            fix.sent = sentn
            fix.subj = subjn
        simfixes.append(fix)
rf.close()

## Data2: corpus cnt file
cntname = 'schilling.cnt'
rf = open(cntname)
sentcnts = []

for line in rf:
    sentcnts.append([int(i) for i in line.split()])
rf.close()

# Step 2: Generate Dundee output
wf = open("dundee_output.txt",'w')
wf.write("ppt text word screennum linenum olen wlen xpos wordnum fdur oblp wdlp laun\n")

for i in range(len(simfixes)):
    sent = sentcnts[simfixes[i].sent]
    
    x = Fixation()
    x.ppt = simfixes[i].subj
    x.text = 1
    x.word = 'unknown'
    x.screennum = 1
    x.linenum = simfixes[i].sent
    if simfixes[i].WordNum == 0:
        x.olen = sent[4] - sent[3]
        x.wlen = sent[4] - sent[3]
    elif simfixes[i].WordNum == sent[2]-1: ## landing out of the right end of the sentence
        x.olen = sent[simfixes[i].WordNum + 3] - sent[simfixes[i].WordNum + 2] - 1
        x.wlen = sent[simfixes[i].WordNum + 3] - sent[simfixes[i].WordNum + 2] - 1
    else:
        x.olen = sent[simfixes[i].WordNum + 4] - sent[simfixes[i].WordNum + 3] - 1 
        x.wlen = sent[simfixes[i].WordNum + 4] - sent[simfixes[i].WordNum + 3] - 1 ## minus the space before the word
    x.xpos = simfixes[i].FixLoc
    x.wordnum = simfixes[i].WordNum
    x.fdur = simfixes[i].FixDur
    if simfixes[i].WordNum == 0:
        x.oblp = simfixes[i].FixLoc
        x.wdlp = simfixes[i].FixLoc
    else:
        x.oblp = simfixes[i].FixLoc - sent[simfixes[i].WordNum + 3] -1
        x.wdlp = simfixes[i].FixLoc - sent[simfixes[i].WordNum + 3] -1
    if simfixes[i].FixNum == 1:
        x.laun = -99
    else:
        x.laun = simfixes[i-1].FixLoc - simfixes[i].FixLoc
    wf.write(x.pretty_print()+'\n')
    
wf.close()
