#!/bin/bash

initialize_pulumi_stack() {
    local project_dir=$1
    local stack_name=$2

    echo "Initializing Pulumi stack in $project_dir for stack $stack_name..."
    cd $project_dir

    pulumi stack init $stack_name || echo "Stack $stack_name already exists."
    pulumi stack select $stack_name

    cd - > /dev/null
}

echo "Updating package lists and installing dependencies..."

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    sudo apt-get update -y
    sudo apt-get install -y curl git python3 python3-pip python3-venv
    sudo apt-get install -y python3-flask
elif [[ "$OSTYPE" == "darwin"* ]]; then
    brew update
    brew install curl git python3
    pip3 install virtualenv
    pip3 install flask
fi

echo "Checking for Pulumi installation..."
if ! command -v pulumi &> /dev/null
then
    echo "Pulumi not found, installing..."
    curl -fsSL https://get.pulumi.com | sh
    export PATH=$PATH:$HOME/.pulumi/bin
    echo 'export PATH=$PATH:$HOME/.pulumi/bin' >> ~/.bash_profile
    source ~/.bash_profile
else
    echo "Pulumi is already installed."
fi

echo "Adding Pulumi to PATH..."
echo 'export PATH=$PATH:$HOME/.pulumi/bin' >> ~/.bash_profile
source ~/.bash_profile

echo "Creating and activating Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate

cd "$(dirname "$0")/.."

for project_dir in pulumi/*; do
    if [ -d "$project_dir" ]; then
        stack_name="dev"
        initialize_pulumi_stack "$project_dir" "$stack_name"
    fi
done

echo "Setup complete!"
