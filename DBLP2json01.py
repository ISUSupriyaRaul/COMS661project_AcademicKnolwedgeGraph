## Create a knowledge graph of a specific research interest as (publication title, [authors], [affiliations]) triples
#!/usr/bin/python
## wget -N http://dblp.uni-trier.de/xml/dblp.xml.gz
## then run this script
import json, gzip, os, sys, xml.sax
import scholarly
import PySimpleGUI as sg    


sg.change_look_and_feel('SystemDefault')      
layout = [[sg.Text('Please insert your research  interest below.')], # retrieves the list of publications having the title with the given keywords
          [sg.Text('Topic of Interest', size=(15, 1)), sg.InputText()],
          [sg.Button('Search'), sg.Exit()]]    
window = sg.Window('DBLP Exploration Window', layout)      
event, values = window.read() 
print(event, values[0])  
window.close()

xml_filename = 'dblp.xml.gz'
json_gz_filename = 'dblp_research_interest1.json.gz'
tmp_filename = 'tmp_dblp3.json.gz'
report_frequency = 10000
autho_notfound = []
      
class DBLPHandler (xml.sax.ContentHandler):
  papertypes = set (['article', 'book', 'inproceedings', 'incollection', 'www', 'proceedings', 'phdthesis', 'mastersthesis'])
  context = values[0] #'foveated rendering'
  contextSplitWords = context.lower().split()
  def __init__ (self, out):
    self.out = out
    self.paper = None
    self.authors = []
    self.affiliation = []
    self.querycount = 0
    self.text = ''
    self.insertedpapercount = 0
    self.papercount = 0
    self.edgecount = 0

  def startElement (self, name, attrs):
    # Signals the start of an element in non-namespace mode.
    # The name parameter contains the raw XML 1.0 name of the element type as a string and the attrs parameter 
    # holds an object of the Attributes interface containing the attributes of the element.
    # Attributes objects implement a portion of the mapping protocol, including the methods get(), has_key(), keys(), and values(). 
    if name in self.papertypes:
      self.paper = str (attrs['key'])
      self.authors = []
      self.affiliation = []
    elif name in ['author', 'title']:
      self.text = ''
  def endElement (self, name):
    # Signals the end of an element in non-namespace mode.
    # The name parameter contains the name of the element type, just as with the startElement() event.
    # Attributes objects implement a portion of the mapping protocol, including the methods get(), has_key(), keys(), and values(). 
    if name == 'author':
      self.authors.append (self.text)
    elif name == 'title' and all(word in self.text.lower() for word in self.contextSplitWords):
      self.paper += (" " + self.text)
      self.write_paper ()
      self.paper = None
      
  def write_paper (self):
    if self.papercount:        
        with gzip.open(self.out, 'wt') as zipfile: 
            zipfile.write (',\n')
            
    self.papercount += 1
    self.edgecount += len (self.authors)
    
    for author in self.authors:
#        self.affiliation.append(" dummy ")
        self.affiliation.append(self.getGoogleScholarInfo(author))

    with gzip.open(self.out, 'wt') as zipfile:
        self.insertedpapercount += 1
        print("Paper %d " %(self.insertedpapercount) , [self.paper, self.authors, self.affiliation])
        json.dump ([self.paper, self.authors, self.affiliation], zipfile)
# dump() method for writing data to files. dumps() method writes to a Python string

    if self.papercount % report_frequency == 0:
      print('... processed %d papers, %d edges so far ...' % (self.papercount, self.edgecount))
      sys.stdout.flush ()
      
  def characters (self, chars):
    # ContentHandler.characters(content) - Receive notification of character data.
    #The Parser will call this method to report each chunk of character data. SAX parsers may return all contiguous 
    # character data in a single chunk, or they may split it into several chunks; however, all of the characters in any 
    # single event must come from the same external entity so that the Locator provides useful information. 
    # content may be a Unicode string or a byte string
    self.text += chars
    
  def getGoogleScholarInfo (self, findThisAuthor):
  #  print('^^^^^ Finding the author from Google Scholar^^^^^^')
    search_query = scholarly.search_author(findThisAuthor) 
    author = next(search_query, None)
    if author is None:
        autho_notfound.append(findThisAuthor)
#        print ("Author not found in Google Scholar- " + findThisAuthor)
        return "not found"
    else:
        return author.affiliation

def force ():
  print('** Parsing XML...')

  xmlfile = gzip.GzipFile (xml_filename, 'r')
  out = gzip.GzipFile (tmp_filename, 'w')
  with gzip.open(out, 'wt') as zipfile: 
      zipfile.write('[\n')
 # encoding/serialization- process of writing data to the disk   
  dblp = DBLPHandler (out)
  parser = xml.sax.parse (xmlfile, dblp)
  # xml.sax.parse(filename_or_stream, handler)
  # Create a SAX parser and use it to parse a document. The document, passed in as filename_or_stream, can be a filename or a file object. 
  # The handler parameter needs to be a SAX ContentHandler instance. 
  with gzip.open(out, 'wt') as zipfile:
      zipfile.write('\n]\n')
  out.close ()
  os.rename (tmp_filename, json_gz_filename)

  print('-- %d papers, %d edges' % (dblp.papercount, dblp.edgecount))
  print("Some authors could not be found in Google Scholar. Find their names below :")
  for author in autho_notfound:
      print(author)
  sg.popup('Number of publications found:', dblp.papercount, 'Number of edges created :',  dblp.edgecount)

def main (parse_args = False):
  try:
    need = (os.stat (xml_filename).st_mtime >= os.stat (json_gz_filename).st_mtime)
    # Get the status of a file - Time of most recent content modification expressed in seconds.
  except OSError:
    need = True
  if parse_args and len (sys.argv) > 1:
    need = True
  if need:
    force ()

def open ():
  main ()
  read_file = gzip.GzipFile (json_gz_filename, 'r')
  if read_file is not None:
      return read_file

def papers ():
  with gzip.open(open(), 'rt') as file: 
     for i, line in enumerate(file):
         print('\n')
         print("----File number %d---- " %i)
         if line.strip () in '[]': continue
         line = line.rstrip ().rstrip (',')
         yield json.loads (line)
         

if __name__ == '__main__': main (True)
