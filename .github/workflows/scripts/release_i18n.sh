traverse_dir()
{
  filepath=$1
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
    $Python_ROOT_DIR/site-packages/qt5_applications/Qt/bin/lrelease $file
  fi
}

traverse_dir "src/resources/i18n"
