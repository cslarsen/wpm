#! /usr/bin/env python
# -*- encoding: utf-8 -*-

"""
Facilitates Addition Of Custom Examples To The data/examples.json File
Through A Command Line Interface.
"""

import json
import pkg_resources

def main():

    pathToDataFile = pkg_resources.resource_filename("wpm",
            "data/examples.json")

    texts = []
    with open(pathToDataFile, 'r') as dataFile:
        texts = json.load(dataFile)

    # Boolean to indicate whether the user wants to add more examples or not
    addMore = True

    print ('*' * 80)
    while(addMore == True):
        queryString = "Would You Like To Add A New Example?[Y/n]  "
        userResponse = raw_input(queryString)

        if (userResponse in ['', 'y', 'Y']):
            print '\n'
            
            # Input Author Details
            authorQuery = "Enter Name Of Author:  "
            authorName = raw_input(authorQuery)
            print '\n'

            # Input Title Details
            titleQuery = "Enter Title Of Work/Source:  "
            titleName = raw_input(titleQuery)
            print '\n'

            # Input Custom Example Text
            exampleQuery = "Enter Example Text:\n"
            exampleText = raw_input(exampleQuery)
            print '\n'

            # Boolean To Facilitate Confirmation Of Entered Data
            confirmData = False

            print ('Confirm Previously Entered Data -\n')
            print ('Author: ' + authorName)
            print ('\n')
            print ('Title Name: ' + titleName)
            print ('\n')
            print ('Text Data: ' + exampleText)
            print('\n')

            # Boolean To Facilitate Confirmation Of Entered Data
            confirmDataQuery = 'Is The Data Displayed Above Accurate?[Y/n]:  '
            confirmData = raw_input(confirmDataQuery)

            if (confirmData in ['', 'y', 'Y']):
                newExample = {}
                newExample["author"] = authorName
                newExample["title"] = titleName
                newExample["text"] = exampleText

                texts.append(newExample)
                print 'New Example Successfully Added.\n'

            elif (confirmData in ['n', 'N']):
                print 'Previous Data Ignored.'

            else:
                print 'Invalid Response. Previous Data Ignored'
                print 'Trying Again'
                continue

        elif (userResponse in ['n', 'N']):
            print ('*' * 80)
            print 'Terminating Program...\n'
            addMore = False

        else:
            print 'Invalid Response Detected. Trying Again...\n'
            pass

    with open(pathToDataFile, "w") as dataFile:
        json.dump(texts, dataFile, indent = 1, sort_keys = True)
