# coding: utf-8
import re, subprocess, pickle

cd ~/Dev/FOSS/Apertium/apertium-dan

dixfile = open("expanded.dix")
dixdat  = dixfile.read().split("\n")

dixdat  = filter(lambda x: "<adj>" in x, dixdat)

def make_list(lines):
    out = []
    temp = []
    lemma = ""
    l = map(lambda x: re.findall(r'([^:]*):([^<]*)(.*)', x)[0], lines)
    l = filter(lambda x: "<adj>" in x[2], l)
    for i in l:
        if lemma != i[1]:
            lemma = i[1]
            out.append(tuple(temp))
            temp = []
        temp.append("{0}:{1}{2}".format(i[0], i[1], i[2]))
        
    #return filter(lambda x: len(x.values()[0]) == 2, out)    
    return set(filter(lambda x: len(x) > 0, out))

def check_forms(tags, f):
    return reduce(lambda x, y: x and y, map(lambda x: x in tags, f.split("|")))

def form_words(l):
    forms = []
    try:
        forms.append(filter(lambda x: check_forms(x, "<adj>|<pst>|<ut>|<sg>|<ind>"), l)[0])
        forms.append(filter(lambda x: check_forms(x, "<adj>|<pst>|<nt>|<sg>|<ind>"), l)[0])
        forms.append(filter(lambda x: check_forms(x, "<adj>|<pst>|<un>|<sp>|<def>"), l)[0])
        forms.append(filter(lambda x: check_forms(x, "<adj>|<comp>|<un>|<sp>"), l)[0])
        forms.append(filter(lambda x: check_forms(x, "<adj>|<sup>|<un>|<sp>|<ind>"), l)[0])
        return map(lambda x: re.findall(r"^(.*?):", x)[0], forms)
    except IndexError:
        pass

def ap_translate(words):
    f = open("word_dump", "w")
    for i in words:
        f.write("%s.\n" % i[1])

    subprocess.check_output('cat word_dump | apertium -d . swe-dan > tr_dump', shell=True)

    f = open("tr_dump", "r")
    l = f.readlines()
    f.close()

    return zip(map(lambda x: x[0], words), l)

out = make_list(dixdat)
dan_words = filter(lambda x: x, map(form_words, out))

cd ~/Dev/FOSS/GF-master/lib/src/translator/

f = open("DictionarySwe.gf")
dictdat = f.read().split("\n")

dictdat = filter(lambda x: "_A " in x and "variants" not in x, filter(lambda x: x.startswith("lin"), dictdat))

words = map(lambda x: x[0], filter(lambda x: len(x) > 0, map(lambda x: re.findall(r'lin (.*?) = mkA "(.*?)"', x), dictdat)))

cd ~/Dev/FOSS/Apertium/apertium-swe-dan

fin_words = map(lambda x: (x[0], x[1].lstrip("#").rstrip(".\n")), filter(lambda x: not x[1].startswith('*'), ap_translate(words)))

out_sets = []
for i in fin_words:
    for j in dan_words:
        if i[1] in j:
            out_sets.append('lin {0} = mkA "{1}" "{2}" "{3}" "{4}"'.format(i[0], *j))


print out_sets

