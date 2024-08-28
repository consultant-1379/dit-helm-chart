pipeline {
    agent {
        node {
            label 'eso_slave'
        }
    }

    parameters {
        string(name: 'CHART_NAME', defaultValue: '')
        string(name: 'CHART_VERSION', defaultValue: '')
        string(name: 'CHART_REPO', defaultValue: '')
    }

    environment {
        GIT_CMD = "docker run --rm -v ${env.WORKSPACE}:/git alpine/git"
        HELM_CMD = "docker run --rm -v ${env.WORKSPACE}/.kube/config:/root/.kube/config -v ${env.WORKSPACE}/helm-home:/root/.helm -v ${env.WORKSPACE}:${env.WORKSPACE} linkyard/docker-helm:2.7.2"
    }

    stages {
        stage('Clean') {
            steps {
                sh '${GIT_CMD} clean -xdff'
            }
        }

        stage('Inject Kubernetes Configuration File') {
            steps {
                configFileProvider([configFile(fileId: 'kube.config.icesat', targetLocation: "${env.WORKSPACE}/.kube/")]) {
                }
            }
        }

        stage('Prepare Helm') {
            steps {
                sh 'mkdir helm-home'
                sh '${HELM_CMD} init --client-only'
                sh '${HELM_CMD} repo add baseline-repo https://arm.rnd.ki.sw.ericsson.se/artifactory/proj-adp-helm-dev-generic-local/cd/sandbox/dit/baseline'
                sh '${HELM_CMD} repo update'
            }
        }

        stage('Initial Install Last Good Version of Baseline Chart') {
           steps {
              sh '${HELM_CMD} upgrade --install --wait dit-baseline baseline-repo/dit --namespace dit-staging'
            }
        }

        stage('Create Updated Chart Locally') {
            steps {
                sh "python scripts/updateymlfiles.py -w ${env.WORKSPACE} --repoRoot=${env.WORKSPACE}/charts --appChartDir=dit --chartName=${CHART_NAME} --chartRepo=${CHART_REPO} --chartVersion=${CHART_VERSION} --helm='${HELM_CMD}'"
            }
        }

        stage('Upgrade to Updated Chart') {
            steps {
                sh "${HELM_CMD} upgrade --wait dit-baseline ${env.WORKSPACE}/charts/dit"
            }
        }

        stage('Final Integration Tests') {
            steps {
                sh 'echo Tests Go Here'
            }
        }

        stage('Commit Changes in Baseline Repo') {
            when {
                expression { params.CHART_NAME != "" }
            }
            steps {
                sh "python scripts/commit.py -w ${env.WORKSPACE} --repoRoot=${env.WORKSPACE}/charts --appChartDir=dit"
            }
        }

        stage('Upload Chart to ARM') {
            when {
                expression { params.CHART_NAME != "" }
            }
            steps {
                sh "python scripts/uploadScript.py -w ${env.WORKSPACE} --repoRoot=${env.WORKSPACE}/charts --appChartDir=dit --helm='${HELM_CMD}'"
            }
        }
    }
}
