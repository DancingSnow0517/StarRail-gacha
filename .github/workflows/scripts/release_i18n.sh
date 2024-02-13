traverse_dir()
{
  filepath="src/resources/i18n"
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
  file=$1

  if [ "${file##*.}"x = "ts"x ]
  then
    echo $file
    lrelease $file
  fi
}
