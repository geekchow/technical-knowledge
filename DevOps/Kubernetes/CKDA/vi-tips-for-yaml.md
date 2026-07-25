# VI tips for K8S yaml edtion

## intent 

`~/.vimrc`
- <Tab> inserts 2 real spaces
- Indentation (>>, auto-formatting) uses 2 spaces
- No real tab characters appear in the file

```bash
set tabstop=2 shiftwidth=2 expandtab
```


## Navigate 

```bash
# go to begigning
gg

# go to end
G

# goto line 8
:8

# search in cmd 'n': next occurrence.
/keyword

```

## Editing

```bash
# open a new line
o

# undo
u

# indent the current line 
shift + > 
shit + <

# indent 5 lines 
5>>
5<<

## substitution
# replace the first occurence
:s/old/new

# replace all occurence in current line 
:s/old/new/g

# replace all occurences in current file
:%s/old/new/g

# Replace keyword with confirmation
:%s/old/new/gc
# y = yes
# n = no
# a = all
# q = quit
# l = last one

# in visual mode 
# copy selected lines
y
# paste selected lines
p
```

### Deletion 

```bash


# delete a line
dd 

# delete to line end 
d$

# delete to begining
d0

# delete 3 lines from the cursor
3dd

# delet to the next word
dw

## by defalut `d` delete actually do cut, so you can do paste with p
p
```

