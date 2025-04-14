provider "aws" {
  region = "us-east-1"
}

# Create a VPC
resource "aws_vpc" "flask_vpc" {
  cidr_block = "10.0.0.0/16"
  enable_dns_support = true
  enable_dns_hostnames = true
}

# Create an ECS Cluster
resource "aws_ecs_cluster" "flask_cluster" {
  name = "flask-cluster"
}

# Create an Elastic Container Registry (ECR)
resource "aws_ecr_repository" "flask_ecr_repo" {
  name = "flask-repo"
}

# Create a Security Group for ECS
resource "aws_security_group" "flask_sg" {
  name   = "flask-sg"
  vpc_id = aws_vpc.flask_vpc.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Define an ECS Task Definition
resource "aws_ecs_task_definition" "flask_task" {
  family                   = "flask-app"
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"
  requires_compatibilities = ["FARGATE"]

  container_definitions = jsonencode([
    {
      name      = "flask-container"
      image     = "${aws_ecr_repository.flask_ecr_repo.repository_url}:latest"
      essential = true
      portMappings = [
        {
          containerPort = 80
          hostPort      = 80
        }
      ]
    }
  ])
}

# Define an ECS Service to run the task
resource "aws_ecs_service" "flask_service" {
  name            = "flask-service"
  cluster         = aws_ecs_cluster.flask_cluster.id
  task_definition = aws_ecs_task_definition.flask_task.arn
  desired_count   = 1
  launch_type     = "FARGATE"
  network_configuration {
    subnets          = [aws_vpc.flask_vpc.subnet_ids[0]]
    security_groups  = [aws_security_group.flask_sg.id]
    assign_public_ip = true
  }
}

# Outputs for easy access
output "ecr_repository_url" {
  value = aws_ecr_repository.flask_ecr_repo.repository_url
}

output "ecs_service_url" {
  value = aws_ecs_service.flask_service.id
}
