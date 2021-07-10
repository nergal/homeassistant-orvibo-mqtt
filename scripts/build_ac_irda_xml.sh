#!/bin/bash
#######################################################################
### This is a helper for learning IR codes from a remote for an A/C ###
#######################################################################

FAN_MODES=("auto" "low" "medium" "high")
TEMPERATURE_MODES=("cool" "heat" "auto")
SWING_MODES=("on" "off")
MIN_TEMPERATURE=18
MAX_TEMPERATURE=30
SWING_MODE="swing"
ON_MODE="on"
OFF_MODE="off"
DRY_MODE="dry"
FAN_MODE="fan_only"

CHECK=false

function readCode {
    IP=$1
    FILENAME=$2
    VALUE_KEY=$3

    if [ "$CHECK" = true ]; then
        SHOULD_COMPLETE=$(cat $FILENAME | grep "\"$VALUE_KEY\"")
        if [ $? -eq 0 ]; then
            echo "Record for ${VALUE_KEY} already present, skipping"
            return
        fi
    fi

    read -p "Reading ${VALUE_KEY} from ${IP}... ready?"
    
    temp_file=$(mktemp)
    pipenv run python -c "import orvibo;device = orvibo.Orvibo('${IP}');print('Learning...');device.learn('${temp_file}', timeout=15)"

    VALUE=$(cat $temp_file | hexdump -e '16/2 "%04x " " "' | sed -e 's/  //g')

    echo "    <code name=\"${VALUE_KEY}\">" >> $FILENAME
    echo "      <ccf>${VALUE}</ccf>" >> $FILENAME
    echo "    </code>" >> $FILENAME
    echo "Ready! Value is [${VALUE:40:99}...]"
    echo ""
}

echo "This is a helper for learning IR codes from a remote for an A/C"
echo "Please, follow the instructins below. The output will be an XML file suitable for \`commands_set\` option in the config"
echo ""

read -p "Enter the name of the template: " filename

FILENAME="etc/${filename}.xml"

if [ -f "$FILENAME" ]; then
    CHECK=true
    echo "File exists at ${FILENAME}"
    echo "Entering completion mode..."
fi

read -p "Enter the IP of AllOne device: " IP

if [ "$CHECK" = false ]; then
    read -p "Enter the name of the device: " name
    echo "<lircremotes>" > $FILENAME
    echo "  <remote name=\"${name}\">" >> $FILENAME
else
    echo "Do not want to put headers in completion mode"
fi

read -p "Enter minimal allowed temperature [18]: " min_temp
read -p "Enter maximal allowed temperature [30]: " max_temp
min_temp=${min_temp:-MIN_TEMPERATURE}
max_temp=${max_temp:-MAX_TEMPERATURE}

echo "Using ${FILENAME}..."
echo ""

readCode $IP $FILENAME $ON_MODE
readCode $IP $FILENAME $OFF_MODE

for fanMode in ${FAN_MODES[*]}
do
    for tempMode in ${TEMPERATURE_MODES[*]}
    do
    
        for ((temp=$min_temp;temp<=$max_temp;temp++))
        do
            readCode $IP $FILENAME "${tempMode}_t${temp}_${fanMode}"
        done
    done
    readCode $IP $FILENAME "${FAN_MODE}_${fanMode}"
    readCode $IP $FILENAME "${DRY_MODE}_${fanMode}"
done

for swingMode in ${SWING_MODES[*]}
do
    readCode $IP $FILENAME "${SWING_MODE}_${swingMode}"
done

echo "  </remote>" >> $FILENAME
echo "</lircremotes>" >> $FILENAME