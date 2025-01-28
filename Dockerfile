FROM codercom/code-server:latest

ENV WORKDIR=/home/coder/lily

RUN mkdir -p $WORKDIR
WORKDIR $WORKDIR

RUN mkdir -p /home/coder/.config/code-server && \
    echo "bind-addr: 0.0.0.0:8080\n\
auth: none\n\
cert: /home/coder/server.crt\n\
cert-key: /home/coder/server.key" > /home/coder/.config/code-server/config.yaml

USER root

RUN apt update && apt install -y openssl && \
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /home/coder/server.key \
    -out /home/coder/server.crt \
    -subj "/C=XX/ST=AT/Linz/O=Johannes Kepler University/CN=172.20.10.6" \
    -addext "subjectAltName = IP:172.20.10.6"

RUN chown coder:coder /home/coder/server.crt /home/coder/server.key && \
    chmod 600 /home/coder/server.crt /home/coder/server.key

RUN mkdir -p /lilypond && \
    cd /lilypond && \
    wget https://gitlab.com/lilypond/lilypond/-/releases/v2.24.4/downloads/lilypond-2.24.4-linux-x86_64.tar.gz && \
    tar -xvf lilypond-2.24.4-linux-x86_64.tar.gz && \
    rm -rf lilypond-2.24.4-linux-x86_64.tar.gz

RUN mkdir -p /home/coder/lily/_runAsAdmin

RUN echo '#!/bin/bash' > /home/coder/generateBat.sh && \
    echo 'BATCH_FILE="/home/coder/lily/runAsAdmin/install_cert.bat"' >> /home/coder/generateBat.sh && \
    echo 'CERT_FILE="/home/coder/server.crt"' >> /home/coder/generateBat.sh && \
    echo 'cat > "$BATCH_FILE" <<EOF' >> /home/coder/generateBat.sh && \
    echo '@echo off' >> /home/coder/generateBat.sh && \
    echo 'echo Creating Certificate under Windows...' >> /home/coder/generateBat.sh && \
    echo 'echo. > "%USERPROFILE%\\Desktop\\server.crt"' >> /home/coder/generateBat.sh && \
    echo 'REM Zertifikatsinhalt schreiben' >> /home/coder/generateBat.sh && \
    echo 'EOF' >> /home/coder/generateBat.sh && \
    echo 'while IFS= read -r line; do' >> /home/coder/generateBat.sh && \
    echo '    echo "echo $line >> \"%USERPROFILE%\\Desktop\\server.crt\"" >> "$BATCH_FILE"' >> /home/coder/generateBat.sh && \
    echo 'done < "$CERT_FILE"' >> /home/coder/generateBat.sh && \
    echo 'cat >> "$BATCH_FILE" <<EOF' >> /home/coder/generateBat.sh && \
    echo 'echo.' >> /home/coder/generateBat.sh && \
    echo 'echo Importing Certificate...' >> /home/coder/generateBat.sh && \
    echo 'powershell -Command "Import-Certificate -FilePath ''%USERPROFILE%\\Desktop\\server.crt'' -CertStoreLocation ''Cert:\\LocalMachine\\Root''"' >> /home/coder/generateBat.sh && \
    echo 'echo Deleting Certificate from Desktop...' >> /home/coder/generateBat.sh && \
    echo 'del "%USERPROFILE%\\Desktop\\server.crt"' >> /home/coder/generateBat.sh && \
    echo 'echo Certificate was imported successfully!' >> /home/coder/generateBat.sh && \
    echo 'pause' >> /home/coder/generateBat.sh && \
    echo 'EOF' >> /home/coder/generateBat.sh && \
    chmod +x /home/coder/generateBat.sh

USER coder

RUN code-server --install-extension adamraichu.pdf-viewer && \
    code-server --install-extension jeandeaual.lilypond-syntax

RUN mkdir -p /home/coder/lily/exercises
RUN git clone https://github.com/rubyy-y/lilypond-turorial.git /home/coder/lily/exercises

RUN git clone https://github.com/rubyy-y/Lilypond-Plugin.git
RUN code-server --install-extension Lilypond-Plugin/runlilypond-0.0.1.vsix
RUN rm -rf Lilypond-Plugin

EXPOSE 8081 8082 8083
