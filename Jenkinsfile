pipeline{
    agent any

    environment {
        MSTEAMS_HOOK = "https://quatrixglobal.webhook.office.com/webhookb2/61fe461b-4257-4bb2-bc64-6b73fbe8351b@a96a137b-5bac-4d28-8f5b-9ded43babdcf/JenkinsCI/c7c81ddb9cd34aa2b6603d178c289273/a423d303-77b2-4f8b-af1e-7f98950259fb/V2X-5LS4W0EzmjeaB5DLS8DOK5e668MlnGiemHWgPbufc1"

    }
    stages{
        stage("setup environment"){
            steps{
                script{
                    if (env.BRANCH_NAME == 'Main'){

                        echo "Setting up Main Branch"

                         sh '''
                    
                             /home/kkiarie/scripts/jenkins.sh

                            '''    

                    }

                    if (env.BRANCH_NAME == 'Work-pc'){

                        sh '''
                    
                            /home/kkiarie/scripts/jenkins.sh

                            '''    
                    }

                    if (env.BRANCH_NAME == 'Home_pc'){
                        sh '''
                    
                            pwd

                            python3 -m venv venv

                            . venv/bin/activate

                            pip install -r odoo_sandbox/requirements.txt

                            '''    
                    }
                }
               
            }
            
        }

        stage("run the tests"){
            steps{
                script{
                     if (env.BRANCH_NAME == 'Main'){
                        sh '''
                    
                            /home/kkiarie/scripts/run_tests.sh

                        '''
                     }


                    if (env.BRANCH_NAME == 'Work-pc'){

                        sh '''
                    
                            /home/kkiarie/scripts/run_tests.sh

                            echo "Script ran without errors!!!"

                        '''
                    }

                    if (env.BRANCH_NAME == 'Home_pc'){
                        sh '''
                    
                            . venv/bin/activate

                            pytest -q --tb=short odoo_sandbox/authentication/test_login.py::test_valid_login

                            echo "test Work-pc branch run tests2"

                        '''
                    }


                }
                
            }
        }

        stage("Deploy changes"){
            steps{
                script{
                    if (env.BRANCH_NAME == 'Main'){
                                
                        sh '''

                            ssh kkiarie@sandbox.erp.quatrixglobal.com << EOF

                            whoami

                            sudo systemctl stop odoo15

                            cd /opt/odoo15

                            /home/kkiarie/.pyenv/versions/odoo15env/bin/python3 ./odoo-bin -c /etc/odoo15/odoo.conf -d odoo15sandbox -u quatrix_dispatch_module --stop-after-init

                            sudo systemctl start odoo15

                            exit

                            EOF
                        '''
                    }

                    if (env.BRANCH_NAME == 'Work-pc'){

                        sh '''
                            ssh kkiarie@sandbox.erp.quatrixglobal.com << EOF 

                            cd /opt/custom_modules/quatrix-odoo

                            git remote -v

                            git branch

                            git fetch origin

                            git checkout Main

                            git merge origin/Work-pc --no-ff -m "JENKINS: Merge Work-pc into Main"

                            git push origin Main
                            
                            exit

                            EOF
                        
                           '''
                    }

                    if (env.BRANCH_NAME == 'Home-pc'){

                        sh '''

                        ssh kkiarie@sandbox.erp.quatrixglobal.com << EOF

                            cd /opt/custom_modules/quatrix-odoo

                            git branch

                            git fetch origin

                            git checkout Main

                            git merge origin/Home-pc --no-ff -m "JENKINS: Merge Home-pc into Main"

                            git push origin Main

                            exit

                            EOF

                            '''
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
                message: "Build failed",
                color: "#FF0000 ",
            )
        }
    }
}