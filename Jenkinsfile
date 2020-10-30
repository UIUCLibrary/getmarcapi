def getDevPiStagingIndex(){

    if (env.TAG_NAME?.trim()){
        return "tag_staging"
    } else{
        return "${env.BRANCH_NAME}_staging"
    }
}

def getToxEnvs(){
    if(isUnix()){
        return sh(returnStdout: true, script: "tox -l").trim().split('\n')
    }
    return bat(returnStdout: true, script: "@tox -l").trim().split('\n')
}
def build_tox_stage(tox_env){
    script{
        if(isUnix()){
            return [tox_env, {
                sh( label: "Running Tox with ${tox_env} environment", script: "tox  -vv -e $tox_env --parallel--safe-build")
                }]
        return [tox_env, {
                    bat( label: "Running Tox with ${tox_env} environment", script: "tox  -vv -e $tox_env")
        }]
        }
    }
}

def get_tox_stages(envs){
    def cmds = envs.collectEntries({ tox_env ->
        build_tox_stage(tox_env)
    })
//     def cmds
//     if(isUnix()){
//         cmds = envs.collectEntries({ tox_env ->
//             [tox_env, {
//                 sh( label: "Running Tox with ${tox_env} environment", script: "tox  -vv -e $tox_env --parallel--safe-build")
//             }]
//         })
//     } else{
//         cmds = envs.collectEntries({ tox_env ->
//             [tox_env, {
//                 bat( label: "Running Tox with ${tox_env} environment", script: "tox  -vv -e $tox_env")
//             }]
//         })
//     }
    return cmds
}
def run_tox_envs(){
    script {
        def envs = getToxEnvs()
        echo "Setting up tox tests for ${envs.join(', ')}"
        parallel(get_tox_stages(envs))
    }
}

def get_sonarqube_unresolved_issues(report_task_file){
    script{
        if (! fileExists(report_task_file)){
            error "File not found ${report_task_file}"
        }
        def props = readProperties  file: report_task_file
        def response = httpRequest url : props['serverUrl'] + "/api/issues/search?componentKeys=" + props['projectKey'] + "&resolved=no"
        def outstandingIssues = readJSON text: response.content
        return outstandingIssues
    }
}

def devpiRunTest(pkgPropertiesFile, devpiIndex, devpiSelector, devpiUsername, devpiPassword, toxEnv){
    script{
        def props = readProperties interpolate: false, file: pkgPropertiesFile
        if (isUnix()){
            sh(
                label: "Running test",
                script: """devpi use https://devpi.library.illinois.edu --clientdir certs/
                           devpi login ${devpiUsername} --password ${devpiPassword} --clientdir certs/
                           devpi use ${devpiIndex} --clientdir certs/
                           devpi test --index ${devpiIndex} ${props.Name}==${props.Version} -s ${devpiSelector} --clientdir certs/ -e ${toxEnv} --tox-args=\"-vv\"
                """
            )
        } else {
            bat(
                label: "Running tests on Devpi",
                script: """devpi use https://devpi.library.illinois.edu --clientdir certs\\
                           devpi login ${devpiUsername} --password ${devpiPassword} --clientdir certs\\
                           devpi use ${devpiIndex} --clientdir certs\\
                           devpi test --index ${devpiIndex} ${props.Name}==${props.Version} -s ${devpiSelector} --clientdir certs\\ -e ${toxEnv} --tox-args=\"-vv\"
                           """
            )
        }
    }
}
def startup(){
    stage("Getting Distribution Info"){
        node('linux && docker') {
            docker.image('python:3.8').inside {
                timeout(2){
                    try{
                        checkout scm
                        sh(
                           label: "Running setup.py with dist_info",
                           script: """python --version
                                      python setup.py dist_info
                                   """
                        )
                        stash includes: "*.dist-info/**", name: 'DIST-INFO'
                        archiveArtifacts artifacts: "*.dist-info/**"
                    } finally{
                        deleteDir()
                    }
                }
            }
        }
    }
}
def get_props(metadataFile){
    stage("Reading Package Metadata"){
        node() {
            try{
                unstash "DIST-INFO"
                def props = readProperties interpolate: true, file: metadataFile
                return props
            } finally {
                deleteDir()
            }
        }
    }
}
startup()
def props = get_props("getmarcapi.dist-info/METADATA")
def DEFAULT_DOCKER_AGENT_FILENAME = 'ci/docker/python/linux/Dockerfile'
def DEFAULT_DOCKER_AGENT_LABELS = 'linux && docker'
def DEFAULT_DOCKER_AGENT_ADDITIONALBUILDARGS = '--build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g) --build-arg PIP_INDEX_URL=https://devpi.library.illinois.edu/production/release --build-arg PIP_EXTRA_INDEX_URL'

