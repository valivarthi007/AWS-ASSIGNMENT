from flask import Flask, render_template
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import psutil
import smtplib
import boto3
import os
# Configure AWS credentials
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
REGION_NAME = 'us-east-1'

# Configure email settings
EMAIL_FROM = 'diwakar.valivarthi@gmail.com'
EMAIL_TO = 'diwakar1994raju@gmail.com'
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USERNAME = 'diwakar.valivarthi@gmail.com'
SMTP_PASSWORD = os.environ.get('email_password')

# Configure thresholds (default values)
CPU_THRESHOLD = 80  # in percent
MEMORY_THRESHOLD = 80  # in percent
DISK_THRESHOLD = 80  # in percent
NETWORK_THRESHOLD = 100  # in percent

# Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(filename='health_check.log', level=logging.INFO)


def send_email(subject, message):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_TO
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(SMTP_USERNAME, SMTP_PASSWORD)
    text = msg.as_string()
    server.sendmail(EMAIL_FROM, EMAIL_TO, text)
    server.quit()


def check_server_health(instance_id, cpu_threshold, memory_threshold, disk_threshold, network_threshold):
    ec2 = boto3.resource('ec2', aws_access_key_id=AWS_ACCESS_KEY_ID,
                         aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name=REGION_NAME)
    instance = ec2.Instance(instance_id)

    # Retrieve CPU usage
    cpu_usage = psutil.cpu_percent(interval=1)
    if cpu_usage > cpu_threshold:
        send_email(
            f'CPU usage alert for {instance_id}', f'CPU usage is {cpu_usage}%')

    # Retrieve memory usage
    memory_usage = psutil.virtual_memory().percent
    if memory_usage > memory_threshold:
        send_email(
            f'Memory usage alert for {instance_id}', f'Memory usage is {memory_usage}%')

    # Retrieve disk usage
    disk_usage = psutil.disk_usage('/').percent
    if disk_usage > disk_threshold:
        send_email(
            f'Disk usage alert for {instance_id}', f'Disk usage is {disk_usage}%')

    # Check network connectivity
    # You may implement additional network checks here
    # For simplicity, we'll just assume network is up if the script is able to execute till this point
    if network_threshold < 100:
        send_email(
            f'Network connectivity alert for {instance_id}', 'Network connectivity is down')


def get_instance_health(instance_id):
    ec2 = boto3.resource('ec2', aws_access_key_id=AWS_ACCESS_KEY_ID,
                         aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name=REGION_NAME)
    instance = ec2.Instance(instance_id)

    # Retrieve CPU usage
    cpu_usage = psutil.cpu_percent(interval=1)

    # Retrieve memory usage
    memory_usage = psutil.virtual_memory().percent

    # Retrieve disk usage
    disk_usage = psutil.disk_usage('/').percent

    # Check network connectivity
    # For simplicity, we'll just assume network is up if the script is able to execute till this point

    return {
        'cpu_usage': cpu_usage,
        'memory_usage': memory_usage,
        'disk_usage': disk_usage,
        'network_status': 'Up'
    }


@app.route('/')
def index():
    instance_health = {}
    ec2 = boto3.client('ec2', aws_access_key_id=AWS_ACCESS_KEY_ID,
                       aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name=REGION_NAME)
    response = ec2.describe_instances()
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            instance_health[instance_id] = get_instance_health(instance_id)
    return render_template('index.html', instance_health=instance_health)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

