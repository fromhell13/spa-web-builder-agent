import logging
import boto3
import os
import randomname
from progress.spinner import PixelSpinner
from dotenv import load_dotenv

# AWS Strands Agent SDK
from strands import Agent
from strands.models import BedrockModel
from strands_tools import file_write, shell

# Custom tools and prompts
from utils.prompts import HTML_GENERATOR_PROMPT, DOCKER_GENERATOR_PROMPT, ECR_PUSH_PROMPT, IAC_AGENT_PROMPT

"""
# Enables Strands debug log level
logging.getLogger("strands").setLevel(logging.DEBUG)

# Sets the logging format and streams logs to stderr
logging.basicConfig(
    format="%(levelname)s | %(name)s | %(message)s", handlers=[logging.StreamHandler()]
)
"""

# Create a BedrockModel
bedrock_model = BedrockModel(
    model_id="us.anthropic.claude-3-5-sonnet-20240620-v1:0",
    region_name="us-east-1",
    temperature=0.2,
)

# Main Orchestrator workflow
def run_builder_workflow(user_input):
    """Run SPA Web builder agents workflow
    
    Args:
        user_input: user SPA web description
    
    Return:
        str: Output, link and result of SPA web built by the agents
    """

    ##################################
    ## Step 1: HTML Generator Agent ##
    ##################################
    print("\n🧠 Step 1: Generate HTML file....")
    
    # Execute HTML Generator Agent
    try:
        ## Initiate html generator agent
        html_generator_agent = Agent(
            bedrock_model,
            system_prompt=HTML_GENERATOR_PROMPT,
            callback_handler=None,
            tools=[file_write]
        )
    
        ## run the HTML Generator Agent
        html_generator_agent(
            f"User Description: {user_input}"
        )
        print("✅ Generate HTML file completed")
    except Exception as e:
        print(f"HTML Generator Agent error: {e}")
    
    #################################
    ## Step 2: Generate Dockerfile ##
    #################################
    print("\n🧠 Step 2: Generate Dockerfile....")
    
    # Execute Dockerfile Generator Agent
    try:
        ## Initiate dockerfile generator agent
        docker_generator_agent = Agent(
            bedrock_model,
            system_prompt=DOCKER_GENERATOR_PROMPT,
            callback_handler=None,
            tools=[file_write]
        )
        docker_generator_agent(
            "Run the Dockerfile generator"
        )
        
        print("✅ Generate Dockerfile completed")
    except Exception as e:
        print(f"HTML Generator Agent error: {e}")
    
    #################################
    ## Step 3: Push Dockerfile     ##
    #################################
    print("\n🧠 Step 3: Build and Push Image to AWS ECR....")
    
    # Execute Build & Push Generator Agent
    try:
        ## Initiate agent
        ecr_push_agent = Agent(
            bedrock_model,
            system_prompt=ECR_PUSH_PROMPT,
            callback_handler=None,
            tools=[shell]
        )
    
        ecr_push_agent("Please run the AWS cli")
        
        print("✅ Build and push image to ECR completed")
    except Exception as e:
        print(f"HTML Generator Agent error: {e}")
        
    ############################################
    ## Step 4: Create Terraform file & deploy ##
    ############################################
    print("\n🧠 Step 4: Generate Terraform file and deploy to AWS....")
    
    # Execute Agent
    try:
        ## Initiate agent
        iac_agent = Agent(
            bedrock_model,
            system_prompt=IAC_AGENT_PROMPT,
            callback_handler=None,
            tools=[file_write, shell]
        )
    
        iac_agent_response = iac_agent("Please run the terraform agent")
        end_result = str(iac_agent_response)
        
        print("✅ Generate Terraform file and deploy completed")
        
        return end_result
    except Exception as e:
        print(f"Terraform Agent error: {e}")
    
    
    return None
    
if __name__ == "__main__":
    # Print welcome message
    print("\n🤖 Agentic Workflow: Web Builder Assistant 🤖\n")
    print("The agent will help you create a SPA web based on your description\n")
    print("🗨️ Please add the description below")
    # Interactive loop
    while True:
        try:
            user_input = input("\n> ")
            if user_input.lower() == "exit":
                print("\nGoodbye!👋")
                break
            
            # Process the input through the workflow of agents
            end_result = run_builder_workflow(user_input)
            if end_result:
                print(end_result)
        except KeyboardInterrupt:
            print("\n\nExecution interrupted. Exiting...")
            break
        except Exception as e:
            print(f"\nAn error occurred: {str(e)}")
            print("Please try a different request.")