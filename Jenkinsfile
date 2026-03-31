pipeline{
    agent any

    environment {
        MSTEAMS_HOOK = "https://quatrixglobal.webhook.office.com/webhookb2/61fe461b-4257-4bb2-bc64-6b73fbe8351b@a96a137b-5bac-4d28-8f5b-9ded43babdcf/JenkinsCI/c7c81ddb9cd34aa2b6603d178c289273/a423d303-77b2-4f8b-af1e-7f98950259fb/V2X-5LS4W0EzmjeaB5DLS8DOK5e668MlnGiemHWgPbufc1"

    }
    stages{
        stage("Setup Environment!!"){
            steps{
                script{
                    sh '''

                    /home/kkiarie/scripts/ci_script.sh stage_setup_environment

                    echo "i'm here!!!!! New setup to implement!!! Installed python3 venv. Changed requirements.txt path.Changed test directory path.Installed google-chrome and chromedriver.Added .env to test dir.Changed tes_login to test_invalid_login in script."

                    '''
                }
                }
               
            }
            
        
        stage("run the tests"){
            steps{
                script{
                     
                    sh '''
                        pwd

                        /home/kkiarie/scripts/ci_script.sh stage_run_tests

                    '''

                }
                
            }
        }

        stage("Deploy changes!!!"){
            steps{
                script{
                    if (env.BRANCH_NAME == 'Main'){
                        sshagent(['sandbox-ssh']){        
                        sh '''

                            ssh kkiarie@sandbox.erp.quatrixglobal.com /opt/custom_modules/quatrix-odoo/scripts/deploy_script.sh stage_deploy_changes

                        '''
                    }
                    }

                    else {
                        sshagent(['sandbox-ssh']){
                        sh '''

                            ssh kkiarie@sandbox.erp.quatrixglobal.com /opt/custom_modules/quatrix-odoo/scripts/deploy_script.sh stage_merge_changes

                        '''

                    }
                    }



                }
                
            }
        }
    }

    
    post{
        always{
            echo "========Build done========"
        }
        success{
            office365ConnectorSend(
                status: "Build Status",
                webhookUrl: "${MSTEAMS_HOOK}",
                message: "Build successful",
                color: "#00FF00",
            )
        }
        failure{
            office365ConnectorSend(
                status: "Build Status",
                webhookUrl: "${MSTEAMS_HOOK}",
                message: "Build failed. Check build console on jenkins to see more details.",
                color: "#FF0000 ",
            )
        }
    }

}
