# pipeline code snippet


## find files via blob expression.

```groovy
pipeline {
    agent any
    
    stages {
        stage('Find and Process Files') {
            steps {
                script {
                    // Define the glob expression to match files
                    def filesToProcess = findFiles(glob: '/path/to/**/*.json')
                    
                    // Loop through the matched files and extract scan_id
                    for (file in filesToProcess) {
                        echo "Found file: ${file.name}"
                        
                        def fileContent = readFile(file.path)
                        def json = new groovy.json.JsonSlurperClassic().parseText(fileContent)
                        def scanId = json.user_id
                        
                        echo "Scan ID: ${user_id}"
                        
                        // Your processing steps here
                    }
                }
            }
        }
    }
}


```

## archive artefacts

```groovy
pipeline {
    agent any
    
    stages {
        stage('Archive Files') {
            steps {
                script {
                    // Define the glob expression to match files
                    def filesToArchive = findFiles(glob: '/path/to/source_directory/**/*.txt')
                    
                    // Archive artifacts with allowEmptyArchive
                    archiveArtifacts allowEmptyArchive: true, artifacts: filesToArchive.collect { it.path }
                }
            }
        }
    }
}

```