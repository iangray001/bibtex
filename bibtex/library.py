import bibtexparser
from bibtexparser.bparser import BibTexParser
import re, sys, logging, os

from django.db.models import Q
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile


def parse_bibstring(bibstring):
	parser = BibTexParser()
	parser.ignore_nonstandard_types = False
	"""
	The \n is added to the bibstring because it appears that the final entry is not 
	correctly parsed if there is no trailing newline.
	"""
	return bibtexparser.loads(bibstring + "\n", parser)

def get_entry_bibtex_data(bibstring, data):
	db = parse_bibstring(bibstring)
	if len(db.entries) != 1:
		#Some parse error
		return None
	try:
		return db.entries[0][data]
	except KeyError:
		#Key does not exist
		return None


def validate_bibtex(bibstring):
	db = parse_bibstring(bibstring)
	if len(db.entries) != 1: 
		return "Your bibtex entry did not parse correctly."
	entry = db.entries[0]
	
	if not 'id' in entry: return "Your Bibtex did not include a key."
	if not 'title' in entry: return "Your Bibtex did not include a title field."
	if not 'author' in entry: return "Your Bibtex did not include an author field."
	if not 'year' in entry: return "Your Bibtex did not include a year field."

	yearstr = entry['year']
	try:
		year = int(yearstr)
	except ValueError:
		return "Your year field was not a valid year (e.g. 2001, 2014)"

	#No problems
	return None


def write_file(uploadedfile, origfilename):
	"""
	Write the file into MEDIA_ROOT
	Will check if there already is a file with that name, and if so, add _x onto the end of the name
	(but before the extension), where x is a positive integer.
	"""
	try:
		name, ext = os.path.splitext(origfilename)
		if default_storage.exists(name + ext):
			add = 1
			while default_storage.exists(name + "_" + str(add) + ext):
				add = add + 1
			outfname = name + "_" + str(add) + ext
		else:
			outfname = name + ext

		path = default_storage.save(outfname, ContentFile(uploadedfile.read()))
		print path
		return path
	except Exception as e:
		print str(e.message)
		#logger = logging.getLogger(__name__)
		#logger.error(str(e))
		return None


def get_username():
	return "iang"


def normalize_query(query_string,
                    findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    normspace=re.compile(r'\s{2,}').sub):
    ''' Splits the query string in invidual keywords, getting rid of unecessary spaces
        and grouping quoted words together.
        Example:
        >>> normalize_query('  some random  words "with   quotes  " and   spaces')
        ['some', 'random', 'words', 'with quotes', 'and', 'spaces']
    '''
    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)] 



def strip_braces(text):
	'''
	Removes curly braces { and } from a string, unless those braces are escaped with
	a preceeding backslash: \{ \}
	The unholy regex uses negative lookbehind.
	'''
	return re.compile(r'(?<!\\)\{|(?<!\\)\}', flags=re.UNICODE).sub("", text)



def get_query(query_string, search_fields):
    ''' Returns a query, that is a combination of Q objects. That combination
        aims to search keywords within a model by testing the given search fields.
    
    '''
    query = None # Query to search for every search term        
    terms = normalize_query(query_string)
    for term in terms:
        or_query = None # Query to search for a given term in each field
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query
