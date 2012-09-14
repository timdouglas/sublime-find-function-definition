import sublime, sublime_plugin
import subprocess
import re
import functools
import os

#borrowed from Git Plugin by David Lynch
#https://github.com/kemayo/sublime-text-2-git/
def do_when(conditional, callback, *args, **kwargs):
  if conditional():
      return callback(*args, **kwargs)
  sublime.set_timeout(functools.partial(do_when, conditional, callback, *args, **kwargs), 50)

#Gets current word and performs a grep on project folders
#to see if it has a function definition or not
class GoToFunctionCommand(sublime_plugin.TextCommand):
  def run(self, text):
    view = self.view

    #get current word
    selection_region = view.sel()[0]
    word_region = view.word(selection_region)
    word = view.substr(word_region).strip()
    word = re.sub('[\(\)\{\}\s]', '', word)

    #get folders to search
    window = sublime.active_window()
    proj_folders = window.folders()
    nodir = self.getExcludedDirs(view)

    if word != "":
      print "[Go2Function] Searching for 'function "+word+"'..."

      for dir in proj_folders:
        resp = self.doGrep(word, dir, nodir)

        if len(resp) > 0:
          self.openFileToDefinition(resp)
          break

      #if not found show error (ie loop ends without a break)
      else:
        print "[Go2Function] "+word+" not found"
        sublime.error_message("could not find function definition for "+word)

  #actually do the grep
  #well, actually use the native python functions, not grep...
  def doGrep(self, word, directory, nodir):
    out = ()
    terms = self.getSearchTerms(word)

    for r,d,f in os.walk(directory):
      if self.canCheckDir(r, nodir):
        for files in f:
          fn = os.path.join(r, files)
          search = open(fn, "r")
          lines = search.readlines()

          for n, line in enumerate(lines):
            for find in terms:
              if find in line:
                out = (fn, n)
                break

          search.close()

          if len(out) > 0:
            break

        if len(out) > 0:
          break

    return out

  def getSearchTerms(self, word):
    wordstr = str(word)

    #search for normal functions and named anonymous functions
    lookup1 = "function "+wordstr
    lookup2 = wordstr+": function"
    lookup3 = wordstr+":function"
    lookup4 = wordstr+" :function"
    lookup5 = wordstr+" = function"
    lookup6 = wordstr+"= function"
    lookup7 = wordstr+"=function"
    lookup8 = wordstr+" =function"

    return (lookup1, lookup2, lookup3, lookup4, lookup5, lookup6, lookup7, lookup8)

  def getExcludedDirs(self, view):
    #this gets the folder_exclude_patterns from the settings file, not the project file
    dirs = view.settings().get("folder_exclude_patterns", [".git", ".svn", "CVS", ".hg"]) #some defaults
    return dirs

  def canCheckDir(self, dir, excludes):
    count = 0

    #potentially quite expensive - better way?
    for no in excludes:
      if no not in dir:
        count = count + 1

    if count == len(excludes):
      return True
    else:
      return False


  #open the file and scroll to the definition
  def openFileToDefinition(self, response):
    file, line = response

    print "[Go2Function] Opening file "+file+" to line "+str(line)
    
    line = line - 1

    window = sublime.active_window()
    new_view = window.open_file(file)

    do_when(
      lambda: not new_view.is_loading(), 
      lambda: new_view.set_viewport_position(new_view.text_to_layout(new_view.text_point(line, 0)))
    )