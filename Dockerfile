# FROM brunneis/python:3.8.3-ubuntu-20.04 as base

# WORKDIR /
# RUN mkdir -p /var/www/test-app

# COPY powertop-auditor-prometheus/requirements.txt requirements.txt
# RUN pip3 install -r requirements.txt 

# COPY powertop-auditor-prometheus /var/www/test-app

# RUN apt-get --yes --force-yes install powertop bash tree zsh locate

# CMD ["/bin/locate python3"]