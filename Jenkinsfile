pipeline {
    agent any

    parameters {
        string(name: 'RUN_DATE', defaultValue: '', description: 'Run date in YYYY-MM-DD. Leave empty to use today.')
    }

    environment {
        IMAGE_NAME = "zoomcar-etl"
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
                    
                    timeout(time: 15, unit: 'MINUTES') {
                        sh """
                            docker run --rm \\
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
                        timeout(time: 10, unit: 'MINUTES') {
                            echo "Starting Data Quality Dashboard generation..."
                            sh """
                                docker run --rm \\
                                  -v zoomcar-ivy-cache:/root/.ivy2 \\
                                  -v "\$PWD":/app \\
                                  -w /app \\
                                  ${IMAGE_NAME} \\
                                  python -m src.data_quality_dashboard
                            """
                            echo "Dashboard generation completed successfully"
                        }
                    } catch (org.jenkinsci.plugins.workflow.steps.FlowInterruptedException e) {
                        echo "WARNING: Dashboard generation timed out after 10 minutes"
                        echo "Continuing with pipeline..."
                        currentBuild.result = 'UNSTABLE'
                    } catch (Exception e) {
                        echo "ERROR: Dashboard generation failed - ${e.message}"
                        echo "Continuing with pipeline..."
                        currentBuild.result = 'UNSTABLE'
                    }
                }
            }
        }

        stage('Archive Results') {
            when {
                expression { fileExists('data/final') }
            }
            steps {
                script {
                    def artifacts = []
                    if (fileExists('data/final')) {
                        artifacts << 'data/final/**/*'
                    }
                    if (fileExists('reports/data_quality_dashboard.html')) {
                        artifacts << 'reports/data_quality_dashboard.html'
                    }
                    if (artifacts) {
                        archiveArtifacts artifacts: artifacts.join(','), fingerprint: true, allowEmptyArchive: true
                    }
                }
            }
        }
    }

    post {
        success {
            echo "✅ Pipeline completed successfully!"
        }
        unstable {
            echo "⚠️ Pipeline completed with warnings (dashboard may have failed)"
        }
        failure {
            echo "❌ Pipeline failed!"
        }
        always {
            cleanWs()
        }
    }
}
