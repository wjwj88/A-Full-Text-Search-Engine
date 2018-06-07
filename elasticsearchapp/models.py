from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from .search import BlogPostIndex, TargetIndex
#
from elasticsearch import Elasticsearch
from django.conf import settings
# Create your models here.

es_client = Elasticsearch()

# Blogpost to be indexed into ElasticSearch
# this model is for testing on small model
class BlogPost(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blogpost')
    posted_date = models.DateField(default=timezone.now)
    title = models.CharField(max_length=200)
    text = models.TextField(max_length=1000)

    # Method for indexing BlogPost model
    def indexing(self):
        obj = BlogPostIndex(
            meta={'id': self.id},
            author=self.author.username,
            posted_date=self.posted_date,
            title=self.title,
            text=self.text
        )
        obj.save()
        return obj.to_dict(include_meta=True)

    def __str__(self):
        return self.title
        


# ssgs model to be indexed
class TargetStatus(models.Model):
    targetID = models.IntegerField(primary_key=True)
    target = models.CharField(max_length=20)
    annotation = models.CharField(max_length=512)
    species = models.CharField(max_length=101)
    status = models.CharField(max_length=50)
    clone = models.CharField(max_length=13)
    protein = models.CharField(max_length=13)
    genePage = models.CharField(max_length=67)
    uniprot = models.CharField(max_length=50)
    # class is a reserved word
    taxonClass = models.CharField(max_length=50)
    superkingdom = models.CharField(max_length=50)
    targetRole = models.CharField(max_length=512)
    batch = models.CharField(max_length=256)
    community = models.CharField(max_length=8)
    # this has to be true to make the db
    maxCode = models.SmallIntegerField(null=True)  

    
    class Meta:
        db_table = 'target_status'

    # method for indexing ssgc model
    def indexing(self):
        obj = TargetIndex(
            meta={'id': self.targetID},
            targetID = self.targetID,
            target = self.target,
            annotation = self.annotation,
            species = self.species,
            status = self.status,
            clone = self.clone,
            protein = self.protein,
            genePage = self.genePage,
            uniprot = self.uniprot,
            taxonClass = self.taxonClass,
            superkingdom = self.superkingdom,
            targetRole = self.targetRole,
            batch = self.batch,
            community = self.community,
            maxCode = self.maxCode
        )
        obj.save()
        return obj.to_dict(include_meta=True)

    def delete(self, *args, **kwargs):
        prev_pk = self.targetID
        super(TargetStatus, self).delete(*args, **kwargs)
        old_indexed_post = TargetIndex.get(id=prev_pk)
        old_indexed_post.delete()


        '''
        es_client.delete(
            index = self._meta.es_index_name,
            doc_type=self._meta.es_type_name,
            id = prev_pk,
            refresh = True,
        ) '''






        '''
        the followings don't work for deletion
        es = Elasticsearch()
        es.delete(index = "targetstatus-index", id=prev_pk)
        
        old_indexed_post = TargetIndex.get(id=prev_pk)
        old_indexed_post.delete()
        
        # ???
        obj.save() 
        # ???
        TargetIndex.save()  '''
        
    def __str__(self):
        return self.target