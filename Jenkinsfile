pipeline {
  agent any
  environment { KUBECONFIG = '/etc/rancher/k3s/k3s.yaml' }
  stages {
    stage('Build Docker image') {
      steps { sh 'docker build -t tikaa:$BUILD_NUMBER .' }
    }
    stage('Load image into Kubernetes') {
      steps { sh 'docker save tikaa:$BUILD_NUMBER | sudo /usr/local/bin/k3s ctr images import -' }
    }
    stage('Deploy to Kubernetes') {
      steps {
        sh '''
          sed "s|IMAGE_PLACEHOLDER|tikaa:$BUILD_NUMBER|" k8s/deployment.yaml | kubectl apply -f -
          kubectl rollout status deployment/tikaa --timeout=120s
        '''
      }
    }
  }
}
