pipeline {
  agent {
    kubernetes {
      yaml '''
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: python
    image: python:3.13.18-slim
    command: ["cat"]
    tty: true
  - name: scanner
    image: sonarsource/sonar-scanner-cli:12.3
    command: ["cat"]
    tty: true
  - name: docker
    image: docker:29.9.2-dind
    securityContext:
      privileged: true
    volumeMounts:
    - name: docker-data
      mountPath: /var/lib/docker
  - name: helm
    image: alpine/helm:4.3.1
    command: ["cat"]
    tty: true
  volumes:
  - name: docker-data
    emptyDir: {}
'''
    }
  }
  triggers {
    pollSCM('H/2 * * * *')
  }
  environment {
    DOCKERHUB = credentials('dockerhub')
  }
  stages {
    stage('Tests') {
      steps {
        container('python') {
          sh 'pip install -q -r requirements.txt && python -m pytest --cov=. --cov-report=xml'
        }
      }
    }
    stage('SonarQube') {
      steps {
        container('scanner') {
          withSonarQubeEnv('sonarqube') {
            sh 'sonar-scanner -Dsonar.projectKey=taskflow -Dsonar.sources=main.py -Dsonar.tests=test_main.py -Dsonar.python.coverage.reportPaths=coverage.xml -Dsonar.scm.disabled=true -Dsonar.host.url=$SONAR_HOST_URL -Dsonar.token=$SONAR_AUTH_TOKEN'
          }
        }
        timeout(time: 5, unit: 'MINUTES') {
          waitForQualityGate abortPipeline: true
        }
      }
    }
    stage('Build image') {
      steps {
        container('docker') {
          sh '''
            until docker info > /dev/null 2>&1; do sleep 2; done
            echo "$DOCKERHUB_PSW" | docker login -u "$DOCKERHUB_USR" --password-stdin
            docker build -t "$DOCKERHUB_USR/taskflow:$BUILD_NUMBER" .
          '''
        }
      }
    }
    stage('Scan Trivy') {
      steps {
        container('docker') {
          sh 'docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy:0.76.1 image --exit-code 1 --severity CRITICAL --ignore-unfixed "$DOCKERHUB_USR/taskflow:$BUILD_NUMBER"'
        }
      }
    }
    stage('Push') {
      steps {
        container('docker') {
          sh 'docker push "$DOCKERHUB_USR/taskflow:$BUILD_NUMBER"'
        }
      }
    }
    stage('Deploy staging') {
      steps {
        container('helm') {
          sh 'helm upgrade taskflow chart/taskflow -n taskflow-staging -f chart/taskflow/values-staging.yaml --set image.repository=$DOCKERHUB_USR/taskflow --set image.tag=$BUILD_NUMBER --wait --timeout 3m'
        }
      }
    }
    stage('Validation') {
      steps {
        timeout(time: 30, unit: 'MINUTES') {
          input message: 'Deployer en production ?', ok: 'Deployer'
        }
      }
    }
    stage('Deploy prod') {
      steps {
        container('helm') {
          sh 'helm upgrade taskflow chart/taskflow -n taskflow-prod -f chart/taskflow/values-prod.yaml --set image.repository=$DOCKERHUB_USR/taskflow --set image.tag=$BUILD_NUMBER --wait --timeout 3m'
        }
      }
    }
  }
}
