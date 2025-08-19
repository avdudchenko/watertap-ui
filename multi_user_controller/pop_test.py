import subprocess

commands = ['conda init', 'conda activate watertap-ui-env', 'python /home/sovietez/github/watertap-ui/backend/app/main.py'] 
process = subprocess.Popen('/home/sovietez/github/watertap-ui/multi_user_controller/start_ui.sh')

