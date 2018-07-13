
node {
    docker.withRegistry('https://newknowledge.azurecr.io', 'acr-creds') {
    
        git url: "https://github.com/NewKnowledge/nk_unicorn.git", credentialsId: '055e98d5-ce0c-45ef-bf0d-ddc6ed9b634a', branch: "${BRANCH_NAME}"
    
        sh "git rev-parse HEAD > .git/commit-id"
        def commit_id = readFile('.git/commit-id').trim()
        def clean_branchname = BRANCH_NAME.replaceAll("/", "-")
        println commit_id
    
        stage "build_docker_image"
        def http_image = docker.build("ds/unicorn-http:${clean_branchname}", "-f http.dockerfile .")
    
        stage "publish_docker_image"
        def images = [http_image]
        for (image in images) {
            image.push "${clean_branchname}"
            image.push "${commit_id}"
            if ("${BRANCH_NAME}" == "master") {
                image.push 'latest'
            }
        }
    }
}