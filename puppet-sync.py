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
    parser = OptionParser(version='%prog 0.1',
                          description='Sync puppet git repo to a destination')
    parser.add_option('-b', '--branch',
                      dest='branch', metavar='BRANCH',
                      default='master',
                      help='repo branch')
    parser.add_option('-t', '--tmp',
                      dest='tmp', metavar='DIR',
                      default='/tmp',
                      help='temp directory location')
    parser.add_option('-d', '--destination',
                      dest='dest', metavar='DIR',
                      default='/etc/puppet/environments',
                      help='destination directory location')
    parser.add_option('-r', '--repository',
                      dest='repo', metavar='URL',
                      help='repository url')
    parser.add_option('-a', '--action',
                      dest='action',
                      default=None,
                      help='Action to execute after sync')
    parser.add_option('-s', '--server',
                      dest='server', metavar='HOST',
                      default=None,
                      help='Specify puppetmaster server')
    parser.add_option('--debug',
                      dest='debug',
                      default=False, action='store_true',
                      help='Enable debugging mode')
    parser.add_option('-v', '--verbose',
                      dest='verbose',
                      action='store_true',
                      help='enable verbosity')
    (options, args) = parser.parse_args()

    #print args
    data = vars(options)
    data['dest_path'] = '%s/%s' % (data['dest'], trans_branch(data['branch']))
    data['git_path'] = sh.which('git')
    data['tmp_path'] = tempfile.mkdtemp(prefix='puppetconf-', dir=data['tmp'])
    data['git_verbose'] = '-qb'

    # some sanity checking
    if data['repo'] is None:
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
    sh.git.checkout(data['git_verbose'], 'deploy',
                    'origin/%s' % data['branch'])

    if data['server']:
        data['executed'] = \
            'rsync -r --del --force %s/ %s:%s' % \
            (data['tmp_path'], data['server'], data['dest_path'])
        sh.rsync('-r', '--del', '--force', '%s/' % data['tmp_path'],
                 '%s:%s' % (data['server'], data['dest_path']))
    else:
        data['executed'] = 'mv %s %s' % (data['tmp_path'], data['dest_path'])
        sh.rm('-rf', data['dest_path'])
        sh.mv(data['tmp_path'], data['dest_path'])
        #sh.touch('%s/.sync-stamp' % data['dest_path'])

    if data['action']:
        action = data['action'].split()
        if data['server']:
            sh.ssh('-t', '-o', 'StrictHostKeyChecking=no',
                   data['server'], action)
        else:
            sh.sudo(action)

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
