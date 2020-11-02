def getToxEnvs(){
    def envs
    if(isUnix()){
        envs = sh(returnStdout: true, script: "tox -l").trim().split('\n')
    } else{
        envs = bat(returnStdout: true, script: "@tox -l").trim().split('\n')
    }
    envs.collect{
        it.trim()
    }
    return envs
}


def getToxTestsParallel(envNamePrefix, label, dockerfile, dockerArgs){
    script{
        def envs
        def originalNodeLabel
        node(label){
            originalNodeLabel = env.NODE_NAME
            checkout scm
            def dockerImageName = "tox${currentBuild.projectName}"
            def dockerImage = docker.build(dockerImageName, "-f ${dockerfile} ${dockerArgs} .")
            dockerImage.inside{
                envs = getToxEnvs()
            }
            if(isUnix()){
                sh(
                    label: "Removing Docker Image used to run tox",
                    script: "docker image ls ${dockerImageName}"
                )
            } else {
                bat(
                    label: "Removing Docker Image used to run tox",
                    script: """docker image ls ${dockerImageName}
                               """
                )
            }
        }
        echo "Found tox environments for ${envs.join(', ')}"
        def dockerImageForTesting
        node(originalNodeLabel){
            def dockerImageName = "tox"
            checkout scm
            dockerImageForTesting = docker.build(dockerImageName, "-f ${dockerfile} ${dockerArgs} . ")

        }
        echo "Adding jobs to ${originalNodeLabel} with ${dockerImageForTesting}"
        def jobs = envs.collectEntries({ tox_env ->
            def tox_result
            def githubChecksName = "Tox: ${tox_env} ${envNamePrefix}"
            def jenkinsStageName = "${envNamePrefix} ${tox_env}"

            [jenkinsStageName,{
                node(originalNodeLabel){
                    checkout scm
                    dockerImageForTesting.inside{
                        try{
                            publishChecks(
                                conclusion: 'NONE',
                                name: githubChecksName,
                                status: 'IN_PROGRESS',
                                summary: 'Use Tox to test installed package',
                                title: 'Running Tox'
                            )
                            if(isUnix()){
                                sh(
                                    label: "Running Tox with ${tox_env} environment",
                                    script: "tox  -vv --parallel--safe-build --result-json=tox_result.json -e $tox_env"
                                )
                            } else {
                                bat(
                                    label: "Running Tox with ${tox_env} environment",
                                    script: "tox  -vv --parallel--safe-build --result-json=tox_result.json -e $tox_env "
                                )
                            }
                        } catch (e){
                            publishChecks(
                                name: githubChecksName,
                                summary: 'Use Tox to test installed package',
                                text: generateToxReport(tox_env, 'tox_result.json'),
                                conclusion: 'FAILURE',
                                title: 'Failed'
                            )
                            throw e
                        }
                        def checksReportText = generateToxReport(tox_env, 'tox_result.json')
                        echo "publishing \n${checksReportText}"
                        publishChecks(
                                name: githubChecksName,
                                summary: 'Use Tox to test installed package',
                                text: "${checksReportText}",
                                title: 'Passed'
                            )
                    }
                }
            }]
        })
        return jobs
    }
}