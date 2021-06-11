#!/bin/bash
source /etc/profile
source /home/oracle/.bash_profile
BAK_SRC_DIR=/home/backup
BAK_DST_DIR=/home/oracle/backup/expdp_bak

DATE=$(date +%Y%m%d)
stime=`date +%s`
echo `date +"%F %T"`################### 全库备份开始##################

expdp system/WYNY888! directory=backup dumpfile=ora_expdp_bak_all_${DATE}.dmp logfile=ora_expdp_bak_all_${DATE}.log buffer=1024000 full=y

tar -zcvf $BAK_DST_DIR/ora_expdp_bak_all_$DATE.tar.gz `ls $BAK_SRC_DIR/ora_expdp_bak_all_${DATE}.dmp`
md5sum $BAK_DST_DIR/ora_expdp_bak_all_$DATE.tar.gz | awk '{print $1}' > $BAK_DST_DIR/md5sum

rm $BAK_SRC_DIR/ora_expdp_bak_all_$DATE.dmp

# delete last week backup file
find $BAK_DST_DIR/ora_expdp_bak_all_*.tar.gz -type f -mtime +6 -exec rm {} \;

rsync -av --delete --bwlimit=4096 /home/oracle/backup/expdp_bak/ 1.1.1.1:/home/oracle/backup/expdp_bak

etime=`date +%s`
s=`echo "scale=0; ($etime - $stime)%60" | bc`
m=`echo "scale=0; ($etime - $stime)/60%60" | bc`
h=`echo "scale=0; ($etime - $stime)/60/60" | bc`

echo `date +"%F %T"`################全库备份结束#####################
echo `date +"%F %T"` end 脚本执行耗时 $h 小时 $m 分钟 $s 秒
