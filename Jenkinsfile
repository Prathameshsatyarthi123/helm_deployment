pipeline {
    agent any

    environment {
        CLUSTER_NAME       = "my-eks-cluster"
        AWS_DEFAULT_REGION = "us-east-1"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Configure AWS, EKS & Deploy with Helm') {
            steps {
                withCredentials([
                    string(credentialsId: 'aws-access-key', variable: 'AWS_ACCESS_KEY_ID'),
                    string(credentialsId: 'aws-secret-key', variable: 'AWS_SECRET_ACCESS_KEY')
                ]) {
                    sh '''
                        echo "🔑 Verifying AWS credentials..."
                        aws sts get-caller-identity

                        echo "⚙️ Updating kubeconfig for EKS..."
                        aws eks update-kubeconfig --region $AWS_DEFAULT_REGION --name $CLUSTER_NAME

                        echo "📦 Checking Kubernetes nodes..."
                        kubectl get nodes

                        echo "🚀 Deploying Helm chart..."
                        helm upgrade --install myservice-main . \
                            --namespace default --create-namespace
                    '''
                }
            }
        }
    }
}
