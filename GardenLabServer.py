#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

# GardenLab Database and Webserver Script
# Quentin McDonald
# May 2017


# Based heavily on simple Python webserver script by Joe Linoff:
# LICENSE
#   Copyright (c) 2015 Joe Linoff
#   
#   Permission is hereby granted, free of charge, to any person obtaining a copy
#   of this software and associated documentation files (the "Software"), to deal
#   in the Software without restriction, including without limitation the rights
#   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#   copies of the Software, and to permit persons to whom the Software is
#   furnished to do so, subject to the following conditions:
#   
#   The above copyright notice and this permission notice shall be included in
#   all copies or substantial portions of the Software.
#   
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#   THE SOFTWARE.

# VERSIONS
#   1.0  initial release
#   1.1  replace req with self in request handler, add favicon
#   1.2  added directory listings, added --no-dirlist, fixed plain text displays, logging level control, daemonize


VERSION = '1.2'

import argparse
import BaseHTTPServer
import cgi
import logging
import os
import sys
import datetime

import GardenLabDB
import GardenLabPlot

last_db_update = datetime.datetime.now()



def make_request_handler_class(opts):
    '''
    Factory to make the request handler and add arguments to it.

    It exists to allow the handler to access the opts.path variable
    locally.
    '''
    class MyRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
        '''
        Factory generated request handler class that contain
        additional class variables.
        '''
        m_opts = opts
        

        def do_HEAD(self):
            '''
            Handle a HEAD request.
            '''
            logging.debug('HEADER %s' % (self.path))
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

        def info(self):
            '''
            Display some useful server information.

            http://127.0.0.1:8080/info
            '''
            self.wfile.write('<html>')
            self.wfile.write('  <head>')
            self.wfile.write('    <title>GardenLab Server Info</title>')
            self.wfile.write('  </head>')
            self.wfile.write('  <body>')
            self.wfile.write('    <table>')
            self.wfile.write('      <tbody>')
            self.wfile.write('        <tr>')
            self.wfile.write('          <td>Client_address:</td>')
            self.wfile.write('          <td>%r</td>' % (repr(self.client_address)))
            self.wfile.write('        </tr>')
            self.wfile.write('        <tr>')
            self.wfile.write('          <td>Command:</td>')
            self.wfile.write('          <td>%r</td>' % (repr(self.command)))
            self.wfile.write('        </tr>')
            self.wfile.write('        <tr>')
            self.wfile.write('          <td>Headers</td>')
            self.wfile.write('          <td>%r</td>' % (repr(self.headers)))
            self.wfile.write('        </tr>')
            self.wfile.write('        <tr>')
            self.wfile.write('          <td>Path</td>')
            self.wfile.write('          <td>%r</td>' % (repr(self.path)))
            self.wfile.write('        </tr>')
            self.wfile.write('        <tr>')
            self.wfile.write('          <td>Server_version</td>')
            self.wfile.write('          <td>%r</td>' % (repr(self.server_version)))
            self.wfile.write('        </tr>')
            self.wfile.write('        <tr>')
            self.wfile.write('          <td>Sys_version</td>')
            self.wfile.write('          <td>%r</td>' % (repr(self.sys_version)))
            self.wfile.write('        </tr>')
            self.wfile.write('        <tr>')
            self.wfile.write('          <td>Database records:</td>')
            self.wfile.write('          <td>%d</td>' % (
                GardenLabDB.count_records()))
            self.wfile.write('        </tr>')
            self.wfile.write('        </tr>')
            self.wfile.write('        <tr>')
            self.wfile.write('          <td>Last add:</td>')
            self.wfile.write('          <td>%s</td>' % (
                str(last_db_update)))
            self.wfile.write('        </tr>')
            self.wfile.write('      </tbody>')
            self.wfile.write('    </table>')
            self.wfile.write('  </body>')
            self.wfile.write('</html>')

        def do_GET(self):
            '''
            Handle a GET request.
            '''
            logging.debug('GET %s' % (self.path))

            # Parse out the arguments.
            # The arguments follow a '?' in the URL. Here is an example:
            #   http://example.com?arg1=val1
            args = {}
            idx = self.path.find('?')
            if idx >= 0:
                rpath = self.path[:idx]
                args = cgi.parse_qs(self.path[idx+1:])
            else:
                rpath = self.path

            # Print out logging information about the path and args.
            if 'content-type' in self.headers:
                ctype, _ = cgi.parse_header(self.headers['content-type'])
                logging.debug('TYPE %s' % (ctype))

            logging.debug('PATH %s' % (rpath))
            logging.debug('ARGS %d' % (len(args)))
            if len(args):
                i = 0
                for key in sorted(args):
                    logging.debug('ARG[%d] %s=%s' % (i, key, args[key]))
                    i += 1

          
            self.send_response(200)  # OK
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.info()
    


        def do_POST(self):
            '''
            Handle POST requests.
            '''

            global last_db_update
            
            logging.debug('POST %s' % (self.path))

            # CITATION: http://stackoverflow.com/questions/4233218/python-basehttprequesthandler-post-variables
            ctype, pdict = cgi.parse_header(self.headers['content-type'])
            if ctype == 'multipart/form-data':
                postvars = cgi.parse_multipart(self.rfile, pdict)
            elif ctype == 'application/x-www-form-urlencoded':
                length = int(self.headers['content-length'])
                postvars = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
            else:
                postvars = {}

            # Print out logging information about the path and args.
            logging.debug('TYPE %s' % (ctype))
            logging.debug('PATH %s' % (self.path))
            logging.debug('ARGS %d' % (len(postvars)))
            if len(postvars):
                i = 0
                for key in sorted(postvars):
                    logging.debug('ARG[%d] %s=%s' % (i, key, postvars[key]))
                    i += 1

            GardenLabDB.insert_data_from_dict( postvars )
            logging.debug("Inserted values in Database")
            last_db_update = datetime.datetime.now()

            GardenLabPlot.generate_all_latest_plots()

            # Tell the browser everything is okay and that there is
            # HTML to display.
            self.send_response(200)  # OK


    return MyRequestHandler


