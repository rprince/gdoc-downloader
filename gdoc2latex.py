# Author: Rob Miller
# Other contributors: Jeff Bigham, Philip Guo

from HTMLParser import HTMLParser, HTMLParseError
from htmlentitydefs import name2codepoint
import re, json, sys, urllib, urllib2
import getpass
from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth

def main():
    if len(sys.argv) < 2:
        print >>sys.stderr, """
usage: python gdoc2latex.py <URL or .gdoc filename>

     example: python gdoc2latex.py https://docs.google.com/document/d/1yEyXxtEeQ5_E7PibjYpofPC6kP4jMG-EieKhwkK7oQE/edit
     example: python gdoc2latex.py test.gdoc
     example for private documents: python gdoc2latex.py https://docs.google.com/document/d/1yEyXxtEeQ5_E7PibjYpofPC6kP4jMG-EieKhwkK7oQE/edit USERNAME
"""
        sys.exit(1)

    if len(sys.argv) == 2:
        html = fetchGoogleDoc(sys.argv[1])
    else:
        password=getpass.getpass()
        html = fetchGoogleDoc(sys.argv[1],sys.argv[2],password)
    text = html_to_text(html)
    latex = unicode_to_latex(text)
    sys.stdout.write(latex)


def download_to_file(gdoc_url, out_filename, email='', passwd=''):
    '''Downloads gdoc_url to your hard disk as out_filename'''
    print 'Downloading', gdoc_url
    html = fetchGoogleDoc(gdoc_url, email, passwd)
    with open(out_filename+".html", 'w') as f:
        f.write(html)
    text = html_to_text(html)
    latex = unicode_to_latex(text)
    with open(out_filename, 'w') as f:
        f.write(latex)
    print 'Wrote', gdoc_url, 'to', out_filename

	
def get_auth_token(email, password, source, service="wise"):
        url = "https://www.google.com/accounts/ClientLogin"
        params = {
                "Email": email, "Passwd": password,
                "service": service,
                "accountType": "HOSTED_OR_GOOGLE",
                "source": source
        }
        req = urllib2.Request(url, urllib.urlencode(params))
        return re.findall(r"Auth=(.*)", urllib2.urlopen(req).read())[0]


def fetchGoogleDoc(urlOrGdocFile,email='',password=''):
    """
    Downloads a Google Doc identified either by a URL or by a local Google Drive .gdoc file
    and returns its contents as a text file.
    Requires the Google Doc to be readable by anyone with the link (Share, Anyone who has the link can view).
    """
    # find the doc url
    if urlOrGdocFile.startswith("https://"):
        url = urlOrGdocFile
    elif urlOrGdocFile.endswith(".gdoc"):
        filename = urlOrGdocFile
        f = open(filename, "r")
        content = json.load(f)
        f.close()
        url = content["url"]
    else:
        raise Exception(str(urlOrGdocFile) + " not a google doc URL or .gdoc filename")
    # pull out the document id
    try:
        docId = re.search("/document/d/([^/]+)/", url).group(1)
    except Exception:
        raise Exception("can't find a google document ID in " + str(urlOrGdocFile))
    # construct an export URL
    exportUrl = "https://docs.google.com/document/d/" + docId + "/export?format=html"

    # open a connection to it
    global gauth

    try:
        if gauth == None:
            gauth = GoogleAuth()
            gauth.LocalWebserverAuth()
        else:
            print "ALREADY HAVE AN AUTH"
    except NameError:
        gauth = GoogleAuth()
        gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)
    file = drive.CreateFile({'id': docId})
    print 'downloading "%s"' % file['title']
    # file.GetContentString('simulation.html', mimetype='text/html')
    file.FetchContent(mimetype='text/html')
    html = file.content.getvalue().decode('utf-8')
    
    return html

def html_to_text(html):
    """
    Given a piece of HTML, return the plain text it contains, as a unicode string.
    Throws away:
       - text from the <head> element
       - text in <style> and <script> elements
       - text in Google Doc sidebar comments
       - text before BEGIN_DOCUMENT string and after END_DOCUMENT string
       - section hyperlinks that Google Docs automatically generates
    Also translates entities and char refs into unicode characters.
    """
    html = re.sub(r'^.*?BEGIN_DOCUMENT', '', html, 1)
    html = re.sub(r'<a href="#cmnt_ref.{1,30}\[a\].*', '', html, 1) # for section hyperlinks
    html = re.sub(r'END_DOCUMENT.*', '', html, 1)

    # pre-format HTML tables for LaTeX

    parser = _HTMLToText()
    try:
        parser.feed(html)
        parser.close()
    except HTMLParseError:
        pass
    return parser.get_text()


