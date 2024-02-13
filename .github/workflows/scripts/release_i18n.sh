traverse_dir()
{
  local filepath=$1
  for file in `ls -a $filepath`
  do
    if [ -d $filepath/$file ]
    then
      if [ $file != '.' ] && [ $file != '..' ]
      then
        traverse_dir $filepath/$file
      fi
    else
      check_and_release ${filepath}/$file
    fi
  done
}


check_and_release()
{
  local file=$1

  if [ "${file##*.}"x = "ts"x ]
  then
    echo $file
    $LIB_PATH/qt5_applications/Qt/bin/lrelease $file
  fi
}

traverse_dir "src/resources/i18n"
