#!/bin/bash
source /etc/profile
source /home/oracle/.bash_profile
BAK_SRC_DIR=/home/backup/rman
BAK_DST_DIR=/home/oracle/backup/rman_bak

DATE=$(date +%Y%m%d)

rman target / << EOF
run {
BACKUP AS COMPRESSED BACKUPSET DATABASE PLUS ARCHIVELOG;
}
crosscheck backup of database;
crosscheck archivelog all;
delete noprompt obsolete;
delete noprompt expired backup;
delete noprompt backup completed before 'sysdate-7';
EOF

tar -zcvf $BAK_DST_DIR/ora_rman_bak_all_$DATE.tar.gz `ls $BAK_SRC_DIR/full_*_${DATE}_bak`
md5sum $BAK_DST_DIR/ora_rman_bak_all_$DATE.tar.gz | awk '{print $1}' > $BAK_DST_DIR/md5sum

# delete last week backup file
find $BAK_DST_DIR/ora_rman_bak_all_*.tar.gz -type f -mtime +7 -exec rm {} \;

rsync -av --delete --bwlimit=4096 /home/oracle/backup/rman_bak/ ip:/home/oracle/backup/rman_bak
