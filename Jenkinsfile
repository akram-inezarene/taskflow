pipeline {
  agent {
    kubernetes {
      yaml '''
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: docker
    image: docker:29.9.2-dind
    securityContext:
      privileged: true
    volumeMounts:
    - name: docker-data
      mountPath: /var/lib/docker
  volumes:
  - name: docker-data
    emptyDir: {}
'''
    }
  }
  stages {
    stage('Image Docker') {
      steps {
        container('docker') {
          withCredentials([usernamePassword(credentialsId: 'dockerhub', usernameVariable: 'DH_USER', passwordVariable: 'DH_TOKEN')]) {
            sh '''
              until docker info > /dev/null 2>&1; do sleep 2; done
              echo "$DH_TOKEN" | docker login -u "$DH_USER" --password-stdin
              docker build -t "$DH_USER/taskflow:$BUILD_NUMBER" .
              docker push "$DH_USER/taskflow:$BUILD_NUMBER"
            '''
          }
        }
      }
    }
  }
}
