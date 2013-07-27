#!/usr/bin/env python

__author__ = 'Sijis Aviles'

from optparse import OptionParser
import tempfile
import sh

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
    data['git_path'] = sh.which('git')
    data['tmp_path'] = tempfile.mkdtemp(prefix='puppetconf-', dir=data['tmp'])
    data['git_verbose'] = '-qb'

    # some sanity checking
    if data['repo'] == None:
        exit('Error: Repository must be defined.')

    print "------------------------------------------------------- Puppet-Sync"
    print " Branch: %s" % data['branch']
    print " Destination: %s" % data['dest']
    print " Repository: %s" % data['repo']
    print " Server: %s" % data['server']
    print "-------------------------------------------------------------------"

    sh.git.clone(data['repo'], data['tmp_path'])
    sh.cd(data['tmp_path'])
    sh.git.config('user.name', 'Git Sync Script')
    sh.git.config('user.email', 'root@git-sync')
    sh.git.checkout(data['git_verbose'], 'deploy', 'origin/%s' % data['branch'])

    if data['server']:
        data['executed'] = 'rsync -r --del --force %s/ %s:%s' % (data['tmp_path'], data['server'], data['dest_path'])
        sh.rsync('-r', '--del', '--force', '%s/' % data['tmp_path'], '%s:%s' % (data['server'], data['dest_path']))
    else:
        data['executed'] = 'mv %s %s' % (data['tmp_path'], data['dest_path'])
        sh.rm('-rf', data['dest_path'])
        sh.mv(data['tmp_path'], data['dest_path'])
        #sh.touch('%s/.sync-stamp' % data['dest_path'])

    if options.debug:
        data['git_verbose'] = '-b'
        print '..-:[ debug ]:-..'
        for opt in data:
            print '%s => %s' % (opt, data[opt])

    # cleanup
    sh.cd(data['tmp'])
    sh.rm('-rfv', data['tmp_path'])


if __name__ == '__main__':
    main()
