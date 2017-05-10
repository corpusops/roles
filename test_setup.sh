#!/usr/bin/env bash
. test_env.sh
for i in $(echo "$IMAGES $CONTROLLER_IMAGE"|xargs -n1|sort -u);do
    img=$(get_user_img $i)
    imgid=$(get_image_id $img)
    if [[ -z $imgid ]];then
        echo "docker pull $img"
        sudo docker pull "$img"
        die_in_error "$img pull failed"
    else
        echo "Using $imgid for $img"
    fi
done
# vim:set et sts=4 ts=4 tw=80:
