#!/usr/bin/python
## wget -N http://dblp.uni-trier.de/xml/dblp.xml.gz
## then run this script
import gzip, json, os
import PySimpleGUI as sg    

import DBLP2json01

sg.change_look_and_feel('SystemDefault')      


def force ():
  print ("** Adding affiliation to the graph **")
  temp_jsonfilename = 'tmp2_dblp_affiliation.json.gz'
  final_jsonfile = 'dblp2_affiliation.json.gz'
  allauthors = set ()
  out = gzip.GzipFile (temp_jsonfilename, 'w')
  with gzip.open(out, 'wt') as zipfile:
      zipfile.write('[\n')
      
  edgecount = 0
        
  for p, paper in enumerate (DBLP2json01.papers ()):
    tag, authors, affiliations = paper
    for i, author in enumerate (authors):
        allauthors.add (author)
        for j, affiliation in enumerate(affiliations):
            if(i==j):
                if edgecount: 
                    with gzip.open(out, 'wt') as zipfile:
                        zipfile.write(',\n')
                edgecount += 1
                with gzip.open(out, 'wt') as zipfile:
                    print("Info " , [author, affiliation, tag])
                    json.dump([author, affiliation, tag], zipfile) 


  with gzip.open(out, 'wt') as zipfile: 
      zipfile.write('\n]\n')
  out.close()
  os.rename (temp_jsonfilename, final_jsonfile)

  print('-- %d unique authours, %d total affiliation edges' % (len (allauthors), edgecount))
  sg.popup('Number of unique authors found:', len (allauthors), 'Number of edges created :',  edgecount)

if __name__ == '__main__': force ()