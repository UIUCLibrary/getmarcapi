library identifier: 'JenkinsPythonHelperLibrary@2024.1.2', retriever: modernSCM(
  [$class: 'GitSCMSource',
   remote: 'https://github.com/UIUCLibrary/JenkinsPythonHelperLibrary.git',
   ])


def getPypiConfig() {
    node(){
        configFileProvider([configFile(fileId: 'pypi_config', variable: 'CONFIG_FILE')]) {
            def config = readJSON( file: CONFIG_FILE)
            return config['deployment']['indexes']
        }
    }
}

def get_sonarqube_unresolved_issues(report_task_file){
    script{
        if(! fileExists(report_task_file)){
            error "Could not find ${report_task_file}"
        }
        def props = readProperties  file: report_task_file
        if(! props['serverUrl'] || ! props['projectKey']){
            error "Could not find serverUrl or projectKey in ${report_task_file}"
        }
        def response = httpRequest url : props['serverUrl'] + '/api/issues/search?componentKeys=' + props['projectKey'] + '&resolved=no'
        def outstandingIssues = readJSON text: response.content
        return outstandingIssues
    }
}


def getVersion(){
    node(){
        checkout scm
        return readTOML( file: 'pyproject.toml')['project']
    }
}


def call(){
    pipeline {
        agent none
        parameters {
            booleanParam(name: 'RUN_CHECKS', defaultValue: true, description: 'Run checks on code')
            booleanParam(name: 'TEST_RUN_TOX', defaultValue: false, description: 'Run Tox Tests')
            booleanParam(name: 'USE_SONARQUBE', defaultValue: true, description: 'Send data test data to SonarQube')
            credentials(name: 'SONARCLOUD_TOKEN', credentialType: 'org.jenkinsci.plugins.plaincredentials.impl.StringCredentialsImpl', defaultValue: 'sonarcloud_token', required: false)
            booleanParam(name: 'BUILD_PACKAGES', defaultValue: false, description: 'Build Python packages')
            booleanParam(name: 'INCLUDE_LINUX-ARM64', defaultValue: false, description: 'Include ARM architecture for Linux')
            booleanParam(name: 'INCLUDE_LINUX-X86_64', defaultValue: true, description: 'Include x86_64 architecture for Linux')
            booleanParam(name: 'TEST_PACKAGES', defaultValue: true, description: 'Test Python packages by installing them and running tests on the installed package')
            booleanParam(name: 'DEPLOY_PYPI', defaultValue: false, description: 'Deploy to pypi')
            booleanParam(name: 'DEPLOY_DOCS', defaultValue: false, description: '')
            booleanParam(name: 'DEPLOY_TO_PRODUCTION', defaultValue: false, description: 'Deploy to Production Server')
        }
        stages {
            stage('Building and Testing'){
                when{
                    anyOf{
                        equals expected: true, actual: params.RUN_CHECKS
                        equals expected: true, actual: params.TEST_RUN_TOX
                    }
                }
                stages{
                    stage('Checks') {
                        stages{
                            stage('Code Quality Checks'){
                                agent {
                                    dockerfile {
                                        filename 'ci/docker/python/linux/Dockerfile'
                                        label 'linux && docker && x86'
                                        additionalBuildArgs '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL --build-arg PIP_CACHE_DIR=/.cache/pip'
                                        args '--mount source=python-jenkins-tmp-getmarcapi,target=/tmp'
                                    }
                                }
                                environment{
                                    PIP_CACHE_DIR='/tmp/pipcache'
                                    UV_INDEX_STRATEGY='unsafe-best-match'
                                    UV_TOOL_DIR='/tmp/uvtools'
                                    UV_PYTHON_INSTALL_DIR='/tmp/uvpython'
                                    UV_CACHE_DIR='/tmp/uvcache'
                                }
                                when{
                                    equals expected: true, actual: params.RUN_CHECKS
                                    beforeAgent true
                                }
                                stages{
                                    stage('Setup'){
                                        environment{
                                            UV_PYTHON='3.11'
                                        }
                                        stages{
                                            stage('Setup Testing Environment'){
                                                steps{
                                                    mineRepository()
                                                    sh(
                                                        label: 'Create virtual environment',
                                                        script: '''python3 -m venv bootstrap_uv
                                                                   bootstrap_uv/bin/pip install --disable-pip-version-check uv
                                                                   bootstrap_uv/bin/uv venv venv
                                                                   . ./venv/bin/activate
                                                                   bootstrap_uv/bin/uv sync --active --frozen --group ci
                                                                   bootstrap_uv/bin/uv pip install --disable-pip-version-check uv
                                                                   rm -rf bootstrap_uv
                                                                   '''
                                                               )
                                                }
                                            }
                                            stage('Configuring Testing Environment'){
                                                steps{
                                                    sh(
                                                        label: 'Creating logging and report directories',
                                                        script: '''
                                                            mkdir -p logs
                                                            mkdir -p reports/coverage
                                                            mkdir -p reports/doctests
                                                            mkdir -p reports/mypy/html
                                                        '''
                                                    )
                                                }
                                            }
                                        }
                                    }
                                    stage('Running Tests'){
                                        parallel {
                                            stage('PyTest'){
                                                steps{
                                                    sh(script: '''. ./venv/bin/activate
                                                                   coverage run --parallel-mode --source getmarcapi -m pytest --junitxml=reports/pytest/junit-pytest.xml
                                                               ''',
                                                       returnStatus: true
                                                       )
                                                }
                                                post {
                                                    always {
                                                        junit 'reports/pytest/junit-pytest.xml'
                                                    }
                                                }
                                            }
                                            stage('Task Scanner'){
                                                steps{
                                                    recordIssues(tools: [taskScanner(highTags: 'FIXME', includePattern: 'getmarcapi"F/**/*.py', normalTags: 'TODO')])
                                                }
                                            }
                                            //   stage('Doctest'){
                                            //       steps {
                                            //           sh 'coverage run --parallel-mode --source getmarcapi -m sphinx -b doctest -d build/docs/doctrees docs reports/doctest -w logs/doctest.log'
                                            //       }
                                            //       post{
                                            //           always {
                                            //               recordIssues(tools: [sphinxBuild(name: 'Sphinx Doctest', pattern: 'logs/doctest.log', id: 'doctest')])
                                            //           }
                                            //       }
                                            //   }
                                            //   stage('Documentation Spell check'){
                                            //       steps {
                                            //           catchError(buildResult: 'SUCCESS', message: 'Found spelling issues in documentation', stageResult: 'UNSTABLE') {
                                            //               sh 'python -m sphinx docs reports/doc_spellcheck -b spelling -d build/docs/doctrees'
                                            //           }
                                            //       }
                                            //   }
                                            stage('pyDocStyle'){
                                                steps{
                                                    catchError(buildResult: 'SUCCESS', message: 'Did not pass all pyDocStyle tests', stageResult: 'UNSTABLE') {
                                                        sh(
                                                            label: 'Run pydocstyle',
                                                            script: '''. ./venv/bin/activate
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
                                            stage('MyPy') {
                                                steps{
                                                    catchError(buildResult: 'SUCCESS', message: 'mypy found issues', stageResult: 'UNSTABLE') {
                                                        // Note: this misses the uiucprescon.getmarc2 namespace package stubs because of this issue https://github.com/python/mypy/issues/10045
                                                        sh '''. ./venv/bin/activate
                                                              mypy -p getmarcapi --ignore-missing-imports --html-report reports/mypy/html/ > logs/mypy.log
                                                           '''
                                                    }
                                                }
                                                post {
                                                    always {
                                                        recordIssues(tools: [myPy(name: 'MyPy', pattern: 'logs/mypy.log')])
                                                        publishHTML([allowMissing: false, alwaysLinkToLastBuild: false, keepAll: false, reportDir: 'reports/mypy/html/', reportFiles: 'index.html', reportName: 'MyPy HTML Report', reportTitles: ''])
                                                    }
                                                }
                                            }
                                            stage('Bandit') {
                                                steps{
                                                    catchError(buildResult: 'SUCCESS', message: 'Bandit found issues', stageResult: 'UNSTABLE') {
                                                        sh(
                                                            label: 'Running bandit',
                                                            script: '''. ./venv/bin/activate
                                                                       bandit --format json --output reports/bandit-report.json --recursive getmarcapi || bandit -f html --recursive getmarcapi --output reports/bandit-report.html
                                                                    '''
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
                                                }
                                            }
                                            stage('PyLint') {
                                                steps{
                                                    catchError(buildResult: 'SUCCESS', message: 'Pylint found issues', stageResult: 'UNSTABLE') {
                                                        tee('reports/pylint.txt'){
                                                            sh(
                                                                script: '''. ./venv/bin/activate
                                                                           pylint getmarcapi -r n --persistent=n --verbose --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}"
                                                                           ''',
                                                                label: 'Running pylint'
                                                            )
                                                        }
                                                    }
                                                    sh(label: 'Running pylint for sonarqube',
                                                        script: '''. ./venv/bin/activate
                                                                   pylint getmarcapi  -r n --persistent=n --msg-template="{path}:{module}:{line}: [{msg_id}({symbol}), {obj}] {msg}" > reports/pylint_issues.txt
                                                                ''',
                                                        returnStatus: true
                                                    )
                                                }
                                                post{
                                                    always{
                                                        recordIssues(tools: [pyLint(pattern: 'reports/pylint.txt')])
                                                    }
                                                }
                                            }
                                            stage('Flake8') {
                                                steps{
                                                    catchError(buildResult: 'SUCCESS', message: 'Flake8 found issues', stageResult: 'UNSTABLE') {
                                                        sh(label: 'Running Flake8',
                                                           script: '''mkdir -p logs
                                                                      . ./venv/bin/activate
                                                                      flake8 getmarcapi --tee --output-file=logs/flake8.log
                                                                   '''
                                                           )
                                                    }
                                                }
                                                post {
                                                    always {
                                                        recordIssues(tools: [flake8(name: 'Flake8', pattern: 'logs/flake8.log')])
                                                    }
                                                }
                                            }
                                        }
                                        post{
                                            always{
                                                sh(
                                                    label: 'Combining coverage results',
                                                    script: '''. ./venv/bin/activate
                                                               coverage combine
                                                               coverage xml -o reports/coverage.xml
                                                               '''
                                                )
                                                recordCoverage(tools: [[parser: 'COBERTURA', pattern: 'reports/coverage.xml']])
                                            }
                                        }
                                    }
                                    stage('Sonarcloud Analysis'){
                                        options{
                                            lock('getmarcapi-sonarscanner')
                                        }
                                        environment{
                                            UV_INDEX_STRATEGY='unsafe-best-match'
                                            SONAR_SCANNER_HOME='/tmp/sonar'
                                            UV_TOOL_DIR='/tmp/uvtools'
                                            UV_PYTHON_INSTALL_DIR='/tmp/uvpython'
                                            UV_CACHE_DIR='/tmp/uvcache'
                                            SONAR_USER_HOME='/tmp/sonar'
                                            VERSION="${readTOML( file: 'pyproject.toml')['project'].version}"

                                        }
                                        when{
                                            allOf{
                                                equals expected: true, actual: params.USE_SONARQUBE
                                                expression{
                                                    try{
                                                        withCredentials([string(credentialsId: params.SONARCLOUD_TOKEN, variable: 'dddd')]) {
                                                            echo 'Found credentials for sonarqube'
                                                        }
                                                    } catch(e){
                                                        echo 'No credentials found for sonarqube.'
                                                        return false
                                                    }
                                                    return true
                                                }
                                            }
                                            beforeAgent true
                                            beforeOptions true
                                        }
                                        steps{
                                            milestone 1
                                            script{
                                                withSonarQubeEnv(installationName: 'sonarcloud', credentialsId: params.SONARCLOUD_TOKEN) {
                                                    withCredentials([string(credentialsId: params.SONARCLOUD_TOKEN, variable: 'token')]) {
                                                        sh(
                                                            label: 'Running Sonar Scanner',
                                                            script: "./venv/bin/pysonar -t \$token -Dsonar.projectVersion=${env.VERSION} -Dsonar.python.xunit.reportPath=./reports/pytest/junit-pytest.xml -Dsonar.python.coverage.reportPaths=./reports/coverage.xml  -Dsonar.python.mypy.reportPaths=./logs/mypy.log ${env.CHANGE_ID ? '-Dsonar.pullrequest.key=$CHANGE_ID -Dsonar.pullrequest.base=$BRANCH_NAME' : '-Dsonar.branch.name=$BRANCH_NAME' }",
                                                        )
                                                    }
                                                }
                                                timeout(time: 1, unit: 'HOURS') {
                                                    def sonarqubeResult = waitForQualityGate(abortPipeline: false, credentialsId: params.SONARCLOUD_TOKEN)
                                                    if (sonarqubeResult.status != 'OK') {
                                                       unstable "SonarQube quality gate: ${sonarqubeResult.status}"
                                                   }
                                                   if(env.BRANCH_IS_PRIMARY){
                                                       writeJSON file: 'reports/sonar-report.json', json: get_sonarqube_unresolved_issues('.sonar/report-task.txt')
                                                       recordIssues(tools: [sonarQube(pattern: 'reports/sonar-report.json')])
                                                   }
                                                }
                                            }
                                        }
                                        post {
                                            always{
                                                script{
                                                    if(fileExists('reports/sonar-report.json')){
                                                        stash includes: 'reports/sonar-report.json', name: 'SONAR_REPORT'
                                                        archiveArtifacts allowEmptyArchive: true, artifacts: 'reports/sonar-report.json'
                                                        recordIssues(tools: [sonarQube(pattern: 'reports/sonar-report.json')])
                                                    }
                                                }
                                            }
                                            cleanup{
                                                cleanWs(
                                                    deleteDirs: true,
                                                    patterns: [
                                                        [pattern: 'venv/', type: 'INCLUDE'],
                                                        [pattern: 'reports/', type: 'INCLUDE'],
                                                        [pattern: 'logs/', type: 'INCLUDE'],
                                                        [pattern: 'getmarcapi.dist-info/', type: 'INCLUDE'],
                                                        [pattern: '.scannerwork/', type: 'INCLUDE'],
                                                        [pattern: 'dist/', type: 'INCLUDE'],
                                                        [pattern: 'build/', type: 'INCLUDE'],
                                                        [pattern: '.coverage', type: 'INCLUDE'],
                                                        [pattern: '.eggs', type: 'INCLUDE'],
                                                        [pattern: '.pytest_cache/', type: 'INCLUDE'],
                                                        [pattern: '**/__pycache__/', type: 'INCLUDE'],
                                                        [pattern: '.mypy_cache/', type: 'INCLUDE'],
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
                            stage('Tox'){
                                when{
                                    equals expected: true, actual: params.TEST_RUN_TOX
                                }
                                environment{
                                    PIP_CACHE_DIR='/tmp/pipcache'
                                    UV_INDEX_STRATEGY='unsafe-best-match'
                                    UV_TOOL_DIR='/tmp/uvtools'
                                    UV_PYTHON_INSTALL_DIR='/tmp/uvpython'
                                    UV_CACHE_DIR='/tmp/uvcache'
                                }
                                steps{
                                    script{
                                        def envs = []
                                        node('docker && linux'){
                                            docker.image('python').inside('--mount source=python-tmp-getmarcapi,target=/tmp'){
                                                try{
                                                    checkout scm
                                                    sh(script: 'python3 -m venv venv && venv/bin/pip install --disable-pip-version-check uv')
                                                    envs = sh(
                                                        label: 'Get tox environments',
                                                        script: './venv/bin/uvx --quiet --with tox-uv tox list -d --no-desc',
                                                        returnStdout: true,
                                                    ).trim().split('\n')
                                                } finally{
                                                    cleanWs(
                                                        patterns: [
                                                            [pattern: 'venv/', type: 'INCLUDE'],
                                                            [pattern: '.tox', type: 'INCLUDE'],
                                                            [pattern: '**/__pycache__/', type: 'INCLUDE'],
                                                        ]
                                                    )
                                                }
                                            }
                                        }
                                        parallel(
                                            envs.collectEntries{toxEnv ->
                                                def version = toxEnv.replaceAll(/py(\d)(\d+)/, '$1.$2')
                                                [
                                                    "Tox Environment: ${toxEnv}",
                                                    {
                                                        node('docker && linux'){
                                                            checkout scm
                                                            def image
                                                            lock("${env.JOB_NAME} - ${env.NODE_NAME}"){
                                                                image = docker.build(UUID.randomUUID().toString(), '-f ci/docker/python/linux/Dockerfile --build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL --build-arg PIP_CACHE_DIR=/.cache/pip .')
                                                            }
                                                            try{
                                                                image.inside('--mount source=python-jenkins-tmp-getmarcapi,target=/tmp'){
                                                                    try{
                                                                        sh( label: 'Running Tox',
                                                                            script: """python3 -m venv venv && venv/bin/pip install uv
                                                                                       ./venv/bin/uv python install cpython-${version}
                                                                                       ./venv/bin/uv run --frozen --only-group tox --with tox-uv tox run -e ${toxEnv} --runner uv-venv-lock-runner
                                                                                    """
                                                                            )
                                                                    } catch(e) {
                                                                        sh(script: '''. ./venv/bin/activate
                                                                              uv python list
                                                                              '''
                                                                                )
                                                                        throw e
                                                                    } finally{
                                                                        cleanWs(
                                                                            patterns: [
                                                                                [pattern: 'venv/', type: 'INCLUDE'],
                                                                                [pattern: '.tox', type: 'INCLUDE'],
                                                                                [pattern: '**/__pycache__/', type: 'INCLUDE'],
                                                                            ]
                                                                        )
                                                                    }
                                                                }
                                                            } finally {
                                                                sh "docker rmi --no-prune ${image.id}"
                                                            }
                                                        }
                                                    }
                                                ]
                                            }
                                        )
                                    }
                                }
                            }
                        }
                    }
                }
            }
            stage('Distribution Packages'){
                when{
                    anyOf{
                        equals expected: true, actual: params.BUILD_PACKAGES
                    }
                    beforeAgent true
                }
                stages{
                    stage('Packaging sdist and wheel'){
                        agent {
                            // This needs to be a specific agent/Dockerfile
                            // container that npm is installed because it is part
                            // of the build chain
                            dockerfile {
                                filename 'ci/docker/python/linux/Dockerfile'
                                label 'linux && docker && x86'
                                additionalBuildArgs '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL --build-arg PIP_CACHE_DIR=/.cache/pip'
                                args '--mount source=python-jenkins-tmp-getmarcapi,target=/tmp'
                            }
                        }
                        environment{
                            PIP_CACHE_DIR='/tmp/pipcache'
                            UV_INDEX_STRATEGY='unsafe-best-match'
                            UV_TOOL_DIR='/tmp/uvtools'
                            UV_PYTHON_INSTALL_DIR='/tmp/uvpython'
                            UV_CACHE_DIR='/tmp/uvcache'
                        }
                        options{
                            retry(2)
                        }
                        steps{
                            timeout(5){
                                withEnv(['PIP_NO_CACHE_DIR=off']) {
                                    sh(label: 'Building Python Package',
                                       script: '''python -m venv venv
                                                  trap "rm -rf venv" EXIT
                                                  venv/bin/pip install --disable-pip-version-check uv
                                                  venv/bin/uv build
                                                  '''
                                       )
                               }
                            }
                        }
                        post{
                            always{
                                stash includes: 'dist/*.whl,dist/*.tar.gz,dist/*.zip', name: 'PYTHON_PACKAGES'
                            }
                            cleanup{
                                cleanWs(
                                    deleteDirs: true,
                                    patterns: [
                                        [pattern: '**/__pycache__/', type: 'INCLUDE'],
                                        [pattern: 'venv/', type: 'INCLUDE'],
                                        [pattern: 'dist/', type: 'INCLUDE']
                                        ]
                                    )
                            }
                        }
                    }
                    stage('Testing'){
                        when{
                            equals expected: true, actual: params.TEST_PACKAGES
                        }
                        environment{
                            PIP_CACHE_DIR='/tmp/pipcache'
                            UV_INDEX_STRATEGY='unsafe-best-match'
                            UV_TOOL_DIR='/tmp/uvtools'
                            UV_PYTHON_INSTALL_DIR='/tmp/uvpython'
                            UV_CACHE_DIR='/tmp/uvcache'
                        }
                        matrix {
                            axes {
                                axis {
                                    name 'PYTHON_VERSION'
                                    values  '3.9', '3.10', '3.11', '3.12', '3.13'
                                }
                                axis {
                                    name 'PACKAGE_TYPE'
                                    values 'wheel', 'sdist'
                                }
                                axis {
                                    name 'ARCHITECTURE'
                                    values 'arm64', 'x86_64'
                                }
                            }
                            when{
                                equals expected: true, actual: params["INCLUDE_LINUX-${ARCHITECTURE}".toUpperCase()]
                                beforeAgent true
                            }
                            stages {
                                stage('Test Wheel Package'){
                                    agent {
                                        docker {
                                            image 'python'
                                            label "linux && ${ARCHITECTURE} && docker"
                                            args '--mount source=python-tmp-getmarapi,target="/tmp"'
                                        }
                                    }
                                    when{
                                        expression{PACKAGE_TYPE == 'wheel'}
                                        beforeAgent true
                                    }
                                    steps{
                                        unstash 'PYTHON_PACKAGES'
                                        script{
                                            def installpkg = findFiles(glob: 'dist/*.whl')[0].path
                                            sh(
                                                label: 'Testing with tox',
                                                script: """python3 -m venv venv
                                                           trap "rm -rf venv" EXIT
                                                           venv/bin/pip install --disable-pip-version-check uv
                                                           trap "rm -rf venv && rm -rf .tox" EXIT
                                                           venv/bin/uv run --frozen --no-dev --only-group tox --with tox-uv tox --installpkg ${installpkg} -e py${PYTHON_VERSION.replace('.', '')}
                                                        """
                                            )
                                        }
                                    }
                                }
                                stage('Test Source Package'){
                                    agent {
                                        dockerfile {
                                            filename 'ci/docker/python/linux/Dockerfile'
                                            label 'linux && docker && x86'
                                            additionalBuildArgs '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL --build-arg PIP_CACHE_DIR=/.cache/pip'
                                            args '--mount source=python-jenkins-tmp-getmarcapi,target=/tmp'
                                        }
                                    }
                                    when{
                                        expression{PACKAGE_TYPE == 'sdist'}
                                        beforeAgent true
                                    }
                                    steps{
                                        unstash 'PYTHON_PACKAGES'
                                        script{
                                            def installpkg = findFiles(glob: 'dist/*.tar.gz')[0].path
                                            sh(
                                                label: 'Testing with tox',
                                                script: """python3 -m venv venv
                                                           trap "rm -rf venv" EXIT
                                                           venv/bin/pip install --disable-pip-version-check uv
                                                           trap "rm -rf venv && rm -rf .tox" EXIT
                                                           venv/bin/uvx --with tox-uv tox --installpkg ${installpkg} -e py${PYTHON_VERSION.replace('.', '')}
                                                        """
                                            )
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
            stage('Deployment'){
                when{
                    anyOf {
                        equals expected: true, actual: params.DEPLOY_PYPI
                        equals expected: true, actual: params.DEPLOY_TO_PRODUCTION
                    }
                }
                stages{
                    stage('Additional Deploy') {
                        when{
                            anyOf {
                                equals expected: true, actual: params.DEPLOY_PYPI
                                equals expected: true, actual: params.DEPLOY_TO_PRODUCTION
                            }
                        }
                        parallel{
                            stage('Deploy to pypi') {
                                agent {
                                    dockerfile {
                                        filename 'ci/docker/python/linux/Dockerfile'
                                        label 'linux && docker && x86'
                                        additionalBuildArgs '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL --build-arg PIP_CACHE_DIR=/.cache/pip'
                                    }
                                }
                                when{
                                    allOf{
                                        equals expected: true, actual: params.DEPLOY_PYPI
                                        equals expected: true, actual: params.BUILD_PACKAGES
                                    }
                                    beforeAgent true
                                    beforeInput true
                                }
                                options{
                                    retry(3)
                                }
                                input {
                                    message 'Upload to pypi server?'
                                    parameters {
                                        choice(
                                            choices: getPypiConfig(),
                                            description: 'Url to the pypi index to upload python packages.',
                                            name: 'SERVER_URL'
                                        )
                                    }
                                }
                                steps{
                                    unstash 'PYTHON_PACKAGES'
                                    pypiUpload(
                                        credentialsId: 'jenkins-nexus',
                                        repositoryUrl: SERVER_URL,
                                        glob: 'dist/*'
                                        )
                                }
                                post{
                                    cleanup{
                                        cleanWs(
                                            deleteDirs: true,
                                            patterns: [
                                                    [pattern: 'dist/', type: 'INCLUDE']
                                                ]
                                        )
                                    }
                                }
                            }
                            stage('Deploy Docker'){
                                when{
                                    equals expected: true, actual: params.DEPLOY_TO_PRODUCTION
                                    beforeAgent true
                                    beforeInput true
                                }
                                input {
                                    message 'Deploy to to server'
                                    parameters {
                                        string defaultValue: "${getVersion()}", description: 'Tag associated with the docker image', name: 'DOCKER_TAG', trim: true
                                        string defaultValue: 'getmarcapi', description: 'Name used for the image by Docker', name: 'IMAGE_NAME', trim: true
                                    }
                                }
                                stages{
                                    stage('Deploy to Private Docker Registry'){
                                        agent{
                                            label 'linux && docker && x86'
                                        }
                                        steps{
                                            script{
                                                withCredentials([string(credentialsId: 'ALMA_API_KEY', variable: 'API_KEY')]) {
                                                    writeFile(
                                                        file: 'api.cfg',
                                                        text: '''[ALMA_API]
                                                                 API_DOMAIN=https://api-na.hosted.exlibrisgroup.com
                                                                 API_KEY=${API_KEY}
                                                                 '''
                                                        )
                                                }
                                                configFileProvider([configFile(fileId: 'getmarc_deployapi', variable: 'CONFIG_FILE')]) {
                                                    def CONFIG = readJSON(file: CONFIG_FILE)['deploy']
                                                    def build_args = CONFIG['docker']['build']['buildArgs'].collect{"--build-arg=${it}"}.join(' ')
                                                    docker.withRegistry(CONFIG['docker']['server']['registry'], 'jenkins-nexus'){
                                                        def dockerImage = docker.build("${IMAGE_NAME}:${DOCKER_TAG}", "${build_args} .")
                                                        dockerImage.push()
                                                        dockerImage.push('latest')
                                                    }
                                                }
                                            }
                                        }
                                    }
                                    stage('Deploy to Production server'){
                                        agent{
                                            label 'linux && docker'
                                        }
                                        input {
                                            message 'Deploy to live server?'
                                            parameters {
                                                string defaultValue: 'getmarc2', description: 'Name of Docker container to use', name: 'CONTAINER_NAME', trim: true
                                                booleanParam defaultValue: true, description: 'Remove any containers with the same name first', name: 'REMOVE_EXISTING_CONTAINER'
                                            }
                                        }
                                        options{
                                            timeout(time: 1, unit: 'DAYS')
                                            retry(3)
                                        }
                                        steps{
                                            script{
                                                configFileProvider([configFile(fileId: 'getmarc_deployapi', variable: 'CONFIG_FILE')]) {
                                                    def CONFIG = readJSON(file: CONFIG_FILE).deploy
                                                    docker.withServer(CONFIG.docker.server.apiUrl, 'DOCKER_TYKO'){
                                                        if(REMOVE_EXISTING_CONTAINER == true){
                                                            sh(
                                                               label:"Stopping ${CONTAINER_NAME} if exists",
                                                               script: "docker stop ${CONTAINER_NAME}",
                                                               returnStatus: true
                                                            )
                                                        }
                                                        docker.withRegistry(CONFIG.docker.server.registry, 'jenkins-nexus'){
                                                            def imageName =  CONFIG.docker.server.registry.replace('http://', '') + "/${IMAGE_NAME}:${DOCKER_TAG}"
                                                            def containerPortsArg = CONFIG.docker.container.ports.collect{"-p ${it}"}.join(' ')
                                                            docker.image(imageName).run("${containerPortsArg} --name ${CONTAINER_NAME} --rm")
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}