from __future__ import division, unicode_literals
from pprint import pprint
from Parser import Parser
import util
import math
import sys
import argparse

class VectorSpace:
    """ A algebraic model for representing text documents as vectors of identifiers. 
    A document is represented as a vector. Each dimension of the vector corresponds to a 
    separate term. If a term occurs in the document, then the value in the vector is non-zero.
    """

    #Collection of document term vectors
    documentVectors = []

    #Mapping of vector index to keyword
    vectorKeywordIndex=[]

    #Tidies terms
    parser=None

    #record  idf of document
    idf =[]
    count = 0 
   
    def __init__(self, documents=[]):
        self.documentVectors=[]
        self.parser = Parser()
        if(len(documents)>0):
            self.build(documents)

    def build(self,documents):
        """ Create the vector space for the passed document strings """
        self.vectorKeywordIndex = self.getVectorKeywordIndex(documents)
        self.idf = [0]*len(self.vectorKeywordIndex)
        self.documentVectors = [self.makeVector(document) for document in documents]
        #只計算一次idf值，因為idf值不受查詢輸入改變
        if self.count ==0:
            for num in range(len(self.vectorKeywordIndex)):
                for i in range(len(self.documentVectors)):
                    if self.documentVectors[i][num]>0:
                        self.idf[num]+=1
            self.count+=1
        
        
    def getVectorKeywordIndex(self, documentList):
        """ create the keyword associated to the position of the elements within the document vectors """

        #Mapped documents into a single word string	
        vocabularyString = " ".join(documentList)

        vocabularyList = self.parser.tokenise(vocabularyString)
        #Remove common words which have no search value
        vocabularyList = self.parser.removeStopWords(vocabularyList)
        uniqueVocabularyList = util.removeDuplicates(vocabularyList)

        vectorIndex={}
        offset=0
        #Associate a position with the keywords which maps to the dimension on the vector used to represent this word
        for word in uniqueVocabularyList:
            vectorIndex[word]=offset
            offset+=1
        return vectorIndex  #(keyword:position)


    def makeVector(self, wordString):
        """ @pre: unique(vectorIndex) """

        #Initialise vector with 0's
        vector = [0] * len(self.vectorKeywordIndex)
        wordList = self.parser.tokenise(wordString)
        wordList = self.parser.removeStopWords(wordList)
        for word in wordList:
            vector[self.vectorKeywordIndex[word]] += 1 #Use simple Term Count Model
            
        return vector


    def buildQueryVector(self, termList):
        """ convert query string into a term vector """
        query = self.makeVector(" ".join(termList))
        return query


    def related(self,documentId):
        """ find documents that are related to the document indexed by passed Id within the document Vectors"""
        ratings = [util.cosine(self.documentVectors[documentId], documentVector) for documentVector in self.documentVectors]
        #ratings.sort(reverse=True)
        return ratings


    def search1(self,searchList):
        """ search for documents that match based on a list of terms """
        queryVector = self.buildQueryVector(searchList)
        ratings = [util.cosine(queryVector, documentVector) for documentVector in self.documentVectors]
        #create diction
        diction = dict()
        for num, n in enumerate(ratings):
            diction[num]=n
        diction = sorted(diction.items(), key=lambda item: item[1], reverse=True)
        #catch max 5
        diction = diction[:5]
        dictdata = {}
        for l in diction:
            dictdata[l[0]] = l[1]
        return dictdata
   
    def search2(self,searchlist):
        queryVector = self.buildQueryVector(searchlist)
        ratings = [util.Euclidean(queryVector, documentVector)
                   for documentVector in self.documentVectors]
        diction = dict()
        for num, n in enumerate(ratings):
            diction[num] = n
        diction = sorted(
            diction.items(), key=lambda item: item[1], reverse=False)
        #catch max 5
        diction = diction[:5]
        dictdata = {}
        for l in diction:
            dictdata[l[0]] = l[1]
        return dictdata
    
    def search3(self,searchList):
        queryVector = self.buildQueryVector(searchList)
        for doc in self.documentVectors:
            for i in range(len(doc)):
                if self.idf[i] > 0:
                    #已知2048篇文章
                    doc[i] = doc[i]*math.log(2048/(self.idf[i]), 10)
                    #更改過一次就好
        for i in range(len(queryVector)):
            if self.idf[i] > 0:
                queryVector[i] = queryVector[i]*math.log(2048/(self.idf[i]),10)
        ratings = [util.cosine(queryVector, documentVector)
                   for documentVector in self.documentVectors]
        diction = dict()
        for num, n in enumerate(ratings):
            diction[num] = n
        diction = sorted(
            diction.items(), key=lambda item: item[1], reverse=True)
        #catch max 5
        diction = diction[:5]
        dictdata = {}
        for l in diction:
            dictdata[l[0]] = l[1]
        return dictdata
    
    def search4(self,searchList):
        queryVector = self.buildQueryVector(searchList)
        for i in range(len(queryVector)):
            if self.idf[i] > 0:
                queryVector[i] = queryVector[i]*math.log(2048/(self.idf[i]),10)
        ratings = [util.Euclidean(queryVector, documentVector)
                   for documentVector in self.documentVectors]
        # return ratings
        diction = dict()
        for num, n in enumerate(ratings):
            diction[num] = n
        diction = sorted(
            diction.items(), key=lambda item: item[1], reverse=False)
        #catch min  5
        diction = diction[:5]
        dictdata = {}
        for l in diction:
            dictdata[l[0]] = l[1]
        return dictdata
    def search5(self,searchList):
        queryVector = self.buildQueryVector(searchList)
        #use the method 3
        for i in range(len(queryVector)):
            if self.idf[i] > 0:
                queryVector[i] = queryVector[i] * math.log(2048/(self.idf[i]), 10)
        ratings = [util.cosine(queryVector, documentVector)
                   for documentVector in self.documentVectors]
        maxID = 0
        maxrate =0
        for num in range(len(ratings)):
            if ratings[num] >maxrate:
                maxrate = ratings[num]
                maxID = num
        #have got the feedback
        queryVector = self.buildQueryVector(searchList)
        
        for i in range(len(queryVector)):
            queryVector[i] += (0.5) *self.documentVectors[maxID][i] 
            
        for i in range(len(queryVector)):
            if self.idf[i] > 0:
                queryVector[i] = queryVector[i] * math.log(2048/(self.idf[i]), 10)
        #重新計算新的rating
        ratings = [util.cosine(queryVector, documentVector)
                   for documentVector in self.documentVectors]

        diction = dict()
        for num, n in enumerate(ratings):
            diction[num] = n
        diction = sorted(
            diction.items(), key=lambda item: item[1], reverse=True)
        #catch max 5
        diction = diction[:5]
        dictdata = {}
        for l in diction:
            dictdata[l[0]] = l[1]
        return dictdata
        
 
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", help="input the query string",
                     required=True, nargs='+')
    args = parser.parse_args()
    queryString = ""
    for ch in args.query:
        queryString += ch
        queryString += " "
    print("the query is: ",queryString)
    if len(queryString)>0:
        #read
        import os
        documents = []
        ########
        docID =dict()
        count=0
        for name in os.listdir('./documents'):
            #print(name)
            f = open('./documents/'+name)
            
            docID[count]=int(name[:-8])
            count +=1
            
            text = ""
            for line in f:
                text+=line
                text += " "
            #print(text)
            documents.append(text)
        vectorSpace = VectorSpace(documents)
        #第一題 
        print("\nTerm Frequency (TF) Weighting + Cosine Similarity\n")
        print("DocID  Score")
        dic1 = vectorSpace.search1([str(queryString)])
        dic1 = sorted( dic1.items(), key=lambda item: item[1], reverse=True)
        for n in dic1:
            print(docID[int(n[0])], n[1])
        #第二題
        print("\nTerm Frequency (TF) Weighting + Euclidean Distance\n")
        print("DocID  Score")
        dic2 = vectorSpace.search2([str(queryString)])
        dic2 = sorted(dic2.items(), key=lambda item: item[1], reverse=False)
        for n in dic2:
            print(docID[int(n[0])], n[1])
        
        #第三題
        print("\nTF-IDF Weighting + Cosine Similarity\n")
        print("DocID  Score")
        dic3=vectorSpace.search3([str(queryString)])
        dic3=sorted(dic3.items(), key=lambda item: item[1], reverse=True)
        for n in dic3:
            print(docID[int(n[0])], n[1])
        
        #第四題
        print("\nTF-IDF Weighting + Euclidean Distance\n")
        print("DocID  Score")
        dic4=vectorSpace.search4([str(queryString)])
        dic4=sorted(dic4.items(), key=lambda item: item[1], reverse=False)
        for n in dic4:
            print(docID[int(n[0])], n[1])
    ###################################################
        #第二大題
        print("\nFeedback Queries + TF-IDF Weighting + Cosine Similarity\n")
        print("DocID  Score")
        dic5 = vectorSpace.search5([str(queryString)])
        dic5=sorted(dic5.items(), key=lambda item: item[1], reverse=True)
        for n in dic5:
            print(docID[int(n[0])], n[1])



