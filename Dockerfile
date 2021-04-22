FROM odoo:14.0

USER root

RUN set -x; \
        apt-get update \
        && apt-get install -y --no-install-recommends \
            git \ 
            vim \
            python3-setuptools

ARG addons=/mnt/extra-addons
COPY . ${addons}
RUN pip3 install --no-cache-dir --upgrade pip setuptools
RUN pip3 install --no-cache-dir -r ${addons}/requirements.txt

USER odoo