pipeline {
    agent none
    parameters {
        booleanParam(name: "RUN_CHECKS", defaultValue: true, description: "Run checks on code")
        booleanParam(name: "TEST_RUN_TOX", defaultValue: false, description: "Run Tox Tests")
        booleanParam(name: "USE_SONARQUBE", defaultValue: true, description: "Send data test data to SonarQube")
        booleanParam(name: "BUILD_PACKAGES", defaultValue: false, description: "Build Python packages")
        booleanParam(name: "DEPLOY_DEVPI", defaultValue: false, description: "Deploy to devpi on http://devpi.library.illinois.edu/DS_Jenkins/${env.BRANCH_NAME}")
        booleanParam(name: "DEPLOY_DEVPI_PRODUCTION", defaultValue: false, description: "Deploy to production devpi on https://devpi.library.illinois.edu/production/release. Master branch Only")
        booleanParam(name: 'DEPLOY_DOCS', defaultValue: false, description: '')
        booleanParam(name: "DEPLOY_TO_PRODUCTION", defaultValue: false, description: "Deploy to Production Server")
    }
    stages {
        stage("Tox"){
//             when{
//                 equals expected: true, actual: params.TEST_RUN_TOX
//             }
            steps{
                script{
                    def envs
                    node(DEFAULT_DOCKER_AGENT_LABELS){
                        checkout scm
                        def container = docker.build("d", "-f ci/docker/python/tox/Dockerfile ${DEFAULT_DOCKER_AGENT_ADDITIONALBUILDARGS} . ")
                        container.inside(){
                            envs = getToxEnvs()
                            echo "Setting up tox tests for ${envs.join(', ')}"
                        }
                    }
                    def moreToxStages = envs.collect{ tox_env ->
                        "dddd"
//                         tox_env
//                         script{
//                             {->
//                                 build_tox_stage(tox_env)
//                             }
//                         }
                    }
                    echo "moreToxStages start"
                    moreToxStages.each{
                        echo "Got ${it}"
                    }
                    echo "moreToxStages end"
//                     def moreToxStages = envs.collectEntries({ tox_env ->
//                         tox_env
// //                         build_tox_stage(tox_env)
//                     })
                    node(DEFAULT_DOCKER_AGENT_LABELS){
                        def toxStages = get_tox_stages(envs)
                        def container = docker.build("d", "-f ci/docker/python/tox/Dockerfile ${DEFAULT_DOCKER_AGENT_ADDITIONALBUILDARGS} . ")
                        container.inside(){
                            parallel(toxStages)
                        }

                    }

                }
            }
        }
        stage("Getting Testing Environment Info"){
            agent {
                dockerfile {
                    filename DEFAULT_DOCKER_AGENT_FILENAME
                    label DEFAULT_DOCKER_AGENT_LABELS
                    additionalBuildArgs DEFAULT_DOCKER_AGENT_ADDITIONALBUILDARGS
                }
            }
            steps{
                timeout(5){
                    sh(
                        label: "Checking Installed Python Packages",
                        script: "python -m pip list"
                    )
                }
            }
        }
//         stage("Sphinx Documentation"){
//             agent{
//                 dockerfile {
//                         filename 'ci/docker/python/linux/Dockerfile'
//                         label 'linux && docker'
//                         additionalBuildArgs "--build-arg USER_ID=\$(id -u) --build-arg GROUP_ID=\$(id -g) --build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL=https://devpi.library.illinois.edu/production/release"
//                     }
//                 }
//                 steps {
//                     sh(
//                         label: "Building docs",
//                         script: '''mkdir -p logs
//                                    python -m sphinx docs build/docs/html -d build/docs/.doctrees -w logs/build_sphinx.log
//                                    '''
//                         )
//                 }
//                 post{
//                     always {
//                         recordIssues(tools: [sphinxBuild(pattern: 'logs/build_sphinx.log')])
//                     }
//                     success{
//                         publishHTML([allowMissing: true, alwaysLinkToLastBuild: false, keepAll: false, reportDir: 'build/docs/html', reportFiles: 'index.html', reportName: 'Documentation', reportTitles: ''])
//                         unstash "DIST-INFO"
//                         script{
//                             def props = readProperties interpolate: false, file: "getmarcapi.dist-info/METADATA"
//                             def DOC_ZIP_FILENAME = "${props.Name}-${props.Version}.doc.zip"
//                             zip archive: true, dir: "${WORKSPACE}/build/docs/html", glob: '', zipFile: "dist/${DOC_ZIP_FILENAME}"
//                             stash includes: "dist/${DOC_ZIP_FILENAME},build/docs/html/**", name: 'DOCS_ARCHIVE'
//                         }
// 
//                     }
//                     cleanup{
//                         cleanWs(
//                             patterns: [
//                                 [pattern: 'logs/', type: 'INCLUDE'],
//                                 [pattern: "build/docs/", type: 'INCLUDE'],
//                                 [pattern: "dist/", type: 'INCLUDE']
//                             ],
//                             deleteDirs: true
//                         )
//                     }
//                 }
//             }
        stage("Checks") {
            when{
                equals expected: true, actual: params.RUN_CHECKS
            }
            stages{
                stage("Code Quality Checks"){
                    agent {
                        dockerfile {
                            filename DEFAULT_DOCKER_AGENT_FILENAME
                            label DEFAULT_DOCKER_AGENT_LABELS
                            additionalBuildArgs DEFAULT_DOCKER_AGENT_ADDITIONALBUILDARGS
                        }
                    }
                    stages{
                        stage("Configuring Testing Environment"){
                            steps{
                                sh(
                                    label: "Creating logging and report directories",
                                    script: """
                                        mkdir -p logs
                                        mkdir -p reports/coverage
                                        mkdir -p reports/doctests
                                        mkdir -p reports/mypy/html
                                    """
                                )
                            }
                        }
                        stage("Running Tests"){
                            parallel {
                                stage("PyTest"){
                                    steps{
                                        sh "coverage run --parallel-mode --source getmarcapi -m pytest --junitxml=reports/pytest/junit-pytest.xml "
                                    }
                                    post {
                                        always {
                                            junit "reports/pytest/junit-pytest.xml"
                                            stash includes: "reports/pytest/*.xml", name: 'PYTEST_REPORT'
                                        }
                                    }
                                }
    //                         stage("Doctest"){
    //                             steps {
    //                                 sh "coverage run --parallel-mode --source getmarcapi -m sphinx -b doctest -d build/docs/doctrees docs reports/doctest -w logs/doctest.log"
    //                             }
    //                             post{
    //                                 always {
    //                                     recordIssues(tools: [sphinxBuild(name: 'Sphinx Doctest', pattern: 'logs/doctest.log', id: 'doctest')])
    //                                 }
    //
    //                             }
    //                         }
    //                         stage("Documentation Spell check"){
    //                             steps {
    //                                 catchError(buildResult: 'SUCCESS', message: 'Found spelling issues in documentation', stageResult: 'UNSTABLE') {
    //                                     sh "python -m sphinx docs reports/doc_spellcheck -b spelling -d build/docs/doctrees"
    //                                 }
    //                             }
    //                         }
                                stage("pyDocStyle"){
                                    steps{
                                        catchError(buildResult: 'SUCCESS', message: 'Did not pass all pyDocStyle tests', stageResult: 'UNSTABLE') {
                                            sh(
                                                label: "Run pydocstyle",
                                                script: '''mkdir -p reports
                                                           pydocstyle getmarcapi > reports/pydocstyle-report.txt
                                                           '''
                                            )
                                        }
                                    }
                                    post {
                                        always{
                                            recordIssues(tools: [pyDocStyle(pattern: 'reports/pydocstyle-report.txt')])
                                        }
                                    }
                                }
                                stage("MyPy") {
                                    steps{
                                        catchError(buildResult: 'SUCCESS', message: 'mypy found issues', stageResult: 'UNSTABLE') {
                                            sh "mypy -p getmarcapi --html-report reports/mypy/html/  > logs/mypy.log"
                                        }
                                    }
                                    post {
                                        always {
                                            recordIssues(tools: [myPy(name: 'MyPy', pattern: 'logs/mypy.log')])
                                            publishHTML([allowMissing: false, alwaysLinkToLastBuild: false, keepAll: false, reportDir: 'reports/mypy/html/', reportFiles: 'index.html', reportName: 'MyPy HTML Report', reportTitles: ''])
                                        }
                                    }
                                }
                                stage("Bandit") {
                                    steps{
                                        catchError(buildResult: 'SUCCESS', message: 'Bandit found issues', stageResult: 'UNSTABLE') {
                                            sh(
                                                label: "Running bandit",
                                                script: "bandit --format json --output reports/bandit-report.json --recursive getmarcapi || bandit -f html --recursive getmarcapi --output reports/bandit-report.html"
                                            )
                                        }
                                    }
                                    post {
                                        unstable{
                                            script{
                                                if(fileExists('reports/bandit-report.html')){
                                                    publishHTML([
                                                        allowMissing: false,
                                                        alwaysLinkToLastBuild: false,
                                                        keepAll: false,
                                                        reportDir: 'reports',
                                                        reportFiles: 'bandit-report.html',
                                                        reportName: 'Bandit Report', reportTitles: ''
                                                        ])
                                                }
                                            }
                                        }
                                        always {
                                            stash includes: "reports/bandit-report.json", name: 'BANDIT_REPORT'
                                        }
                                    }
                                }
                                stage("PyLint") {
                                    steps{
                                        catchError(buildResult: 'SUCCESS', message: 'Pylint found issues', stageResult: 'UNSTABLE') {
                                            tee("reports/pylint.txt"){
                                                sh(
                                                    script: '''pylint getmarcapi -r n --persistent=n --verbose --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}"
                                                               ''',
                                                    label: "Running pylint"
                                                )
                                            }
                                        }
                                        sh(
                                            script: 'pylint getmarcapi  -r n --persistent=n --msg-template="{path}:{module}:{line}: [{msg_id}({symbol}), {obj}] {msg}" > reports/pylint_issues.txt',
                                            label: "Running pylint for sonarqube",
                                            returnStatus: true
                                        )
                                    }
                                    post{
                                        always{
                                            stash includes: "reports/pylint_issues.txt,reports/pylint.txt", name: 'PYLINT_REPORT'
                                            recordIssues(tools: [pyLint(pattern: 'reports/pylint.txt')])
                                        }
                                    }
                                }
                                stage("Flake8") {
                                    steps{
                                        catchError(buildResult: 'SUCCESS', message: 'Flake8 found issues', stageResult: 'UNSTABLE') {
                                            sh(label: "Running Flake8",
                                               script: '''mkdir -p logs
                                                          flake8 getmarcapi --tee --output-file=logs/flake8.log
                                                       '''
                                               )
                                        }
                                    }
                                    post {
                                        always {
                                            recordIssues(tools: [flake8(name: 'Flake8', pattern: 'logs/flake8.log')])
                                            stash includes: "logs/flake8.log", name: 'FLAKE8_REPORT'
                                        }
                                    }
                                }
                            }
                            post{
                                always{
                                    sh(
                                        label: "Combining coverage results",
                                        script: '''coverage combine
                                                   coverage xml -o reports/coverage.xml
                                                   '''
                                    )
                                    stash includes: "reports/coverage.xml", name: 'COVERAGE_REPORT'
                                    publishCoverage(
                                        adapters: [
                                            coberturaAdapter('reports/coverage.xml')
                                        ],
                                        sourceFileResolver: sourceFiles('STORE_ALL_BUILD')
                                    )

                                }
                                cleanup{
                                    cleanWs(
                                        deleteDirs: true,
                                        patterns: [
                                            [pattern: "dist/", type: 'INCLUDE'],
                                            [pattern: 'build/', type: 'INCLUDE'],
                                            [pattern: '.coverage', type: 'INCLUDE'],
                                            [pattern: '.eggs', type: 'INCLUDE'],
                                            [pattern: '.pytest_cache/', type: 'INCLUDE'],
                                            [pattern: '**/__pycache__/', type: 'INCLUDE'],
                                            [pattern: '.mypy_cache/', type: 'INCLUDE'],
                                            [pattern: '.tox/', type: 'INCLUDE'],
                                            [pattern: 'getmarcapi1.stats', type: 'INCLUDE'],
                                            [pattern: 'getmarcapi.egg-info/', type: 'INCLUDE'],
                                            [pattern: 'reports/', type: 'INCLUDE'],
                                            [pattern: 'logs/', type: 'INCLUDE']
                                            ]
                                    )
                                }
                            }
                        }
                    }
                }

                stage("Sonarcloud Analysis"){
                    agent {
                        dockerfile {
                            filename DEFAULT_DOCKER_AGENT_FILENAME
                            label DEFAULT_DOCKER_AGENT_LABELS
                            additionalBuildArgs DEFAULT_DOCKER_AGENT_ADDITIONALBUILDARGS
                            args '--mount source=sonar-cache-getmarcapi,target=/home/user/.sonar/cache'
                        }
                    }
                    options{
                        lock("getmarcapi-sonarscanner")
                    }
                    when{
                        equals expected: true, actual: params.USE_SONARQUBE
                        beforeAgent true
                        beforeOptions true
                    }
                    steps{
                        unstash "COVERAGE_REPORT"
                        unstash "PYTEST_REPORT"
                        unstash "BANDIT_REPORT"
                        unstash "PYLINT_REPORT"
                        unstash "FLAKE8_REPORT"
                        script{
                            withSonarQubeEnv(installationName:"sonarcloud", credentialsId: 'sonarcloud-getmarcapi') {
                                if (env.CHANGE_ID){
                                    sh(
                                        label: "Running Sonar Scanner",
                                        script:"sonar-scanner -Dsonar.projectVersion=${props.Version} -Dsonar.buildString=\"${env.BUILD_TAG}\" -Dsonar.pullrequest.key=${env.CHANGE_ID} -Dsonar.pullrequest.base=${env.CHANGE_TARGET}"
                                        )
                                } else {
                                    sh(
                                        label: "Running Sonar Scanner",
                                        script: "sonar-scanner -Dsonar.projectVersion=${props.Version} -Dsonar.buildString=\"${env.BUILD_TAG}\" -Dsonar.branch.name=${env.BRANCH_NAME}"
                                        )
                                }
                            }
                            timeout(time: 1, unit: 'HOURS') {
                                def sonarqube_result = waitForQualityGate(abortPipeline: false)
                                if (sonarqube_result.status != 'OK') {
                                    unstable "SonarQube quality gate: ${sonarqube_result.status}"
                                }
                                def outstandingIssues = get_sonarqube_unresolved_issues(".scannerwork/report-task.txt")
                                writeJSON file: 'reports/sonar-report.json', json: outstandingIssues
                            }
                        }
                    }
                    post {
                        always{
                            script{
                                if(fileExists('reports/sonar-report.json')){
                                    stash includes: "reports/sonar-report.json", name: 'SONAR_REPORT'
                                    archiveArtifacts allowEmptyArchive: true, artifacts: 'reports/sonar-report.json'
                                    recordIssues(tools: [sonarQube(pattern: 'reports/sonar-report.json')])
                                }
                            }
                        }
                        cleanup{
                            cleanWs(
                                deleteDirs: true,
                                patterns: [
                                    [pattern: 'reports/', type: 'INCLUDE'],
                                    [pattern: 'logs/', type: 'INCLUDE'],
                                    [pattern: 'getmarcapi.dist-info/', type: 'INCLUDE'],
                                    [pattern: '.scannerwork/', type: 'INCLUDE'],
                                ]
                            )
                        }
                    }
                }
            }
        }
        stage("Distribution Packages"){
            when{
                anyOf{
                    equals expected: true, actual: params.BUILD_PACKAGES
                    equals expected: true, actual: params.DEPLOY_DEVPI
                    equals expected: true, actual: params.DEPLOY_DEVPI_PRODUCTION
                }
                beforeAgent true
            }
            stages{
                stage("Creating Package") {
                    agent {
                        dockerfile {
                            filename DEFAULT_DOCKER_AGENT_FILENAME
                            label DEFAULT_DOCKER_AGENT_LABELS
                            additionalBuildArgs DEFAULT_DOCKER_AGENT_ADDITIONALBUILDARGS
                        }
                    }
                    steps {
                        sh(label: "Building python distribution packages", script: 'python -m pep517.build .')
                    }
                    post {
                        always{
                            stash includes: 'dist/*.*', name: "PYTHON_PACKAGES"
                        }
                        success {
                            archiveArtifacts artifacts: "dist/*.whl,dist/*.tar.gz,dist/*.zip", fingerprint: true
                        }
                        cleanup{
                            cleanWs(
                                deleteDirs: true,
                                patterns: [
                                    [pattern: 'dist/', type: 'INCLUDE'],
                                    [pattern: 'build/', type: 'INCLUDE'],
                                    [pattern: 'getmarcapi.egg-info/', type: 'INCLUDE'],
                                ]
                            )
                        }
                    }
                }
                stage('Testing all Package') {
                    matrix{
                        axes{
                            axis {
                                name "PYTHON_VERSION"
                                values(
                                    "3.7",
                                    "3.8"
                                )
                            }
                        }
                        agent {
                            dockerfile {
                                filename DEFAULT_DOCKER_AGENT_FILENAME
                                label DEFAULT_DOCKER_AGENT_LABELS
                                additionalBuildArgs "--build-arg PYTHON_VERSION=${PYTHON_VERSION} --build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL=https://devpi.library.illinois.edu/production/release"
                            }
                        }
                        stages{
                            stage("Testing Package sdist"){
                                options {
                                    warnError('Package Testing Failed')
                                }
                                steps{
                                    unstash "PYTHON_PACKAGES"
                                    script{
                                        findFiles(glob: "**/*.tar.gz").each{
                                            timeout(15){
                                                sh(
                                                    script: """python --version
                                                               tox --installpkg=${it.path} -e py -vv
                                                               """,
                                                    label: "Testing ${it}"
                                                )
                                            }
                                        }
                                    }
                                }
                                post{
                                    cleanup{
                                        cleanWs(
                                            notFailBuild: true,
                                            deleteDirs: true,
                                            patterns: [
                                                [pattern: 'dist/', type: 'INCLUDE'],
                                                [pattern: 'tests/__pycache__/', type: 'INCLUDE'],
                                                [pattern: 'build/', type: 'INCLUDE'],
                                                [pattern: '.tox/', type: 'INCLUDE'],
                                            ]
                                        )
                                    }
                                }
                            }
                            stage("Testing Package Wheel"){
                                options {
                                    warnError('Package Testing Failed')
                                }
                                steps{
                                    unstash "PYTHON_PACKAGES"
                                    script{
                                        findFiles(glob: "**/*.whl").each{
                                            timeout(15){
                                                sh(
                                                    script: """python --version
                                                               tox --installpkg=${it.path} -e py -vv
                                                               """,
                                                    label: "Testing ${it}"
                                                )
                                            }
                                        }
                                    }
                                }
                                post{
                                    cleanup{
                                        cleanWs(
                                            notFailBuild: true,
                                            deleteDirs: true,
                                            patterns: [
                                                [pattern: 'dist/', type: 'INCLUDE'],
                                                [pattern: 'tests/__pycache__/', type: 'INCLUDE'],
                                                [pattern: 'build/', type: 'INCLUDE'],
                                                [pattern: '.tox/', type: 'INCLUDE'],
                                            ]
                                        )
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        stage("Deployment"){
            stages{

                stage("Deploy to Devpi"){
                    when {
                        allOf{
                            equals expected: true, actual: params.DEPLOY_DEVPI
                            anyOf {
                                equals expected: "master", actual: env.BRANCH_NAME
                                equals expected: "dev", actual: env.BRANCH_NAME
                                tag "*"
                            }
                        }
                        beforeAgent true
                        beforeOptions true
                    }
                    agent none
                    environment{
                        DEVPI = credentials("DS_devpi")
                        devpiStagingIndex = getDevPiStagingIndex()
                    }
                    options{
                        lock("getmarcapi-devpi")
                    }
                    stages{
                        stage("Deploy to Devpi Staging") {
                            agent{
                                dockerfile {
                                    filename DEFAULT_DOCKER_AGENT_FILENAME
                                    label DEFAULT_DOCKER_AGENT_LABELS
                                    additionalBuildArgs DEFAULT_DOCKER_AGENT_ADDITIONALBUILDARGS
                                }
                            }
                            steps {
                                unstash "PYTHON_PACKAGES"
        //                         unstash "DOCS_ARCHIVE"
                                sh(
                                    label: "Uploading to DevPi Staging",
                                    script: """devpi use https://devpi.library.illinois.edu --clientdir ./devpi
                                               devpi login $DEVPI_USR --password $DEVPI_PSW --clientdir ./devpi
                                               devpi use /${env.DEVPI_USR}/${env.devpiStagingIndex} --clientdir ./devpi
                                               devpi upload --from-dir dist --clientdir ./devpi"""
                                )
                            }
                        }
                        stage("Test DevPi Package") {
                            matrix {
                                axes {
                                    axis {
                                        name 'PYTHON_VERSION'
                                        values '3.7', '3.8'
                                    }
                                }
                                agent none
                                stages{
                                    stage("Testing DevPi wheel Package"){
                                        agent {
                                            dockerfile {
                                                filename DEFAULT_DOCKER_AGENT_FILENAME
                                                label DEFAULT_DOCKER_AGENT_LABELS
                                                additionalBuildArgs "--build-arg PYTHON_VERSION=${PYTHON_VERSION} --build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL=https://devpi.library.illinois.edu/production/release"
                                            }
                                        }
                                        options {
                                            warnError('Package Testing Failed')
                                        }
                                        steps{
                                            timeout(10){
                                                unstash "DIST-INFO"
                                                devpiRunTest(
                                                    "getmarcapi.dist-info/METADATA",
                                                    env.devpiStagingIndex,
                                                    "whl",
                                                    DEVPI_USR,
                                                    DEVPI_PSW,
                                                    "py${PYTHON_VERSION.replace('.', '')}"
                                                    )
                                            }
                                        }
                                    }
                                    stage("Testing DevPi sdist Package"){
                                        agent {
                                            dockerfile {
                                                filename DEFAULT_DOCKER_AGENT_FILENAME
                                                label DEFAULT_DOCKER_AGENT_LABELS
                                                additionalBuildArgs "--build-arg PYTHON_VERSION=${PYTHON_VERSION} --build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL=https://devpi.library.illinois.edu/production/release"
                                            }
                                        }
                                        options {
                                            warnError('Package Testing Failed')
                                        }
                                        steps{
                                            timeout(10){
                                                unstash "DIST-INFO"
                                                devpiRunTest(
                                                    "getmarcapi.dist-info/METADATA",
                                                    env.devpiStagingIndex,
                                                    "tar.gz",
                                                    DEVPI_USR,
                                                    DEVPI_PSW,
                                                    "py${PYTHON_VERSION.replace('.', '')}"
                                                    )
                                            }
                                        }
                                    }
                                }
                            }
                        }
                        stage("Deploy to DevPi Production") {
                            when {
                                allOf{
                                    equals expected: true, actual: params.DEPLOY_DEVPI_PRODUCTION
                                    anyOf {
                                        branch "master"
                                        tag "*"
                                    }
                                }
                                beforeInput true
                            }
                            options{
                                  timeout(time: 1, unit: 'DAYS')
                            }
                            input {
                              message 'Release to DevPi Production? '
                            }
                            agent {
                                dockerfile {
                                    filename DEFAULT_DOCKER_AGENT_FILENAME
                                    label DEFAULT_DOCKER_AGENT_LABELS
                                    additionalBuildArgs DEFAULT_DOCKER_AGENT_ADDITIONALBUILDARGS
                                }
                            }
                            steps {
                                script {
                                    sh(
                                        label: "Pushing to production/release index",
                                        script: """devpi use https://devpi.library.illinois.edu --clientdir ./devpi
                                                   devpi login $DEVPI_USR --password $DEVPI_PSW --clientdir ./devpi
                                                   devpi push --index DS_Jenkins/${env.devpiStagingIndex} ${props.Name}==${props.Version} production/release --clientdir ./devpi
                                                   """
                                    )
                                }
                            }
                        }
                    }
                    post{
                        success{
                            node('linux && docker') {
                               script{
                                    if (!env.TAG_NAME?.trim()){
                                        docker.build("getmarc:devpi",'-f ./ci/docker/python/linux/Dockerfile --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g) --build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL=https://devpi.library.illinois.edu/production/release .').inside{
                                            sh(
                                                label: "Moving DevPi package from staging index to index",
                                                script: """devpi use https://devpi.library.illinois.edu --clientdir ./devpi
                                                           devpi login $DEVPI_USR --password $DEVPI_PSW --clientdir ./devpi
                                                           devpi use /DS_Jenkins/${env.devpiStagingIndex} --clientdir ./devpi
                                                           devpi push ${props.Name}==${props.Version} DS_Jenkins/${env.BRANCH_NAME} --clientdir ./devpi
                                                           """
                                            )
                                        }
                                   }
                               }
                            }
                        }
                        cleanup{
                            node('linux && docker') {
                               script{
                                    docker.build("getmarc:devpi",'-f ./ci/docker/python/linux/Dockerfile --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g) --build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL=https://devpi.library.illinois.edu/production/release .').inside{
                                        sh(
                                            label: "Removing Package from DevPi staging index",
                                            script: """devpi use https://devpi.library.illinois.edu --clientdir ./devpi
                                                       devpi login $DEVPI_USR --password $DEVPI_PSW --clientdir ./devpi
                                                       devpi use /DS_Jenkins/${env.devpiStagingIndex} --clientdir ./devpi
                                                       devpi remove -y ${props.Name}==${props.Version} --clientdir ./devpi
                                                       """
                                           )
                                    }
                               }
                            }
                        }
                    }
                }
                stage("Additional Deploy") {
                    parallel{
                        stage("Deploy to Production"){
                            when{
                                equals expected: true, actual: params.DEPLOY_TO_PRODUCTION
                                beforeAgent true
                                beforeInput true
                            }
                            agent{
                                label "linux && docker"
                            }
                            input {
                                message 'Deploy to to server'
                            }
                            steps{
                                script{
                                    withCredentials([string(credentialsId: 'ALMA_API_KEY', variable: 'API_KEY')]) {
                                        writeFile(
                                            file: 'api.cfg',
                                            text: """[ALMA_API]
                                                     API_DOMAIN=https://api-na.hosted.exlibrisgroup.com
                                                     API_KEY=${API_KEY}
                                                     """
                                            )
                                    }
                                    configFileProvider([configFile(fileId: 'getmarc_deployapi', variable: 'CONFIG_FILE')]) {
                                        def CONFIG = readJSON(file: CONFIG_FILE)['deploy']
                                        echo "Got ${CONFIG}"
                                        def build_args = CONFIG['docker']['build']['buildArgs'].collect{"--build-arg=${it}"}.join(" ")
                                        def container_config = CONFIG['docker']['container']
                                        def container_name = container_config['name']
                                        def container_ports_arg = container_config['ports'] .collect{"-p ${it}"}.join(" ")

                                        docker.withServer(CONFIG['docker']['server']['apiUrl'], "DOCKER_TYKO"){
                                            def dockerImage = docker.build("getmarcapi:${env.BUILD_ID}", "${build_args} .")
                                            sh "docker stop ${container_name}"
                                            dockerImage.run("${container_ports_arg} --name ${container_name} --rm")
                                        }
                                    }
                                }
                            }
                        }
                        stage("Deploy Documentation"){
                            when{
                                equals expected: true, actual: params.DEPLOY_DOCS
                                beforeInput true
                            }
                            input {
                                message 'Deploy documentation'
                                id 'DEPLOY_DOCUMENTATION'
                                parameters {
                                    string defaultValue: 'getmarc2', description: '', name: 'DEPLOY_DOCS_URL_SUBFOLDER', trim: true
                                }
                            }
                            agent any
                            steps{
                                unstash "DOCS_ARCHIVE"
                                sshPublisher(
                                    publishers: [
                                        sshPublisherDesc(
                                            configName: 'apache-ns - lib-dccuser-updater',
                                            transfers: [
                                                sshTransfer(
                                                    cleanRemote: false,
                                                    excludes: '',
                                                    execCommand: '',
                                                    execTimeout: 120000,
                                                    flatten: false,
                                                    makeEmptyDirs: false,
                                                    noDefaultExcludes: false,
                                                    patternSeparator: '[, ]+',
                                                    remoteDirectory: "${DEPLOY_DOCS_URL_SUBFOLDER}",
                                                    remoteDirectorySDF: false,
                                                    removePrefix: 'build/docs/html',
                                                    sourceFiles: 'build/docs/html/**'
                                                )
                                            ],
                                            usePromotionTimestamp: false,
                                            useWorkspaceInPromotion: false,
                                            verbose: false
                                        )
                                    ]
                                )
                            }
                            post{
                                cleanup{
                                    cleanWs(
                                        deleteDirs: true,
                                        patterns: [
                                            [pattern: "build/", type: 'INCLUDE'],
                                            [pattern: "dist/", type: 'INCLUDE'],
                                        ]
                                    )
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}