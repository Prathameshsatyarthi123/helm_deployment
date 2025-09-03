pipeline {
    agent any

    environment {
        AWS_DEFAULT_REGION = 'us-east-1'
        CLUSTER_NAME = 'my-eks-cluster'
        CHART_PATH = './charts/myservice'
        RELEASE_NAME = "myservice-${env.BRANCH_NAME}" // separate release per branch
        NAMESPACE = 'default'
    }

    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }

        stage('Configure AWS & EKS') {
            steps {
                withCredentials([
                    string(credentialsId: 'aws-access-key', variable: 'AWS_ACCESS_KEY_ID'),
                    string(credentialsId: 'aws-secret-key', variable: 'AWS_SECRET_ACCESS_KEY')
                ]) {
                    sh '''
                    aws eks update-kubeconfig --region $AWS_DEFAULT_REGION --name $CLUSTER_NAME
                    kubectl get nodes
                    '''
                }
            }
        }

        stage('Deploy with Helm') {
            steps {
                sh '''
                helm upgrade --install $RELEASE_NAME $CHART_PATH --namespace $NAMESPACE --create-namespace
                '''
            }
        }
    }
}
