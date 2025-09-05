pipeline {
    agent any

    environment {
        CLUSTER_NAME       = "my-eks-cluster"
        AWS_DEFAULT_REGION = "us-east-1"
        ECR_URI            = "242201311297.dkr.ecr.us-east-1.amazonaws.com"
        IMAGE_TAG          = "${BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build & Push microservice-one') {
            steps {
                withCredentials([
                    string(credentialsId: 'aws-access-key', variable: 'AWS_ACCESS_KEY_ID'),
                    string(credentialsId: 'aws-secret-key', variable: 'AWS_SECRET_ACCESS_KEY')
                ]) {
                    sh '''
                        aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin $ECR_URI
                        echo "🔨 Building Docker image for microservice-one..."
                        docker build -t $ECR_URI/microservice-one:$IMAGE_TAG -f ./ping_svc/Dockerfile.ping ./ping_svc
                        docker push $ECR_URI/microservice-one:$IMAGE_TAG
                    '''
                }
            }
        }

        stage('Build & Push microservice-two') {
            steps {
                withCredentials([
                    string(credentialsId: 'aws-access-key', variable: 'AWS_ACCESS_KEY_ID'),
                    string(credentialsId: 'aws-secret-key', variable: 'AWS_SECRET_ACCESS_KEY')
                ]) {
                    sh '''
                        echo "🔨 Building Docker image for microservice-two..."
                        docker build -t $ECR_URI/microservice-two:$IMAGE_TAG -f ./metric_svc/Dockerfile.metrics ./metric_svc
                        docker push $ECR_URI/microservice-two:$IMAGE_TAG
                    '''
                }
            }
        }

        stage('Deploy to EKS with Helm') {
            steps {
                withCredentials([
                    string(credentialsId: 'aws-access-key', variable: 'AWS_ACCESS_KEY_ID'),
                    string(credentialsId: 'aws-secret-key', variable: 'AWS_SECRET_ACCESS_KEY')
                ]) {
                    sh '''
                        aws eks update-kubeconfig --region $AWS_DEFAULT_REGION --name $CLUSTER_NAME
                        echo "🚀 Deploying Helm chart with both updated images..."
                        helm upgrade --install myservice-main . \
                          --namespace dev --create-namespace \
                          --set ping_svc.image.repository=$ECR_URI/microservice-one \
                          --set ping_svc.image.tag=$IMAGE_TAG \
                          --set metric_svc.image.repository=$ECR_URI/microservice-two \
                          --set metric_svc.image.tag=$IMAGE_TAG
                    '''
                }
            }
        }
    }
}
