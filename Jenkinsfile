pipeline {
    agent any

    parameters {
        string(name: 'RUN_DATE', defaultValue: '', description: 'Run date in YYYY-MM-DD. Leave empty to use today.')
    }

    environment {
        IMAGE_NAME = "zoomcar-etl"
        DOCKER_MEMORY = "4g"
        DOCKER_CPUS = "2"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    sh "docker build -t ${IMAGE_NAME} ."
                }
            }
        }

        stage('Run ETL') {
            steps {
                script {
                    def runDate = params.RUN_DATE?.trim()
                    if (runDate?.contains("=")) {
                        runDate = runDate.tokenize("=").last().trim()
                    }
                    def runDateArg = runDate ? "--run-date ${runDate}" : ""
                    
                    timeout(time: 20, unit: 'MINUTES') {
                        sh """
                            docker run --rm \\
                              --memory=${DOCKER_MEMORY} \\
                              --cpus=${DOCKER_CPUS} \\
                              -v zoomcar-ivy-cache:/root/.ivy2 \\
                              -v "\$PWD":/app \\
                              -w /app \\
                              ${IMAGE_NAME} \\
                              python -m src.main_pipeline ${runDateArg}
                        """
                    }
                }
            }
        }

        stage('Data Quality & Dashboard') {
            steps {
                script {
                    try {
                        timeout(time: 20, unit: 'MINUTES') {
                            echo "Starting Data Quality Dashboard generation..."
                            sh """
                                docker run --rm \\
                                  --memory=${DOCKER_MEMORY} \\
                                  --cpus=${DOCKER_CPUS} \\
                                  -v zoomcar-ivy-cache:/root/.ivy2 \\
                                  -v "\$PWD":/app \\
                                  -w /app \\
                                  ${IMAGE_NAME} \\
                                  python -m src.data_quality_dashboard
                            """
                            echo "✅ Dashboard generation completed successfully"
                        }
                    } catch (org.jenkinsci.plugins.workflow.steps.FlowInterruptedException e) {
                        echo "⚠️ WARNING: Dashboard generation timed out after 20 minutes"
                        echo "This may indicate performance issues. Check logs for bottlenecks."
                        echo "Continuing with pipeline..."
                        currentBuild.result = 'UNSTABLE'
                    } catch (Exception e) {
                        echo "❌ ERROR: Dashboard generation failed - ${e.message}"
                        echo "Stack trace: ${e}"
                        echo "Continuing with pipeline..."
                        currentBuild.result = 'UNSTABLE'
                    }
                }
            }
        }

        stage('Archive Results') {
            steps {
                script {
                    def artifacts = []
                    
                    if (fileExists('data/final')) {
                        echo "Found final data directory"
                        artifacts << 'data/final/**/*'
                    }
                    
                    if (fileExists('reports/data_quality_dashboard.html')) {
                        echo "Found dashboard report"
                        artifacts << 'reports/data_quality_dashboard.html'
                    }
                    
                    if (fileExists('logs')) {
                        echo "Found logs directory"
                        artifacts << 'logs/**/*.log'
                    }
                    
                    if (artifacts) {
                        archiveArtifacts artifacts: artifacts.join(','), 
                                       fingerprint: true, 
                                       allowEmptyArchive: true,
                                       onlyIfSuccessful: false
                    } else {
                        echo "⚠️ No artifacts found to archive"
                    }
                }
            }
        }
    }

    post {
        success {
            echo "✅ Pipeline completed successfully!"
            echo "All stages executed without errors"
        }
        unstable {
            echo "⚠️ Pipeline completed with warnings"
            echo "Dashboard generation may have failed or timed out"
            echo "Check the logs for more details"
        }
        failure {
            echo "❌ Pipeline failed!"
            echo "Check the stage logs to identify the issue"
        }
        always {
            echo "Cleaning up workspace..."
            cleanWs()
        }
    }
}