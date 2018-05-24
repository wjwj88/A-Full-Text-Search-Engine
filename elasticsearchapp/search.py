from elasticsearch_dsl.connections import connections
from elasticsearch_dsl import DocType, Text, Date, Long, Integer, \
            Search, FacetedSearch, TermsFacet, Keyword, A, analyzer, tokenizer
from elasticsearch_dsl.query import MultiMatch, Match
from elasticsearch.helpers import bulk
from elasticsearch import Elasticsearch
from . import models
from django.db.models import Q

connections.create_connection()

fieldNameList = ['superkingdom', 'current_status', 
                 'clone_availability', 'protein_availability']


ngramAnalyzer = analyzer('ngramAnalyzer',
    tokenizer=tokenizer('trigram', 'nGram', min_gram=4, max_gram=30),
    filter=['lowercase']
)

class BlogPostIndex(DocType):
    author = Text()
    posted_date = Date()
    title = Text()
    text = Text()

    class Meta:
        index = 'blogpost-index'

def bulk_indexing():
    BlogPostIndex.init()
    es = Elasticsearch()
    bulk(client=es, actions=(b.indexing() for b in models.BlogPost.objects.all().iterator()))


class TargetIndex(DocType):

    targetID = Long()
    target = Text()
    annotation = Text(analyzer=ngramAnalyzer)
    species = Text(analyzer=ngramAnalyzer)
    status = Keyword()   #  Text()  
    clone = Keyword()   #  Text() 
    protein = Keyword()   #  Text() 
    genePage = Text(analyzer=ngramAnalyzer)
    uniprot = Text(analyzer=ngramAnalyzer)
    taxonClass = Text(analyzer=ngramAnalyzer)
    superkingdom = Keyword()
    targetRole = Text(analyzer=ngramAnalyzer)
    batch = Text(analyzer=ngramAnalyzer)
    community = Text(analyzer=ngramAnalyzer)
    maxCode = Long()






    '''
    targetID = Long()
    target = Text()
    annotation = Text()
    species = Text()
    status = Keyword()   #  Text()  
    clone = Keyword()   #  Text() 
    protein = Keyword()   #  Text() 
    genePage = Text()
    uniprot = Text()
    taxonClass = Text()
    superkingdom = Keyword()
    targetRole = Text()
    batch = Text()
    community = Text()
    maxCode = Long() '''

    class Meta:
        index = "targetstatus-index"

def target_bulk_indexing():
    TargetIndex.init()
    es = Elasticsearch()
    bulk(client=es, actions=(t.indexing() for t in models.TargetStatus.objects.all().iterator()))


# simple search function
def search(uniprot):
    s = Search().filter('term', uniprot=uniprot)
        #.query("match", taxonClass="kinetoplastida")
        #.query("match", batch="cr_66")
    response = s.execute()
    return response

def simpleAndSearch(userInput, fieldName, fieldKey):
    client = Elasticsearch()
    fields = ['target','annotation','species',
              'status','clone','protein','genePage','uniprot',
              'taxonClass','superkingdom','targetRole',
              'batch','community']
    q = MultiMatch(query=userInput,
                   fields=fields,
                   type = 'cross_fields',
                   #analyzer = 'standard',
                   operator = 'and')

    s = Search(using=client, index='targetstatus-index') \
        .filter('term', fieldName=fieldKey).query(q)
    '''
    s = Search(using=client, index='targetstatus-index') \
        .filter('term', fieldName=fieldKey).query(q) '''
    count = s.count()
    response = s[0:count].execute()
    return response



# find all rows if any field contains the passed word
# or search on interger and text indivitually, then combine 
# through dictionary and return dictionarys???? may be too slow??? 
def multiFieldSearch(word):
    fields=[]
    if word.isdigit():
        fields = ['targetID', 'maxCode']
    else:
        fields = ['target','annotation','species',
                           'status','clone','protein','genePage','uniprot',
                           'taxonClass','superkingdom','targetRole',
                           'batch','community']

    q = MultiMatch(query=word,
                   type ="phrase_prefix",
                   fields=fields)

    s=Search().query(q)
    count = s.count()
    response = s[0:count].execute()
    return response

# main function to do searching for backend
def MainSearch(word):
    # keep track of the search words user typed
    targetList = []
    # do exact matching first
    bs = FS(word)
    re = bs.execute()
    if re.hits.total > 0:
        bs = FS(word, )
    #else:




    #return bs.execute()  #ignore_cache=True



# default to be or, not and
class FS(FacetedSearch):
    doc_types = [TargetIndex, ]

    # fields to be searched(used for searching integer field as needed)
    fieldsI = ['targetID','target','annotation^3','species^2',
              'status','clone','protein','genePage','uniprot',
              'taxonClass','superkingdom','targetRole',
              'batch','community','maxCode']

    # fields to be searched(used for searching only text field as needed)
    fieldsS = ['target','annotation','species',
              'status','clone','protein','genePage','uniprot',
              'taxonClass','superkingdom','targetRole',
              'batch','community']
    
    facets = {
        # use bucket aggregations to define facets
        'superkingdom': TermsFacet(field='superkingdom'), 
        'current_status': TermsFacet(field='status'),
        'clone_availability': TermsFacet(field='clone'),
        'protein_availability': TermsFacet(field='protein')    
    } 

    def query(self, search, search_terms):
        if search_terms:
            list = search_terms.split()
            hasInterger = False
            for word in list:
                if word.isdigit():
                    hasInterger = True

            q = MultiMatch(query=search_terms,
                   fields=self.fieldsI,
                   type = 'cross_fields',
                   analyzer = 'standard',
                   operator = 'and')

            '''
            if hasInterger:
                q = MultiMatch(query=search_terms,
                       fields=self.fieldsI,
                       type = 'cross_fields',
                       analyzer = 'standard',
                       operator = 'and') '''
            return search.query(q)
        return search



# fuzzy search
class FuzzySearch(FacetedSearch):
    doc_types = [TargetIndex, ]

    # fields to be searched
    fields = ['target','annotation','species','status',
              'clone','protein','genePage','uniprot',
              'taxonClass','superkingdom','targetRole',
              'batch','community']
    facets = {
        # use bucket aggregations to define facets
        'superkingdom': TermsFacet(field='superkingdom'),
        'current_status': TermsFacet(field='status'),
        'clone_availability': TermsFacet(field='clone'),
        'protein_availability': TermsFacet(field='protein')     
    }

    
    def query(self, search, search_terms):
        if search_terms:
            q = MultiMatch(query=search_terms,
                           fields=self.fields,
                           #type = 'cross_fields',
                           analyzer = 'standard',
                           operator = 'or',
                           fuzziness = 'AUTO',
                           prefix_length = 3,                          
                           max_expansions = 100)
                           #transpositions = True)
            return search.query(q)
        return search    

    '''
    def simpleAndSearch(self, search_terms, fieldName, fieldKey):
        client = Elasticsearch()
        self.mysearch = search_terms
        return Search(using=client, index='targetstatus-index').filter('term', fieldName=fieldKey).query(self.myquery)        
        #return self.search().filter('term', fieldName=fieldKey).query(self.myquery)   ''' 

# print the search response 
def printSearch(re, word):
  dic = re.facets
  for key in dic:
    print(key,'   : -------------------')
    for category, count, isSelected in dic[key]:
      print(category,' has ', count,' hits')
      bs = FS(word, filters={key: category})
      response = bs.execute()
      for i in range(response.hits.total):
        print(response[i].to_dict())


