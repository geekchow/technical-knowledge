script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "$script_dir"

docker run \
    -p 8080:8080 \
    -p 50000:50000 \
    -v "${script_dir}"/jenkins_home:/var/jenkins_home \
    phil-jenkins-master:latest