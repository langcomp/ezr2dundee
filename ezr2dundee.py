#       EZR2DUNDEE Change the format of EZ Reader 'fixation' output to a format similar to the Dundee corpus
# Usage: python ezr2dundee.py <simulation_file> <cnt_file> <output_file> (e.g. python ezr2dundee.py 'SimulationResults.txt' 'schilling.cnt' 'dundee_output.txt') 
#   simulation_file is a txt file which is directly exported from EZ Reader 'fixation' simulation
#   cnt_file        is a cnt file, containing word length information of words in each sentence
#   output_file     is a txt file where you save the dundee-like output
# Logic & assumptions: 1. Currently the corpus is the schilling corpus.
#                      2. Interpretation of each column of the output:
#                         ppt:       participant id, = Subject in simulation_file
#                         text:      = Sentence in simulation_file (schilling corpus has 48 sentences)
#                         word:      always 'unknown'
#                         screennum: always 1
#                         linenum:   always 1
#                         olen:      always = wlen (punctuation ignored)
#                         wlen:      calculated from cnt_file. Column 5: 1st word end; Column 6: 2nd word end;... etc. Space count toward the second word.
#                         xpos:      = FixLoc in simulation_file
#                         wordnum:   = Word# in simulation_file
#                         fdur:      = FixDur in simulation_file
#                         oblp:      always = wdlp (punctuation ignored)
#                         wdlp:      calculated from simulation FixLoc and cnt word length.
#                         laun:      calculated from simulation FixLoc. Launch site of the 1st fixation on each sentence is always -99. 
# Written by Yunyan Duan, 03/06/2016

import re, argparse, bisect

parser = argparse.ArgumentParser(description='make dundee file from ez reader.')
parser.add_argument('simulation_file', help = 'EZ Reader fixation output txt file')
parser.add_argument('cnt_file', help = 'cnt file')
parser.add_argument('output_file', help = 'give a name for the output file')
args = parser.parse_args()

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
filename = args.simulation_file

simfixes = []
with open(filename) as rf: 
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


## Data2: corpus cnt file
cntname = args.cnt_file

sentcnts = []
with open(cntname) as rf:
    for line in rf:
        sentcnts.append([int(i) for i in line.split()])

# Step 2: Generate Dundee output
wf = open(args.output_file,'w')
wf.write("ppt text word screennum linenum olen wlen xpos wordnum fdur oblp wdlp laun\n")

for i in range(len(simfixes)):
    sent = sentcnts[simfixes[i].sent]
    
    x = Fixation()
    x.ppt = simfixes[i].subj
    x.text = simfixes[i].sent
    x.word = 'unknown'
    x.screennum = 1
    x.linenum = 1
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
#    x.wordnum = simfixes[i].WordNum + 1
    x.wordnum = bisect.bisect_left(sent[3:], x.xpos)
    if x.wordnum != simfixes[i].WordNum + 1:
        print 'Warning: wordnum mismatch! subject: {subj}, sentence: {text}, xpos: {xpos}, EZ_Reader wordnum: {ezrwn}, New wordnum: {nwn}.'.format(subj = x.ppt, text = x.text, xpos = x.xpos, ezrwn = (simfixes[i].WordNum + 1), nwn = x.wordnum)
        print sent
        print '\n'
    if x.xpos > sent[-1]: ## landing out of the right end of the sentence
        print 'Warning: fixation out of sentence! subject: {subj}, sentence: {text}, xpos: {xpos}, sentence end: {snd}.\n'.format(subj = x.ppt, text = x.text, xpos = x.xpos, snd = sent[-1])
        x.wordnum = x.wordnum -1
    x.fdur = simfixes[i].FixDur
    if x.wordnum == 0:
        x.oblp = simfixes[i].FixLoc
        x.wdlp = simfixes[i].FixLoc
    else:
        x.oblp = simfixes[i].FixLoc - sent[x.wordnum + 3] -1
        x.wdlp = simfixes[i].FixLoc - sent[x.wordnum + 3] -1
    if simfixes[i].FixNum == 1:
        x.laun = -99
    else:
        x.laun = simfixes[i-1].FixLoc - simfixes[i].FixLoc
    wf.write(x.pretty_print()+'\n')
    
wf.close()
