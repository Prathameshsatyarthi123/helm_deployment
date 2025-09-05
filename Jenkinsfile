pipeline {
    agent any

    environment {
        AWS_DEFAULT_REGION = "us-east-1"
        ECR_REGISTRY       = "242201311297.dkr.ecr.us-east-1.amazonaws.com"
        CLUSTER_NAME       = "my-eks-cluster"
        HELM_RELEASE       = "myservice-main"
        HELM_NAMESPACE     = "dev"
    }

    stages {
        stage('Build & Push microservice-one') {
            steps {
                withCredentials([
                    string(credentialsId: 'aws-access-key', variable: 'AWS_ACCESS_KEY_ID'),
                    string(credentialsId: 'aws-secret-key', variable: 'AWS_SECRET_ACCESS_KEY')
                ]) {
                    script {
                        def IMAGE_TAG = env.BUILD_NUMBER
                        echo "🔨 Building Docker image for microservice-one..."
                        sh """
                            docker build -t $ECR_REGISTRY/microservice-one:${IMAGE_TAG} -f ./ping_svc/Dockerfile.ping ./ping_svc
                            docker push $ECR_REGISTRY/microservice-one:${IMAGE_TAG}
                        """
                    }
                }
            }
        }

        stage('Build & Push microservice-two') {
            steps {
                withCredentials([
                    string(credentialsId: 'aws-access-key', variable: 'AWS_ACCESS_KEY_ID'),
                    string(credentialsId: 'aws-secret-key', variable: 'AWS_SECRET_ACCESS_KEY')
                ]) {
                    script {
                        def IMAGE_TAG = env.BUILD_NUMBER
                        echo "🔨 Building Docker image for microservice-two..."
                        sh """
                            docker build -t $ECR_REGISTRY/microservice-two:${IMAGE_TAG} -f ./metric_svc/Dockerfile.metrics ./metric_svc
                            docker push $ECR_REGISTRY/microservice-two:${IMAGE_TAG}
                        """
                    }
                }
            }
        }

        stage('Deploy to EKS with Helm') {
            steps {
                withCredentials([
                    string(credentialsId: 'aws-access-key', variable: 'AWS_ACCESS_KEY_ID'),
                    string(credentialsId: 'aws-secret-key', variable: 'AWS_SECRET_ACCESS_KEY')
                ]) {
                    script {
                        def IMAGE_TAG = env.BUILD_NUMBER
                        sh "aws eks update-kubeconfig --region $AWS_DEFAULT_REGION --name $CLUSTER_NAME"

                        echo "🚀 Deploying Helm chart with both updated images..."
                        sh """
                            helm upgrade --install $HELM_RELEASE . --namespace $HELM_NAMESPACE --create-namespace \
                                --set ping_svc.image.repository=$ECR_REGISTRY/microservice-one \
                                --set ping_svc.image.tag=${IMAGE_TAG} \
                                --set metric_svc.image.repository=$ECR_REGISTRY/microservice-two \
                                --set metric_svc.image.tag=${IMAGE_TAG}
                        """
                    }
                }
            }
        }

        stage('Manual Rollback Approval') {
            steps {
                script {
                    timeout(time: 10, unit: 'MINUTES') {
                        withCredentials([
                            string(credentialsId: 'aws-access-key', variable: 'AWS_ACCESS_KEY_ID'),
                            string(credentialsId: 'aws-secret-key', variable: 'AWS_SECRET_ACCESS_KEY')
                        ]) {
                            sh "aws eks update-kubeconfig --region $AWS_DEFAULT_REGION --name $CLUSTER_NAME"

                            // Get available helm revisions
                            def revisions = sh(
                                script: "helm history $HELM_RELEASE --namespace $HELM_NAMESPACE --output json | jq -r '.[].revision'",
                                returnStdout: true
                            ).trim().split("\n")

                            // Show dropdown for rollback selection
                            def userInput = input(
                                id: 'RollbackInput',
                                message: 'Do you want to rollback? Select revision:',
                                parameters: [
                                    choice(name: 'REVISION', choices: revisions.join('\n'), description: 'Pick a Helm revision to rollback to')
                                ]
                            )

                            echo "⚠️ Rolling back Helm release to revision ${userInput}..."
                            sh "helm rollback $HELM_RELEASE ${userInput} --namespace $HELM_NAMESPACE"
                        }
                    }
                }
            }
        }
    }
}


