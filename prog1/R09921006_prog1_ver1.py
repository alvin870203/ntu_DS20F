#!/usr/bin/env python
# python 3.7.8
# numpy 1.19.1

import sys
import numpy as np

def Graph2Matrix(Graph):
    indexOfWeb, webOfIndex = {}, {}
    for index, web in enumerate(G.keys()):
        indexOfWeb[web] = index
        webOfIndex[index]  = web
    n = len(G) # num of nodes
    Matrix = np.zeros([n,n]) # matrix M, shape of (n,n)
    for source in G.keys():
        for link in G[source]:
            try:
                Matrix[indexOfWeb[link], indexOfWeb[source]] = 1/len(G[source]) # col=source, row=link
            except:
                print('ERROR*************************************************')
                print(link)
                continue
    return Matrix, indexOfWeb, webOfIndex

def PageRank(M, d, DIFF):
    '''PageRank algorithm'''
    PR_result = []
    N = len(M)
    PR_init = np.full((N), 1/N)
    PR = PR_init
    diff = DIFF + 1 # initialize diff to be larger than DIFF
    while diff >= DIFF:
        PRbefore = PR
        PR = (1 - d) * PR_init + d * np.matmul(M, PR)
        diff = np.sum(abs(PRbefore - PR))
    for index, rank in enumerate(PR):
        PR_result.append((webOfIndex[index], rank))
    PR_result = sorted(PR_result, key = lambda x: x[1], reverse = True)
    return PR_result

def TopPages(pages_list, PRlist_dict):
    pagesOfWord = []
    line = ''
    if len(pages_list) == 0:
        return 'none'
    for page in pages_list:
        pagesOfWord.append((page, PRlist_dict[page]))
    pagesOfWord = sorted(pagesOfWord, key = lambda x: x[1], reverse=True)[:10]
    for i in range(len(pagesOfWord)):
        line += f'page{pagesOfWord[i][0]} '
    return line

def SearchEngine(search, RevInd, PRlist):
    '''find pages for search'''
    PRlist_dict = dict(PRlist)
    pages_list = []
    AND_list = []
    OR_list = []
    if len(search) > 1:
        for word in search:
            if word not in RevInd.keys():
                pages_list.append(set())
                continue
            pages_list.append(set(RevInd[word]))
        AND_list = list(set.intersection(*pages_list))
        OR_list = list(set.union(*pages_list))
        line_AND = TopPages(AND_list, PRlist_dict)
        line_OR = TopPages(OR_list, PRlist_dict)
        return f'AND {line_AND}\nOR {line_OR}\n'
    elif len(search) == 1:
        if search[0] not in RevInd.keys():
            pages_list = []
        else:
            pages_list = RevInd[search[0]]
        line_Single = TopPages(pages_list, PRlist_dict)
        return f'{line_Single}\n'
    else:
        print('ERROR!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')

    

if __name__ == '__main__':
    numberOfArgs = len(sys.argv)

    G = {}
    outbranching = {}
    wordsOfWeb = {}
    wordsList = []
    
    if numberOfArgs != 3:
        sys.stderr.write(f'Usage: {sys.argv[0]} <directory path of page files> <path of list.txt>\nFor example: python R09921006_prog1_ver1.py ./web-search-files2 list.txt\n')
        sys.exit(1)

    try:
        for page_num in range(500):
            G[str(page_num)] = {}
            with open(sys.argv[1] + '/page' + str(page_num), 'r') as f: # sys.argv[1] = './web-search-files2/page50'
                
                # read in page number
                for line in f:
                    if '---------------------' in line: break
                    G.setdefault(str(page_num), {})[''.join(filter(str.isdigit, line))] = 1
                # read in keywords
                tmp_words = []
                for word in next(f).split():
                    tmp_words.append(word)
                    wordsList.append(word)
                wordsOfWeb[str(page_num)] = tmp_words
                outbranching[str(page_num)] = len(G[str(page_num)])
    except OSError as err:
        sys.stderr.write(str(err)+'\n')
        sys.exit(2)
    
    wordsList = sorted(list(set(wordsList)))
    G['500'] = {}
    outbranching['500'] = 0

    reverseIndex = {}
    with open('reverseindex.txt', 'w') as f:
        for w in wordsList:
            reverseIndex[w] = [k for k, v in wordsOfWeb.items() if w in v]
            tmp_webs = ''
            for v in reverseIndex[w]:
                tmp_webs += (' page' + v)
            f.write(f'{w:<20} {tmp_webs}\n')

    M, indexOfWeb, webOfIndex = Graph2Matrix(G)
    
    d_list = [0.25, 0.45, 0.65, 0.85]
    DIFF_list = [0.100, 0.010, 0.001]
    
    for d in d_list:
        for DIFF in DIFF_list:
            pr = PageRank(M, d, DIFF)
            filename = "pr_" + str(int(100*d)) + "_" + str(int(1000*DIFF)).zfill(3) + ".txt"
            with open(filename, "w") as f:
                for line in pr:
                    f.write(f'page{line[0]:<5} {outbranching[line[0]]:<4} {line[1]:<10.8f}\n') # Need to print page500?


            searchWords = []
            try:
                with open(sys.argv[2], 'r') as f: # sys.argv[2] = './list.txt'
                    # read in page number
                    for line in f:
                        searchWords.append(line.split())
            except OSError as err:
                sys.stderr.write(str(err)+'\n')
                sys.exit(3)

            filename = "result_" + str(int(100*d)) + "_" + str(int(1000*DIFF)).zfill(3) + ".txt"
            with open(filename, 'w') as f:
                for w in searchWords:
                    f.write(SearchEngine(w, reverseIndex, pr))