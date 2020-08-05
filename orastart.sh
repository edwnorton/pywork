#!/bin/bash
LINE=devdb:/home/oracle/product/11.2.0/db_1:Y

LOGMSG="logger -puser.alert -s "

trap 'exit' 1 2 3

# for script tracing
case $ORACLE_TRACE in
  T) set -x ;;
esac
    
# Set path if path not set (if called from /etc/rc)
SAVE_PATH=/bin:/usr/bin:/etc:${PATH} ; export PATH
SAVE_LLP=$LD_LIBRARY_PATH

# First argument is used to bring up Oracle Net Listener
ORACLE_HOME_LISTNER=$ORACLE_HOME
if [ ! $ORACLE_HOME_LISTNER ] ; then
  echo "ORACLE_HOME_LISTNER is not SET, unable to auto-start Oracle Net Listener"
  echo "Usage: $0 ORACLE_HOME"
else
  LOG=$ORACLE_HOME_LISTNER/listener.log

  # Set the ORACLE_HOME for the Oracle Net Listener, it gets reset to
  # a different ORACLE_HOME for each entry in the oratab.
  ORACLE_HOME=$ORACLE_HOME_LISTNER ; export ORACLE_HOME

  # Start Oracle Net Listener
  if [ -x $ORACLE_HOME_LISTNER/bin/tnslsnr ] ; then
    echo "$0: Starting Oracle Net Listener" >> $LOG 2>&1
    $ORACLE_HOME_LISTNER/bin/lsnrctl start >> $LOG 2>&1 &
    VER10LIST=`$ORACLE_HOME_LISTNER/bin/lsnrctl version | grep "LSNRCTL for " | cut -d' ' -f5 | cut -d'.' -f1`
    export VER10LIST
  else
    echo "Failed to auto-start Oracle Net Listener using $ORACLE_HOME_LISTNER/bin/tnslsnr"
  fi
fi

checkversionmismatch() {
  if [ $VER10LIST ] ; then
    VER10INST=`sqlplus -V | grep "Release " | cut -d' ' -f3 | cut -d'.' -f1`
    if [ $VER10LIST -lt $VER10INST ] ; then
      $LOGMSG "Listener version $VER10LIST NOT supported with Database version $VER10INST"
      $LOGMSG "Restart Oracle Net Listener using an alternate ORACLE_HOME_LISTNER:"
      $LOGMSG "lsnrctl start"
    fi
  fi
}



# Starts a Database Instance
startinst() {
  # Called programs use same database ID
  export ORACLE_SID

  # Put $ORACLE_HOME/bin into PATH and export.
  PATH=$ORACLE_HOME/bin:${SAVE_PATH} ; export PATH
  # add for bug # 652997
  LD_LIBRARY_PATH=${ORACLE_HOME}/lib:${SAVE_LLP} ; export LD_LIBRARY_PATH
  PFILE=${ORACLE_HOME}/dbs/init${ORACLE_SID}.ora
  SPFILE=${ORACLE_HOME}/dbs/spfile${ORACLE_SID}.ora
  SPFILE1=${ORACLE_HOME}/dbs/spfile.ora

  echo ""
  echo "$0: Starting up database \"$ORACLE_SID\""
  date
  echo ""

  checkversionmismatch

  # See if it is a V6 or V7 database
  VERSION=undef
  if [ -f $ORACLE_HOME/bin/sqldba ] ; then
    SQLDBA=sqldba
    VERSION=`$ORACLE_HOME/bin/sqldba command=exit | awk '
      /SQL\*DBA: (Release|Version)/ {split($3, V, ".") ;
      print V[1]}'`
    case $VERSION in
      "6") ;;
      *) VERSION="internal" ;;
    esac
  else
    if [ -f $ORACLE_HOME/bin/svrmgrl ] ; then
      SQLDBA=svrmgrl
      VERSION="internal"
    else
      SQLDBA="sqlplus /nolog"
    fi
  fi

  STATUS=1
  if [ -f $ORACLE_HOME/dbs/sgadef${ORACLE_SID}.dbf ] ; then
    STATUS="-1"
  fi
  if [ -f $ORACLE_HOME/dbs/sgadef${ORACLE_SID}.ora ] ; then
    STATUS="-1"
  fi
  pmon=`ps -ef | grep -w "ora_pmon_$ORACLE_SID"  | grep -v grep`
  if [ "$pmon" != "" ] ; then
    STATUS="-1"
    $LOGMSG "Warning: ${INST} \"${ORACLE_SID}\" already started."
  fi

  if [ $STATUS -eq -1 ] ; then
    $LOGMSG "Warning: ${INST} \"${ORACLE_SID}\" possibly left running when system went down (system crash?)."
    $LOGMSG "Action: Notify Database Administrator."
    case $VERSION in
      "6")  sqldba "command=shutdown abort" ;;
      "internal")  $SQLDBA $args <<EOF
connect internal
shutdown abort
EOF
        ;;
      *)  $SQLDBA $args <<EOF
connect / as sysdba
shutdown abort
quit
EOF
        ;;
    esac

    if [ $? -eq 0 ] ; then
      STATUS=1
    else
      $LOGMSG "Error: ${INST} \"${ORACLE_SID}\" NOT started."
    fi
  fi

  if [ $STATUS -eq 1 ] ; then
    if [ -e $SPFILE -o -e $SPFILE1 -o -e $PFILE ] ; then
      case $VERSION in
        "6")  sqldba command=startup ;;
        "internal")  $SQLDBA <<EOF 
connect internal
startup
EOF
          ;;
        *)  $SQLDBA <<EOF 
connect / as sysdba
startup
quit
EOF
          ;;
      esac

      if [ $? -eq 0 ] ; then
        echo "" 
        echo "$0: ${INST} \"${ORACLE_SID}\" warm started." 
      else
        $LOGMSG "" 
        $LOGMSG "Error: ${INST} \"${ORACLE_SID}\" NOT started." 
      fi
    else
      $LOGMSG "" 
      $LOGMSG "No init file found for ${INST} \"${ORACLE_SID}\"." 
      $LOGMSG "Error: ${INST} \"${ORACLE_SID}\" NOT started." 
    fi
  fi
}


ORACLE_SID=`echo $LINE | awk -F: '{print $1}' -`
if [ "$ORACLE_SID" = '*' ] ; then
  # same as NULL SID - ignore this entry
  ORACLE_SID=""
  continue
fi
# Proceed only if last field is 'Y'.
if [ "`echo $LINE | awk -F: '{print $NF}' -`" = "Y" ] ; then
  INST="Database instance"
  ORACLE_HOME=`echo $LINE | awk -F: '{print $2}' -`
  # Called scripts use same home directory
  export ORACLE_HOME
  # file for logging script's output
  LOG=$ORACLE_HOME/startup.log
  touch $LOG
  chmod a+r $LOG
  echo "Processing $INST \"$ORACLE_SID\": log file $ORACLE_HOME/startup.log"
  startinst >> $LOG 2>&1
fi
