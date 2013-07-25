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
  files = []
  excludedFiles = None
  excludedDirs = None
  settings = None

  def run(self, text):
    self.settings = sublime.load_settings("go2function.sublime-settings")
    self.excludedDirs = self.settings.get("folder_exclude_patterns")
    # sublime.message_dialog(str(self.excludedDirs))
    view = self.view

    #get current word
    selection_region = view.sel()[0]
    word_region = view.word(selection_region)
    word = view.substr(word_region).strip()
    word = re.sub('[\(\)\{\}\s]', '', word)

    #get folders to search
    window = sublime.active_window()
    proj_folders = window.folders()

    if word != "":
      print "[Go2Function] Searching for 'function "+word+"'..."
      files = []

      for dir in proj_folders:
        resp = self.doGrep(word, dir, self.getExcludedDirs(view))
        if len(resp) > 0:
          files.append(resp)

      if len(files) == 0:
        print "[Go2Function] "+word+" not found"
        sublime.error_message("could not find function definition for "+word)
      elif len(files) == 1:
        self.openFileToDefinition(files[0])
      else:
        self.files = files
        paths = []

        for path,line in files:
          paths.append(path+":"+str(line))

        window.show_quick_panel(paths, lambda i: self.selectFile(i))

  def selectFile(self, index):
    if index > -1 and len(self.files) > index:
      self.openFileToDefinition(self.files[index])

  #actually do the search
  def doGrep(self, word, directory, nodir):
    out = ()
    search_terms = self.getSearchTerms(word)
    # sublime.message_dialog(str(self.excludedDirs))
    for r,d,f in os.walk(directory):
      
      if self.canCheckDir(r, nodir):
        for files in f:
          fn = os.path.join(r, files)

          if self.canCheckFile(fn): #a long list of patterns can slow this down...
            search = open(fn, "r")
            lines = search.readlines()

            for n, line in enumerate(lines):
              
              for find in search_terms:
                
                if find in line:
                  out = (fn, n)
                  break

            search.close()

    return out

  def getSearchTerms(self, word):
    wordstr = str(word)
    definitions = self.settings.get("definitions")
    lookup = []

    for func in definitions:
      lookup.append(str(re.sub('\$NAME\$', wordstr, func)))

    return lookup

  def getExcludedDirs(self, view):
    #this gets the folder_exclude_patterns from the settings file, not the project file
    if self.excludedDirs:
      return self.excludedDirs
    else:
      dirs = view.settings().get("folder_exclude_patterns", [".git", ".svn", "CVS", ".hg"]) #some defaults
      self.excludedDirs = dirs
      return dirs

  def getExcludedFiles(self):
    if self.excludedFiles:
      return self.excludedFiles
    else:
      #check plugin settings, then global
      patterns = self.settings.get("file_exclude_patterns", self.view.settings().get("file_exclude_patterns"))

      #no file_exclude rules
      if not patterns:
        return None

      #merge patterns into single regex
      rpatterns = []

      for pattern in patterns:
        pattern = re.sub('\*\.', '.', pattern)
        pattern = re.escape(str(pattern))
        rpatterns.append(pattern)

      combined = "(" + ")|(".join(rpatterns) + ")"

      #store regex
      self.excludedFiles = combined

      return combined

  def canCheckDir(self, dir, excludes):
    for exclude in excludes:
      if exclude in dir:
        return False

    return True

  def canCheckFile(self, filename):
    patterns = self.getExcludedFiles()

    if not patterns:
      return True

    if(re.match(patterns, filename)):
      return False

    return True

  #open the file and scroll to the definition
  def openFileToDefinition(self, response):
    file, line = response

    print "[Go2Function] Opening file "+file+" to line "+str(line)
    
    window = sublime.active_window()
    new_view = window.open_file(file)

    do_when(
      lambda: not new_view.is_loading(), 
      lambda: self.cursorToPos(new_view, line)
    )

  #move cursor to the definition too
  def cursorToPos(self, view, line):
    nav_line = line - 1
    nav_pt = view.text_point(nav_line, 0)
    fn_line = line
    pt = view.text_point(fn_line, 0)

    view.set_viewport_position(view.text_to_layout(nav_pt))

    view.sel().clear()
    view.sel().add(sublime.Region(pt))

    view.show(pt)
