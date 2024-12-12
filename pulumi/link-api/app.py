from flask import Flask, request, jsonify, send_file, make_response
from io import BytesIO
from datetime import datetime
import zipfile
import os

app = Flask(__name__)

sent_info_results = []
cloud_provider = None
public_ip = None

@app.route('/sendinfo', methods=['POST'])
def sendinfo():
    global cloud_provider, public_ip
    data = request.get_json()
    cloud_provider = data.get('cloud_provider', 'Unknown')
    public_ip = data.get('public_ip', 'Unknown')
    print(f'Received info from {cloud_provider} with IP: {public_ip}')

    send_info_entry = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'cloud_provider': cloud_provider,
        'public_ip': public_ip
    }
    sent_info_results.append(send_info_entry)
    return jsonify(data)

@app.route('/currentinfo', methods=['GET'])
def currentinfo():
    return jsonify(sent_info_results), 200

@app.route('/clearinfo', methods=['POST'])
def clearinfo():
    global cloud_provider, public_ip
    sent_info_results.clear()
    cloud_provider = None
    public_ip = None
    return jsonify({"message": "Link cleared."}), 200

@app.route('/makenodeconfig', methods=['POST'])
def makenodeconfig():
    global cloud_provider, public_ip
    if sent_info_results:
        try:
            print('Generating config file based on cloud provider information.')

            if cloud_provider == 'Google Cloud':
                config_content = f"""
config:
  gcp:project: pulumi-workspace
  mc-gcp:mcn_vpc_name: 'mcn-vpc'

  mc-gcp:mcn_subnet_name: 'mcn-subnet'
  mc-gcp:mcn_subnet_ip: '10.0.0.0/24'
  mc-gcp:mcn_subnet_region: "us-central1"

  mc-gcp:mcn_firewall_name: 'mcn-firewall'
  mc-gcp:mcn_firewall_rules: [{"protocol" : "tcp","ports" : ["22", "1234","5001","80"]},{"protocol" : "icmp"},{ "protocol" : "udp", "ports" : ["4789"]}]
  
  mc-gcp:mcn_vm_name: 'mcn-vm'
  mc-gcp:mcn_vm_machine_type: 'e2-micro'
  mc-gcp:mcn_vm_zone: 'us-central1-a'
  mc-gcp:mcn_vm_image: 'debian-12-bookworm-v20240312'
  mc-gcp:mcn_vm_ip_name: 'mcn-ip'
  mc-gcp:mcn_vm_region: "us-central1"
  mc-gcp:package_name_1: 'netcat-traditional ncat'
  mc-gcp:package_name_2: 'iperf3'
"""
                config_filename = 'Pulumi.dev.yaml'

            elif cloud_provider == 'AWS':
                config_content = f"""
config:
  aws:region: 'us-west-2'
  mcn_vpc_name: 'user-vpc'
  mcn_subnet_name: 'user-subnet'
  mcn_subnet_ip: '10.0.0.0/24'
  mcn_subnet_region: 'us-west-2a'
  mcn_security_group_name: 'user-security-group'
  mcn_security_group_rules:
    ingress:
      - protocol: tcp
        from_port: 22
        to_port: 22
        cidr_blocks: ['0.0.0.0/0']
      - protocol: tcp
        from_port: 1234
        to_port: 1234
        cidr_blocks: ['0.0.0.0/0']
      - protocol: tcp
        from_port: 5001
        to_port: 5001
        cidr_blocks: ['0.0.0.0/0']
      - protocol: tcp
        from_port: 80
        to_port: 80
        cidr_blocks: ['0.0.0.0/0']
      - protocol: icmp
        from_port: -1
        to_port: -1
        cidr_blocks: ['0.0.0.0/0']
      - protocol: udp
        from_port: 4789
        to_port: 4789
        cidr_blocks: ['0.0.0.0/0']
    egress:
      - protocol: -1
        from_port: 0
        to_port: 0
        cidr_blocks: ['0.0.0.0/0']
  mcn_vm_name: 'user-vm'
  mcn_vm_instance_type: 't2.micro'
  mcn_vm_key_name: 'user-aws-key'
  mcn_vm_region: 'us-west-2'
"""
                config_filename = 'Pulumi.dev.yaml'

            else:
                print(f'Unsupported cloud provider: {cloud_provider}')
                return jsonify({"message": "Unsupported cloud provider"}), 400
            
            temp_dir = '/tmp'
            temp_filepath = os.path.join(temp_dir, config_filename)
            with open(temp_filepath, 'w') as config_file:
                config_file.write(config_content)

            return send_file(temp_filepath, as_attachment=True, download_name=config_filename)

        except Exception as e:
            print(f'Error occurred: {e}')
            return jsonify({"message": f"Error occurred while creating or sending the config file: {e}"}), 500
    else:
        print('Information has not been sent. Use /sendinfo to send linking information.')
        return jsonify({"message": "Link information has not been sent. Use /sendinfo to send linking information."}), 400

