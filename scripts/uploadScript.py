#!/usr/bin/python
import os
from optparse import OptionParser

from commonScripts import *


DEFAULT_APP_HELM_REPO="https://arm.rnd.ki.sw.ericsson.se/artifactory/proj-adp-helm-dev-generic-local/cd/sandbox/dit/baseline"
DEFAULT_ARMUSER="adpauto"
DEFAULT_ARMTOKEN="AKCp5Zkxbnwu5eezdN5AaY7SbZUx1rwEPfdohB9mJ38Zt6BUap4H7e8smvxCGz6JGpWSWH3kJ"


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
    parser.add_option("--appHelmRepo", dest="appHelmRepo", default=DEFAULT_APP_HELM_REPO,
                      help="Path to test-app chart directory [OPTIONAL]")
    parser.add_option("--armUserName", dest="armUserName", default=DEFAULT_ARMUSER,
                      help="User name in ARM [OPTIONAL]")
    parser.add_option("--armUserToken", dest="armUserToken", default=DEFAULT_ARMTOKEN,
                      help="User token in ARM [OPTIONAL]")
    # parser.add_option("--chartName", dest="chartName",
    #                   help="Chart name [OPTIONAL]")
    # parser.add_option("--chartRepo", dest="chartRepo",
    #                   help="Chart repository uri [OPTIONAL]")
    # parser.add_option("--chartVersion", dest="chartVersion",
    #                   help="Chart version [OPTIONAL]")
    # parser.add_option("--imageName", dest="imageName",
    #                   help="The name of the image. E.g.: filebeat [OPTIONAL]")
    # parser.add_option("--imageRepo", dest="imageRepo",
    #                   help="The repository path of the image. E.g.: armdocker.rnd.ericsson.se/proj-pigs [OPTIONAL]")
    # parser.add_option("--imageVersion", dest="imageVersion",
    #                   help="The version of the image. E.g.: 2.2.0 [OPTIONAL]")
    parser.add_option("-d", "--dryRun", action="store_true", default=False, dest="dryRun",
                      help="DryRun [OPTIONAL]")
    parser.add_option("--helm", dest="helmCommand",
                      help="Helm command [MANDATORY]")
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
    # if options.chartName and not options.chartVersion:
    #     parser.print_help()
    #     exit_and_fail("If --chartName set, --chartVersion and --chartRepo should be also set")
    # if options.imageName and not options.imageVersion:
    #     parser.print_help()
    #     exit_and_fail("If --imageName set, --imageVersion and --imageRepo should be also set")
    if not options.helmCommand:
        exit_and_fail("The --helm parameter is not set.")


    # Initialize variables
    appChartDir = options.gitRepoRoot + "/" + options.appChartDir
    chartYaml = "%s/Chart.yaml" % options.appChartDir;

    testAppChartYaml = "%s/%s" % (options.gitRepoRoot, chartYaml);

    # Read Chart.yaml
    chart = read_yaml(testAppChartYaml)

    # Create chart package
    chartPackageName = "%s-%s.tgz" % (chart["name"], chart["version"]);
    chartPackagePath = "%s/%s" % (options.workspace, chartPackageName);
    if os.path.exists(chartPackagePath):
        os.remove(chartPackagePath)

    # Create helm package
    run_cmd(options.workspace,
            "%s package --destination %s %s" % (options.helmCommand, options.workspace, appChartDir));

    # Fetch last index.yaml
    run_cmd(options.workspace, "curl -k -u %s:%s -X GET \"%s/index.yaml\" -o %s/index.yaml" % (
        options.armUserName, options.armUserToken, options.appHelmRepo, options.workspace))
    # Generate new index.yaml
    run_cmd(options.workspace,
            "%s repo index --merge %s/index.yaml --url %s %s" % (
                options.helmCommand, options.workspace, options.appHelmRepo, options.workspace))
    # if options.chartName:
    #     # Push back to git
    #     run_cmd(options.gitRepoRoot, "git add %s %s %s" % (chartYaml, requirementsYaml, valuesYaml), options.dryRun)
    #     run_cmd(options.gitRepoRoot, "git commit -m 'Automatic new version %s due to %s %s'" % (
    #         chart["version"], options.chartName, options.chartVersion), options.dryRun)
    #     run_cmd(options.gitRepoRoot, "git push --force origin HEAD:master", options.dryRun)
    #     run_cmd(options.gitRepoRoot, "git tag -a %s -m 'Automatic new version %s due to %s %s'" % (
    #         chart["version"], chart["version"], options.chartName, options.chartVersion), options.dryRun)
    # else:
    #     run_cmd(options.gitRepoRoot,
    #             "git tag -a %s -m 'Automatic new version %s'" % (chart["version"], chart["version"]),
    #             options.dryRun)
    # run_cmd(options.gitRepoRoot, "git push --force origin %s" % (chart["version"]), options.dryRun)

    # Upload to helm repository

    # Upload new chart package
    run_cmd(options.workspace, "curl -k -u %s:%s -X PUT \"%s/%s\" -T %s" % (
        options.armUserName, options.armUserToken, options.appHelmRepo, chartPackageName, chartPackagePath),
            options.dryRun)
    # Upload new index.yaml
    run_cmd(options.workspace, "curl -k -u %s:%s -X PUT \"%s/index.yaml\" -T index.yaml" % (
        options.armUserName, options.armUserToken, options.appHelmRepo), options.dryRun)
