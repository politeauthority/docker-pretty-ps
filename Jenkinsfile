

def isImportantBranch() {
    return "${env.BRANCH_NAME}" == "master"
}

def reportFailure(error) {

    echo("Caught error:" + error)
    currentBuild.description="Error"

    // Notify slack, if appropriate
    if (isImportantBranch()) {
        // slackSend channel: SLACK_CHANNEL, color: "#FF0000", message: "Job failed attempting to run Scattershot. ${env.BUILD_URL}"
    } else {
        echo "Not notifying slack beacuse this isn't an important branch."
    }
}

def reportSuccess(clients, cycles, org) {
    // Sends a slack message reporting success if we're on the correct branch.
    currentBuild.description="Success"

    if (isImportantBranch()) {
        slackSend channel: SLACK_CHANNEL, color: "#008000", message: "Scattershot has completed. Ran ${clients} clients, ${cycles} cycles for org ${org} against staging. \n ${env.BUILD_URL}"
    } else {
        echo "Not notifying slack beacuse this isn't an important branch."
    }
}

label = "docker-pretty-ps-${UUID.randomUUID().toString()}"
podTemplate(
    label: label,
    cloud: "kubernetes",
    containers: 
        [
            containerTemplate(
                image: 'politeauthority/docker-pretty-ps:latest',
                name: 'docker-pretty-ps',
                ttyEnabled: true,
                command: 'tail -f /dev/null',
                envVars: [],
                alwaysPullImage: true
            )
        ],

    volumes: [
        hostPathVolume(hostPath: '/var/run/docker.sock', mountPath: '/var/run/docker.sock'),
    ]
) {
    node(label) {
        try {
            currentBuild.description = "Docker-Pretty-Ps Testing"
            // Stage One
            // Initialize terraform and create the Scattershot instance, which will also start Scattershot on boot
            stage('Running unit tests') {
                echo "Running unit tests"
                checkout scm
                container("docker-pretty-ps") {
                    ansiColor('gnome-terminal') {
                        sh """#!/usr/bin/env bash
                            pytest
                        """
                    }
                }
            }
            stage('Running flake8') {
                echo "Running flake8"
                checkout scm
                container("docker-pretty-ps") {
                    ansiColor('gnome-terminal') {
                        sh """#!/usr/bin/env bash
                            flake8
                        """
                    }
                }
            }

        // FlowInterruptedExceptions (at least those with a cause of UserInterruption) are
        // aborts via the UI of Jenkins.  We don't want to treat these as errors so we detect
        // them specifically and basically just halt processing.
        } catch(org.jenkinsci.plugins.workflow.steps.FlowInterruptedException fe) {

            wasUserInterruption = false
            for (item in fe.getCauses()) {
                if (item instanceof jenkins.model.CauseOfInterruption$UserInterruption) {
                    currentBuild.description=""
                    wasUserInterruption = true
                    break
                }
            }

            // Note: I haven't seen a FlowInterruptedException that _wasn't_ caused by
            // UserInterruption yet, but the exception documentation seems to suggest that there
            // are other possibilities.  We'll treat anything else as an error for now.
            if (!wasUserInterruption) {
                reportFailure(fe)
                throw fe
            }

        } catch(error) {
            reportFailure(error)
            throw error
        }
    }
}