
node {
    docker.withRegistry('https://newknowledge.azurecr.io', 'acr-creds') {
    
        git url: "https://github.com/NewKnowledge/nk_unicorn.git", credentialsId: '055e98d5-ce0c-45ef-bf0d-ddc6ed9b634a'
    
        sh "git rev-parse HEAD > .git/commit-id"
        def commit_id = readFile('.git/commit-id').trim()
        println commit_id
    
        stage "build_docker_image"
        def http_image_gpu = docker.build("ds/unicorn-http-gpu", "-f http.gpu.dockerfile .")
        def http_image_slim = docker.build("ds/unicorn-http-slim", "-f http.slim.dockerfile .")
    
        stage "publish_docker_image"
        def images = [http_image_slim, http_image_gpu]
        def branches = sh(returnStdout: true, script: "git branch --contains ${commit_id}")
        for (image in images) {
            image.push "${BRANCH_NAME}"
            image.push "${commit_id}"
            if ("${BRANCH_NAME}" == "master") {
                image.push 'latest'
            }
        }
    }
}