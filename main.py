from agents.github_actions_agent import GitHubActionsAgent, GitHubActionsConfig
from agents.dockerfile_agent import DockerfileAgent, DockerfileConfig
from agents.build_predictor_agent import BuildPredictorAgent, BuildPredictorConfig
from agents.build_status_agent import BuildStatusAgent, BuildStatusConfig
import os
import datetime
import subprocess
from dotenv import load_dotenv

# Load environment variables from .env file and GitHub Actions
load_dotenv()

def main():
    print("🤖 DevOps AI Team Starting Up...")

    # 1. Create GitHub Actions Pipeline
    print("\n1️⃣ GitHub Actions Agent: Creating CI/CD Pipeline...")
    gha_config = GitHubActionsConfig(
        workflow_name="CI Pipeline",
        python_version="3.13.0",
        run_tests=True,
        groq_api_endpoint=os.getenv("GROQ_API_ENDPOINT"),
        groq_api_key=os.getenv("GROQ_API_KEY")
    )
    gha_agent = GitHubActionsAgent(config=gha_config)
    pipeline = gha_agent.generate_pipeline()

    with open(".github/workflows/CI3.yml", "w", encoding="utf-8") as f:
        f.write(pipeline)
    print("✅ CI/CD Pipeline created!")

    # 2. Create Dockerfile
    print("\n2️⃣ Dockerfile Agent: Creating Dockerfile...")
    docker_config = DockerfileConfig(
        base_image="nginx:alpine",
        expose_port=80,
        copy_source="./html",
        work_dir="/usr/share/nginx/html",
        groq_api_endpoint=os.getenv("GROQ_API_ENDPOINT"),
        groq_api_key=os.getenv("GROQ_API_KEY")
    )
    docker_agent = DockerfileAgent(config=docker_config)
    dockerfile = docker_agent.generate_dockerfile()

    with open("Dockerfile", "w") as f:
        f.write(dockerfile)
    print("✅ Dockerfile created!")

    # 3. Build and Push Docker Image
    print("\n3️⃣ Build Status Agent: Building and pushing Docker image...")

    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    version_tag = f"v1-{timestamp}"

    dockerhub_user = os.getenv("DOCKERHUB_USERNAME")
    dockerhub_pass = os.getenv("DOCKERHUB_PASSWORD")

    # Check if credentials are present
    if not dockerhub_user or not dockerhub_pass:
        print("❌ Error: DockerHub credentials are not set in environment variables.")
        print("➡️ Please set DOCKERHUB_USERNAME and DOCKERHUB_PASSWORD in GitHub Secrets.")
        exit(1)

    full_image_tag = f"{dockerhub_user}/myapp:{version_tag}"

    status_config = BuildStatusConfig(image_tag=full_image_tag)
    status_agent = BuildStatusAgent(config=status_config)

    # Docker login
    print("🔐 Logging in to Docker Hub...")
    login_result = subprocess.run(
        ["docker", "login", "--username", dockerhub_user, "--password-stdin"],
        input=dockerhub_pass,
        capture_output=True,
        text=True
    )
    if login_result.returncode != 0:
        print("❌ Docker login failed:")
        print(login_result.stderr)
        exit(1)
    print("✅ Docker login successful.")

    # Build Docker image
    print(f"🔨 Building Docker image: {full_image_tag}...")
    build_result = subprocess.run(
        ["docker", "build", "-t", full_image_tag, "."],
        capture_output=True,
        text=True
    )
    if build_result.returncode != 0:
        print("❌ Docker build failed:")
        print(build_result.stderr)
        exit(1)
    print("✅ Docker image built successfully.")

    # Push Docker image
    print(f"📦 Pushing Docker image: {full_image_tag}...")
    push_result = subprocess.run(
        ["docker", "push", full_image_tag],
        capture_output=True,
        text=True
    )
    if push_result.returncode != 0:
        print("❌ Docker push failed:")
        print(push_result.stderr)
        exit(1)
    print("✅ Docker image pushed successfully!")

    # Check build status
    status = status_agent.check_build_status()
    print(f"📊 Build Status: {status}")

    # 4. Predict Build Success/Failure
    print("\n4️⃣ Build Predictor Agent: Analyzing build patterns...")
    predictor_config = BuildPredictorConfig(
        model="llama3-8b-8192",
        groq_api_endpoint=os.getenv("GROQ_API_ENDPOINT"),
        groq_api_key=os.getenv("GROQ_API_KEY")
    )
    predictor_agent = BuildPredictorAgent(config=predictor_config)

    build_data = {
        "dockerfile_exists": True,
        "ci_pipeline_exists": True,
        "last_build_status": status,
        "python_version": "3.13.0",
        "dependencies_updated": True
    }

    prediction = predictor_agent.predict_build_failure(build_data)
    print(f"🔮 Build Prediction: {prediction}")

    print("\n✨ DevOps AI Team has completed their tasks!")

if __name__ == "__main__":
    main()
