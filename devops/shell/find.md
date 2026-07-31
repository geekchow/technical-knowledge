# find

## purely find 
```shell
# find all *.md files under current directory
# first mandatory param: search directory
# -type: f -> file; d -> directory
# -name: name pattern
find . -type f -name *.md

# `find` search all subdirectories by default, 
# but we can specify depth with param -maxdepth
# maxdepth 1 represent only search current directory.
# Caution: for zsh on mac, name pattern with * must be quoted 
# for eg: `*.md`, otherwise zsh can't interpert your cmd.
find . -maxdepth 2 -type f -name *.md

```

## find combine exec
```shell

# find all markdown files and list the details.
find . -type f -name "*.md" -exec ls -l {} \;

# make 'phil' to be all txt file owner
find /home/user -name *.txt -exec chown phil {} \;

# list all mp3 files and printout the file info
find . -type f -name "*.mp3" -exec file {} \;
```

> references
- https://stackoverflow.com/questions/12753889/why-is-zsh-globbing-not-working-with-find-command
- https://www.baeldung.com/linux/find-exec-command