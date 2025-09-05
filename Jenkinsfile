pipeline {
    agent any

    environment {
        AWS_DEFAULT_REGION = 'us-east-1'
        CLUSTER_NAME       = 'my-eks-cluster'
        AWS_ACCOUNT_ID     = '242201311297'
        DOCKER_REGISTRY    = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com"
        IMAGE_TAG          = "${BUILD_NUMBER}"
    }

    stages {
        stage('Build & Push microservice-one') {
            steps {
                withCredentials([
                    string(credentialsId: 'aws-access-key', variable: 'AWS_ACCESS_KEY_ID'),
                    string(credentialsId: 'aws-secret-key', variable: 'AWS_SECRET_ACCESS_KEY')
                ]) {
                    sh """
                        echo 🔨 Building Docker image for microservice-one...
                        docker build -t $DOCKER_REGISTRY/microservice-one:$IMAGE_TAG -f ./ping_svc/Dockerfile.ping ./ping_svc
                        docker push $DOCKER_REGISTRY/microservice-one:$IMAGE_TAG
                    """
                }
            }
        }

        stage('Build & Push microservice-two') {
            steps {
                withCredentials([
                    string(credentialsId: 'aws-access-key', variable: 'AWS_ACCESS_KEY_ID'),
                    string(credentialsId: 'aws-secret-key', variable: 'AWS_SECRET_ACCESS_KEY')
                ]) {
                    sh """
                        echo 🔨 Building Docker image for microservice-two...
                        docker build -t $DOCKER_REGISTRY/microservice-two:$IMAGE_TAG -f ./metric_svc/Dockerfile.metrics ./metric_svc
                        docker push $DOCKER_REGISTRY/microservice-two:$IMAGE_TAG
                    """
                }
            }
        }

        stage('Deploy to EKS with Helm') {
            steps {
                withCredentials([
                    string(credentialsId: 'aws-access-key', variable: 'AWS_ACCESS_KEY_ID'),
                    string(credentialsId: 'aws-secret-key', variable: 'AWS_SECRET_ACCESS_KEY')
                ]) {
                    sh """
                        aws eks update-kubeconfig --region $AWS_DEFAULT_REGION --name $CLUSTER_NAME
                        echo 🚀 Deploying Helm chart with both updated images...
                        helm upgrade --install myservice-main . \
                          --namespace dev --create-namespace \
                          --set ping_svc.image.repository=$DOCKER_REGISTRY/microservice-one \
                          --set ping_svc.image.tag=$IMAGE_TAG \
                          --set metric_svc.image.repository=$DOCKER_REGISTRY/microservice-two \
                          --set metric_svc.image.tag=$IMAGE_TAG
                    """
                }
            }
        }

        stage('Manual Rollback Approval') {
            steps {
                script {
                    catchError(buildResult: 'SUCCESS', stageResult: 'SUCCESS') {
                        timeout(time: 10, unit: 'MINUTES') {
                            withCredentials([
                                string(credentialsId: 'aws-access-key', variable: 'AWS_ACCESS_KEY_ID'),
                                string(credentialsId: 'aws-secret-key', variable: 'AWS_SECRET_ACCESS_KEY')
                            ]) {
                                sh "aws eks update-kubeconfig --region $AWS_DEFAULT_REGION --name $CLUSTER_NAME"

                                // Fetch available revisions dynamically
                                def revisions = sh(
                                    script: "helm history myservice-main --namespace dev --output json | jq -r '.[].revision'",
                                    returnStdout: true
                                ).trim().split("\\n")

                                def userInput = input(
                                    id: 'RollbackInput',
                                    message: 'Select revision to rollback (or wait 10min to skip)',
                                    parameters: [
                                        choice(
                                            name: 'REVISION',
                                            choices: revisions.join('\\n'),
                                            description: 'Pick a Helm revision to rollback to'
                                        )
                                    ]
                                )

                                echo "⚠️ Rolling back Helm release to revision ${userInput}..."
                                sh "helm rollback myservice-main ${userInput} --namespace dev"
                            }
                        }
                    }
                }
            }
        }
    }

    post {
        success {
            echo "✅ Pipeline completed successfully!"
        }
        failure {
            echo "❌ Pipeline failed!"
        }
    }
}


