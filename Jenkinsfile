pipeline {
    agent any

    parameters {
        string(name: 'RUN_DATE', defaultValue: '', description: 'Reference date in YYYY-MM-DD. Leave empty to use today.')
        choice(name: 'PIPELINE_MODE', choices: ['realtime', 'batch'], description: 'Pipeline mode: realtime (Kafka+PostgreSQL) or batch (file-based)')
    }

    environment {
        IMAGE_NAME = "zoomcar-etl"
        DOCKER_MEMORY = "4g"
        DOCKER_CPUS = "2"
        COMPOSE_PROJECT_NAME = "zoomcar-pipeline"
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

        stage('Start Infrastructure') {
            when {
                expression { params.PIPELINE_MODE == 'realtime' }
            }
            steps {
                script {
                    echo "🚀 Starting Kafka + PostgreSQL infrastructure..."
                    sh """
                        docker-compose up -d
                        sleep 20
                    """
                    
                    echo "📊 Creating Kafka topic..."
                    sh """
                        docker-compose exec -T kafka kafka-topics --create \\
                          --bootstrap-server localhost:9092 \\
                          --topic zoomcar-raw-events \\
                          --partitions 3 \\
                          --replication-factor 1 \\
                          --if-not-exists || true
                    """
                    
                    echo "💾 Initializing PostgreSQL schema..."
                    sh """
                        docker run --rm \\
                          --network ${COMPOSE_PROJECT_NAME}_zoomcar-network \\
                          -v "\$PWD":/app \\
                          -w /app \\
                          ${IMAGE_NAME} \\
                          python -m src.config.database
                    """
                }
            }
        }

        stage('Send Test Data to Kafka') {
            when {
                expression { params.PIPELINE_MODE == 'realtime' }
            }
            steps {
                script {
                    echo "📤 Sending test data to Kafka..."
                    def runDate = params.RUN_DATE?.trim() ?: new Date().format('yyyy-MM-dd')
                    def dateStr = runDate.replaceAll('-', '')
                    def jsonFile = "data/raw/zoom_car_events_${dateStr}.json"
                    
                    if (fileExists(jsonFile)) {
                        sh """
                            docker run --rm \\
                              --network ${COMPOSE_PROJECT_NAME}_zoomcar-network \\
                              -v "\$PWD":/app \\
                              -w /app \\
                              -e KAFKA_BOOTSTRAP_SERVERS=kafka:9092 \\
                              ${IMAGE_NAME} \\
                              python -m src.kafka.producer ${jsonFile}
                        """
                    } else {
                        echo "⚠️ Test data file not found: ${jsonFile}"
                        echo "Skipping data ingestion. Pipeline will process any existing Kafka messages."
                    }
                }
            }
        }

        stage('Run Real-time ETL') {
            when {
                expression { params.PIPELINE_MODE == 'realtime' }
            }
            steps {
                script {
                    def runDate = params.RUN_DATE?.trim()
                    if (runDate?.contains("=")) {
                        runDate = runDate.tokenize("=").last().trim()
                    }
                    def runDateArg = runDate ? "--run-date ${runDate}" : ""
                    
                    timeout(time: 30, unit: 'MINUTES') {
                        sh """
                            docker run --rm \\
                              --memory=${DOCKER_MEMORY} \\
                              --cpus=${DOCKER_CPUS} \\
                              --network ${COMPOSE_PROJECT_NAME}_zoomcar-network \\
                              -v zoomcar-ivy-cache:/root/.ivy2 \\
                              -v "\$PWD":/app \\
                              -w /app \\
                              -e KAFKA_BOOTSTRAP_SERVERS=kafka:9092 \\
                              -e POSTGRES_HOST=postgres \\
                              ${IMAGE_NAME} \\
                              python -m src.realtime_pipeline ${runDateArg}
                        """
                    }
                }
            }
        }

        stage('Run Batch ETL') {
            when {
                expression { params.PIPELINE_MODE == 'batch' }
            }
            steps {
                script {
                    def runDate = params.RUN_DATE?.trim()
                    if (runDate?.contains("=")) {
                        runDate = runDate.tokenize("=").last().trim()
                    }
                    def runDateArg = runDate ? "--run-date ${runDate}" : ""
                    
                    timeout(time: 30, unit: 'MINUTES') {
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
                        timeout(time: 40, unit: 'MINUTES') {
                            echo "📊 Generating Data Quality Dashboard..."
                            
                            def dockerCmd = """
                                docker run --rm \\
                                  --memory=${DOCKER_MEMORY} \\
                                  --cpus=${DOCKER_CPUS} \\
                                  -v zoomcar-ivy-cache:/root/.ivy2 \\
                                  -v "\$PWD":/app \\
                                  -w /app \\
                                  ${IMAGE_NAME} \\
                                  python -m src.data_quality_dashboard
                            """
                            
                            if (params.PIPELINE_MODE == 'realtime') {
                                dockerCmd = """
                                    docker run --rm \\
                                      --memory=${DOCKER_MEMORY} \\
                                      --cpus=${DOCKER_CPUS} \\
                                      --network ${COMPOSE_PROJECT_NAME}_zoomcar-network \\
                                      -v zoomcar-ivy-cache:/root/.ivy2 \\
                                      -v "\$PWD":/app \\
                                      -w /app \\
                                      -e POSTGRES_HOST=postgres \\
                                      ${IMAGE_NAME} \\
                                      python -m src.data_quality_dashboard
                                """
                            }
                            
                            sh dockerCmd
                            echo "✅ Dashboard generation completed"
                        }
                    } catch (Exception e) {
                        echo "⚠️ Dashboard generation failed: ${e.message}"
                        echo "Continuing pipeline..."
                    }
                }
            }
        }

        stage('Archive Results') {
            steps {
                script {
                    def artifacts = []
                    
                    if (fileExists('reports/data_quality_dashboard.html')) {
                        artifacts << 'reports/data_quality_dashboard.html'
                    }
                    
                    if (params.PIPELINE_MODE == 'batch') {
                        if (fileExists('data/final')) {
                            artifacts << 'data/final/**/*'
                        }
                        if (fileExists('data/export')) {
                            artifacts << 'data/export/**/*'
                        }
                    }
                    
                    if (artifacts) {
                        archiveArtifacts artifacts: artifacts.join(','), 
                                       fingerprint: true, 
                                       allowEmptyArchive: true,
                                       onlyIfSuccessful: false
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
            echo "❌ Pipeline failed! Check logs above."
        }
        always {
            script {
                if (params.PIPELINE_MODE == 'realtime') {
                    echo "🛑 Stopping infrastructure services..."
                    sh "docker-compose down -v || true"
                }
                echo "🧹 Cleaning workspace..."
                cleanWs()
            }
        }
    }
}
