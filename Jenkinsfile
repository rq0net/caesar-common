// Jenkinsfile for Continuous Integration/Continuous Deployment pipeline

import groovy.json.JsonSlurper

// Define global variables
def testPrompt = false // Flag for testing confirmation prompt
def gcloudPrivateKey = "/.gcloud-config.json" // Path to Google Cloud Platform private key
def helmChart = "./django-daphne" // Path to Helm chart for main deployment
def helmCeleryChart = "." // Path to Helm chart for Celery deployment
def cause = currentBuild.getBuildCauses('hudson.model.Cause$UserIdCause')

// Pipeline definition
pipeline {
  // Define the agent for running pipeline stages
  agent {
    // Kubernetes pod configuration
    kubernetes {
      inheritFrom 'kaniko' // Inherit pod configuration from 'kaniko' template
    }
  }

  // Define environment variables
  environment {
    environment = credentials('environment') // Environment type (e.g., uat, prod)
    acrUrl = credentials('acr-url') // URL for Azure Container Registry
    project = "caesar-${environment}" // Project name with environment suffix
    appName = 'common' // Application name
    servicename = "${project}-${appName}" // Service name for helm release
    imageTag = "${acrUrl}/${project}/${appName}:${env.BUILD_NUMBER}" // Docker image tag
    webHook = credentials('discord-webhook') // Discord webhook for notifications
  }

  // Define pipeline stages
  stages {

    stage('Install Dependencies') { 
        steps {
          // Install any project dependencies
          echo  "Install Dependencies"
        }
    }

    // stage('Build Environment') { 
    //     steps {
    //       // Generate Kubernetes configuration files using Jinja2
    //       container(name: 'jinja2') {
    //         dir("chart") {
    //           sh 'jinja2 --format=json beat.yaml.j2 /.caesar-env.json -o beat.yaml'
    //           sh 'jinja2 --format=json env.yaml.j2 /.caesar-env.json -o env.yaml'
    //           sh 'jinja2 --format=json tgbot.yaml.j2 /.caesar-env.json -o tgbot.yaml'
    //           sh 'jinja2 --format=json worker-hipri.yaml.j2 /.caesar-env.json -o worker-hipri.yaml'
    //           sh 'jinja2 --format=json worker.yaml.j2 /.caesar-env.json -o worker.yaml'
    //         }
    //       }
    //     }
    // }

    stage('SonarQube analysis') {
      steps {
        // Perform static code analysis using SonarQube
        withSonarQubeEnv("qube.cwcdn.com") {
          script {
            def scannerHome = tool 'SonarScanner';
            sh "${scannerHome}/bin/sonar-scanner"
          }
        }
      }
    }

    // stage("Quality Gate"){
    //   steps {
    //     script {
    //       sleep time: 10, unit: 'SECONDS'

    //       def qg = null

    //       // Loop until quality gate is not null and status is not "PENDING"
    //       while (qg == null || qg.status == 'PENDING' || qg.status == 'IN_PROGRESS') {
    //           qg = waitForQualityGate()
    //           sleep 10  // Optional: Adding a short delay to avoid too frequent polling
    //       }
    //       if (qg.status != 'OK') {
    //         error "Pipeline aborted due to quality gate failure: ${qg.status}"
    //       }
    //     }
    //   }
    // }

    stage('GCLOUD Authentication') {
      steps {
        // Authenticate with Google Cloud Platform
        container(name: 'gcloud') {
          script {
            sh "gcloud auth activate-service-account --key-file=${gcloudPrivateKey}"
            sh "gcloud auth configure-docker" 
          }
        }
      }
    }

    stage('Build with Kaniko') {
      environment {
        // Set PATH to include Kaniko for building Docker images
        PATH = "/busybox:/kaniko:$PATH"
      }
      steps {
        // Build Docker image using Kaniko
        container(name: 'kaniko', shell: '/busybox/sh') {
          script {
            sh "executor -f ${env.WORKSPACE}/Dockerfile -c ${env.WORKSPACE} --skip-tls-verify --cache=true --destination='${imageTag}'"
          }
        }
      }
    }

    // stage('Deploy to K8s') {
    //   steps {
    //     // Deploy Helm charts to Kubernetes cluster
    //     container(name: 'helm', shell: '/bin/sh') {
    //       script {
    //         sh 'helm version'
            
    //         dir("chart") {
    //           script {
    //             sh "helm upgrade --install ${servicename} $helmChart -f ./env.yaml --set image.tag=${env.BUILD_NUMBER} --wait-for-jobs --wait"
    //             sh "helm upgrade --install ${servicename}-celery-worker $helmCeleryChart -f ./env.yaml -f ./worker.yaml --set image.tag=${env.BUILD_NUMBER} --wait-for-jobs --wait"
    //             sh "helm upgrade --install ${servicename}-celery-worker-hipri $helmCeleryChart -f ./env.yaml -f ./worker-hipri.yaml --set image.tag=${env.BUILD_NUMBER} --wait-for-jobs --wait"
    //             sh "helm upgrade --install ${servicename}-celery-beat $helmCeleryChart -f ./env.yaml -f ./beat.yaml --set image.tag=${env.BUILD_NUMBER} --wait-for-jobs --wait"
    //             sh "helm upgrade --install ${servicename}-tgbot $helmCeleryChart -f ./env.yaml -f ./tgbot.yaml --set image.tag=${env.BUILD_NUMBER} --wait-for-jobs --wait"
    //           } 
    //         }
    //       }
    //     }
    //   }
    // }

    // stage('Confirm') {
    //   steps {
    //     script {
    //       try {
    //         timeout(time: 1, unit: 'HOURS') { // change to a convenient timeout for you
    //           testPrompt = input(
    //               id: 'Test_Prompt', message: 'Have these changes been tested?', parameters: [
    //               [$class: 'BooleanParameterDefinition', defaultValue: false, description: '', name: 'Please confirm that all things are working']
    //               ])
    //         }
    //       } catch(err) { // input false
    //           def user = cause.userName
    //           userInput = false
    //           echo "Aborted by: [${user}]"
    //       }
    //     }
    //   }
    // }
  }

  // Post-build actions
  post {
    always {
      script {
        // Notify on completion of pipeline execution
        jobLink = "${env.BUILD_URL}"
      }
      echo 'Notification Trigger point.'
      discordSend description: "Project Pipeline for ${project} ${appName} \n Job Name : ${currentBuild.projectName} \n Job Status : ${currentBuild.currentResult} \n Triggered by: ${cause.userName}", footer: "", link: "${jobLink}", image: '', result: currentBuild.currentResult, scmWebUrl: '', thumbnail: '', title: "Caesar - ${appName}", webhookURL: "${webHook}"
    }
  }
}