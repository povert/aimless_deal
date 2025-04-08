# -*- coding: utf-8 -*-
import re
import svnutil.parser
import svnutil.objects


def svn_lastest_version(svn_url):
    return svnutil.parser.get_latest_version(svn_url)


def svn_log(svn_url, version_start, version_end):
    return svnutil.parser.get_patch_by_version(svn_url, version_start, version_end)


def get_jobid_from_commit(commit_message):
    match = re.search(r'@T:.(\d+)', commit_message)
    if not match:
        return 0
    return int(match.group(1))


def create_svnfile(filename):
    return svnutil.objects.SVNFile(filename)
