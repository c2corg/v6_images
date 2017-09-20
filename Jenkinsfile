#!groovy
@Library('c2c-pipeline-library')
import static com.camptocamp.utils.*

@NonCPS
def getMajorRelease() {
    def numMajorReleaseMatcher = (env.BRANCH_NAME =~ /^release_(\d+)$/)
    if (numMajorReleaseMatcher.matches()) return "v${numMajorReleaseMatcher[0][1]}"

    def relMajorReleaseMatcher = (env.BRANCH_NAME =~ /^release_(int|prod)$/)
    relMajorReleaseMatcher.matches() ? relMajorReleaseMatcher[0][1] : ''
}
def majorRelease = getMajorRelease()

env.TRAVIS = "true"

// We don't want to publish the same branch twice at the same time.
dockerBuild {
    stage('Update docker') {
        checkout scm
        sh 'make pull'
        sh 'git clean -f -d'
    }
    stage('Build') {
        checkout scm
        sh 'make build'
    }
    stage('Test') {
        checkout scm
        lock("acceptance-${env.NODE_NAME}") {  //only one acceptance test at a time on a machine
            sh 'make test-inside'
        }
    }

    def CURRENT_TAG = sh(returnStdout: true, script: "git fetch --tags && git tag -l --points-at HEAD | tail -1").trim()
    if (CURRENT_TAG != "") {
        if (CURRENT_TAG ==~ /^v\d+(?:\.\d+)*(-\d+)?$/) {
            parts = CURRENT_TAG.tokenize('.-')
            tags = []
            // if the tag is 1.2.3-4, puts two values in tags: ['v1.2', 'v1.2.3', 'v1.2.3.4']
            // the major version is managed later another way
            for (int i=2; i<=parts.size(); ++i) {
                curTag = ""
                for (int j = 0; j < i; ++j) {
                    if (j > 0) curTag += '.'
                    curTag += parts[j]
                }
                tags << curTag
            }
        } else {
            tags = [CURRENT_TAG]
        }


        stage("publish ${tags} on docker hub") {
            withCredentials([[$class          : 'UsernamePasswordMultiBinding', credentialsId: 'dockerhub',
                              usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD']]) {
                sh 'docker login -u "$USERNAME" -p "$PASSWORD"'
                for (String tag: tags) {
                    sh "docker tag c2corg/v6_images:latest camptocamp/saccas_suissealpine_photo:${tag}"
                    sh "docker push camptocamp/saccas_suissealpine_photo:${tag}"
                }
                sh 'rm -rf ~/.docker*'
            }
        }
    }

    if (env.BRANCH_NAME == 'master') {
        stage("publish latest on docker hub") {
            withCredentials([[$class          : 'UsernamePasswordMultiBinding', credentialsId: 'dockerhub',
                              usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD']]) {
                sh 'docker login -u "$USERNAME" -p "$PASSWORD"'
                sh "docker tag c2corg/v6_images:latest camptocamp/saccas_suissealpine_photo:latest"
                sh 'docker push camptocamp/saccas_suissealpine_photo:latest'
                sh 'rm -rf ~/.docker*'
            }
        }
    }

    if (majorRelease != '') {
        stage("publish ${majorRelease} on docker hub") {
            checkout scm
            setCronTrigger('H H(0-8) * * *')
            withCredentials([[$class          : 'UsernamePasswordMultiBinding', credentialsId: 'dockerhub',
                              usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD']]) {
                sh 'docker login -u "$USERNAME" -p "$PASSWORD"'
                sh "docker tag c2corg/v6_images:latest camptocamp/saccas_suissealpine_photo:${majorRelease}"
                sh "docker push camptocamp/saccas_suissealpine_photo:${majorRelease}"
                sh 'rm -rf ~/.docker*'
            }
        }
    }
}
