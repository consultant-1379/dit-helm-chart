#!/usr/bin/python
import os
from optparse import OptionParser

from commonScripts import *

if __name__ == '__main__':
    """
    Creates a OptionParser with all necessary options.
    """
    parser = OptionParser()
    parser.add_option("-w", "--workspace", dest="workspace",
                      help="Path to workspace [MANDATORY]")
    parser.add_option("--appChartDir", dest="appChartDir",
                      help="Relative path to application chart directory in git repository (--gitRepoRoot) [MANDATORY]")
    parser.add_option("--repoRoot", dest="gitRepoRoot",
                      help="Path to test-app chart directory [MANDATORY]")
    parser.add_option("-d", "--dryRun", action="store_true", default=False, dest="dryRun",
                      help="DryRun [OPTIONAL]")
    (options, args) = parser.parse_args()
    if not options.workspace:
        parser.print_help()
        exit_and_fail("The -w, --workspace parameter is not set")
    else:
        if not os.path.exists(options.workspace) or not os.path.isdir(options.workspace):
            exit_and_fail("Workspace directory %s does not exists" % options.workspace)
    if not options.appChartDir or not options.gitRepoRoot:
        parser.print_help()
        exit_and_fail("The --appChartDir or --gitRepoRoot parameter is not set. Both are mandatory")
    else:
        if not os.path.exists(options.gitRepoRoot) or not os.path.isdir(options.gitRepoRoot):
            exit_and_fail("repoRoot directory %s does not exists" % options.gitRepoRoot)
        if not os.path.exists(options.gitRepoRoot + "/" + options.appChartDir) or not os.path.isdir(
                options.gitRepoRoot + "/" + options.appChartDir):
            exit_and_fail("appChartDir directory %s/%s does not exists" % (options.gitRepoRoot, options.appChartDir))

    # Initialize variables
    appChartDir = options.gitRepoRoot + "/" + options.appChartDir
    chartYaml = "%s/Chart.yaml" % options.appChartDir;
    requirementsYaml = "%s/requirements.yaml" % options.appChartDir;

    testAppChartYaml = "%s/%s" % (options.gitRepoRoot, chartYaml);

    # Read Chart.yaml
    chart = read_yaml(testAppChartYaml)

    # Push back to git
    run_cmd(options.gitRepoRoot, "git add %s %s" % (chartYaml, requirementsYaml), options.dryRun)
    run_cmd(options.gitRepoRoot, "git commit -m 'Automatic new version %s'" % (
        chart["version"]), options.dryRun)
    run_cmd(options.gitRepoRoot, "git push --force origin HEAD:master", options.dryRun)
    run_cmd(options.gitRepoRoot, "git tag -a %s -m 'Automatic new version %s'" % (
        chart["version"], chart["version"]), options.dryRun)
