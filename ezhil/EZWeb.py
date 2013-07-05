#!/usr/bin/python
# -*- coding: utf-8 -*-
## 
## (C) 2013 Muthiah Annamalai,
## Licensed under GPL Version 3
## 
## Interpreter for Ezhil language on the web

## Ref: http://wiki.python.org/moin/BaseHttpServer

import time
from ezhil import EzhilFileExecuter, EzhilInterpExecuter
import BaseHTTPServer, tempfile
from os import unlink
import cgi

class EzhilOnTheWeb(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):        
        print str(self.headers)
        if self.path.find('/ezhil') >= 0:
            GETvars = cgi.parse_qs( self.path )
            print str(GETvars)
            if GETvars.has_key('prog'):
                program = "\n".join(GETvars['prog'])
            else:
                program = 'printf("Welcome to Ezhil! You can type a program and see its output here!")\n'
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.do_ezhil_execute( program )
        else: 
            self.send_error(404)
        return
    
    def do_ezhil_execute(self,program):
        # write the input program into a temporary file and execute the Ezhil Interpreter
        tmpf=tempfile.NamedTemporaryFile(suffix='.n',delete=False)
        tmpf.write(program)
        tmpf.close()
        
        print( "Source program" )
        print( open(tmpf.name).read() )
        print( "*"*60 )
        
        program_fmt = "\n".join(["<li>%s</li>"%(prog_line)  for line_no,prog_line in enumerate(program.split('\n'))]);

        # run the interpreter in a sandbox and capture the output hopefully
        try:
            failed = False
            #obj = EzhilFileExecuter( file_input = tmpf.name, redirectop = True )
            obj = EzhilInterpExecuter( file_input = tmpf.name, redirectop = True )
            progout = obj.get_output()            
            op = "<B>Succeeded Execution</B> for program <font color=\"blue\"><ol>%s</ol></font> as <br/> <font color=\"green\"><pre>%s</pre></font>"%(program_fmt,progout)
        except Exception as e:
            print str(e)
            failed = True
            op = "<B>FAILED Execution</B> for program <font color=\"blue\"><ol>%s</ol></font> with <font color=\"red\">error <pre>%s</pre> </font>"%(program_fmt,str(e))
        else:
            print "Output file"
            obj.get_output()
        
        # delete the temporary file
        unlink(tmpf.name)
        
        if failed:
            op = "<H2> Your program has some errors! Try correcting it and re-evaluate the code</H2><HR/><BR/>"+op
        else:
            op = "<H2> Your program executed correctly! Congratulations. </H2><HR/><BR/>"+op            
        
        self.wfile.write("<html> <head> <title>Ezhil interpreter</title> </head><body> %s </body></html>\n"%op)
        
        return op

HOST_NAME = "localhost"
PORT_NUMBER = 8080

if __name__ == "__main__":
    httpd = BaseHTTPServer.HTTPServer((HOST_NAME, PORT_NUMBER), EzhilOnTheWeb)
    print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)