def err(msg):
    '''
    Report an error message and exit.
    '''
    print('ERROR: %s' % (msg))
    sys.exit(1)


def getopts():
    '''
    Get the command line options.
    '''

    # Get the help from the module documentation.
    this = os.path.basename(sys.argv[0])
    description = 'GardenLab webserver'
    epilog = ' '
    rawd = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(formatter_class=rawd,
                                     description=description,
                                     epilog=epilog)

    parser.add_argument('-d', '--daemonize',
                        action='store',
                        type=str,
                        default='.',
                        metavar='DIR',
                        help='daemonize this process, store the 3 run files (.log, .err, .pid) in DIR (default "%(default)s")')

    parser.add_argument('-H', '--host',
                        action='store',
                        type=str,
                        default='localhost',
                        help='hostname, default=%(default)s')

    parser.add_argument('-l', '--level',
                        action='store',
                        type=str,
                        default='info',
                        choices=['notset', 'debug', 'info', 'warning', 'error', 'critical',],
                        help='define the logging level, the default is %(default)s')

    parser.add_argument('--no-dirlist',
                        action='store_true',
                        help='disable directory listings')

    parser.add_argument('-p', '--port',
                        action='store',
                        type=int,
                        default=8080,
                        help='port, default=%(default)s')

    parser.add_argument('-r', '--rootdir',
                        action='store',
                        type=str,
                        default=os.path.abspath('.'),
                        help='web directory root that contains the HTML/CSS/JS files %(default)s')

    parser.add_argument('-v', '--verbose',
                        action='count',
                        help='level of verbosity')

    parser.add_argument('-V', '--version',
                        action='version',
                        version='%(prog)s - v' + VERSION)

    opts = parser.parse_args()
    opts.rootdir = os.path.abspath(opts.rootdir)
    if not os.path.isdir(opts.rootdir):
        err('Root directory does not exist: ' + opts.rootdir)
    if opts.port < 1 or opts.port > 65535:
        err('Port is out of range [1..65535]: %d' % (opts.port))
    return opts


def httpd(opts):
    '''
    HTTP server
    '''
    RequestHandlerClass = make_request_handler_class(opts)
    server = BaseHTTPServer.HTTPServer((opts.host, opts.port), RequestHandlerClass)
 
    logging.info('Server starting %s:%s (level=%s)' % (opts.host, opts.port, opts.level))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
    logging.info('Server stopping %s:%s' % (opts.host, opts.port))


def get_logging_level(opts):
    '''
    Get the logging levels specified on the command line.
    The level can only be set once.
    '''
    if opts.level == 'notset':
        return logging.NOTSET
    elif opts.level == 'debug':
        return logging.DEBUG
    elif opts.level == 'info':
        return logging.INFO
    elif opts.level == 'warning':
        return logging.WARNING
    elif opts.level == 'error':
        return logging.ERROR
    elif opts.level == 'critical':
        return logging.CRITICAL


def daemonize(opts):
    '''
    Daemonize this process.

    CITATION: http://stackoverflow.com/questions/115974/what-would-be-the-simplest-way-to-daemonize-a-python-script-in-linux
    '''
    if os.path.exists(opts.daemonize) is False:
        err('directory does not exist: ' + opts.daemonize)

    if os.path.isdir(opts.daemonize) is False:
        err('not a directory: ' + opts.daemonize)

    bname = 'webserver-%s-%d' % (opts.host, opts.port)
    outfile = os.path.abspath(os.path.join(opts.daemonize, bname + '.log'))
    errfile = os.path.abspath(os.path.join(opts.daemonize, bname + '.err'))
    pidfile = os.path.abspath(os.path.join(opts.daemonize, bname + '.pid'))

    if os.path.exists(pidfile):
        err('pid file exists, cannot continue: ' + pidfile)
    if os.path.exists(outfile):
        os.unlink(outfile)
    if os.path.exists(errfile):
        os.unlink(errfile)

    if os.fork():
        sys.exit(0)  # exit the parent

    os.umask(0)
    os.setsid()
    if os.fork():
        sys.exit(0)  # exit the parent

    print('daemon pid %d' % (os.getpid()))

    sys.stdout.flush()
    sys.stderr.flush()

    stdin = file('/dev/null', 'r')
    stdout = file(outfile, 'a+')
    stderr = file(errfile, 'a+', 0)

    os.dup2(stdin.fileno(), sys.stdin.fileno())
    os.dup2(stdout.fileno(), sys.stdout.fileno())
    os.dup2(stderr.fileno(), sys.stderr.fileno())

    with open(pidfile, 'w') as ofp:
        ofp.write('%i' % (os.getpid()))


def main():
    ''' main entry '''
    opts = getopts()
    if opts.daemonize:
        daemonize(opts)
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=get_logging_level(opts))
    

    httpd(opts)


if __name__ == '__main__':
    main()  # this allows library functionality
