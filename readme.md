# Multi Cloud Networking

This project file contains tools to build a connection between different cloud providers using VXLAN.
Currently all of the files work with the intention of transferring from Google to AWS or from AWS to Google. It uses
VXLAN to establish network connections that do not require VPC Peering and work at decent speed.

This project should be used on a machine that has permission to interact with your chosen cloud providers with the
corresponding CLI's and access set up and working. It will also require a free Pulumi account. The Link API Python Flask app 
is configured on Google Cloud so it will need to be hosted on that platform for the link-api pulumi project to be able to deploy. However,
it could be deployed manually on any provider and it would likely not affect how it works.

## GETTING STARTED

Clone the repository:

```
git clone git@github.com:JustinCosta10/MultiCloudNetworking.git
```

Navigate to /scripts and allow each script to be ran on the machine. Example:

```
chmod +x setup.sh
chomd +x attachvm.sh
chmod +x cloudconfig.sh
```
setup.sh installs the necessary dependencies and pulumi.
attachvm.sh is ran on virtual machines to establish the multi-cloud connections.
cloudconfig.sh is an attempt to help with setting up cloud credentials if it is not already set up.

From the /scripts folder, run setup.sh. setup.sh will install the necessary dependencies and prompt you to log in to a Pulumi account.

If your cloud credentials are not already configured, run cloudconfig.sh to enter cloud credentials. cloudconfig.sh uses access keys in the
case of AWS and service account JSON file for GCP. This is not necessary if your cloud credentials are configured and Pulumi already sees it.


## Pulumi Project Files Explained

There are 5 Pulumi project files in the /pulumi folder. The "user" machines are simply a way to quickly create unrelated machines to connect between each other. 
The mc projects, standing for "Multi-Cloud" are the machines that are generated to connect the clouds. 

The user-aws and mc-aws projects generate AWS infrastructure while user-gcp and mc-gcp generate GCP infrastructure.

The link-api project file is a flask server built for GCP that generates the config files necessary to build the dynamic network. 
This will need to be hosted first.


## Hosting Link API
The Link API is built in GCP and must be curled, so it needs a static IP. 
Create a hosted GCP static IP and enter it into mcn_vm_public_ip_address at the top of __main__.py in the link-api folder.
Also enter this IP into the LINK_STATIC_IP variable in /scripts/attachvm.sh so that the curl commands in that script can use the correct IP address.

After setup.sh is ran, the project file /pulumi/link-api should be able to be deployed when `pulumi up` is ran from inside of the /link-api directory:
Select yes and let it begin generating. This will deploy a VM that will automatically run a Python Flask web app. 
The scripts that create configuration files curl this server to send and receive the necessary information.

The Link API web server will take a minute or two to start fully working, since it has to boot and install flask.

To take down any individual Pulumi project, use `pulumi destroy` in the project folder.


## Creating Connection

In the directory /scripts there is attachvm.sh. This script curls the Link API and sends the cloud type and IP to the API. Run this script
on a VM to start the creation of the dynamic network. 

Now, run the script on each VM that is intended to be attached to this generated VM node. Each attached VM will be able to network with the others.

For an AWS connection use mc-aws and for a GCP connection use mc-gcp. Use `pulumi up` to generate the connecting node in the pulumi project. Once it is generated it will output a new IP.

Insert the new IP and the static IP of the link-api project into this command and the flask server will send back scripts to be ran on each VM to complete the entire connection:

```
curl -X POST http://<INSERT_STATIC_IP>:5001/generate_script -H "Content-Type: application/json" -d '{"central_node_ip": "<INSERT_NODE_IP>"}' -o vxlan_scripts.zip
```
There will be 1 script for each VM that was attached and a script for the central node mc-aws or mc-gcp. 
The script for mc-aws or mc-gcp will be called setup_central_node.sh.
The individual VM scripts will be titled setup_vxlan_vm{<number>}, with the number being the order the machines were attached with attachvm.sh.

## Current Issue

There is something wrong with the generated routing scripts from the curl command /generate_script in the Flask API that I am trying to track down. I can manually build the "via" connections after the infrastructure is generated but I have not yet nailed down the issue with the routing. The generate_script is all set up to create variablized scripts, but I am clearly missing something with the routing commands. As far as I can tell the actual script generation is happening accurately I am just missing something with the linux commands themselves to set up the VXLAN connections. I am getting "invalid NextHop gateway" when the current generated scripts are ran.

If they are modified to route correctly I think the whole thing will work with these steps. However I figured I would put this up anyways.








