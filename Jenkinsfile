
pipeline{
    agent any

    environment {
        MSTEAMS_HOOK = "https://quatrixglobal.webhook.office.com/webhookb2/61fe461b-4257-4bb2-bc64-6b73fbe8351b@a96a137b-5bac-4d28-8f5b-9ded43babdcf/JenkinsCI/c7c81ddb9cd34aa2b6603d178c289273/a423d303-77b2-4f8b-af1e-7f98950259fb/V2X-5LS4W0EzmjeaB5DLS8DOK5e668MlnGiemHWgPbufc1"

    }
    stages{
        stage("setup environment"){
            steps{
               
                sh '''
                    

                    pwd


                    python3 -m venv venv

                    . venv/bin/activate

                    


                '''
                

            }
            
        }

        stage("run the tests"){
            steps{
                sh '''
                    
                    . venv/bin/activate

                    pytest -q --tb=short odoo_sandbox/carrier_module

                    echo "Finished"

                '''
            }
        }
    }
    post{
        always{
            echo "========always========"
        }
        success{
            office365ConnectorSend(
                status: "Build Status",
                webhookUrl: "${MSTEAMS_HOOK}",
                message: "Build successful",
                color: "#00FF00"
            )

        }
        failure{
             office365ConnectorSend(
                status: "Build Status",
                webhookUrl: "${MSTEAMS_HOOK}",
                message: "Build failed",
                color: "#FF0000 "
            )

        }
    }
}
