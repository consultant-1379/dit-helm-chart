
import os
import subprocess
import sys
import yaml

cmd_pushd = 'pushd %s > /dev/null'
cmd_popd = 'popd > /dev/null'


# cmd_git_get_previous_file = 'git show HEAD~1:%s > %s'


def exit_and_fail(msg):
    if msg:
        log_error(msg)
    sys.exit(1)


def log_info(msg):
    print "INFO: " + msg


def log_warn(msg):
    print "WARN: " + msg


def log_error(msg):
    print "ERROR: " + msg

def run_cmd(root, cmd, dryRun = False):

    if dryRun:
        print "DryRun: " + cmd
        return ""
    else:
        print("Execute: " + cmd)

        try:
            output = subprocess.check_output(cmd, cwd=root, shell=True)
        except subprocess.CalledProcessError as e:
            print e.output
            exit_and_fail("Command execution failed: %s. Output: %s" % (cmd, e.output) )

        print("--OUT--")
        print(output)
        print("--END--\n")

        return output;

# def run_cmd(root, cmd, dryRun=False):
#     if dryRun:
#         print "DryRun: " + cmd
#         return ""
#     else:
#         print("Execute: " + cmd)
#         _cmd_pushd = cmd_pushd % root
#         command = "%s && %s && %s" % (_cmd_pushd, cmd, cmd_popd)
#         output = commands.getstatusoutput(command)
#         print("--OUT--")
#         print(output[1])
#         print("--END--\n")
#         if output[0] != 0:
#             exit_and_fail("Command execution failed: " + cmd)
#         return output[1];


def read_yaml(yamlFile):
    if not os.path.exists(yamlFile):
        exit_and_fail("Could not find %s" % yamlFile)
    with open(yamlFile, 'r') as stream:
        try:
            doc = yaml.load(stream)
        except yaml.Error as exc:
            print(exc)
    return doc


def write_doc_to_yaml(doc, yamlFile):
    with open(yamlFile, 'w') as stream:
        yaml.dump(doc, stream, default_flow_style=False);


def step_version(version):
    taglist = version.split(".")
    if len(taglist) == 3:
        digit = int(taglist[2])
        digit = digit + 1
        new_post_fix = str(digit)
        return "%s.%s.%s" % (taglist[0], taglist[1], new_post_fix)
    else:
        exit_and_fail("Wrong version format: %s. Should be '0.0.0' format" % version)


def update_requirements(requirements, chartName, chartVersion, chartRepo):
    found = False
    for dep in requirements["dependencies"]:
        if dep["name"] == chartName:
            found = True
            dep["version"] = chartVersion
            if chartRepo:
                dep["repository"] = chartRepo
    if not found:
        exit_and_fail("Could not find " + chartName + " in dependencies")


def get_dependency_repos(requirements):
    repos = {}
    for dep in requirements["dependencies"]:
        name = dep["name"]
        repo = dep["repository"]
        if not repo in repos:
            repos[repo] = name
    return repos


def compare_versions(remote, local):
    if not remote or remote == "results":
        return True;
    if remote == local:
        exit_and_fail("Local %s and remote %s version are the same" % (local, remote))
    taglistR = remote.split(".")
    taglistL = local.split(".")
    if len(taglistR) == 3 and len(taglistL) == 3:
        rMajor = int(taglistR[0])
        rMinor = int(taglistR[1])
        rSmall = int(taglistR[2])
        lMajor = int(taglistL[0])
        lMinor = int(taglistL[1])
        lSmall = int(taglistL[2])
        if lMajor < rMajor:
            exit_and_fail("Local %s version is lower than remote %s" % (local, remote))
        elif lMajor == rMajor:
            if lMinor < rMinor:
                exit_and_fail("Local %s version is lower than remote %s" % (local, remote))
            elif lMinor == rMinor:
                if lSmall < rSmall:
                    exit_and_fail("Local %s version is lower than remote %s" % (local, remote))
    else:
        exit_and_fail("Local '%s' or remote '%s' version has wrong format" % (local, remote))


def compare_prev_versions(prevVersion, currentVersion):
    if prevVersion == currentVersion:
        exit_and_fail("Current %s and previous %s version are the same" % (currentVersion, prevVersion))
    taglistR = prevVersion.split(".")
    taglistL = currentVersion.split(".")
    if len(taglistR) == 3 and len(taglistL) == 3:
        rMajor = int(taglistR[0])
        rMinor = int(taglistR[1])
        rSmall = int(taglistR[2])
        lMajor = int(taglistL[0])
        lMinor = int(taglistL[1])
        lSmall = int(taglistL[2])
        if lMajor < rMajor:
            exit_and_fail("Current %s version is lower than previous %s" % (currentVersion, prevVersion))
        elif lMajor == rMajor:
            if lMinor < rMinor:
                exit_and_fail("Current %s version is lower than previous %s" % (currentVersion, prevVersion))
            elif lMinor == rMinor:
                if lSmall < rSmall:
                    exit_and_fail("Current %s version is lower than previous %s" % (currentVersion, prevVersion))
    else:
        exit_and_fail("Current '%s' or remote '%s' version has wrong previous" % (currentVersion, prevVersion))
