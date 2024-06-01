# Bedrock-Streamlit-Redis-Application
 Streamlit Application for AWS Bedrock LLM with Redis

## Prerequisites
- AWS CLI installed and configured
- Docker and Docker Compose installed
- Access to AWS account and AWS Elastic Container Registry (ECR)

## 1. Starting an EC2 Instance
Before proceeding, ensure that your AWS CLI is configured. You can set it up by running:

```bash
aws configure
```
Enter your AWS Access Key, Secret Key, default region, and output format when prompted.

## 2. Connecting to Docker via AWS ECR
Authenticate Docker to your AWS Elastic Container Registry using the following command:
```bash
aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <aws_account_id>.dkr.ecr.<region>.amazonaws.com
```
Replace `<region>` with your AWS region (e.g., us-west-2) and `<aws_account_id>` with your actual AWS account ID.

## 3. SSH Configuration for Easy Access
To simplify the SSH process into your EC2 instance, configure your SSH as follows:
```
Host streamlit-app
    HostName <EC2_Instance_IP>
    User ec2-user
    IdentityFile '<path_to_your_pem_file>'
```
Replace `<EC2_Instance_IP>` with your instance's IP address and `<path_to_your_pem_file>` with the path to your .pem file.

```
Host streamlit-app
    HostName 54.242.41.58
    User ec2-user
    IdentityFile '/Users/jyeo_/.ssh/jon-mbp.pem'
```

## 4. Installing and Configuring Docker
Gain root access and install Docker:
```bash
sudo -i
yum install docker
```
Install Docker Compose:
```bash
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

## 5. Running Docker Containers
Navigate to your project directory where your `docker-compose.yml` is located and run:
```bash
docker-compose pull
docker-compose up -d
```

## 6. Managing Docker Containers
To stop your Docker containers:
```bash
docker-compose stop
```
To remove your Docker containers completely:
```bash
docker-compose down
```

## Accessing Your Application
Visit your application via:
```
https://jyeo.capeguy.net/
```

End of documentation.
