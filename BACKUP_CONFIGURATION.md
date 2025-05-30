# Backup Configuration and Recovery Procedures

**Version:** 1.0.0  
**Environment:** Production Ready  
**Last Updated:** 2025-05-30  

## Table of Contents

- [Overview](#overview)
- [Backup Strategy](#backup-strategy)
- [Database Backup](#database-backup)
- [Application Backup](#application-backup)
- [Static Files Backup](#static-files-backup)
- [User Data Backup](#user-data-backup)
- [Automated Backup Scripts](#automated-backup-scripts)
- [Recovery Procedures](#recovery-procedures)
- [Testing Backup Integrity](#testing-backup-integrity)
- [Monitoring and Alerting](#monitoring-and-alerting)

## Overview

This document outlines comprehensive backup and recovery procedures for the Thesis Grey Literature application, ensuring data protection and business continuity.

### Backup Objectives

- **Recovery Time Objective (RTO)**: 4 hours maximum
- **Recovery Point Objective (RPO)**: 1 hour maximum data loss
- **Retention Policy**: 
  - Daily backups: 30 days
  - Weekly backups: 12 weeks
  - Monthly backups: 12 months
  - Yearly backups: 7 years

### Critical Data Components

1. **PostgreSQL Database** - All application data
2. **User-uploaded Files** - Session documents and attachments
3. **Application Code** - Source code and configurations
4. **System Configuration** - Server configurations and secrets
5. **Log Files** - Application and system logs

## Backup Strategy

### 3-2-1 Backup Rule

- **3** copies of important data
- **2** different storage media types
- **1** offsite backup location

### Storage Locations

1. **Primary**: Local server storage
2. **Secondary**: Network-attached storage (NAS)
3. **Offsite**: Cloud storage (AWS S3, Azure Blob, or Google Cloud)

## Database Backup

### PostgreSQL Backup Configuration

#### 1. Full Database Backup Script

```bash
#!/bin/bash
# /opt/thesis-grey/scripts/backup_database.sh

# Configuration
DB_NAME="thesis_grey_db"
DB_USER="thesis_grey_user"
BACKUP_DIR="/opt/thesis-grey/backups/database"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/full_backup_${DATE}.sql"
LOG_FILE="/var/log/thesis-grey/backup.log"

# Create backup directory
mkdir -p ${BACKUP_DIR}

# Log start
echo "$(date): Starting database backup" >> ${LOG_FILE}

# Create full backup
pg_dump -h localhost -U ${DB_USER} -W ${DB_NAME} \
    --verbose \
    --clean \
    --create \
    --format=custom \
    --file=${BACKUP_FILE}.backup

# Create SQL dump for portability
pg_dump -h localhost -U ${DB_USER} -W ${DB_NAME} \
    --verbose \
    --clean \
    --create \
    --format=plain \
    --file=${BACKUP_FILE}

# Compress backups
gzip ${BACKUP_FILE}

# Verify backup integrity
if [ $? -eq 0 ]; then
    echo "$(date): Database backup completed successfully: ${BACKUP_FILE}.gz" >> ${LOG_FILE}
    
    # Calculate backup size
    BACKUP_SIZE=$(du -h ${BACKUP_FILE}.gz | cut -f1)
    echo "$(date): Backup size: ${BACKUP_SIZE}" >> ${LOG_FILE}
    
    # Test backup integrity
    gunzip -t ${BACKUP_FILE}.gz
    if [ $? -eq 0 ]; then
        echo "$(date): Backup integrity verified" >> ${LOG_FILE}
    else
        echo "$(date): ERROR: Backup integrity check failed" >> ${LOG_FILE}
        exit 1
    fi
else
    echo "$(date): ERROR: Database backup failed" >> ${LOG_FILE}
    exit 1
fi

# Clean up old backups (keep last 30 days)
find ${BACKUP_DIR} -name "full_backup_*.sql.gz" -mtime +30 -delete
echo "$(date): Old backups cleaned up" >> ${LOG_FILE}

# Upload to cloud storage (optional)
if [ -n "$CLOUD_BACKUP_ENABLED" ] && [ "$CLOUD_BACKUP_ENABLED" = "true" ]; then
    aws s3 cp ${BACKUP_FILE}.gz s3://thesis-grey-backups/database/ \
        --storage-class STANDARD_IA
    
    if [ $? -eq 0 ]; then
        echo "$(date): Backup uploaded to cloud storage" >> ${LOG_FILE}
    else
        echo "$(date): WARNING: Cloud upload failed" >> ${LOG_FILE}
    fi
fi
```

#### 2. Incremental Backup with WAL Archiving

```bash
#!/bin/bash
# /opt/thesis-grey/scripts/backup_wal.sh

# Configuration
WAL_ARCHIVE_DIR="/opt/thesis-grey/backups/wal"
CLOUD_WAL_BUCKET="s3://thesis-grey-backups/wal"

# Create WAL archive directory
mkdir -p ${WAL_ARCHIVE_DIR}

# Archive WAL file
cp $1 ${WAL_ARCHIVE_DIR}/

# Upload to cloud
if [ -n "$CLOUD_BACKUP_ENABLED" ] && [ "$CLOUD_BACKUP_ENABLED" = "true" ]; then
    aws s3 cp ${WAL_ARCHIVE_DIR}/$(basename $1) ${CLOUD_WAL_BUCKET}/
fi

echo "$(date): WAL file archived: $(basename $1)" >> /var/log/thesis-grey/wal-archive.log
```

#### 3. PostgreSQL Configuration for WAL Archiving

Add to `/etc/postgresql/*/main/postgresql.conf`:

```ini
# WAL archiving for point-in-time recovery
wal_level = replica
archive_mode = on
archive_command = '/opt/thesis-grey/scripts/backup_wal.sh %p'
archive_timeout = 300  # Archive every 5 minutes

# Backup settings
max_wal_size = 2GB
min_wal_size = 80MB
```

### Cron Schedule for Database Backups

```bash
# /etc/cron.d/thesis-grey-backup

# Full database backup daily at 2 AM
0 2 * * * thesis-grey /opt/thesis-grey/scripts/backup_database.sh

# Weekly backup verification at 3 AM Sunday
0 3 * * 0 thesis-grey /opt/thesis-grey/scripts/verify_backup.sh

# Monthly backup to long-term storage
0 4 1 * * thesis-grey /opt/thesis-grey/scripts/monthly_backup.sh
```

## Application Backup

### Application Code and Configuration Backup

```bash
#!/bin/bash
# /opt/thesis-grey/scripts/backup_application.sh

# Configuration
APP_DIR="/opt/thesis-grey"
BACKUP_DIR="/opt/thesis-grey/backups/application"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/app_backup_${DATE}.tar.gz"
LOG_FILE="/var/log/thesis-grey/app-backup.log"

# Create backup directory
mkdir -p ${BACKUP_DIR}

echo "$(date): Starting application backup" >> ${LOG_FILE}

# Create application backup excluding unnecessary files
tar -czf ${BACKUP_FILE} \
    --exclude='${APP_DIR}/backups' \
    --exclude='${APP_DIR}/venv' \
    --exclude='${APP_DIR}/staticfiles' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='*.log' \
    --exclude='.git' \
    --exclude='node_modules' \
    -C ${APP_DIR} .

if [ $? -eq 0 ]; then
    echo "$(date): Application backup completed: ${BACKUP_FILE}" >> ${LOG_FILE}
    
    # Calculate backup size
    BACKUP_SIZE=$(du -h ${BACKUP_FILE} | cut -f1)
    echo "$(date): Application backup size: ${BACKUP_SIZE}" >> ${LOG_FILE}
else
    echo "$(date): ERROR: Application backup failed" >> ${LOG_FILE}
    exit 1
fi

# Clean up old backups (keep last 7 days)
find ${BACKUP_DIR} -name "app_backup_*.tar.gz" -mtime +7 -delete

# Upload to cloud storage
if [ -n "$CLOUD_BACKUP_ENABLED" ] && [ "$CLOUD_BACKUP_ENABLED" = "true" ]; then
    aws s3 cp ${BACKUP_FILE} s3://thesis-grey-backups/application/
    echo "$(date): Application backup uploaded to cloud" >> ${LOG_FILE}
fi
```

### System Configuration Backup

```bash
#!/bin/bash
# /opt/thesis-grey/scripts/backup_system_config.sh

CONFIG_BACKUP_DIR="/opt/thesis-grey/backups/config"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${CONFIG_BACKUP_DIR}/system_config_${DATE}.tar.gz"

mkdir -p ${CONFIG_BACKUP_DIR}

# Backup system configuration files
tar -czf ${BACKUP_FILE} \
    /etc/nginx/sites-available/thesis-grey \
    /etc/systemd/system/thesis-grey*.service \
    /etc/postgresql/*/main/postgresql.conf \
    /etc/postgresql/*/main/pg_hba.conf \
    /etc/redis/redis.conf \
    /etc/cron.d/thesis-grey-backup \
    /opt/thesis-grey/.env \
    2>/dev/null

echo "$(date): System configuration backed up: ${BACKUP_FILE}" >> /var/log/thesis-grey/config-backup.log
```

## Static Files Backup

### User Uploads and Static Assets

```bash
#!/bin/bash
# /opt/thesis-grey/scripts/backup_static_files.sh

STATIC_DIR="/opt/thesis-grey/static"
MEDIA_DIR="/opt/thesis-grey/media"
BACKUP_DIR="/opt/thesis-grey/backups/static"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p ${BACKUP_DIR}

# Backup static files
if [ -d "${STATIC_DIR}" ]; then
    tar -czf ${BACKUP_DIR}/static_files_${DATE}.tar.gz -C ${STATIC_DIR} .
    echo "$(date): Static files backed up" >> /var/log/thesis-grey/static-backup.log
fi

# Backup media files (user uploads)
if [ -d "${MEDIA_DIR}" ]; then
    tar -czf ${BACKUP_DIR}/media_files_${DATE}.tar.gz -C ${MEDIA_DIR} .
    echo "$(date): Media files backed up" >> /var/log/thesis-grey/static-backup.log
fi

# Sync to cloud storage with versioning
if [ -n "$CLOUD_BACKUP_ENABLED" ] && [ "$CLOUD_BACKUP_ENABLED" = "true" ]; then
    aws s3 sync ${MEDIA_DIR} s3://thesis-grey-backups/media/ --delete
    aws s3 sync ${STATIC_DIR} s3://thesis-grey-backups/static/ --delete
fi
```

## User Data Backup

### Session and Activity Data Export

```python
#!/usr/bin/env python3
# /opt/thesis-grey/scripts/export_user_data.py

import os
import sys
import json
import django
from datetime import datetime

# Setup Django environment
sys.path.append('/opt/thesis-grey/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'thesis_grey_project.settings.production')
django.setup()

from django.contrib.auth import get_user_model
from apps.review_manager.models import SearchSession, SessionActivity

User = get_user_model()

def export_user_data(user_id=None, output_dir='/opt/thesis-grey/backups/user_data'):
    """Export user data to JSON files."""
    
    os.makedirs(output_dir, exist_ok=True)
    
    if user_id:
        users = [User.objects.get(id=user_id)]
    else:
        users = User.objects.all()
    
    for user in users:
        user_data = {
            'user': {
                'id': str(user.id),
                'username': user.username,
                'email': user.email,
                'date_joined': user.date_joined.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None,
            },
            'sessions': [],
            'activities': []
        }
        
        # Export sessions
        sessions = SearchSession.objects.filter(created_by=user)
        for session in sessions:
            session_data = {
                'id': str(session.id),
                'title': session.title,
                'description': session.description,
                'status': session.status,
                'created_at': session.created_at.isoformat(),
                'updated_at': session.updated_at.isoformat(),
            }
            user_data['sessions'].append(session_data)
            
            # Export activities for this session
            activities = SessionActivity.objects.filter(session=session)
            for activity in activities:
                activity_data = {
                    'id': str(activity.id),
                    'session_id': str(activity.session.id),
                    'action': activity.action,
                    'description': activity.description,
                    'timestamp': activity.timestamp.isoformat(),
                    'details': activity.details,
                }
                user_data['activities'].append(activity_data)
        
        # Save to file
        filename = f"{output_dir}/user_{user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(user_data, f, indent=2, default=str)
        
        print(f"User data exported: {filename}")

if __name__ == '__main__':
    export_user_data()
```

## Recovery Procedures

### Database Recovery

#### Full Database Restore

```bash
#!/bin/bash
# /opt/thesis-grey/scripts/restore_database.sh

BACKUP_FILE=$1
DB_NAME="thesis_grey_db"
DB_USER="thesis_grey_user"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file>"
    exit 1
fi

echo "Starting database restore from: $BACKUP_FILE"

# Stop application services
systemctl stop thesis-grey thesis-grey-celery thesis-grey-celery-beat

# Drop and recreate database
sudo -u postgres psql << EOF
DROP DATABASE IF EXISTS ${DB_NAME};
CREATE DATABASE ${DB_NAME} OWNER ${DB_USER};
EOF

# Restore from backup
if [[ $BACKUP_FILE == *.backup ]]; then
    # Custom format backup
    pg_restore -h localhost -U ${DB_USER} -d ${DB_NAME} --verbose --clean --create $BACKUP_FILE
elif [[ $BACKUP_FILE == *.sql.gz ]]; then
    # Compressed SQL dump
    gunzip -c $BACKUP_FILE | psql -h localhost -U ${DB_USER} -d ${DB_NAME}
elif [[ $BACKUP_FILE == *.sql ]]; then
    # Plain SQL dump
    psql -h localhost -U ${DB_USER} -d ${DB_NAME} < $BACKUP_FILE
else
    echo "Unsupported backup format"
    exit 1
fi

if [ $? -eq 0 ]; then
    echo "Database restore completed successfully"
    
    # Start application services
    systemctl start thesis-grey thesis-grey-celery thesis-grey-celery-beat
    
    echo "Application services restarted"
else
    echo "Database restore failed"
    exit 1
fi
```

#### Point-in-Time Recovery

```bash
#!/bin/bash
# /opt/thesis-grey/scripts/point_in_time_recovery.sh

BACKUP_FILE=$1
RECOVERY_TIME=$2  # Format: 'YYYY-MM-DD HH:MM:SS'

if [ -z "$BACKUP_FILE" ] || [ -z "$RECOVERY_TIME" ]; then
    echo "Usage: $0 <backup_file> 'YYYY-MM-DD HH:MM:SS'"
    exit 1
fi

echo "Starting point-in-time recovery to: $RECOVERY_TIME"

# Stop services
systemctl stop thesis-grey thesis-grey-celery thesis-grey-celery-beat

# Restore base backup
pg_restore -h localhost -U thesis_grey_user -d thesis_grey_db --clean --create $BACKUP_FILE

# Create recovery configuration
cat > /var/lib/postgresql/*/main/recovery.conf << EOF
restore_command = 'cp /opt/thesis-grey/backups/wal/%f %p'
recovery_target_time = '$RECOVERY_TIME'
recovery_target_timeline = 'latest'
EOF

# Start PostgreSQL for recovery
systemctl restart postgresql

# Wait for recovery to complete
echo "Waiting for recovery to complete..."
sleep 30

# Promote to primary
sudo -u postgres psql -c "SELECT pg_promote();"

# Start application services
systemctl start thesis-grey thesis-grey-celery thesis-grey-celery-beat

echo "Point-in-time recovery completed"
```

### Application Recovery

```bash
#!/bin/bash
# /opt/thesis-grey/scripts/restore_application.sh

BACKUP_FILE=$1
APP_DIR="/opt/thesis-grey"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file>"
    exit 1
fi

echo "Starting application restore from: $BACKUP_FILE"

# Stop services
systemctl stop thesis-grey thesis-grey-celery thesis-grey-celery-beat nginx

# Backup current application (just in case)
mv ${APP_DIR}/app ${APP_DIR}/app.backup.$(date +%Y%m%d_%H%M%S)

# Extract backup
mkdir -p ${APP_DIR}/app
tar -xzf $BACKUP_FILE -C ${APP_DIR}/app

# Set proper permissions
chown -R thesis-grey:thesis-grey ${APP_DIR}/app
chmod -R 755 ${APP_DIR}/app

# Activate virtual environment and install dependencies
cd ${APP_DIR}
source venv/bin/activate
pip install -r app/requirements.txt

# Run migrations (if needed)
cd app
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Start services
systemctl start thesis-grey thesis-grey-celery thesis-grey-celery-beat nginx

echo "Application restore completed"
```

## Testing Backup Integrity

### Automated Backup Verification

```bash
#!/bin/bash
# /opt/thesis-grey/scripts/verify_backup.sh

BACKUP_DIR="/opt/thesis-grey/backups"
LOG_FILE="/var/log/thesis-grey/backup-verification.log"
TEST_DB="thesis_grey_test_restore"

echo "$(date): Starting backup verification" >> ${LOG_FILE}

# Find latest backup
LATEST_BACKUP=$(find ${BACKUP_DIR}/database -name "full_backup_*.sql.gz" -type f -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2)

if [ -z "$LATEST_BACKUP" ]; then
    echo "$(date): ERROR: No backup found for verification" >> ${LOG_FILE}
    exit 1
fi

echo "$(date): Verifying backup: $LATEST_BACKUP" >> ${LOG_FILE}

# Create test database
sudo -u postgres createdb ${TEST_DB}

# Restore backup to test database
gunzip -c ${LATEST_BACKUP} | sudo -u postgres psql ${TEST_DB}

if [ $? -eq 0 ]; then
    echo "$(date): Backup restoration test PASSED" >> ${LOG_FILE}
    
    # Run basic integrity checks
    RECORD_COUNT=$(sudo -u postgres psql -t -c "SELECT count(*) FROM review_manager_searchsession;" ${TEST_DB} | tr -d ' ')
    echo "$(date): Session count in backup: ${RECORD_COUNT}" >> ${LOG_FILE}
    
    # Check for recent data
    LATEST_SESSION=$(sudo -u postgres psql -t -c "SELECT MAX(created_at) FROM review_manager_searchsession;" ${TEST_DB} | tr -d ' ')
    echo "$(date): Latest session in backup: ${LATEST_SESSION}" >> ${LOG_FILE}
    
else
    echo "$(date): ERROR: Backup restoration test FAILED" >> ${LOG_FILE}
fi

# Clean up test database
sudo -u postgres dropdb ${TEST_DB}

echo "$(date): Backup verification completed" >> ${LOG_FILE}
```

### Monthly Recovery Test

```bash
#!/bin/bash
# /opt/thesis-grey/scripts/monthly_recovery_test.sh

# Run on separate test server
TEST_SERVER="test-recovery.example.com"
LOG_FILE="/var/log/thesis-grey/recovery-test.log"

echo "$(date): Starting monthly recovery test" >> ${LOG_FILE}

# Download latest backups from cloud
aws s3 sync s3://thesis-grey-backups/database/ /tmp/recovery-test/database/
aws s3 sync s3://thesis-grey-backups/application/ /tmp/recovery-test/application/

# Test database recovery
LATEST_DB_BACKUP=$(find /tmp/recovery-test/database -name "full_backup_*.sql.gz" | head -1)
if [ -n "$LATEST_DB_BACKUP" ]; then
    scp ${LATEST_DB_BACKUP} ${TEST_SERVER}:/tmp/
    ssh ${TEST_SERVER} "/opt/thesis-grey/scripts/restore_database.sh /tmp/$(basename ${LATEST_DB_BACKUP})"
    
    if [ $? -eq 0 ]; then
        echo "$(date): Database recovery test PASSED" >> ${LOG_FILE}
    else
        echo "$(date): ERROR: Database recovery test FAILED" >> ${LOG_FILE}
    fi
fi

# Test application recovery
LATEST_APP_BACKUP=$(find /tmp/recovery-test/application -name "app_backup_*.tar.gz" | head -1)
if [ -n "$LATEST_APP_BACKUP" ]; then
    scp ${LATEST_APP_BACKUP} ${TEST_SERVER}:/tmp/
    ssh ${TEST_SERVER} "/opt/thesis-grey/scripts/restore_application.sh /tmp/$(basename ${LATEST_APP_BACKUP})"
    
    if [ $? -eq 0 ]; then
        echo "$(date): Application recovery test PASSED" >> ${LOG_FILE}
    else
        echo "$(date): ERROR: Application recovery test FAILED" >> ${LOG_FILE}
    fi
fi

# Clean up
rm -rf /tmp/recovery-test/

echo "$(date): Monthly recovery test completed" >> ${LOG_FILE}
```

## Monitoring and Alerting

### Backup Monitoring Script

```bash
#!/bin/bash
# /opt/thesis-grey/scripts/monitor_backups.sh

BACKUP_DIR="/opt/thesis-grey/backups"
ALERT_EMAIL="admin@your-domain.com"
LOG_FILE="/var/log/thesis-grey/backup-monitoring.log"

# Check if backups are current
LAST_DB_BACKUP=$(find ${BACKUP_DIR}/database -name "full_backup_*.sql.gz" -mtime -1 | wc -l)
LAST_APP_BACKUP=$(find ${BACKUP_DIR}/application -name "app_backup_*.tar.gz" -mtime -7 | wc -l)

# Check backup integrity
CORRUPT_BACKUPS=$(find ${BACKUP_DIR}/database -name "*.gz" -exec gzip -t {} \; 2>&1 | grep -c "NOT OK")

# Alert if backups are missing or corrupt
if [ ${LAST_DB_BACKUP} -eq 0 ]; then
    echo "$(date): ALERT: No database backup in last 24 hours" >> ${LOG_FILE}
    echo "No database backup in last 24 hours" | mail -s "Backup Alert: Missing Database Backup" ${ALERT_EMAIL}
fi

if [ ${LAST_APP_BACKUP} -eq 0 ]; then
    echo "$(date): ALERT: No application backup in last 7 days" >> ${LOG_FILE}
    echo "No application backup in last 7 days" | mail -s "Backup Alert: Missing Application Backup" ${ALERT_EMAIL}
fi

if [ ${CORRUPT_BACKUPS} -gt 0 ]; then
    echo "$(date): ALERT: ${CORRUPT_BACKUPS} corrupt backups found" >> ${LOG_FILE}
    echo "${CORRUPT_BACKUPS} corrupt backups found" | mail -s "Backup Alert: Corrupt Backups" ${ALERT_EMAIL}
fi

# Check cloud backup sync
if [ -n "$CLOUD_BACKUP_ENABLED" ] && [ "$CLOUD_BACKUP_ENABLED" = "true" ]; then
    aws s3 ls s3://thesis-grey-backups/database/ --recursive | tail -1 > /tmp/last_cloud_backup
    LAST_CLOUD_BACKUP=$(cat /tmp/last_cloud_backup | awk '{print $1}')
    TODAY=$(date +%Y-%m-%d)
    
    if [ "$LAST_CLOUD_BACKUP" != "$TODAY" ]; then
        echo "$(date): ALERT: Cloud backup not current" >> ${LOG_FILE}
        echo "Cloud backup not current. Last backup: $LAST_CLOUD_BACKUP" | mail -s "Backup Alert: Cloud Backup Outdated" ${ALERT_EMAIL}
    fi
fi

echo "$(date): Backup monitoring completed" >> ${LOG_FILE}
```

### Backup Dashboard

```python
#!/usr/bin/env python3
# /opt/thesis-grey/scripts/backup_dashboard.py

import os
import glob
import json
from datetime import datetime, timedelta
from pathlib import Path

def generate_backup_status():
    """Generate backup status report."""
    
    backup_dir = Path("/opt/thesis-grey/backups")
    report = {
        "timestamp": datetime.now().isoformat(),
        "database_backups": [],
        "application_backups": [],
        "static_backups": [],
        "status": "OK",
        "alerts": []
    }
    
    # Check database backups
    db_backups = sorted(glob.glob(str(backup_dir / "database" / "full_backup_*.sql.gz")))
    for backup in db_backups[-5:]:  # Last 5 backups
        stat = os.stat(backup)
        report["database_backups"].append({
            "file": os.path.basename(backup),
            "size": stat.st_size,
            "created": datetime.fromtimestamp(stat.st_mtime).isoformat()
        })
    
    # Check if latest backup is within 24 hours
    if db_backups:
        latest_backup = max(db_backups, key=os.path.getmtime)
        backup_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(latest_backup))
        if backup_age > timedelta(hours=25):  # Allow 1 hour grace
            report["alerts"].append(f"Database backup is {backup_age} old")
            report["status"] = "WARNING"
    else:
        report["alerts"].append("No database backups found")
        report["status"] = "ERROR"
    
    # Check application backups
    app_backups = sorted(glob.glob(str(backup_dir / "application" / "app_backup_*.tar.gz")))
    for backup in app_backups[-3:]:  # Last 3 backups
        stat = os.stat(backup)
        report["application_backups"].append({
            "file": os.path.basename(backup),
            "size": stat.st_size,
            "created": datetime.fromtimestamp(stat.st_mtime).isoformat()
        })
    
    # Save report
    with open("/opt/thesis-grey/backups/status.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(json.dumps(report, indent=2))
    
    return report["status"] == "OK"

if __name__ == "__main__":
    success = generate_backup_status()
    exit(0 if success else 1)
```

## Backup Security

### Encryption for Offsite Backups

```bash
#!/bin/bash
# /opt/thesis-grey/scripts/encrypt_backup.sh

BACKUP_FILE=$1
GPG_RECIPIENT="backup@your-domain.com"
ENCRYPTED_FILE="${BACKUP_FILE}.gpg"

# Encrypt backup file
gpg --trust-model always --encrypt --recipient ${GPG_RECIPIENT} --output ${ENCRYPTED_FILE} ${BACKUP_FILE}

if [ $? -eq 0 ]; then
    echo "Backup encrypted successfully: ${ENCRYPTED_FILE}"
    
    # Upload encrypted backup to cloud
    aws s3 cp ${ENCRYPTED_FILE} s3://thesis-grey-secure-backups/
    
    # Remove unencrypted local copy
    rm ${BACKUP_FILE}
    
else
    echo "Backup encryption failed"
    exit 1
fi
```

### Access Control for Backup Files

```bash
# Set proper permissions for backup files
chmod 600 /opt/thesis-grey/backups/database/*.gz
chmod 600 /opt/thesis-grey/backups/application/*.tar.gz
chmod 700 /opt/thesis-grey/backups/

# Restrict access to backup scripts
chmod 750 /opt/thesis-grey/scripts/backup_*.sh
chown thesis-grey:thesis-grey /opt/thesis-grey/scripts/backup_*.sh
```

## Disaster Recovery Plan

### Complete System Recovery

1. **Assess the situation**
   - Determine scope of data loss
   - Identify recovery point objective

2. **Prepare new environment**
   - Provision new server if needed
   - Install base system and dependencies

3. **Restore system configuration**
   - Restore from system configuration backup
   - Configure network and security settings

4. **Restore database**
   - Use latest full backup
   - Apply WAL files for point-in-time recovery if needed

5. **Restore application**
   - Deploy application code from backup
   - Configure environment variables and secrets

6. **Restore static files**
   - Restore user uploads and static assets

7. **Verify system integrity**
   - Run application tests
   - Verify user access and functionality

8. **Update DNS and routing**
   - Point domain to new server
   - Update load balancer configuration

## Backup Schedule Summary

| Component | Frequency | Retention | Storage Location |
|-----------|-----------|-----------|------------------|
| Database Full | Daily 2:00 AM | 30 days local, 12 months cloud | Local + S3 |
| Database WAL | Continuous | 7 days local, 30 days cloud | Local + S3 |
| Application | Weekly | 4 weeks local, 12 weeks cloud | Local + S3 |
| Static Files | Daily | 30 days local, 12 months cloud | Local + S3 |
| System Config | Weekly | 12 weeks local, 12 months cloud | Local + S3 |
| User Data Export | Monthly | 12 months | Local + S3 |

## Contact Information

**Backup Administrator**: backup-admin@your-domain.com  
**Emergency Contact**: +1-555-0123  
**Cloud Provider Support**: AWS/Azure/GCP Support  

---

**Document Status**: ✅ Complete  
**Review Date**: 2025-11-30  
**Next Update**: As needed for infrastructure changes