# sublime-find-function-definition

Sublime Text 2 plugin to find and open a function's declaration in your project

##Installation

### The easy way...

1. Just use [Package Control](https://github.com/wbond/package_control_channel) to install it
 
### The slightly less (but still fairly) easy way...

1. Click Preferences -> Browse Packages
2. Download the source code folder and paste into the packages folder
 
### The slightly geeky way...

1. `git clone` this repo into your sublime packages directory

## Usage

Highlight a function and either hit F8 or right click and go to `Find Function Definition`.  Plugin will search your project for the function and open a file up to it, or if multiple instances found display a list of files to open.

Takes into account `folder_exclude_patterns` and `file_exclude_patterns` settings.

## Settings

The following function definition patterns are used by default, but you can add your own by going to `Preferences` -> `Package Settings` -> `Find Function Definition` -> `Settings - User`

```
{
  "definitions": /* where $NAME$ is the name of the function */
  [
    "function $NAME$",
    "$NAME$: function",
    "$NAME$:function",
    "$NAME$ = function",
    "$NAME$= function",
    "$NAME$=function",
    "def $NAME$("
  ],
  "file_exclude_patterns": [] /* optional list of files to exclude, falls back to global setting if not set */
}
```
