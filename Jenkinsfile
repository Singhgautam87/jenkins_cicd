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
                    def runDateArg = params.RUN_DATE ? "--run-date ${params.RUN_DATE}" : ""
                    sh """
                        docker run --rm \\
                          -v "\$PWD":/app \\
                          -w /app \\
                          ${IMAGE_NAME} \\
                          python -m src.main_pipeline ${runDateArg}
                    """
                }
            }
        }

        stage('Data Quality & Dashboard') {
            steps {
                script {
                    sh """
                        docker run --rm \\
                          -v "\$PWD":/app \\
                          -w /app \\
                          ${IMAGE_NAME} \\
                          python -m src.data_quality_dashboard
                    """
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
                        archiveArtifacts artifacts: artifacts.join(','), fingerprint: true
                    }
                }
            }
        }
    }

    post {
        always {
            cleanWs()
        }
    }
}