class _HTMLToText(HTMLParser):
    """
    HTMLParser subclass that finds all the text in an html doc.
    Used by html_to_text.
    """
    def __init__(self):
        HTMLParser.__init__(self)
        self._buf = []
        self.hide_output_nesting_level = 0
        self.chapter_title_depth = 0

    def handle_starttag(self, tag, attrs):
        attrsDict = self.to_dict(attrs)
        if tag in ['script', 'style', 'head']:
            self.hide_output_nesting_level = 1
        elif tag == "a" and "name" in attrsDict and attrsDict["name"].startswith("cmnt_"):
            # found a Google Doc comment -- remove it
            self.hide_output_nesting_level = 1
        elif self.hide_output_nesting_level > 0:
            self.hide_output_nesting_level += 1
        if tag in ('p', 'br') and not self.at_start_of_line():
            self.append('\n')

        # Handle headings
        if tag == 'p':
            if self.chapter_title_depth > 0:
                self.chapter_title_depth += 1
            if "class" in attrsDict and "title" in attrsDict["class"].split():
                self.append('\n\chapter{')
                self.chapter_title_depth = 1
        if tag == 'h1':
            self.append('\n\section{')
        elif tag == 'h2':
            self.append('\n\subsection{')
        elif tag == 'h3':
            self.append('\n\subsubsection{')
        elif tag == 'h4':
            self.append('\n\paragraph{')

        # Handle lists
        if tag == 'ul':
            self.append('\\begin{itemize}\n')
        elif tag == 'ol':
            self.append('\\begin{enumerate}\n')
        elif tag == 'li':
            self.append('\item ')

        # Handle tables
        if tag == 'table':
            self.append('\\begin{tabular}{ |p{2cm}| p{2cm}| p{2cm}| p{2cm}| p{2cm}| p{2cm}| p{2cm}| p{2cm}| p{2cm}| p{2cm}| }\n')

    def handle_startendtag(self, tag, attrs):
        if tag == 'br':
            self.append('\n')

    def handle_endtag(self, tag):
        if tag == 'p':
            if self.chapter_title_depth == 1:
                self.append('}\n')
            if self.chapter_title_depth > 0:
                self.chapter_title_depth -= 1
            self.append('\n')

        # Handle headings
        if tag in ['h1','h2','h3','h4']:
            self.append('}\n')

        # Handle lists
        if tag == 'ul':
            self.append('\\end{itemize}\n')
        elif tag == 'ol':
            self.append('\\end{enumerate}\n')
        elif tag == 'li':
            self.append('\n')

        # Handle tables
        if tag == 'table':
            self.append('\\end{tabular}\n')
        elif tag == 'td':
            self.append(' & ')
        elif tag == 'tr':
            self.append('\\\\\n')

        if self.hide_output_nesting_level > 0:
            self.hide_output_nesting_level -= 1

    def handle_data(self, text):
        if text:
            self.append(re.sub(r'\s+', ' ', text))

    def handle_entityref(self, name):
        if name in name2codepoint:
            c = unichr(name2codepoint[name])
            self.append(c)

    def handle_charref(self, name):
        n = int(name[1:], 16) if name.startswith('x') else int(name)
        self.append(unichr(n))

    def append(self, str):
        if self.hide_output_nesting_level == 0:
            self._buf.append(str)

    def at_start_of_line(self):
        return len(self._buf) == 0 or self._buf[-1][-1] == '\n'

    def to_dict(self,attrs):
        dict = {}
        for (name,val) in attrs:
            dict[name] = val
        return dict

    def get_text(self):
        return re.sub(r' +', ' ', ''.join(self._buf))

def unicode_to_latex(text):
    """
    Converts unicode into Latex format: 
    primarily utf8, with some special characters converted to Latex syntax 
    """ 
    tr = [
        (u'\u2013', "--"),
        (u'\u2014', "---"),
        (u'\u2018', "`"),
        (u'\u2019', "'"),
        (u'\u201c', "``"),
        (u'\u201d', "''"),
        (u'\u2026', "..."),
        (u'\xa0', ' '), # no-break space
    ]
    for a, b in tr:
        text = text.replace(a, b)
    return text.encode("utf8")


if __name__ == "__main__":
    main()
