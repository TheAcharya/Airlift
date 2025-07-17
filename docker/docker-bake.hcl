group "default" {
    targets = ["airlift_python"]
}

target "airlift_python" {
  context = "."
  dockerfile = "docker/Dockerfile"
  tags = ["airlift_python:latest"]
}