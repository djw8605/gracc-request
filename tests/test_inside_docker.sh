#!/bin/sh -xe


# Install all the things
rpm -Uvh https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
yum -y update

yum -y install python-pip git rabbitmq-server java-1.8.0-openjdk
rpm -Uvh https://download.elastic.co/elasticsearch/release/org/elasticsearch/distribution/rpm/elasticsearch/2.3.2/elasticsearch-2.3.2.rpm

systemctl start elasticsearch.service
systemctl start rabbitmq-server.service

cd /gracc-request
pip install -r requirements.txt

# Install and Start overmind
python setup.py install
groupadd -r gracc
useradd -r -s /bin/false -g gracc gracc

mkdir -p /etc/gracc/config.d/
cp tests/gracc-request-test.toml /etc/gracc/config.d/gracc-request.toml
cp config/graccreq.service /lib/systemd/system/
systemctl start graccreq.service

# Wait for the overmind to start up
sleep 10
#journalctl -u graccreq.service --no-pager

# Install the test data
curl -O https://nodejs.org/dist/v4.4.4/node-v4.4.4-linux-x64.tar.xz
tar xf node-v4.4.4-linux-x64.tar.xz
export PATH=$PATH:`pwd`/node-v4.4.4-linux-x64/bin
npm install elasticdump -g

git clone https://github.com/djw8605/gracc-test-data.git
pushd gracc-test-data
bash -x ./import.sh
popd

python -m unittest discover tests/unittests "test_*.py"

sleep 1
journalctl -u graccreq.service --no-pager -n 20


