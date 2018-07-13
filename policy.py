import json
import http.client
from flask import Flask
app = Flask(__name__)

def load_policy():
	with open('policy.json', 'r') as f:
                data = json.load(f)
	return data

def get_pods_status(host, port, namespace):
	print(host)
	print(port)
	print(namespace)
	conn = http.client.HTTPConnection(host, port)
	conn.request("GET", "/kubernetes/pods?namespace=" + namespace)
	response = conn.getresponse()
	return response
	

@app.route('/cluster_status')
def cluster_status():
	policy = load_policy()
	print(policy['console'])

	health = True
	for index_policy in range(len(policy['policy'])):	
		if health == False:
			break
		response = get_pods_status(policy['console']['host'], policy['console']['port'], policy['policy'][index_policy]['namespace']['name'])

		if response.status == 200 :
			data = json.loads(response.read())
			for index_policy_pod in range(len(policy['policy'][index_policy]['namespace']['pod'])):
				for index in range(len(data['pods'])):
					if policy['policy'][index_policy]['namespace']['pod'][index_policy_pod]['running_num'] <= 0:
						break
					if data['pods'][index]['name'].startswith(policy['policy'][index_policy]['namespace']['pod'][index_policy_pod]['name']):
						policy['policy'][index_policy]['namespace']['pod'][index_policy_pod]['running_num']-=1
			
				if policy['policy'][index_policy]['namespace']['pod'][index_policy_pod]['running_num'] > 0:
					health = False
					break
 		
	
	if health == False:
		return 'unhealth'

	return 'health' 

if __name__ == '__main__':
	app.run(port="9000")
