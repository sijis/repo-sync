#!/usr/bin/env python

__author__ = 'Sijis Aviles'

from optparse import OptionParser
from subprocess import Popen, PIPE
import tempfile
import shutil


def trans_branch(branch):
    t_branch = 'production'
    if branch != 'master':
        t_branch = branch
    return t_branch


def main():
    parser = OptionParser(version='%prog 0.1', description='Sync puppet git repo to a destination')
    parser.add_option('-b', '--branch', help='repo branch', metavar='BRANCH', dest='branch', default='master')
    parser.add_option('-t', '--tmp', help='temp directory location', metavar='DIR', dest='tmp', default='/tmp')
    parser.add_option('-d', '--destination', help='destination directory location', metavar='DIR', dest='dest', default='/etc/puppet/environments')
    parser.add_option('-r', '--repository', help='repository url', metavar='URL', dest='repo')
    parser.add_option('-p', '--passenger', help='Restart apache/passenger instead of puppetmaster', dest='passenger', action='store_true', default=False)
    parser.add_option('-s', '--server', help='Specify puppetmaster server', metavar='HOST', dest='server', default=None)
    parser.add_option('--debug', help='Enable debugging mode', dest='debug', action='store_true', default=False)
    parser.add_option('-v', '--verbose', help='enable verbosity', dest='verbose', action='store_true')
    (options, args) = parser.parse_args()

    #print args
    data = vars(options)
    data['dest_path'] = '%s/%s' % (data['dest'], trans_branch(data['branch']))
    t_stdout, t_stderr = Popen('which git', stdout=PIPE, shell=True).communicate()
    data['git_path'] = t_stdout.strip('\n')
    data['tmp_path'] = tempfile.mkdtemp(prefix='puppetconf-', dir=data['tmp'])
    shutil.rmtree(data['tmp_path'])
    if options.debug:
        for opt in data:
            print '%s => %s' % (opt, data[opt])

    print "----------------------------------------------------------------- Puppet-Sync"
    print " Branch: %s" % data['branch']
    print " Destination: %s" % data['dest']
    print " Repository: %s" % data['repo']
    print " Server: %s" % data['server']
    print "-----------------------------------------------------------------------------"


if __name__ == '__main__':
    main()
