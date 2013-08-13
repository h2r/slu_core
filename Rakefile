here=File.dirname(__FILE__)
$slu_home=File.expand_path("#{here}")
require "#{here}/rakefile.rb"

task :apt do
  sh "sudo apt-get install python-numpy pyqt4-dev-tools python-nltk"
end

task :setup do
  mkdir_p($include_build_dir)
  mkdir_p($python_build_dir)
  mkdir_p($jar_build_dir)
  mkdir_p($data_home)
  sh "echo \"import nltk; nltk.download('wordnet')\" | rake python"
  sh "cd tools/stanford_parser && make setup"
  sh "cd tools/mallet && make setup"
#  sh "cd tools/reconcile && make setup"
  sh "cd tools/jpype && make setup"
  sh "cd tools/utilities && make setup"
  sh "cd tools/features && make setup"
  sh "rake buildGui"
  sh "rake touch"
end

task :touch do 
  sh "find tools -mount -name '*.py'"
  sh "find tools -mount -name '*.c'"
  sh "find tools -mount -name '*.java'"
  sh "rm -rf build/last_build"
end

task :buildGui do
  sh "cd tools/esdcs && rake buildGui"
  sh "cd tools/forklift && rake buildGui"
  sh "cd tools/g3 && rake buildGui"
end

task :default => [:setup, :everything]


task :build_carmen do
  carmen = "#{here}/nlp/3rdParty/carmen/carmen"
  sh "cd #{carmen}/src/ && echo -e 'Y\nY\nY\n\n\n8\n' | ./configure"
  sh "cd #{carmen}/src && make ECHO=echo"
  sh "cd #{carmen}/src/python && make all ECHO=echo"
end

task :clean do
  sh "make clean"
end

task :clean_build => [:clean,
                      :touch,
                      :everything]
