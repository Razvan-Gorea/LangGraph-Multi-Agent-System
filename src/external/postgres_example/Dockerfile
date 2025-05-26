FROM postgres:alpine

# Set environment variables (DON'T DO IT THIS WAY IN PRODUCTION)
ENV POSTGRES_USER=myuser
ENV POSTGRES_PASSWORD=mypassword
ENV POSTGRES_DB=mydatabase

# Create a custom init script that will run when the container starts
RUN echo '#!/bin/bash' > /docker-entrypoint-initdb.d/update-config.sh && \
    echo 'echo "wal_level = logical" >> $PGDATA/postgresql.conf' >> /docker-entrypoint-initdb.d/update-config.sh && \
    echo 'echo "max_wal_senders = 10" >> $PGDATA/postgresql.conf' >> /docker-entrypoint-initdb.d/update-config.sh && \
    echo 'echo "max_replication_slots = 10" >> $PGDATA/postgresql.conf' >> /docker-entrypoint-initdb.d/update-config.sh && \
    chmod +x /docker-entrypoint-initdb.d/update-config.sh

EXPOSE 5432
