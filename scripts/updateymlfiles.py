#!/usr/bin/python
from commonScripts import *
from optparse import OptionParser
import yaml



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
    parser.add_option("--chartName", dest="chartName",
                      help="Chart name [OPTIONAL]")
    parser.add_option("--chartRepo", dest="chartRepo",
                      help="Chart repository uri [OPTIONAL]")
    parser.add_option("--chartVersion", dest="chartVersion",
                      help="Chart version [OPTIONAL]")
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
        exit_and_fail("The --appChartDir or --repoRoot parameter is not set. Both are mandatory")
    else:
        if not os.path.exists(options.gitRepoRoot) or not os.path.isdir(options.gitRepoRoot):
            exit_and_fail("gitRepoRoot directory %s does not exists" % options.gitRepoRoot)
        if not os.path.exists(options.gitRepoRoot + "/" + options.appChartDir) or not os.path.isdir(
                options.gitRepoRoot + "/" + options.appChartDir):
            exit_and_fail("appChartDir directory %s/%s does not exists" % (options.gitRepoRoot, options.appChartDir))
    if options.chartName and not options.chartVersion:
        parser.print_help()
        exit_and_fail("If --chartName set, --chartVersion and --chartRepo should be also set")
    if not options.helmCommand:
        exit_and_fail("The --helm parameter is not set.")


    # Initialize variables
    chartYaml = "%s/Chart.yaml" % options.appChartDir;
    requirementsYaml = "%s/requirements.yaml" % options.appChartDir;

    testAppChartYaml = "%s/%s" % (options.gitRepoRoot, chartYaml);
    testAppRequirementsYaml = "%s/%s" % (options.gitRepoRoot, requirementsYaml);

    # Read Chart.yaml
    chart = read_yaml(testAppChartYaml)
    # Read requirements.yaml
    requirements = read_yaml(testAppRequirementsYaml)

    if options.chartName:
        # Update Chart.yaml
        newVersion = step_version(chart["version"]);
        chart["version"] = newVersion;
        print("# Updated Chart.yaml with new version: " + newVersion)
        yaml.dump(chart, sys.stdout, default_flow_style=False)
        print("")
        if not options.dryRun:
            write_doc_to_yaml(chart, testAppChartYaml)

        # Update requirements.yaml
        update_requirements(requirements, options.chartName, options.chartVersion, options.chartRepo)
        print("# Updated requirements.yaml with " + options.chartName + " " + options.chartVersion)
        yaml.dump(requirements, sys.stdout, default_flow_style=False)
        print("")
        if not options.dryRun:
            write_doc_to_yaml(requirements, testAppRequirementsYaml)

    # Add dependecy repos
    for req in requirements['dependencies']:
        print req
        run_cmd(options.workspace, "%s repo add %s %s" % (options.helmCommand, req['name'], req['repository']))

    run_cmd(options.workspace, "%s dependency update %s/%s" % (options.helmCommand, options.gitRepoRoot, options.appChartDir))
