#!/usr/bin/python
# -*- coding: utf8 -*-

import os 
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "elasticSearchProject.settings")
import django
django.setup()
from elasticsearchapp.models import TargetStatus 

attributes = ['id','target','annotation','species','status',
        'clone','protein','genePage','uniprot','taxonClass',
        'superkingdom','targetRole','batch','community','maxCode']

def populate(fileName):
    file = open(fileName,'r')
    for line in file:
        li = line.strip('\n').split('\t')
        while len(li)!=15:
            for i in range(0,len(li)):
                if len(li[i])==0:
                    li.pop(i)
                    break        
        add_targetStatus(li)
    print('done with population......................')


def add_targetStatus(targetList):
    t = TargetStatus.objects.get_or_create(targetID=int(targetList[0]))[0]
    t.target = targetList[1].strip(' ')
    t.annotation = targetList[2].strip(' ')
    t.species = targetList[3].strip(' ')
    t.status = targetList[4].strip(' ')
    t.clone = targetList[5].strip(' ')
    t.protein = targetList[6].strip(' ')
    t.genePage = targetList[7].strip(' ')
    t.uniprot = targetList[8].strip(' ')
    t.taxonClass = targetList[9].strip(' ')
    t.superkingdom = targetList[10].strip(' ')
    t.targetRole = targetList[11].strip(' ')
    t.batch = targetList[12].strip(' ')
    t.community = 'c'
    t.maxCode = int(targetList[14].strip(' '))
    t.save()
    return t

# Start execution here!
if __name__ == '__main__':
    print("Starting target population script...")
    populate('target_status_data.txt')