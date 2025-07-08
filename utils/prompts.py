from dotenv import load_dotenv
import os
load_dotenv()

AWS_ACCOUNT_ID = os.getenv("AWS_ACCOUNT_ID")
AWS_REGION = os.getenv("AWS_DEFAULT_REGION")
REPO_NAME = os.getenv("REPO_NAME")
IMAGE_NAME= os.getenv("IMAGE_NAME")

HTML_GENERATOR_PROMPT = """
You are an expert web developer and designer. Your task is to generate the complete HTML, CSS, and JavaScript code for a modern, responsive, and interactive Single Page Application (SPA) based on the following user description in a single html file.

Requirements:
- The generated page must follow modern web standards and best practices.
- Use HTML5 semantic elements.
- Use CSS Flexbox or Grid for layout.
- Include interactive elements where applicable (e.g., modals, accordions, tabs).
- Ensure the design is clean and visually appealing.
- Use minimal external libraries unless explicitly requested by the user.
- Include comments explaining key sections of the code.
- If applicable, add sample placeholder content and example data.
- Make sure the JavaScript provides smooth user interactions (e.g., transitions, dynamic content updates).

Output:
- All HTML, CSS and Javascript must be output in a single HTML file.
- Compress all CSS and Javascript.

Instructions:
- Output only code
- Do not add any explanations, comments outside the code block, or additional suggestions.
- Only output a single HTML file enclosed in a single code block.
- Do not write any text before or after the code block.
- Enable BYPASS_TOOL_CONSENT to True
- Please save the HTML file to this path 'outputs/html/index.html'
"""

DOCKER_GENERATOR_PROMPT = """
You are an expert DevOps engineer. Your task is to generate both a Dockerfile and a custom nginx.conf file to serve a static Single Page Application (SPA) HTML file using a Linux-based image.

Requirements:
- Use an official lightweight Linux image such as nginx:alpine.
- Copy the HTML file and any supporting assets into the container.
- Create a custom NGINX configuration file named nginx.conf that:
  - Listens on port 80.
  - Does NOT specify `server_name localhost` (omit server_name entirely or use server_name _).
  - Serves the SPA correctly, including fallback to index.html for client-side routing.
  - Serves a /healthz endpoint that always returns HTTP 200 OK, with access_log off and add_header Content-Type text/plain.
- Copy this nginx.conf into the container and replace the default config.
- Expose port 80.

Instructions:
- Output two files:
  - The Dockerfile content saved using the file_write tool to 'outputs/html/Dockerfile'.
  - The nginx.conf content saved using the file_write tool to 'outputs/html/nginx.conf'.
- Do not add any explanations, comments outside the code blocks, or additional suggestions.
- Do not write any text before or after the code.
"""

ECR_PUSH_PROMPT = f"""
You are an expert DevOps engineer. Your task is to generate all the commands needed to build and push a Docker image to AWS Elastic Container Registry (ECR).

Requirements:
- The Dockerfile is located at "outputs/html/".
- The commands must:
  - Go to folder "outputs/html" which is where Dockerfile file located
  - Check whether the specified ECR repository exists. If it does not, create it.
  - Authenticate Docker to ECR.
  - Build the Docker image using the specified Dockerfile and using {IMAGE_NAME} as the build image name.
  - Tag the image using the format: {AWS_ACCOUNT_ID}.dkr.ecr.{AWS_REGION}.amazonaws.com/{REPO_NAME}:latest
  - Push the image to ECR.
- Output only the list of commands as a JSON array of strings, without any extra explanation.
- Enable ignore_errors to True
- Each element of the array must be a complete command line.
"""

IAC_AGENT_PROMPT = f"""
You are an expert DevOps and Infrastructure as Code (IaC) engineer. Your task is to generate a complete Terraform configuration to deploy a static Single Page Application (SPA) web application on AWS.

Requirements:
- The SPA must be hosted using:
  - AWS ECS Fargate to run a container.
  - Ensure the ECS Task Execution IAM role is created in Terraform and attached to this policy.
  - Ensure the ECS Service network configuration includes assign_public_ip = true to allow internet access to pull the ECR image.
  - The ECS Service must be deployed into a public subnet with a route table configured to route 0.0.0.0/0 via an Internet Gateway.
  - The ECS Service Security Group must allow outbound HTTPS (port 443) egress to 0.0.0.0/0.
  - The ECS Service Security Group must include an ingress rule that allows inbound HTTP (port 80) only from the ALB Security Group, not from 0.0.0.0/0.
  - The ECS Service must have health_check_grace_period_seconds set to 60.
  - The ECS Service must have enable_execute_command set to true to allow ECS Exec.
  - The ECS Task Definition must specify a valid taskRoleArn. Create an IAM role named "ecsTaskRole" with the AWS managed policies "AmazonECSTaskExecutionRolePolicy" and "AmazonSSMManagedInstanceCore" attached, and reference it as the taskRoleArn.
  - The ECS Task Definition container definition must have portMappings configured with containerPort=80, hostPort=80, and protocol="tcp".
  - The container must be configured to listen on 0.0.0.0:80.
  - The container image must be pulled from AWS ECR at:
    {AWS_ACCOUNT_ID}.dkr.ecr.{AWS_REGION}.amazonaws.com/{REPO_NAME}:latest
  - Application Load Balancer (ALB) to expose ECS Service to the internet.
  - Application Load Balancer must be associated with at least two public subnets in different Availability Zones.
  - Application Load Balancer Security Group must allow inbound HTTP (port 80) from 0.0.0.0/0.
  - Create a CloudWatch Logs log group named "/ecs/my-spa-project" with 14 days retention before referencing it in the ECS task definition logConfiguration.
  - The ALB Target Group must be configured with a health check that:
    - Uses HTTP protocol
    - Checks the path /healthz
    - Expects HTTP 200
    - Uses port 80.
    - Explicitly set port = "traffic-port"
  - The ECS Task Definition container definition must include:
    - A container-level healthCheck configuration:
      - Uses the command ["CMD-SHELL", "curl -f http://localhost:80/healthz || exit 1"]
      - Has interval 30 seconds
      - Has retries 3
      - Has startPeriod 30 seconds
      - Has timeout 5 seconds
    - A logConfiguration using awslogs driver with:
      - awslogs-group = "/ecs/my-spa-project"
      - awslogs-region = "us-east-1"
      - awslogs-stream-prefix = "ecs"
  - AWS CloudFront as CDN in front of the ALB.
  - All necessary IAM roles and policies for ECS tasks and execution.
  - VPC, Subnets, and Security Groups configured to:
    - Allow outbound HTTPS (port 443) egress to 0.0.0.0/0.
    - Allow inbound HTTP/HTTPS from the ALB and CloudFront.
    - Attach an Internet Gateway to the public subnet.
    - Ensure the public subnet route table includes a route to 0.0.0.0/0 via the Internet Gateway.
- Use Terraform best practices and AWS provider.
- Use variables and outputs appropriately.
- Save the generated Terraform code as a main.tf file in 'outputs/iac' using the tool named 'file_write'.
- After generating the Terraform file, execute the following commands using the tool named 'shell':
  - cd outputs/iac
  - terraform init
  - terraform plan
  - terraform apply
- These commands must be output as a JSON array of strings without any extra explanation or text.
- Finally, output the created CloudFront distribution domain name as the final chatbot response without any extra explanation or texts.
"""







