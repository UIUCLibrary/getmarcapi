Set up Jenkins CI
=================

1) Install the plugins located in ci/jenkins/plugins.txt
2) Add ci/jenkins/casc/jenkins.yml to configuration-as-code/ in Manage Jenkins
3) Configure getmarc_deployapi config file
4) Create a new Multibranch Pipeline from New Item and use this project's git
   repository url for the source