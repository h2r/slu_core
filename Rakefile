here=File.dirname(__FILE__)
$home=File.expand_path("#{here}")
require "#{here}/rakefile.rb"

task :setup do
  mkdir_p($include_build_dir)
  mkdir_p($python_build_dir)
  mkdir_p($jar_build_dir)
  mkdir_p($data_home)
  sh "echo \"import nltk; nltk.download('wordnet')\" | rake python"
  sh "cd tools/stanford_parser && make setup"
  sh "cd tools/mallet && make setup"
  sh "cd tools/jpype && make setup"
  sh "cd tools/features && make setup"
  sh "rake touch"
  sh "rake everything"
end

task :touch do 
  sh "find tools -mount -name '*.py'"
  sh "find tools -mount -name '*.c'"
  sh "find tools -mount -name '*.java'"
  sh "rm -rf build/last_build"
end


task :default => [:setup, :everything]

task :clean do
  sh "make clean"
end

task :clean_build => [:clean,
                      :touch,
                      :everything]