@app.route('/generate_script', methods=['POST'])
def generate_script():
    data = request.get_json()
    central_node_ip = data.get('central_node_ip')
    
    if not central_node_ip:
        return jsonify({"message": "Central node IP is required"}), 400

    if sent_info_results:
        try:
            print('Generating shell scripts to set up VXLAN tunnels for each VM to the central node.')

            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w') as zip_file:

                central_node_script_content = """#!/bin/bash

# Enable IP forwarding
sudo sysctl -w net.ipv4.ip_forward=1
echo 'net.ipv4.ip_forward = 1' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
"""
                for idx, vm in enumerate(sent_info_results, start=1):
                    vxlan_id = 42 + idx
                    public_ip = vm['public_ip']
                    central_node_script_content += f"""
# VM{idx} VXLAN interface
sudo ip link add vxlan{vxlan_id} type vxlan id {vxlan_id} dstport 4789 remote {public_ip} local {central_node_ip}
sudo ip addr add 192.168.{vxlan_id}.1/24 dev vxlan{vxlan_id}
sudo ip link set up dev vxlan{vxlan_id}
"""

                central_node_script_content += """
# Add routes for VXLAN networks
"""
                for idx in range(1, len(sent_info_results) + 1):
                    vxlan_id = 42 + idx
                    central_node_script_content += f"""
sudo ip route add 192.168.{vxlan_id}.0/24 dev vxlan{vxlan_id}
"""

                zip_file.writestr('setup_central_node.sh', central_node_script_content)

                # VM scripts setup
                for idx, vm in enumerate(sent_info_results, start=1):
                    public_ip = vm['public_ip']
                    vxlan_id = 42 + idx
                    script_content = f"""#!/bin/bash

# Create VXLAN interface
sudo ip link add vxlan{vxlan_id} type vxlan id {vxlan_id} dstport 4789 remote {central_node_ip} local {public_ip}
sudo ip addr add 192.168.{vxlan_id}.1/24 dev vxlan{vxlan_id}
sudo ip link set up dev vxlan{vxlan_id}

# Verify VXLAN interface
sudo ip link show vxlan{vxlan_id}
sudo ip addr show dev vxlan{vxlan_id}

# Add route to VXLAN network
sudo ip route add 192.168.{vxlan_id}.0/24 dev vxlan{vxlan_id}
"""
                    for other_idx, other_vm in enumerate(sent_info_results, start=1):
                        if other_idx != idx:
                            other_vxlan_id = 42 + other_idx
                            other_vm_ip = f"192.168.{other_vxlan_id}.1"
                            script_content += f"""
sudo ip route add 192.168.{other_vxlan_id}.0/24 via {other_vm_ip} dev vxlan{vxlan_id}
"""
                    script_filename = f'setup_vxlan_vm{idx}.sh'
                    zip_file.writestr(script_filename, script_content)

            zip_buffer.seek(0)
            return send_file(zip_buffer, as_attachment=True, download_name='vxlan_scripts.zip', mimetype='application/zip')

        except Exception as e:
            print(f'Error occurred: {e}')
            return jsonify({"message": f"Error occurred while creating or sending the script files: {e}"}), 500
    else:
        print('Information has not been sent. Use /sendinfo to send linking information.')
        return jsonify({"message": "Link information has not been sent. Use /sendinfo to send linking information."}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)